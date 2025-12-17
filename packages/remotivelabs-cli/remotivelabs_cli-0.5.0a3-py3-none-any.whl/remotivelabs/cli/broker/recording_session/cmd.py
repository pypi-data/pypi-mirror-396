from __future__ import annotations

import asyncio
import datetime
from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Any, AsyncIterator, Optional

import typer

from remotivelabs.broker.auth import ApiKeyAuth, NoAuth
from remotivelabs.broker.recording_session import RecordingSessionClient, RecordingSessionPlaybackStatus
from remotivelabs.cli.broker.recording_session.client import RecursiveFilesListingClient
from remotivelabs.cli.broker.recording_session.time import time_offset_to_us
from remotivelabs.cli.broker.typer import ApiKeyOption, BrokerUrlOption
from remotivelabs.cli.typer import typer_utils
from remotivelabs.cli.utils.console import print_generic_error, print_result

app = typer_utils.create_typer(
    help="""
Manage playback of recording sessions

All offsets are in microseconds (μs)
"""
)


def _int_or_none(offset: Optional[str | int]) -> Optional[int]:
    return offset if offset is None else int(offset)


def _print_offset_help(cmd: str) -> str:
    return f"""
    Offsets can be specified in minutes (1:15min), seconds(10s), millis(10000ms) or micros(10000000us), default without suffix is micros.
    Sample offsets
    {cmd} 1.15min, 10s, 10000ms, 10000000us, 10000000,
    """


def _custom_types(o: Any) -> Any:
    if isinstance(o, Enum):
        return o.name
    if is_dataclass(type(o)):
        return asdict(o)
    if isinstance(o, datetime.datetime):
        return o.isoformat(timespec="seconds")
    raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")


async def _list_files_async(path: str, recursive: bool, url: str, api_key: str) -> None:
    if recursive:
        client = RecordingSessionClient(url, auth=ApiKeyAuth(api_key) if api_key else NoAuth())
        file_listing_client = RecursiveFilesListingClient(client)
        print_result(
            await file_listing_client.list_all_files(path, file_types=None),
            default=_custom_types,
        )
    else:
        client = RecordingSessionClient(url, auth=ApiKeyAuth(api_key) if api_key else NoAuth())
        print_result(await client.list_recording_files(path), default=_custom_types)


@app.command()
def list_files(
    path: str = typer.Argument("/", help="Optional subdirectory to list files in, defaults to /"),
    recursive: bool = typer.Option(False, help="List subdirectories recursively"),
    url: str = BrokerUrlOption,
    api_key: str = ApiKeyOption,
) -> None:
    """
    List files on broker.
    """
    try:
        asyncio.run(_list_files_async(path, recursive, url, api_key))
    except Exception as e:
        print_generic_error(str(e))


# --------------------------------------------------------------------------- #
# play
# --------------------------------------------------------------------------- #


async def _play_async(path: str, offset: str, url: str, api_key: str) -> None:
    client = RecordingSessionClient(url, auth=ApiKeyAuth(api_key) if api_key else NoAuth())
    result = await client.get_session(path=path).play(offset=_int_or_none(offset))
    print_result(result, default=_custom_types)


@app.command(
    help=f"""
Starts playing the recording at current offset or from specified offset
{_print_offset_help("--offset")}
"""
)
def play(  # noqa: PLR0913
    path: str = typer.Argument(..., help="Path to the recording session", envvar="REMOTIVE_RECORDING_SESSION_PATH"),
    offset: str = typer.Option(None, callback=time_offset_to_us, help="Offset to play from"),
    url: str = BrokerUrlOption,
    api_key: str = ApiKeyOption,
) -> None:
    try:
        asyncio.run(_play_async(path, offset, url, api_key))
    except Exception as e:
        print_generic_error(str(e))


async def _repeat_async(path: str, start_offset: str, end_offset: str, clear: bool, url: str, api_key: str) -> None:  # noqa: PLR0913
    session = RecordingSessionClient(url, auth=ApiKeyAuth(api_key) if api_key else NoAuth()).get_session(path)
    if clear:
        result = await session.set_repeat(start_offset=None, end_offset=None)
    else:
        result = await session.set_repeat(start_offset=int(start_offset), end_offset=_int_or_none(end_offset))
    print_result(result, _custom_types)


