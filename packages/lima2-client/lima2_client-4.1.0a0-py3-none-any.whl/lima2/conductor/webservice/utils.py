# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Conductor server utils."""


import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Any


class ColoredFormatter(logging.Formatter):
    """A formatter that adds color to log levels and file:line."""

    LEVEL_COLORS = {
        "DEBUG": "\x1b[38;5;244m",  # Light gray
        "INFO": "\x1b[38;5;15m",  # White
        "WARNING": "\x1b[33m",  # Yellow
        "ERROR": "\x1b[31m",  # Red
        "CRITICAL": "\x1b[31;1m",  # Bold red
    }

    RESET = "\x1b[0m"
    FILE_LINE_COLOR = "\x1b[36m"  # Cyan

    def format(self, record: logging.LogRecord) -> str:
        """Formats the log record."""
        log_level = record.levelname
        color = self.LEVEL_COLORS.get(log_level, self.RESET)

        try:
            pathname = str(Path(record.pathname).relative_to(Path.cwd()))
        except ValueError:
            pathname = record.pathname
        lineno = record.lineno

        format_str = (
            f"{color}{log_level:<8}{self.RESET} "
            f"{self.FILE_LINE_COLOR}[{pathname}:{lineno}]{self.RESET} "
            f"{record.msg}"
        )
        if record.args:
            format_str = format_str % record.args

        return format_str


def configure_logger(file_path: Path, stdout_log_level: str | int) -> None:
    """Configure the 'lima2' logger, from which all loggers in this package inherit.

    Sets up a rotating file handler in DEBUG level to write at `file_path`, and a
    stream handler to print logs above `stdout_log_level` to stdout.
    """
    logger = logging.getLogger("lima2")

    sh = logging.StreamHandler(sys.stdout)
    fh = logging.handlers.RotatingFileHandler(
        file_path, maxBytes=10 * 1024 * 1024, backupCount=10
    )

    sh.setFormatter(
        ColoredFormatter("%(levelname)-10s [%(pathname)s:%(lineno)d] %(message)s")
    )
    fh.setFormatter(
        logging.Formatter(
            "[%(asctime)s][%(levelname)s][%(pathname)s:%(lineno)d] %(message)s"
        )
    )

    sh.setLevel(stdout_log_level)
    fh.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)

    logger.addHandler(sh)
    logger.addHandler(fh)

    # Send HTTP server logs to file
    logging.getLogger("uvicorn.access").addHandler(fh)
    logging.getLogger("uvicorn.error").addHandler(fh)


def env_or(key: str, default: Any) -> Any:
    """Return the value of environment variable 'key', or a default value."""
    try:
        return os.environ[key]
    except KeyError:
        return default


def env_or_die(key: str) -> str:
    """Get value from environ or raise."""
    try:
        return os.environ[key]
    except KeyError:
        raise EnvironmentError(
            f"Environment variable {key} is not set. "
            "It must either be exported or defined in '.env'."
        ) from None
