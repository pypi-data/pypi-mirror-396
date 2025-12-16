import typer

from remotivelabs.cli.topology.context import ContainerEngine

TopologyCommandOption = typer.Option(
    None, envvar="REMOTIVE_TOPOLOGY_COMMAND", hidden=True, help="Optional path to RemotiveTopology command"
)
TopologyImageOption = typer.Option(None, envvar="REMOTIVE_TOPOLOGY_IMAGE", help="Optional docker image for RemotiveTopology ")
ContainerEngineOption = typer.Option(ContainerEngine.docker, envvar="CONTAINER_ENGINE", help="Specify container engine")