@app.command(
    help=f"""
Repeat RecordingSession in specific interval or complete recording
To remove existing repeat config, use --clear flag.
{_print_offset_help("--start-offset/--end-offset")}
"""
)
def repeat(  # noqa: PLR0913
    path: str = typer.Argument(..., help="Path to the recording session", envvar="REMOTIVE_RECORDING_SESSION_PATH"),
    start_offset: str = typer.Option(0, callback=time_offset_to_us, help="Repeat start offset, defaults to start"),
    end_offset: str = typer.Option(None, callback=time_offset_to_us, help="Repeat end offset, defaults to end"),
    clear: bool = typer.Option(False, help="Clear repeat"),
    url: str = BrokerUrlOption,
    api_key: str = ApiKeyOption,
) -> None:
    try:
        asyncio.run(_repeat_async(path, start_offset, end_offset, clear, url, api_key))
    except Exception as e:
        print_generic_error(str(e))


async def _pause_async(path: str, offset: str, url: str, api_key: str) -> None:
    session = RecordingSessionClient(url, auth=ApiKeyAuth(api_key) if api_key else NoAuth()).get_session(path)
    result = await session.pause(offset=_int_or_none(offset))
    print_result(result, default=_custom_types)


@app.command(
    help=f"""
    Pause the recording at current offset or specified offset
    {_print_offset_help("--offset")}
    """
)
def pause(
    path: str = typer.Argument(..., help="Path to the recording session", envvar="REMOTIVE_RECORDING_SESSION_PATH"),
    offset: str = typer.Option(None, callback=time_offset_to_us, help="Offset to play from"),
    url: str = BrokerUrlOption,
    api_key: str = ApiKeyOption,
) -> None:
    try:
        asyncio.run(_pause_async(path, offset, url, api_key))
    except Exception as e:
        print_generic_error(str(e))


async def _seek_async(path: str, offset: str, url: str, api_key: str) -> None:
    session = RecordingSessionClient(url, auth=ApiKeyAuth(api_key) if api_key else NoAuth()).get_session(path)
    result = await session.seek(offset=int(offset))
    print_result(result, default=_custom_types)


@app.command(
    help=f"""
    Seek to specified offset
    {_print_offset_help("--offset")}
    """
)
def seek(
    path: str = typer.Argument(..., help="Path to the recording session", envvar="REMOTIVE_RECORDING_SESSION_PATH"),
    offset: str = typer.Option(..., callback=time_offset_to_us, help="Offset to seek to"),
    url: str = BrokerUrlOption,
    api_key: str = ApiKeyOption,
) -> None:
    try:
        asyncio.run(_seek_async(path, offset, url, api_key))
    except Exception as e:
        print_generic_error(str(e))


async def _open_async(path: str, force: bool, url: str, api_key: str) -> None:
    session = RecordingSessionClient(url, auth=ApiKeyAuth(api_key) if api_key else NoAuth()).get_session(path)
    result = await session.open(force_reopen=force)
    print_result(result, default=_custom_types)


@app.command()
def open(  # noqa: PLR0913
    path: str = typer.Argument(..., help="Path to the recording session", envvar="REMOTIVE_RECORDING_SESSION_PATH"),
    force: bool = typer.Option(False, help="Force close and re-open recording session if exists"),
    url: str = BrokerUrlOption,
    api_key: str = ApiKeyOption,
) -> None:
    """
    Open a recording session.
    """
    try:
        asyncio.run(_open_async(path, force, url, api_key))
    except Exception as e:
        print_generic_error(str(e))


async def _close_async(path: str, url: str, api_key: str) -> None:
    session = RecordingSessionClient(url, auth=ApiKeyAuth(api_key) if api_key else NoAuth()).get_session(path)
    result = await session.close()
    print_result(result, default=_custom_types)


@app.command()
def close(
    path: str = typer.Argument(..., help="Path to the recording session", envvar="REMOTIVE_RECORDING_SESSION_PATH"),
    url: str = BrokerUrlOption,
    api_key: str = ApiKeyOption,
) -> None:
    """
    Close a recording session.
    """
    try:
        asyncio.run(_close_async(path, url, api_key))
    except Exception as e:
        print_generic_error(str(e))


async def _status_async(stream: bool, url: str, api_key: str) -> None:
    client = RecordingSessionClient(url, auth=ApiKeyAuth(api_key) if api_key else NoAuth())

    async def _async_playback_stream() -> None:
        _stream: AsyncIterator[list[RecordingSessionPlaybackStatus]] = client.playback_status()
        async for f in _stream:
            print_result(f, default=_custom_types)
            if not stream:
                break

    await _async_playback_stream()


@app.command()
def status(
    stream: bool = typer.Option(False, help="Blocks and continuously streams statuses"),
    url: str = BrokerUrlOption,
    api_key: str = ApiKeyOption,
) -> None:
    """
    Get the status of all opened Recording sessions
    """

    try:
        asyncio.run(_status_async(stream, url, api_key))
    except KeyboardInterrupt:
        raise typer.Exit(code=0)
    except Exception as e:
        print_generic_error(str(e))
