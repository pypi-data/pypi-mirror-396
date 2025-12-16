# ruff: noqa
from __future__ import annotations

import typer

from remotivelabs.cli.topology.cmd import app as topology
from remotivelabs.cli.topology.cli import run_topology_cli
from remotivelabs.cli.typer import typer_utils

app = topology

topology_show = typer_utils.create_typer_sorted(
    rich_markup_mode="rich",
    help="""
Show information from database file
""",
)

topology.add_typer(topology_show, name="show")


@topology_show.command("signals")
def topology_show_signals(
    ctx: typer.Context,
    path: str = typer.Argument(
        ..., help="Path to the Database file, supported extensions: extensions: '.arxml', '.dbc', '.xml', '.ldf', '.signaldb.yaml'"
    ),
    out_path: str | None = typer.Argument(None, help="Write content to provided file path"),
    json: bool = typer.Option(False, "--json", help="Output results in JSON format"),
    yaml: bool = typer.Option(False, "--yaml", help="Output results in YAML format (default)"),
    jsonl: bool = typer.Option(False, "--jsonl", help="Output results in JSONL format"),
    broker_format: bool = typer.Option(False, "--bf", help="Output results in broker format"),
) -> None:
    """
    [EXPERIMENTAL] Show signals in the provided database file
    """
    cmd = ["show", "signals"]
    cmd.append(path)
    if out_path is not None:
        cmd.append(out_path)
    if json:
        cmd.append("--json")
    if yaml:
        cmd.append("--yaml")
    if jsonl:
        cmd.append("--jsonl")
    if broker_format:
        cmd.append("--bf")
    run_topology_cli(ctx, cmd)


@topology_show.command("constants")
def topology_show_constants(
    ctx: typer.Context,
    path: str = typer.Argument(..., help="Path to the Database file, supported extensions: extensions: '.arxml'"),
    json: bool = typer.Option(False, "--json", help="Output results in JSON format"),
    yaml: bool = typer.Option(False, "--yaml", help="Output results in YAML format (default)"),
) -> None:
    """
    [EXPERIMENTAL] Extract constants from database file
    """
    cmd = ["show", "constants"]
    cmd.append(path)
    if json:
        cmd.append("--json")
    if yaml:
        cmd.append("--yaml")
    run_topology_cli(ctx, cmd)


@topology_show.command("topology")
def topology_show_topology(
    ctx: typer.Context,
    path: str = typer.Argument(
        ...,
        help="Path to the Database file, supported extensions: extensions: '.arxml', '.xml', '.instance.yaml', '.platform.yaml', '.dbc', '.ldf', '.signaldb.yaml'",
    ),
    json: bool = typer.Option(False, "--json", help="Output results in JSON format"),
    yaml: bool = typer.Option(False, "--yaml", help="Output results in YAML format (default)"),
    resolve: bool = typer.Option(False, "--resolve", help="Show the resolved topology"),
    check: bool = typer.Option(False, "--check", help="Check topology, requires --resolve"),
    verbose: bool = typer.Option(False, "--verbose", help="Show verbose output"),
    out_path: str | None = typer.Option(None, "-o", "--out-path", help="Write content to provided file path"),
) -> None:
    """
    Shows the topology from database or instance file
    """
    cmd = ["show", "topology"]
    cmd.append(path)
    if json:
        cmd.append("--json")
    if yaml:
        cmd.append("--yaml")
    if resolve:
        cmd.append("--resolve")
    if check:
        cmd.append("--check")
    if verbose:
        cmd.append("--verbose")
    if out_path is not None:
        cmd.extend(["--out-path", out_path])
    run_topology_cli(ctx, cmd)


@topology_show.command("ethernet")
def topology_show_ethernet(
    ctx: typer.Context,
    path: str = typer.Argument(..., help="Path to the Database file, supported extensions: extensions: '.arxml'"),
    json: bool = typer.Option(False, "--json", help="Output results in JSON format"),
    yaml: bool = typer.Option(False, "--yaml", help="Output results in YAML format (default)"),
) -> None:
    """
    [EXPERIMENTAL] Shows Ethernet configuration from database file
    """
    cmd = ["show", "ethernet"]
    cmd.append(path)
    if json:
        cmd.append("--json")
    if yaml:
        cmd.append("--yaml")
    run_topology_cli(ctx, cmd)


@topology_show.command("services")
def topology_show_services(
    ctx: typer.Context,
    path: str = typer.Argument(..., help="Path to the Database file, supported extensions: extensions: '.arxml'"),
    json: bool = typer.Option(False, "--json", help="Output results in JSON format"),
    yaml: bool = typer.Option(False, "--yaml", help="Output results in YAML format (default)"),
    services: list[str] = typer.Option([], "-s", "--services", help="List of SOME/IP services to process"),
) -> None:
    """
    [EXPERIMENTAL] Show SOME/IP services from database file
    """
    cmd = ["show", "services"]
    cmd.append(path)
    if json:
        cmd.append("--json")
    if yaml:
        cmd.append("--yaml")
    for item in services:
        cmd.extend(["--services", item])
    run_topology_cli(ctx, cmd)


@topology.command("generate")
def topology_generate(
    ctx: typer.Context,
    topology_output_path: str = typer.Argument(..., help="Path to where generated files should be written"),
    name: str | None = typer.Option(None, "-n", "--name", help="Name of the generated topology"),
    topology_files: list[str] = typer.Option(
        [], "-f", "--file", help="RemotiveTopology .instance.yaml file(s), applied in the order they are provided"
    ),
) -> None:
    """
    Generate topology environment based on instance descriptions
    """
    cmd = ["generate"]
    cmd.append(topology_output_path)
    if name is not None:
        cmd.extend(["--name", name])
    for item in topology_files:
        cmd.extend(["--file", item])
    run_topology_cli(ctx, cmd)


