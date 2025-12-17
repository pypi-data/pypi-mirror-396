"""
Delegate all arguments to the remotive-topology CLI inside Docker.
Example:
  remotive topology status --help
"""

import os
import shutil
import subprocess

import typer

from remotivelabs.cli.topology.context import TopologyContext


def check_docker_installed() -> None:
    """Check if Docker is installed and accessible."""
    if shutil.which("docker") is None:
        typer.echo("❌ Docker is not installed or not in PATH.", err=True)
        typer.echo("👉 Please install Docker: https://docs.docker.com/get-docker/", err=True)
        raise typer.Exit(code=1)


def run_topology_cli_in_docker(ctx: TopologyContext, args: list[str], capture_output: bool) -> subprocess.CompletedProcess[str]:
    check_docker_installed()

    topology_image = ctx.image or "remotivelabs/remotive-topology:0.14.4"
    container_engine = ctx.container_engine.value
    # Build base docker command equivalent to your alias
    docker_cmd = [
        container_engine,
        "run",
    ]
    # -u flag only works on Unix (os.getuid/getgid not available on Windows)
    if hasattr(os, "getuid") and hasattr(os, "getgid"):
        docker_cmd += ["-u", f"{os.getuid()}:{os.getgid()}"]  # type: ignore[unused-ignore, attr-defined]  # needed on Windows
    docker_cmd += [
        "--rm",
        "-v",
        f"{os.path.expanduser('~')}/.config/remotive/:/.config/remotive",
        "-v",
        f"{str(ctx.workspace)}:{str(ctx.workspace)}",
        "-w",
        str(ctx.workspace),
        "-e",
        f"REMOTIVE_TOPOLOGY_WORKSPACE={ctx.workspace}",
        "-e",
        f"REMOTIVE_CLOUD_ORGANIZATION={os.environ.get('REMOTIVE_CLOUD_ORGANIZATION', '')}",
        "-e",
        f"REMOTIVE_CLOUD_AUTH_TOKEN={os.environ.get('REMOTIVE_CLOUD_AUTH_TOKEN', '')}",
        "-e",
        "REMOTIVE_CONFIG_DIR=/.config/remotive",
    ]
    docker_cmd += [topology_image] + args

    try:
        return subprocess.run(docker_cmd, check=True, capture_output=capture_output, text=capture_output)
    except FileNotFoundError:
        typer.echo(f"❌ {container_engine} not found. Make sure {container_engine} is installed and in PATH.", err=True)
        raise typer.Exit(code=1)
