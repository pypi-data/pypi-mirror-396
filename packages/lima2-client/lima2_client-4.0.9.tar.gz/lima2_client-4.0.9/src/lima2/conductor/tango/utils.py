# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Lima2 tango device utils"""

import contextlib
import logging
import textwrap
from typing import Iterator, Protocol, cast

import orjson
import tango as tg

from lima2.common.exceptions import Lima2DeviceError
from lima2.common.state import DeviceState
from lima2.conductor.utils import DecoratedFunc

logger = logging.getLogger(__name__)


def unpack_exception(payload: str) -> tuple[str, str]:
    """Decode and unpack a tango exception from the Lima2 backends.

    If the payload can't be JSON-decoded, use it as a plain error message.

    Raises KeyError if the JSON object is missing items.
    """
    try:
        decoded = orjson.loads(payload)
        what = decoded["what"]
        errinfo = decoded["errinfo"]
    except orjson.JSONDecodeError as decode_exc:
        logger.debug(
            f"Unable to json-decode tango exception payload '{payload}': {decode_exc}"
        )
        what = payload
        errinfo = {}

    if stacktrace := errinfo.pop("stacktrace", ""):
        logger.debug(f"Server-side stack trace:\n{stacktrace}")

    additional_info = ", ".join(f"{key}: {value}" for key, value in errinfo.items())

    return what, additional_info


def format_exception(where: str, when: str, what: str, info: str) -> str:
    """Format a remote error unpacked by unpack_exception()."""
    return f"On device {where}, exception {when}:\n" + textwrap.indent(
        f"Reason: {what}." + (f"\nAdditional info: ({info})" if info else ""),
        prefix="  ",
    )


def handle_tango_errors(method: DecoratedFunc) -> DecoratedFunc:
    """Decorator for an async method that may raise a DevFailed / AttributeError.

    If it does, a Lima2DeviceError will be raised with a helpful message.

    Handling AttributeErrors is required for offline devices.
    """

    async def wrapper(self: TangoDevice, *args, **kwargs):  # type: ignore
        try:
            # logger.debug(f"Calling {self.name}.{method.__name__}()")
            return await method(self, *args, **kwargs)
        except tg.DevFailed as e:
            if len(e.args) == 2 and e.args[0].reason == "LIMA_Exception":
                what, additional_info = unpack_exception(payload=e.args[0].desc)
            else:
                what = str(e)
                additional_info = ""

            raise Lima2DeviceError(
                format_exception(
                    where=self.name,
                    when=f"in call to {method.__name__}()",
                    what=what,
                    info=additional_info,
                ),
                device_name=self.name,
            ) from e
        except AttributeError as e:
            raise Lima2DeviceError(
                f"Attribute error from device {self.name} in call to {method.__name__}(): {e}",
                device_name=self.name,
            ) from e

    return cast(DecoratedFunc, wrapper)


class TangoDevice(Protocol):
    """Lima2 tango device interface.

    Used to benefit from type checking, e.g. when using the list [control, *receivers].
    """

    @property
    def name(self) -> str:
        raise NotImplementedError

    async def ping(self) -> int:
        raise NotImplementedError

    async def reset(self) -> None:
        raise NotImplementedError

    async def acq_state(self) -> DeviceState:
        raise NotImplementedError

    async def start(self) -> None:
        raise NotImplementedError

    async def stop(self) -> None:
        raise NotImplementedError

    @contextlib.contextmanager
    def attach(self) -> Iterator[None]:
        raise NotImplementedError
