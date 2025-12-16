import tomli
from threading import Thread
from contextlib import suppress
from dataclasses import dataclass
import logging
from pathlib import Path
from time import sleep
from typing import Literal
from docker import DockerClient
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from nobs.models import CompiledProject, Project, secrets_for, settings_for_secrets
from nobs.runners import default_runner
from nobs.secrets import ResourceTags, S3StorageConfig, settings_for_resources
from hashlib import sha256 

logger = logging.getLogger(__name__)
console = Console()

@dataclass
class Container:
    name: str
    image: str
    restart: str
    environments: dict[str, str]
    volumes: list[str]
    ports: dict[str, int]


def needed_containers(project: CompiledProject) -> tuple[list[Container], dict[ResourceTags, str]]:
    containers = []

    needed_res: set[str] = {
        val.data_type
        for val in project.shared_secrets
        if val.data_type in [ResourceTags.psql_dsn, ResourceTags.redis_dsn]
    }

    resource_tags = set(ResourceTags)

    for secret in project.shared_secrets:
        tags = set(secret.tags).intersection(resource_tags)
        needed_res.update(tags)


    resource_values: dict[ResourceTags, str] = {}

    current_dir = Path.cwd().absolute()
    data_dir = current_dir / ".data"

    for dtype in needed_res:
        if dtype == ResourceTags.psql_dsn:

            protocol = "postgresql"

            with suppress(ImportError):
                import psycopg
                protocol = "postgresql+psycopg"

            with suppress(ImportError):
                import psycopg2
                protocol = "postgresql+psycopg2"

            with suppress(ImportError):
                import asyncpg
                protocol = "postgresql+asyncpg"

            resource_values[ResourceTags.psql_dsn] = f"{protocol}://user:pass@psql:5432/db"
            resource_values[ResourceTags.database_host] = "psql"
            resource_values[ResourceTags.database_name] = "db"
            resource_values[ResourceTags.database_username] = "user"
            resource_values[ResourceTags.database_password] = "pass"
            resource_values[ResourceTags.database_ssl] = "false"

            containers.append(
                Container(
                    name="psql",
                    image="postgres:15",
                    restart="always",
                    environments={
                        "POSTGRES_USER": "user",
                        "POSTGRES_PASSWORD": "pass",
                        "POSTGRES_DB": "db"
                    },
                    volumes=[f"{data_dir.as_posix()}/postgresql:/var/lib/postgresql/data"],
                    ports={"5432/tcp": 5432},
                )
            )

        if dtype == ResourceTags.redis_dsn:
            resource_values[ResourceTags.redis_dsn] = "redis://redis:6379"
            resource_values[ResourceTags.redis_username] = ""
            resource_values[ResourceTags.redis_password] = ""
            containers.append(
                Container(
                    name="redis",
                    image="redis:7.2.11",
                    restart="always",
                    environments={},
                    volumes=[
                        f"{data_dir.as_posix()}/valkey:/data"
                    ],
                    ports={"6379/tcp": 6379},
                )
            )


    if project.subscribers:
        name = "nats"
        nats_url = f"nats://{name}:4222"

        resource_values[ResourceTags.nats_dsn] = nats_url
        containers.append(
            Container(
                name=name,
                image="nats:2.12.2-alpine",
                restart="always",
                environments={},
                volumes=[],
                ports={"4222/tcp": 4222},
            )
        )

    if ResourceTags.loki_push_endpoint in needed_res:

        name = "loki"
        resource_values[ResourceTags.loki_push_endpoint] = f"http://{name}:3100/loki/api/v1/push"

        containers.append(
            Container(
                name=name,
                image="grafana/loki",
                restart="always",
                ports={"3100/tcp": 3100},
                environments={},
                volumes=[],
            )
        )

    needs_localstack = False

    if ResourceTags.s3_secret_key in needed_res:
        needs_localstack = True

    if needs_localstack or project.workers:
        name = "infra"

        resource_values.update({
            ResourceTags.sqs_endpoint: f"http://{name}:4566",
            ResourceTags.sqs_access_key: "local",
            ResourceTags.sqs_secret_key: "local",
            ResourceTags.sqs_region_name: "us-east-1",

            ResourceTags.s3_endpoint: f"http://{name}:4566",
            ResourceTags.s3_access_key: "local",
            ResourceTags.s3_secret_key: "local",
            ResourceTags.s3_region_name: "us-east-1",
            ResourceTags.s3_bucket_name: "local",
        })

        containers.append(
            Container(
                name=name,
                image="localstack/localstack",
                restart="always",
                ports={"4566/tcp": 4566},
                environments={},
                volumes=[
                    "/var/run/docker.sock:/var/run/docker.sock"
                ],
            )
        )

    return (containers, resource_values)


