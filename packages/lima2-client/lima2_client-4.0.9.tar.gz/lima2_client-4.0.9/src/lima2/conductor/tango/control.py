# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Lima2 control tango device.

Specializes the ControlDevice protocol for lima2 tango control devices.

Allows us to add typechecking to all attributes and remote procedure calls.
"""

import asyncio
import contextlib
import functools
import logging
import traceback
from typing import Any, Awaitable, Callable, Iterator, cast
from uuid import UUID

import orjson
import tango as tg

from lima2.common.exceptions import Lima2DeviceError
from lima2.common.progress_counter import SingleCounter
from lima2.common.state import DeviceState
from lima2.conductor.tango.utils import TangoDevice, handle_tango_errors

logger = logging.getLogger(__name__)


class TangoControl(TangoDevice):
    """Wrapper around the raw control DeviceProxy.

    Provides type-annotated methods and attributes.
    """

    def __init__(self, url: str, timeout_ms: int):
        self.device = tg.DeviceProxy(url, green_mode=tg.GreenMode.Asyncio)
        self.device.set_timeout_millis(timeout_ms)

        self.prev_state = DeviceState.OFFLINE
        """Last device state value polled in poll_state()."""

        self.state_change_callback: (
            Callable[[DeviceState], Awaitable[None]] | None
        ) = None
        """Callback registered in on_state_change()."""

        self.connect_callback: (Callable[[DeviceState], Awaitable[None]] | None) = None
        """
        Callback registered in on_connect(), called when the remote device comes
        online (or reconnects).
        """

        self.state_polling_task: asyncio.Task[None] | None = None
        """Polling task for acq_state attribute."""

    @property
    def name(self) -> str:
        return str(self.device.dev_name())

    @handle_tango_errors
    async def ping(self) -> int:
        value = int(await self.device.ping())
        logger.debug(f"Ping {self.name}: {value}µs")
        return value

    @handle_tango_errors
    async def prepare(self, uuid: UUID, params: dict[str, Any]) -> None:
        logger.debug(f"Passing prepare params to CONTROL ({self.name})")

        await self.device.write_attribute("acq_params", orjson.dumps(params))
        logger.debug(f"Executing prepare on CONTROL ({self.name})")
        await self.device.Prepare(str(uuid))

    @handle_tango_errors
    async def start(self) -> None:
        await self.device.Start()

    @handle_tango_errors
    async def trigger(self) -> None:
        await self.device.Trigger()

    @handle_tango_errors
    async def stop(self) -> None:
        await self.device.Stop()

    @handle_tango_errors
    async def close(self) -> None:
        await self.device.Close()

    @handle_tango_errors
    async def reset(self) -> None:
        await self.device.Reset()

    @handle_tango_errors
    async def write_attribute(self, name: str, value: Any) -> None:
        """Set an attribute's value given its name."""
        try:
            await self.device.write_attribute(name, value)
        except Exception as e:
            # NOTE(mdu) for some reason, tango raises a TypeError if
            # write_attribute fails. Wrap that into a DeviceError.
            raise Lima2DeviceError(
                f"Error setting attribute '{name}' to {value}: {e}",
                device_name=self.name,
            ) from None

    @handle_tango_errors
    async def read_attribute(self, name: str) -> Any:
        """Get an attribute's value given its name."""
        return (await self.device.read_attribute(name)).value

    @handle_tango_errors
    async def command(self, name: str, arg: Any) -> Any:
        """Execute a command given its name and (optionally) an argument."""
        if arg is None:
            return await self.device.command_inout(name)
        else:
            return await self.device.command_inout(name, arg)

    @handle_tango_errors
    async def acq_state(self) -> DeviceState:
        """Request the device's acq_state attribute.

        If the request fails, assume the device is offline.
        """
        try:
            return DeviceState(int(await self.read_attribute("acq_state")))
        except Lima2DeviceError:
            return DeviceState.OFFLINE

    @handle_tango_errors
    async def nb_frames_acquired(self) -> SingleCounter:
        value = await self.read_attribute("nb_frames_acquired")
        return SingleCounter(
            name="nb_frames_acquired",
            value=value,
            source=self.name,
        )

    @handle_tango_errors
    async def det_info(self) -> dict[str, Any]:
        value: str = await self.read_attribute("det_info")
        return cast(dict[str, Any], orjson.loads(value))

    @handle_tango_errors
    async def det_status(self) -> dict[str, Any]:
        value: str = await self.read_attribute("det_status")
        return cast(dict[str, Any], orjson.loads(value))

    @handle_tango_errors
    async def det_capabilities(self) -> dict[str, Any]:
        value: str = await self.read_attribute("det_capabilities")
        return cast(dict[str, Any], orjson.loads(value))

    # TODO(mdu) cached method leaks self
    # https://docs.astral.sh/ruff/rules/cached-instance-method/
    @functools.cache
    def fetch_params_schema(self) -> str:
        """Retrieve 'acq_params' schema for this device from the tango database.

        Use the cached value if we have fetched it already.
        """
        tango_db = tg.Database()

        dev_class = tango_db.get_device_info(self.name).class_name

        prop = tango_db.get_class_attribute_property(dev_class, "acq_params")
        # Each attribute property is a StdStringVector with a single value
        try:
            return str(prop["acq_params"]["schema"][0])
        except KeyError as e:
            raise RuntimeError(
                f"Schema for 'acq_params' not found on {dev_class} in tango db"
            ) from e

    ###################################
    # State and polling
    ###################################

    @contextlib.contextmanager
    def attach(self) -> Iterator[None]:
        self.state_polling_task = asyncio.create_task(
            self.poll_state(), name=f"{self.name} acq_state polling task"
        )
        logger.info(f"Listening to {self.name}...")
        yield
        logger.info(f"Stop listening to {self.name}.")
        self.state_polling_task.cancel()
        self.state_polling_task = None

    def on_state_change(
        self, callback: Callable[[DeviceState], Awaitable[None]]
    ) -> None:
        """Register a callback to changes in DeviceState.

        The callback should be an async function which takes the new DeviceState
        value as parameter.
        """
        logger.debug(f"Registering on_state_change callback on {self.name}")
        self.state_change_callback = callback

    def on_connect(self, callback: Callable[[DeviceState], Awaitable[None]]) -> None:
        """Register a function to be called when the device connects.

        It will be called both on the first connection, and also any subsequent
        reconnect.

        The callback should be an async function which takes the new DeviceState value
        as parameter.
        """
        logger.debug(f"Registering on_connect callback on {self.name}")
        self.connect_callback = callback

    async def poll_state(self, interval_s: float = 0.05) -> None:
        """Poll the device's acq_state periodically to notify of changes/disconnects.

        This loop calls the registered state_change_callback on every acq_state change.
        """
        while True:
            await asyncio.sleep(interval_s)

            new_state = await self.acq_state()

            if new_state != self.prev_state:
                logger.debug(f"{self.name}: {self.prev_state} -> {new_state}")
                if self.prev_state == DeviceState.OFFLINE:
                    if self.connect_callback is not None:
                        try:
                            await self.connect_callback(new_state)
                        except Exception:  # pragma: no cover
                            logger.error(
                                f"Exception raised in control {self.name} "
                                f"on_connect callback:\n"
                                f"{traceback.format_exc()}"
                            )

                if self.state_change_callback is None:
                    logger.info(
                        f"State change on {self.name} but no callback is registered."
                    )
                else:
                    try:
                        await self.state_change_callback(new_state)
                    except Exception:  # pragma: no cover
                        logger.error(
                            f"Exception raised in control {self.name} "
                            f"on_state_change callback:\n"
                            f"{traceback.format_exc()}"
                        )

                self.prev_state = new_state
