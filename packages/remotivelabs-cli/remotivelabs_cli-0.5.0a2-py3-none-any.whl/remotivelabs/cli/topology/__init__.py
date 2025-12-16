import os
from pathlib import Path

import typer as t

from remotivelabs.cli.topology.context import ContainerEngine, TopologyContext
from remotivelabs.cli.topology.typer import (
    ContainerEngineOption,
    TopologyCommandOption,
    TopologyImageOption,
)
from remotivelabs.cli.topology.wrapper import app
from remotivelabs.cli.utils.analytics import require_consent


@app.callback()
def service_callback(
    ctx: t.Context,
    topology_cmd: str = TopologyCommandOption,
    topology_image: str = TopologyImageOption,
    container_engine: ContainerEngine = ContainerEngineOption,
    topology_workspace: Path = t.Option(
        os.curdir,
        envvar="REMOTIVE_TOPOLOGY_WORKSPACE",
        help="Override workspace for RemotiveTopology",
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        readable=True,
    ),
) -> None:
    require_consent()
    ctx.obj = ctx.obj or {}
    ctx.obj["topology"] = TopologyContext(
        container_engine=container_engine,
        cmd=topology_cmd,
        workspace=topology_workspace.absolute().resolve(),
        image=topology_image,
    )


__all__ = ["app"]