def stream_container(
    container_id: str, 
    container_type: Literal["resource", "app", "worker", "subscriber"]
) -> None:

    color_map = {
        "resource": "blue", 
        "app": "yellow", 
        "worker": "green", 
        "subscriber": "red", 
        "other": "cyan"
    }

    color = color_map.get(container_type, "cyan")

    client = DockerClient.from_env()
    cont = client.containers.get(container_id)
    
    for log in cont.logs(stream=True, follow=True):
        log_text = Text()
        log_text.append(f"[{cont.name}]", style=f"bold {color}")
        log_text.append(" ")
        log_text.append(log.decode('utf-8').rstrip())
        console.print(log_text)

    cont = client.containers.get(container_id)

    status = cont.attrs.get("State", {})
    exit_code = status.get("ExitCode")
    error = status.get("Error")
    is_oom_killed = status.get("OOMKilled")

    logger.info(f"Container {cont.name} {cont.status} with exit code {exit_code}")

    if is_oom_killed:
        logger.error(f"OOM! Consider increasing the the memory limit of {cont.name}")

    if error:
        logger.error(f"Container had error message {error}")




def compose(project: Project, base_image: str, volumes: dict[str, dict[str, str]]) -> None:
    from dotenv.main import dotenv_values, find_dotenv
    from docker.models.containers import Container as ContainerType

    console.print()
    console.print(Panel(
        f"Starting project: [bold cyan]{project.name}[/bold cyan]\n"
        f"Base image: [dim]{base_image}[/dim]",
        title="Docker Compose",
        border_style="blue"
    ))

    env_file = find_dotenv() or ".env"
    dotenvs = dotenv_values(dotenv_path=env_file)

    client = DockerClient.from_env()
    containers: list[ContainerType] = []
    log_treads: list[Thread] = []

    compiled = CompiledProject.from_project(project, packages=[])

    networks = [
        net for net in client.networks.list()
        if net.name == project.name
    ]
    platform_arc = "linux/amd64"

    conts: list[ContainerType] = client.containers.list(
        all=True, filters={"label": "nobs"}
    )

    for cont in conts:
        cont.remove(force=True)

    if networks:
        network = networks[0]
    else:
        network = client.networks.create(name=project.name, driver="bridge")

    application_volume = volumes
    resource_containers, resource_values = needed_containers(compiled)

    for container in resource_containers:
        console.print(f"[bold blue]→[/bold blue] Creating resource: [cyan]{container.name}[/cyan]")

        cont = client.containers.run(
            image=container.image,
            environment=container.environments,
            volumes=container.volumes,
            ports=container.ports,
            network=network.name,
            name=container.name,
            labels=["nobs"],
            detach=True,
            remove=True,

            # restart_policy=container.restart,
            # ports=container.ports,
        )

        console.print(f"[dim]  Waiting for {container.name} to start...[/dim]")
        while cont.status != "running":
            cont = client.containers.get(cont.id)
            sleep(1)
        console.print(f"[bold green]✓[/bold green] {container.name} is running")

        containers.append(cont)
        thread = Thread(target=stream_container, args=(cont.id, "resource"))
        thread.daemon = True
        thread.start()
        log_treads.append(thread)


    shared_secrets = {}

    for secret_type in project.shared_secrets or []:
        shared_secrets.update(
            settings_for_secrets(
                secrets_for(secret_type),
                resource_values, 
            )
        )

    if ResourceTags.s3_secret_key in resource_values:
        import boto3
        conf = settings_for_resources(resource_values, S3StorageConfig)

        assert conf.s3_endpoint
        url = conf.s3_endpoint.encoded_string().replace(conf.s3_endpoint.host or "", "localhost")

        s3 = boto3.client(
            "s3",
            endpoint_url=url,
            aws_access_key_id=conf.s3_access_key,
            aws_secret_access_key=conf.s3_secret_key.get_secret_value(),
            region_name=conf.s3_region
        )
        try:
            s3.head_bucket(Bucket=conf.s3_bucket)
            logger.info(f"Bucket '{conf.s3_bucket}' already exists")
        except Exception:
            logger.info(f"Creating bucket '{conf.s3_bucket}'")
            s3.create_bucket(Bucket=conf.s3_bucket)
            logger.info(f"Created bucket '{conf.s3_bucket}'")
            


    for container in compiled.network_apps:

        console.print(f"[bold blue]→[/bold blue] Creating app: [yellow]{container.name}[/yellow]")

        envs = settings_for_secrets(
            container.secrets or [], resource_values
        )

        if container.command:
            if "uvicorn" in container.command[-1] and "--reload" not in container.command:
                container.command[-1] = container.command[-1] + " --reload"

            if "fastapi" in container.command[-1]:
                container.command[-1] = container.command[-1].replace("run", "dev")

        console.print(container.command)

        cont = client.containers.run(
            image=container.docker_image or base_image,
            name=container.name,
            environment={
                **(container.environments or {}),
                **envs,
                **shared_secrets,
                **{
                    key: value for key, value 
                    in dotenvs.items()
                    if key not in envs and key not in shared_secrets
                }
            },
            volumes=application_volume,
            command=container.command,
            network=network.name,
            detach=True,
            labels=["nobs"],
            ports={f"{container.port}/tcp": container.port},
            mem_limit=f"{container.compute.mb_memory_limit}m",
            cpu_quota=container.compute.mvcpu_limit * 100,
            cpu_period=100_000,
            platform=platform_arc,
        )
        containers.append(cont)

        thread = Thread(target=stream_container, args=(cont.id, "app"))
        thread.daemon = True
        thread.start()
        log_treads.append(thread)


    for container in compiled.subscribers:
        envs = settings_for_secrets(
            container.secrets or [], resource_values
        )

        console.print(f"[bold blue]→[/bold blue] Creating subscriber: [red]{container.name}[/red]")
        cont = client.containers.run(
            image=base_image,
            name=container.name,
            environment={
                **(container.environments or {}),
                **envs,
                **shared_secrets,
                **{
                    key: value for key, value 
                    in dotenvs.items()
                    if key not in envs and key not in shared_secrets
                }
            },
            volumes=application_volume,
            command=["/bin/bash", "-c", f"nobs subscriber {container.name}"],
            network=network.name,
            detach=True,
            labels=["nobs"],
            cpu_quota=container.compute.mvcpu_limit * 100,
            cpu_period=100_000,
            mem_limit=f"{container.compute.mb_memory_limit}m",
            platform=platform_arc,
        )

        containers.append(cont)

        thread = Thread(target=stream_container, args=(cont.id, "subscriber"))
        thread.daemon = True
        thread.start()
        log_treads.append(thread)


    for container in compiled.workers:
        envs = settings_for_secrets(
            container.secrets or [], resource_values
        )
        console.print(f"[bold blue]→[/bold blue] Creating worker: [green]{container.name}[/green]")
        cont = client.containers.run(
            image=base_image,
            name=container.name,
            environment={ 
                **envs,
                **shared_secrets,
                **{
                    key: value for key, value 
                    in dotenvs.items()
                    if key not in envs and key not in shared_secrets
                }
            },
            volumes=application_volume,
            command=["/bin/bash", "-c", f"nobs process-queue {container.name}"],
            network=network.name,
            detach=True,
            labels=["nobs"],
            cpu_quota=container.compute.mvcpu_limit * 100,
            cpu_period=100_000,
            mem_limit=f"{container.compute.mb_memory_limit}m",
            platform=platform_arc,
        )

        containers.append(cont)

        thread = Thread(target=stream_container, args=(cont.id, "worker"))
        thread.daemon = True
        thread.start()
        log_treads.append(thread)


    table = Table(title="Running Containers", show_header=True, header_style="bold magenta")
    table.add_column("Container", style="cyan", no_wrap=True)
    table.add_column("ID", style="dim")
    table.add_column("Type", style="green")
    table.add_column("Access", style="blue")
    table.add_column("Credentials", style="blue")

    resource_names = {rc.name for rc in resource_containers}
    app_names = {app.name for app in compiled.network_apps}
    worker_names = {worker.name for worker in compiled.workers}
    subscriber_names = {sub.name for sub in compiled.subscribers}

    for container in containers:
        ports = container.ports

        if not ports:
            ports = container.attrs.get("Config", {}).get("ExposedPorts")

        credentials = ""

        container_type = "other"
        if container.name in resource_names:
            container_type = "resource"

            if container.name == "psql":
                print_values = {
                    "Username": ResourceTags.database_username,
                    "Password": ResourceTags.database_password,
                    "Database": ResourceTags.database_name
                }
                credentials = "\n".join([
                    f"{key}: {resource_values.get(value, '')}" for key, value in print_values.items()
                ])

            if container.name == "redis":
                print_values = {
                    "Username": ResourceTags.redis_username,
                    "Password": ResourceTags.redis_password,
                }
                credentials = "\n".join([
                    f"{key}: {resource_values.get(value, '')}" for key, value in print_values.items()
                ])

        elif container.name in app_names:
            container_type = "app"
        elif container.name in worker_names:
            container_type = "worker"
        elif container.name in subscriber_names:
            container_type = "subscriber"

        if ports:
            port_numbers = sorted([int(str(port).removesuffix('/tcp')) for port in ports.keys()])
            
            if len(port_numbers) > 3:
                min_port = min(port_numbers)
                max_port = max(port_numbers)
                access_urls = f"http://localhost:{min_port}-{max_port}"
            else:
                access_urls = "\n".join([
                    f"http://localhost:{port}"
                    for port in port_numbers
                ])
        else:
            access_urls = "background"

        table.add_row(
            container.name,
            container.id[:12],
            container_type,
            access_urls, 
            credentials
        )

    console.print()
    console.print(table)
    console.print()

    try:
        while True:
            sleep(10000)
    except KeyboardInterrupt:
        console.print()
        console.print(Panel(
            "Received shutdown signal, stopping all containers...",
            title="Shutdown",
            border_style="red"
        ))
        for container in reversed(containers):
            console.print(f"[dim]Stopping {container.name}...[/dim]")
            container.stop()

        console.print("[bold green]✓[/bold green] All containers stopped")