topology_recording_session = typer_utils.create_typer_sorted(
    rich_markup_mode="rich",
    help="""
Work with recording sessions
""",
)

topology.add_typer(topology_recording_session, name="recording-session")


@topology_recording_session.command("create")
def topology_recording_session_create(
    ctx: typer.Context,
    out_path: str | None = typer.Argument(None, help="Write content to provided file path"),
    json: bool = typer.Option(False, "--json", help="Output results in JSON format"),
    yaml: bool = typer.Option(False, "--yaml", help="Output results in YAML format (default)"),
    recording_files: list[str] = typer.Option(
        [], "-f", "--file", help="Recording file(s), applied in the order they are provided, e.g. candump.log, .csv"
    ),
) -> None:
    """
    Create a new recording session from recording files
    """
    cmd = ["recording_session", "create"]
    if out_path is not None:
        cmd.append(out_path)
    if json:
        cmd.append("--json")
    if yaml:
        cmd.append("--yaml")
    for item in recording_files:
        cmd.extend(["--file", item])
    run_topology_cli(ctx, cmd)


@topology_recording_session.command("instantiate")
def topology_recording_session_instantiate(
    ctx: typer.Context,
    recording_session: str = typer.Argument(..., help="Path to the recording session file"),
    out_path: str | None = typer.Argument(None, help="Write content to provided file path"),
    json: bool = typer.Option(False, "--json", help="Output results in JSON format"),
    yaml: bool = typer.Option(False, "--yaml", help="Output results in YAML format (default)"),
) -> None:
    """
    Create a topology instance ready to play a recording session
    """
    cmd = ["recording_session", "instantiate"]
    cmd.append(recording_session)
    if out_path is not None:
        cmd.append(out_path)
    if json:
        cmd.append("--json")
    if yaml:
        cmd.append("--yaml")
    run_topology_cli(ctx, cmd)


@topology_recording_session.command("recalculate")
def topology_recording_session_recalculate(
    ctx: typer.Context,
    recording_session: str = typer.Argument(..., help="Path to the recording session file"),
    out_path: str | None = typer.Argument(None, help="Write content to provided file path"),
    json: bool = typer.Option(False, "--json", help="Output results in JSON format"),
    yaml: bool = typer.Option(False, "--yaml", help="Output results in YAML format (default)"),
) -> None:
    """
    Recalculate the recording session start and end time based on the files and their offsets
    """
    cmd = ["recording_session", "recalculate"]
    cmd.append(recording_session)
    if out_path is not None:
        cmd.append(out_path)
    if json:
        cmd.append("--json")
    if yaml:
        cmd.append("--yaml")
    run_topology_cli(ctx, cmd)


@topology.command("split")
def topology_split(
    ctx: typer.Context,
    topology_output_path: str = typer.Argument(..., help="Path to a folder where generated signal databases should be written"),
    topology_description_files: list[str] = typer.Option(
        [], "-f", "--file", help="RemotiveTopology platform file(s), applied in the order they are provided"
    ),
) -> None:
    """
    [DEPRECATED] Extract individual signal databases for each channel in a RemotiveTopology platform.
    """
    cmd = ["split"]
    cmd.append(topology_output_path)
    for item in topology_description_files:
        cmd.extend(["--file", item])
    run_topology_cli(ctx, cmd)


@topology.command("convert")
def topology_convert(
    ctx: typer.Context,
    topology_description_files: str = typer.Option(..., "-f", "--file", help="RemotiveTopology platform file"),
    output_file: str | None = typer.Option(
        None,
        "-o",
        "--output",
        help="Optional path to a file where generated signal database should be written. If not provided, the result will be printed to stdout.",
    ),
    format: str | None = typer.Option(None, "--format", help="Format to convert to. Currently only 'remotive' is supported."),
    channel_names: list[str] = typer.Option(
        [], "-c", "--channel", help="Optional channel(s) to convert. If not provided, all CAN channels will be converted."
    ),
) -> None:
    """
    [EXPERIMENTAL] Convert signal database to different format. Currently only CAN frames is supported.
    """
    cmd = ["convert"]
    cmd.extend(["--file", topology_description_files])
    if output_file is not None:
        cmd.extend(["--output", output_file])
    if format is not None:
        cmd.extend(["--format", format])
    for item in channel_names:
        cmd.extend(["--channel", item])
    run_topology_cli(ctx, cmd)


@topology.command("validate")
def topology_validate(
    ctx: typer.Context, path: str = typer.Argument(..., help="Path to the Database file, supported extensions: extensions: '.arxml'")
) -> None:
    """
    [EXPERIMENTAL] Validate file
    """
    cmd = ["validate"]
    cmd.append(path)
    run_topology_cli(ctx, cmd)


@topology.command("gateway-mapping")
def topology_gateway_mapping(
    ctx: typer.Context,
    out_path: str = typer.Argument(..., help="Path to file where extracted gateway mapping should be written"),
    only_fully_resolved: bool = typer.Option(False, "-o", "--only-fully-resolved", help="Only show fully resolved mapping"),
    gateway_ecu: str = typer.Option(..., "-g", "--gateway-ecu", help="Gateway ECU name"),
    platform: str = typer.Option(..., "-p", "--platform", help="Topology platform"),
) -> None:
    """
    [EXPERIMENTAL] List gateway mapping for ECU
    """
    cmd = ["gateway_mapping"]
    cmd.append(out_path)
    if only_fully_resolved:
        cmd.append("--only-fully-resolved")
    cmd.extend(["--gateway-ecu", gateway_ecu])
    cmd.extend(["--platform", platform])
    run_topology_cli(ctx, cmd)
