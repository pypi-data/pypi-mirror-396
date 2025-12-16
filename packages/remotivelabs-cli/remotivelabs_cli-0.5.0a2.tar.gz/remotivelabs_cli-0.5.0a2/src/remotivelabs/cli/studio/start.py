import os
import socket
import webbrowser

import uvicorn

from remotivelabs.cli.studio.api import api
from remotivelabs.cli.topology.context import TopologyContext
from remotivelabs.cli.utils.analytics import require_consent


def start_studio(ctx: TopologyContext, port: int, browser: bool, log_level: str) -> None:
    require_consent()

    host = "0.0.0.0"

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(2048)
    _, port = sock.getsockname()

    def startup() -> None:
        print(f"🚀 RemotiveStudio is running: http://{host}:{port}")
        if browser:
            # TODO: open RemotiveStudio main page when ready
            webbrowser.open(f"http://{host}:{port}/docs")

    api.state.startup = startup
    api.state.topology = ctx

    os.putenv("REMOTIVE_STUDIO", "true")

    uvicorn.run(
        api,
        fd=sock.fileno(),
        log_level=log_level,
        lifespan="on",
    )