def default_docker_image(
    uv_image: str, 
    source_code_dir: str, 
    pre_lock_add: str,
    lock_file: Path,
    pyproject_file: Path,
    copy_additional_dirs: str,
    source_dir: Path
) -> str:

    docker_source = "/app" / source_dir

    return f"""FROM {uv_image} AS builder

WORKDIR /app

{pre_lock_add}

COPY {lock_file} {docker_source}/uv.lock
COPY {pyproject_file} {docker_source}/pyproject.toml

{copy_additional_dirs}
WORKDIR {docker_source}

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable --no-install-project

COPY {source_code_dir} {docker_source}

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

FROM {uv_image}

COPY --from=builder --chown=app:app {docker_source}/.venv {docker_source}/.venv

WORKDIR {docker_source}

{copy_additional_dirs}
COPY {source_dir} {docker_source}

ENV PATH="{docker_source}/.venv/bin:$PATH"
"""


def create_dockerfile_for(
    project: Project, dockerfile: Path, pyproject: Path, lockfile: Path, path_packages: list[str], python_version: str
) -> tuple[Path, Path]:
    import os

    context = Path(".")
    source_dir_sub_dir = Path()

    if path_packages:
        context = Path(os.path.commonpath([
            context.resolve(),
            *[
                Path(path).resolve() 
                for path in path_packages
            ]
        ]))
        source_dir_sub_dir = Path(".").resolve().relative_to(context)

    source_code_dir_name = "src" 
    source_code_dir = source_dir_sub_dir / source_code_dir_name

    def copy_from_path(path: Path) -> str:
        if context.resolve() == Path(".").resolve():
            return path.as_posix()
        return path.resolve().relative_to(context.resolve()).as_posix()

    if not source_code_dir.is_dir():
        source_code_dir_name = project.name.replace("-", "_").replace("/", "")
        source_code_dir = source_dir_sub_dir / source_code_dir

    if not source_code_dir.is_dir():
        source_code_dir = source_dir_sub_dir.resolve()
        source_code_dir_name = source_dir_sub_dir.as_posix()

    uv_image = f"ghcr.io/astral-sh/uv:python{python_version}-bookworm-slim"

    if not source_code_dir.is_dir():
        raise ValueError(f"Expected to find source code at '{source_code_dir_name}', but found nothing.")

    pre_lock_add = ""
    copy_additional_dirs = ""

    deps = pyproject.read_text()
    if "git =" in deps or "git=" in deps:
        # Install git so that git dependencies can be loaded in the slim image
        pre_lock_add += "RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*\n"

    if "psycopg2-binary" in deps:
        pre_lock_add += "RUN apt-get update && apt-get -y install libpq-dev gcc"

    if path_packages:
        for path in path_packages:
            package_path = Path(path).resolve()
            rel_path = package_path.relative_to(context)

            copy_additional_dirs += f"COPY {rel_path.as_posix()} /app/{rel_path.as_posix()}\n"

    if project.additional_dirs:
        copy_additional_dirs += "\n".join([
            f"COPY {copy_from_path(path)} /app/{source_dir_sub_dir / path.as_posix()}"
            for path in project.additional_dirs
        ])

    if "workspace = " in deps or "workspace=" in deps:
        current = Path.cwd()

        paths = []

        while not (current / ".git").is_dir():
            paths.insert(0, current.name)
            current = (current / "..").resolve()

        context = current

        pre_lock_add += "COPY . ."

        if paths:
            source_code_dir_name = (Path("/".join(paths)) / source_code_dir_name).as_posix()
            pyproject = Path("/".join(paths)) / pyproject


    file = default_docker_image(
        uv_image, 
        source_code_dir_name, 
        pre_lock_add,
        lock_file=source_dir_sub_dir / lockfile,
        pyproject_file=source_dir_sub_dir / pyproject,
        copy_additional_dirs=copy_additional_dirs,
        source_dir=source_dir_sub_dir
    )

    logger.debug(file)
    dockerfile.write_text(file)
    return context, source_dir_sub_dir

