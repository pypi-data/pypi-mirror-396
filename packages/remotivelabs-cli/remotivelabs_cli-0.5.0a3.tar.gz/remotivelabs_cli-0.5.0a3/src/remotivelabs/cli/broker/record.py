from __future__ import annotations

from typing import List

import grpc
import typer

from remotivelabs.cli.broker.lib.broker import Broker
from remotivelabs.cli.broker.typer import ApiKeyOption, BrokerUrlOption
from remotivelabs.cli.typer import typer_utils
from remotivelabs.cli.utils.console import print_grpc_error, print_success

app = typer_utils.create_typer(help=help)


@app.command()
def start(
    filename: str = typer.Argument(..., help="Path to local file to upload"),
    namespace: List[str] = typer.Option(..., help="Namespace to record"),
    url: str = BrokerUrlOption,
    api_key: str = ApiKeyOption,
) -> None:
    try:
        broker = Broker(url, api_key)
        broker.record_multiple(namespace, filename)
    except grpc.RpcError as rpc_error:
        print_grpc_error(rpc_error)


@app.command()
def stop(
    filename: str = typer.Argument(..., help="Path to local file to upload"),
    namespace: List[str] = typer.Option(..., help="Namespace to record"),
    url: str = BrokerUrlOption,
    api_key: str = ApiKeyOption,
) -> None:
    try:
        broker = Broker(url, api_key)
        broker.stop_multiple(namespace, filename)
        print_success("Recording stopped")
    except grpc.RpcError as rpc_error:
        print_grpc_error(rpc_error)
