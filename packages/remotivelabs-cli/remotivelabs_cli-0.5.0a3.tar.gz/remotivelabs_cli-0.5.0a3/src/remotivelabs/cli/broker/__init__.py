from __future__ import annotations

import os

from remotivelabs.cli.broker import export, files, licenses, record, recording_session, scripting, signals
from remotivelabs.cli.broker.discovery import discover as discover_cmd
from remotivelabs.cli.broker.typer import BrokerUrlOption
from remotivelabs.cli.typer import typer_utils

app = typer_utils.create_typer(rich_markup_mode="rich")


# TODO: remove this?
def cb(url: str = BrokerUrlOption) -> None:
    # This can be used to override the --url per command, lets see if this is a better approach
    if url is not None:
        os.environ["REMOTIVE_BROKER_URL"] = url


# TODO: move broker commands to subcommand instead?
app.command(help="Discover brokers on this network")(discover_cmd)
app.callback()(cb)

# subcommands

app.add_typer(recording_session.app, name="playback")
app.add_typer(record.app, name="record", help="Record data on buses")
app.add_typer(files.app, name="files", help="Upload/Download configurations and recordings")
app.add_typer(signals.app, name="signals", help="Find and subscribe to signals")
app.add_typer(export.app, name="export", help="Export to external formats")
app.add_typer(scripting.app, name="scripting", help="LUA scripting utilities")
app.add_typer(licenses.app, name="license", help="View and request license to broker")
