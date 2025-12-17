import os
import subprocess

import typer

from remotivelabs.cli.topology.cli.run_in_docker import run_topology_cli_in_docker
from remotivelabs.cli.topology.context import TopologyContext


def run_topology_cli(ctx: typer.Context, args: list[str]) -> None:
    try:
        run_topology(ctx.obj["topology"], args, capture_output=False)
    except subprocess.CalledProcessError as e:
        raise typer.Exit(code=e.returncode)


def run_topology(ctx: TopologyContext, args: list[str], capture_output: bool = True) -> subprocess.CompletedProcess[str]:
    if ctx.cmd is None:
        return run_topology_cli_in_docker(ctx, args, capture_output=capture_output)
    cmd = [ctx.cmd] + args
    os.putenv("REMOTIVE_TOPOLOGY_WORKSPACE", str(ctx.workspace))
    return subprocess.run(cmd, check=True, capture_output=capture_output, text=capture_output)
