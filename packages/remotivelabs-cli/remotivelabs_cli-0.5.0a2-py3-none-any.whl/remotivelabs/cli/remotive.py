from __future__ import annotations

import os
import sys
from pathlib import Path

import typer
from trogon import Trogon
from typer.main import get_group

from remotivelabs.cli.broker import app as broker_app
from remotivelabs.cli.cloud import app as cloud_app
from remotivelabs.cli.connect.connect import app as connect_app
from remotivelabs.cli.settings import Settings, settings
from remotivelabs.cli.settings.migration.migrate_all_token_files import migrate_any_legacy_tokens
from remotivelabs.cli.settings.migration.migrate_config_file import migrate_config_file
from remotivelabs.cli.settings.migration.migrate_legacy_dirs import migrate_legacy_settings_dirs
from remotivelabs.cli.studio.start import start_studio
from remotivelabs.cli.tools.tools import app as tools_app
from remotivelabs.cli.topology.cmd import app as topology_app
from remotivelabs.cli.topology.context import ContainerEngine, TopologyContext
from remotivelabs.cli.topology.typer import ContainerEngineOption, TopologyCommandOption, TopologyImageOption
from remotivelabs.cli.typer import typer_utils
from remotivelabs.cli.utils import versions
from remotivelabs.cli.utils.analytics import NoConsentError
from remotivelabs.cli.utils.console import print_generic_error, print_generic_message


def is_featue_flag_enabled(env_var: str) -> bool:
    """Check if an environment variable indicates a feature is enabled."""
    return os.getenv(env_var, "").lower() in ("true", "1", "yes", "on")


if os.getenv("GRPC_VERBOSITY") is None:
    os.environ["GRPC_VERBOSITY"] = "NONE"

app = typer_utils.create_typer(
    rich_markup_mode="rich",
    help="""
Welcome to RemotiveLabs CLI - Simplify and automate tasks for cloud resources and brokers

For documentation - https://docs.remotivelabs.com
""",
)


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"remotivelabs-cli {versions.cli_version()} ({versions.platform_info()})")


def test_callback(value: int) -> None:
    if value:
        print_generic_message(str(value))
        raise typer.Exit()


def check_for_newer_version(settings: Settings) -> None:
    versions.check_for_update(settings)


def run_migrations(settings: Settings) -> None:
    """
    Run all migration scripts.

    Each migration script is responsible for a particular migration, and order matters.
    """
    # 1. Migrate legacy settings dirs
    migrate_legacy_settings_dirs(settings.config_dir)

    # 2. Migrate any legacy tokens
    has_migrated_tokens = migrate_any_legacy_tokens(settings)

    # 3. Migrate legacy config file format
    migrate_config_file(settings.config_file_path, settings)

    if has_migrated_tokens:
        print_generic_error("Migrated old credentials and configuration files, you may need to login again or activate correct credentials")


def set_default_org_as_env(settings: Settings) -> None:
    """
    If not already set, take the default organisation from file and set as env
    This has to be done early before it is read
    """
    if "REMOTIVE_CLOUD_ORGANIZATION" not in os.environ:
        active_account = settings.get_active_account()
        if active_account and active_account.default_organization:
            os.environ["REMOTIVE_CLOUD_ORGANIZATION"] = active_account.default_organization


@app.callback()
def remotive(
    _the_version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Print current version",
    ),
) -> None:
    run_migrations(settings)
    check_for_newer_version(settings)
    set_default_org_as_env(settings)
    # Do other global stuff, handle other global options here


@app.command()
def tui(ctx: typer.Context) -> None:
    """
    Explore remotive-cli and generate commands with this textual user interface application
    """

    Trogon(get_group(app), click_context=ctx).run()


if not is_featue_flag_enabled("RUNS_IN_DOCKER"):
    app.add_typer(
        topology_app,
        name="topology",
        help="""
    Interact and manage RemotiveTopology resources

    Read more at https://docs.remotivelabs.com/docs/remotive-topology
    """,
    )

    if is_featue_flag_enabled("REMOTIVE_STUDIO_ENABLED"):

        @app.command()
        def studio(  # noqa: PLR0913
            topology_cmd: str = TopologyCommandOption,
            topology_image: str = TopologyImageOption,
            container_engine: ContainerEngine = ContainerEngineOption,
            workspace_path: Path = typer.Argument(
                ...,
                help="Workspace path",
                exists=True,
                file_okay=False,
                dir_okay=True,
                writable=True,
                readable=True,
            ),
            port: int = typer.Option(default=0, help="Port to run RemotiveStudio"),
            browser: bool = typer.Option(default=False, help="Open RemotiveStudio in a web browser"),
            log_level: str = typer.Option(default="warning", help="Log level for RemotiveStudio server"),
        ) -> None:
            """
            Start a RemotiveStudio instance
            """
            context = TopologyContext(
                container_engine=container_engine,
                cmd=topology_cmd,
                workspace=workspace_path.absolute().resolve(),
                image=topology_image,
            )
            start_studio(context, port=port, browser=browser, log_level=log_level)

else:
    app.add_typer(
        typer_utils.create_typer_sorted(rich_markup_mode="rich"),
        name="topology",
        help="""
    NOT AVAILABLE WHEN RUNNING IN DOCKER

    Read more at https://docs.remotivelabs.com/docs/remotive-topology
    """,
    )


app.add_typer(broker_app, name="broker", help="Manage a single broker - local or cloud")
app.add_typer(cloud_app, name="cloud", help="Manage resources in RemotiveCloud")
app.add_typer(connect_app, name="connect", help="Integrations with other systems")
app.add_typer(tools_app, name="tools")


def main() -> None:
    try:
        app()
    except NoConsentError:
        print_generic_error("E072: Analytics consent is required to use this feature without authentication")
        sys.exit(1)
    except Exception as e:
        print_generic_error(f"Unexpected error: {e}")
        sys.exit(1)
