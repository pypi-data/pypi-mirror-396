# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Conductor server command-line interface, available as `lima2-conductor`"""

import os
from enum import Enum
from typing import Annotated

import typer
import uvicorn

from lima2.conductor.webservice import webapp

cli = typer.Typer()


class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@cli.command()
def start(
    tango_host: str,
    topology: str,
    control_url: str,
    receiver_urls: list[str],
    tango_timeout: Annotated[int, typer.Option(help="In seconds")] = 30,
    port: int = webapp.DEFAULT_PORT,
    log_level: LogLevel = LogLevel.INFO,
) -> None:
    """Start the conductor"""
    print(f"Starting Conductor server on port {port}...")

    os.environ["TANGO_HOST"] = tango_host
    os.environ["LIMA2_TOPOLOGY"] = topology
    os.environ["LIMA2_CONTROL_URL"] = control_url
    os.environ["LIMA2_RECEIVER_URLS"] = ",".join(receiver_urls)
    os.environ["LIMA2_TANGO_TIMEOUT"] = str(tango_timeout)
    os.environ["LOG_LEVEL"] = log_level

    uvicorn.run(
        app="lima2.conductor.webservice.main:app",
        host="0.0.0.0",
        port=port,
    )


@cli.command()
def dev(
    tango_host: str,
    topology: str,
    control_url: str,
    receiver_urls: list[str],
    tango_timeout: Annotated[int, typer.Option(help="In seconds")] = 30,
    port: int = webapp.DEFAULT_PORT,
    log_level: LogLevel = LogLevel.DEBUG,
) -> None:
    """Start the conductor in dev mode (auto-reload)"""
    print(f"Starting Conductor server with auto-reload on port {port}...")

    os.environ["TANGO_HOST"] = tango_host
    os.environ["LIMA2_TOPOLOGY"] = topology
    os.environ["LIMA2_CONTROL_URL"] = control_url
    os.environ["LIMA2_RECEIVER_URLS"] = ",".join(receiver_urls)
    os.environ["LIMA2_TANGO_TIMEOUT"] = str(tango_timeout)
    os.environ["LOG_LEVEL"] = log_level
    # See https://docs.python.org/3/library/asyncio-dev.html
    os.environ["PYTHONASYNCIODEBUG"] = "1"

    uvicorn.run(
        app="lima2.conductor.webservice.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
    )


if __name__ == "__main__":
    cli()