def find_lockfile() -> Path:
    max_checks = 10
    lockfile = Path("uv.lock")
    n_checks = 0

    while not lockfile.is_file():
        lockfile = ".." / lockfile 
        n_checks += 1
        if n_checks > max_checks:
            raise ValueError("Unable to find a uv.lock file")

    return lockfile


@dataclass
class LockfileInfo:
    packages: list[str]
    path_packages: list[str]

def packages_from_lockfile(file: Path) -> LockfileInfo:
    packages: list[str] = []
    path_packages: list[str] = []

    lock_file = tomli.loads(
        file.read_text()
    )
    for package in lock_file["package"]:
        packages.append(package["name"])

        source = package["source"]
        if "directory" in source:
            path_packages.append(source["directory"])
        elif "editable" in source:
            path_packages.append(source["editable"])

    return LockfileInfo(
        packages=packages, path_packages=path_packages
        
    ) 


def build_image(
    project: Project, 
    tag: str, 
    context: str | None = None,
) -> str:
    pyproject_path = Path("pyproject.toml")
    dockerfile = Path("Dockerfile")

    version: str = tomli.loads(
        pyproject_path.read_text()
    ).get("project", {}).get("requires-python", "3.12").split(",")[0]

    if version.startswith(">="):
        version = "3.13"
    else:
        version = "".join([
            c for c in version
            if c.isnumeric() or c == "."
        ])

    lockfile = find_lockfile()
    lockhash = sha256(lockfile.read_bytes(), usedforsecurity=False).hexdigest()
    lockfile_info = packages_from_lockfile(lockfile)

    if not pyproject_path.is_file():
        raise ValueError("Expected a pyproject.toml file using uv.")

    should_delete_dockerfile = False

    source_dir = Path("")
    if not dockerfile.is_file():
        temp_context, source_dir = create_dockerfile_for(
            project, 
            dockerfile, 
            pyproject_path, 
            lockfile=lockfile,
            path_packages=lockfile_info.path_packages,
            python_version=version or "3.12"
        )

        should_delete_dockerfile = True
        if context is None:
            context = temp_context.resolve().as_posix()

    platform = "linux/amd64"
    reg_url = f"{project.name}:{tag}"

    build_dir = Path.cwd()
    try:
        if context:
            context_path = (build_dir / context).resolve().as_posix()
            logger.info(f"Using context {context_path} with dockerfile {dockerfile.resolve().as_posix()}")
        else:
            context_path = "."

        default_runner([
            "docker", "build", context_path, 
            "-t", reg_url, 
            "-f", dockerfile.resolve().as_posix(), 
            "--platform", platform,
            "--label", f"com.nobspython.lockhash={lockhash}",
            "--label", f"com.nobspython.source-dir={source_dir.as_posix()}"
        ])
    except Exception as e:
        logger.error("Unable to build image")

    if should_delete_dockerfile:
        dockerfile.unlink(True)

    return reg_url
