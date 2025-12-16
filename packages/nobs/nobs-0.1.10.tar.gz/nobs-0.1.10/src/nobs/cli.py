from contextlib import suppress
import functools
import json
from pathlib import Path
from uuid import uuid4
import click
import logging
import asyncio

from docker import DockerClient
from pydantic import BaseModel, SecretStr, ValidationError
from rich.console import Console
from rich.panel import Panel
from rich.status import Status
from rich.text import Text

from nobs.docker import build_image, find_lockfile, packages_from_lockfile
from nobs.models import Job, NetworkApp, Project, Subscriber, NobsClient, NobsServer
from nobs.runners import default_runner


logger = logging.getLogger(__name__)
console = Console()

def async_(func):  # noqa
    """Decorator to run async functions."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):  # noqa
        return asyncio.run(func(*args, **kwargs))

    return wrapper


@click.group()
def cli():
    from dotenv import load_dotenv

    logging.basicConfig(level=logging.INFO)
    load_dotenv(".env")
    pass


def read_project_at(ref: str | None = None, env: str | None = None) -> Project:
    import sys


    if ref is None:
        ref = "project:project"

    path = Path.cwd().as_posix()
    if path not in sys.path:
        sys.path.append(path)

    return project_at(ref)


def project_at(ref: str, env: str | None = None) -> Project:
    import importlib
    import os

    if env:
        os.environ["NOBS_ENV"] = env

    module_name, attr_name = ref.split(":")

    module = importlib.import_module(module_name)
    project = getattr(module, attr_name)

    assert isinstance(project, Project), f"Expected a project got '{type(project)}'"

    return project


@cli.command()
@click.option("--ref")
@click.option("--server")
@click.option("--env", default="test")
@click.option("--no-push", is_flag=True)
@click.option("--create-resources", is_flag=True)
@click.option("--experimental", is_flag=True)
@click.option("--context")
@async_
async def deploy(
    ref: str | None, 
    server: str | None, 
    env: str, 
    no_push: bool, 
    experimental: bool = False,
    context: str | None = None,
    create_resources: bool = False
) -> None:
    import sys

    click.echo("Deploying project")

    path = Path.cwd().as_posix()

    if ref is None:
        ref = "project:project"

    if server:
        config = NobsServer(nobs_api=server) # type: ignore
    else:
        config = NobsServer.read()

    if path not in sys.path:
        sys.path.append(path)

    project = project_at(ref, env)


    lockfile_info = packages_from_lockfile(
        find_lockfile()
    )

    if not no_push:
        local_image = build_image(
            project, 
            tag=env, 
            context=context, 
        )
        await push_image(project, env, local_image)
        logger.info("Source image is updated")

    client = NobsClient(settings=config)
    res = await client.update(project, env=env, packages=lockfile_info.packages)

    if create_resources:
        await client.deploy(res.project_env_id)



@cli.command()
@click.argument("name")
@click.option("--ref")
@click.option("--platform")
@async_
async def run(name: str, ref: str | None, platform: str | None) -> None:
    import sys
    import inspect

    if ref is None:
        ref = "project:project"

    path = Path.cwd().as_posix()
    if path not in sys.path:
        sys.path.append(path)

    if platform is None:
        platform = "linux/amd64"

    project = project_at(ref)

    if name not in project.components:
        raise ValueError(f"Unable to find '{name}'")

    comp = project.components[name]

    logger.info(comp)

    if isinstance(comp, NetworkApp):
        command = comp.command
    elif isinstance(comp, Job):
        from dotenv import load_dotenv

        load_dotenv()

        if inspect.iscoroutinefunction(comp.main_function):
            await comp.main_function(comp.arguments)
        else:
            comp.main_function(comp.arguments)
        return
    elif isinstance(comp, Subscriber):
        return
    else:
        command = comp.network_app(Path.cwd()).command

    logger.info(f"Running command {command} in docker file {project.docker_image}")

    if project.docker_image:
        command = ["docker", "run", f"--platform={platform}", project.docker_image, *command]

    _ = default_runner(command)




@cli.command()
@click.option("--project-name")
@click.option("--job-id")
@click.option("--file-ref")
@click.option("--args")
@async_
async def run_job(project_name: str, job_id: str, file_ref: str, args: str) -> None:
    import importlib
    import inspect

    click.echo(f"Running ref: {file_ref}")

    try:
        from logging_loki import LokiHandler # type: ignore
        from nobs.secrets import LokiLoggerConfig

        config = LokiLoggerConfig() # type: ignore

        auth = None
        if config.loki_user and config.loki_token:
            auth = (config.loki_user, config.loki_token.get_secret_value())

        handler = LokiHandler(
            url=config.loki_push_endpoint,
            auth=auth,
            tags={"job_function": file_ref},
            version=f"{config.loki_logger_version}"
        )

        logging.basicConfig(level=logging.INFO)
        logging.getLogger("").addHandler(handler)
        logger.info("Managed to setup Loki logger")
    except Exception as e:
        print(f"Unable to setup Loki logger for '{file_ref}' due to error: {e}")

    logger.info(f"Running function at '{file_ref}'")
    file, function_name = file_ref.split(":")

    function_module = importlib.import_module(file)
    function = getattr(function_module, function_name)

    assert callable(function)
    sign = inspect.signature(function)   
    params = sign.parameters
    if len(params) == 0:
        if inspect.iscoroutinefunction(function):
            asyncio.run(function())
        else:
            function()
        return

    assert len(params) == 1
    _, param = list(params.items())[0]

    arg_type = param.annotation
    assert not isinstance(arg_type, str), f"Make sure to not use string annotations for {arg_type}"
    assert issubclass(arg_type, BaseModel), f"Expected a subclass of BaseModel got {arg_type}"

    if args:
        encoded_args = arg_type.model_validate_json(args.strip("'"))
    else:
        encoded_args = arg_type()

    try:
        if inspect.iscoroutinefunction(function):
            await function(encoded_args)
        else:
            function(encoded_args)
    except Exception as e:
        logger.exception(e)

        client = NobsClient()
        await client.notify_about_failure(project_name, job_id=job_id, exception=e)

        raise e




@cli.command()
@click.argument("name")
@async_
async def process_queue(name: str) -> None:
    from nobs.secrets import SqsConfig
    from nobs.models import QueueMessage
    from nobs.queue import QueueBroker, SqsQueueBroker

    project = read_project_at()
    assert project.workers, f"Expected at least one worker got {project.workers}"

    queue = next(queue for queue in project.workers if queue.name == name)
    broker: QueueBroker = SqsQueueBroker(
        config=SqsConfig(), # type: ignore
        queue_settings=queue.queue_settings 
    )
    queue = broker.with_name(name)

    logger.info(f"Ready to receive work at queue '{name}'")

    while True:
        messages = await queue.receive()
        while messages:
            message = messages[0]

            try:
                content = QueueMessage.model_validate_json(message.body)

                _, name = content.function_ref.split(":")
                logger.info(f"Running function named '{name}'")

                await content.run()
                await queue.delete(message)
            except Exception as e:
                logger.exception(e)

            if len(messages) > 1:
                messages = messages[1:]
            else:
                messages = await queue.receive()


@cli.command()
@click.argument("name")
@async_
async def subscriber(name: str, ref: str | None = None) -> None:
    import inspect
    import nats

    project = read_project_at(ref)

    sub = project.components[name]
    assert isinstance(sub, Subscriber)

    sign = inspect.signature(sub.method)   
    params = sign.parameters

    assert len(params) == 1
    _, param = list(params.items())[0]

    arg_type = param.annotation
    assert not isinstance(arg_type, str), f"Make sure to not use string annotations for {arg_type}"
    assert issubclass(arg_type, BaseModel), f"Expected a subclass of BaseModel got {arg_type}"

    con = await nats.connect("nats://nats:4222")
    subscriber = await con.subscribe(sub.subject)

    while True:
        try:
            message = await subscriber.next_msg()
        except TimeoutError:
            await asyncio.sleep(1)
            continue

        try:
            content = arg_type.model_validate_json(message.data)
            sub.method(content)
        except ValidationError as e:
            logger.exception(e)
            logger.error("Unable to decode message")
        except Exception as e:
            logger.exception(e)




@cli.command()
@click.option("--env", default="dev")
@click.option("--context", default=None)
@async_
async def up(env: str, ref: str | None = None, context: str | None = None) -> None:
    from hashlib import sha256
    from nobs.docker import compose
    from pathlib import Path 

    current_dir = Path.cwd()
    project = read_project_at(ref)

    client = DockerClient.from_env()
    image = client.images.get(name=f"{project.name}:latest")
    labels = image.attrs.get("Config", {}).get("Labels", {})

    sub_source_dir = labels.get("com.nobspython.source-dir", "")
    source_dir = f"/app/{sub_source_dir}"


    if (current_dir / project.name).is_dir():
        src_dir = current_dir / project.name
        volumes = {
            src_dir.absolute().as_posix(): {
                "bind": f"{source_dir}/{src_dir.name}",
                "mode": "ro"
            }
        }
    elif (current_dir / "src").is_dir():
        src_dir = current_dir / "src"
        volumes = {
            src_dir.absolute().as_posix(): {
                "bind": f"{source_dir}/{src_dir.name}",
                "mode": "ro"
            }
        }
    else:
        import os
        src_dir = current_dir
        volumes = {}

        ignore_paths = [".venv", "venv", ".git", ".cursor", "tests", "__pycache__", ".github"]

        for sub_dir in os.listdir(src_dir.as_posix()):

            if sub_dir in ignore_paths:
                continue

            sub_path = src_dir / sub_dir

            if sub_path.is_dir():
                volumes[sub_path.absolute().as_posix()] = {
                    "bind": f"{source_dir}/{sub_dir}",
                    "mode": "ro"
                }

    # for pyfile in src_dir.glob("*.py"):
    #     if pyfile.is_file():
    #         volumes[pyfile.absolute().as_posix()] = {
    #             "bind": f"{source_dir}/{pyfile.name}",
    #             "mode": "ro"
    #         }

    project_file = Path.cwd() / "project.py"
    if project_file.is_file():
        volumes[project_file.absolute().as_posix()] = {
            "bind": f"{source_dir}/{project_file.name}",
            "mode": "ro"
        }


    for path in project.additional_dirs or []:
        volumes[path.absolute().as_posix()] = {
            "bind": f"{source_dir}/{path.as_posix()}",
            "mode": "ro"
        }


    if env in ["prod", "test"]:
        console.print(Panel(
            f"Loading resources to connect to '[bold yellow]{env}[/bold yellow]'\n"
            "However, this is not supported yet but will be!",
            title="Environment Setup",
            border_style="yellow"
        ))
    else:
        console.print(Panel(
            "Setting up local '[bold green]dev[/bold green]' resources",
            title="Environment Setup",
            border_style="green"
        ))

    should_build = True

    lockfile = find_lockfile()
    lockhash = sha256(lockfile.read_bytes(), usedforsecurity=False).hexdigest()

    key = "com.nobspython.lockhash"

    with suppress(Exception):
        image = client.images.get(name=f"{project.name}:latest")
        labels = image.attrs.get("Config", {}).get("Labels", {})
        if labels.get(key, "") == lockhash:
            should_build = False

    if should_build:
        with Status(f"[bold blue]Building image for {project.name}...", console=console):
            build_image(project, tag="latest", context=context)
        console.print("[bold green]✓[/bold green] Image built successfully")

    volume_names = [Path(path).name for path in volumes.keys()]
    volumes_text = Text()
    volumes_text.append("Mounted volumes: ", style="bold")
    volumes_text.append(", ".join(volume_names), style="cyan")
    console.print(volumes_text)

    compose(
        project, 
        base_image=f"{project.name}:latest",
        volumes=volumes
    )



@cli.command()
@click.option("--context")
@click.option("--tag")
@click.option("--push", is_flag=True)
@async_
async def build(push: bool, tag: str | None = None, ref: str | None = None, context: str | None = None) -> None:
    project = read_project_at(ref)

    if project.docker_image is not None:
        click.echo("Found docker image definition so will skip build.")
        return 

    if not tag:
        tag = "latest"

    local_image = build_image(project, tag, context)

    if push:
        await push_image(project, tag, local_image)


@cli.command()
@click.option("--context")
@click.option("--tag")
@click.option("--push", is_flag=True)
@async_
async def shell(push: bool, tag: str | None = None, ref: str | None = None, context: str | None = None) -> None:
    project = read_project_at(ref)

    if project.docker_image is not None:
        click.echo("Found docker image definition so will skip build.")
        return 


    default_runner([
        "docker", "run", "-it", "--platform=linux/amd64", project.name, "bash"
    ])
    



async def push_image(project: Project, tag: str, local_image: str) -> None:
    from docker import DockerClient
    creds = await NobsClient().docker_creds()

    client = DockerClient.from_env()
    client.login(
        password=creds.password, 
        registry=creds.registry,
        username="nologin"
    )

    repo = f"{creds.registry}/{project.name}:{tag}"

    client.images.get(local_image).tag(
        repository=repo, tag=tag
    )
    client.images.push(repo, tag=tag)
    client.images.remove(repo)



@cli.command()
@click.option("--api", default=None)
@async_
async def auth(api: str | None) -> None:
    import webbrowser
    from nobs.models import default_nobs_file

    settings = NobsServer(nobs_token=SecretStr("auth"))
    if api:
        settings.nobs_api = api

    request_id = uuid4()
    non_api = settings.nobs_api.removesuffix("/api/v1")    
    url = f"{non_api}/users/cli-login/{request_id}"
    webbrowser.open(url)

    client = NobsClient(settings)
    token = await client.auth_cli(request_id)
    settings.nobs_token = SecretStr(secret_value=token)

    output = json.dumps({
        key: value.get_secret_value() if isinstance(value, SecretStr) else value
        for key, value in settings.model_dump().items()
    })
    default_nobs_file.write_text(output)

    click.echo(f"Created token with info {output}")


if __name__ == "__main__":
    cli()
