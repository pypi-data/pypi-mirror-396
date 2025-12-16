# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Lima2 receiver tango device.

Specializes the ReceiverDevice protocol for lima2 tango receiver device.

Allows us to add typechecking to all attributes and remote procedure calls.
"""

import asyncio
import contextlib
import functools
import logging
import traceback
from typing import Any, Awaitable, Callable, Iterator
from uuid import UUID

import orjson
import tango as tg

from lima2.common.exceptions import Lima2DeviceError
from lima2.common.progress_counter import SingleCounter
from lima2.common.state import DeviceState
from lima2.conductor.tango.utils import TangoDevice, handle_tango_errors

logger = logging.getLogger(__name__)


class TangoReceiver(TangoDevice):
    """Wrapper around the raw receiver DeviceProxy.

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
    async def prepare(
        self,
        uuid: UUID,
        acq_params: dict[str, Any],
        proc_params: dict[str, Any],
    ) -> None:
        logger.debug(f"Passing prepare params to RECEIVER ({self.name})")

        # NOTE(mdu) Workaround for a pytango 10.0.2 bug: calling write_attribute
        # on a device which is offline will not raise a DevFailed exception.
        # To make sure we can catch an error and print a useful message, ping
        # devices before setting the params
        await self.ping()

        await self.device.write_attribute("acq_params", orjson.dumps(acq_params))
        await self.device.write_attribute("proc_params", orjson.dumps(proc_params))
        logger.debug(f"Executing prepare on RECEIVER ({self.name})")
        await self.device.Prepare(str(uuid))

    @handle_tango_errors
    async def start(self) -> None:
        await self.device.Start()

    @handle_tango_errors
    async def stop(self) -> None:
        await self.device.Stop()

    @handle_tango_errors
    async def reset(self) -> None:
        await self.device.Reset()

    @handle_tango_errors
    async def read_attribute(self, name: str) -> Any:
        """Get an attribute's value given its name."""
        return (await self.device.read_attribute(name)).value

    @handle_tango_errors
    async def acq_state(self) -> DeviceState:
        """Request the device's acq_state attribute.

        If the request raises, assume the device is offline.
        """
        try:
            return DeviceState(int(await self.read_attribute("acq_state")))
        except Lima2DeviceError:
            return DeviceState.OFFLINE

    @handle_tango_errors
    async def nb_frames_xferred(self) -> SingleCounter:
        value = await self.read_attribute("nb_frames_xferred")
        return SingleCounter(
            name="nb_frames_xferred",
            value=value,
            source=self.name,
        )

    @handle_tango_errors
    async def list_pipelines(self) -> list[str]:
        value: list[str] = await self.read_attribute("pipelines")
        return value

    @handle_tango_errors
    async def erase_pipeline(self, uuid: str) -> None:
        await self.device.erasePipeline(uuid)

    @handle_tango_errors
    async def last_error(self) -> str:
        return str(await self.read_attribute("last_error"))

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

    # TODO(mdu) cached method leaks self
    # https://docs.astral.sh/ruff/rules/cached-instance-method/
    @functools.cache
    def fetch_proc_schema(self, proc_class: str) -> str:
        """Retrieve 'proc_params' schema for a processing class from the tango database.

        Use the cached value if we have fetched it already.
        """
        tango_db = tg.Database()

        prop = tango_db.get_class_attribute_property(proc_class, "proc_params")
        # Each attribute property is a StdStringVector with a single value
        try:
            return str(prop["proc_params"]["schema"][0])
        except KeyError as e:
            raise RuntimeError(
                f"Schema for 'proc_params' not found for "
                f"processing class '{proc_class}'"
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
                                f"Exception raised in receiver {self.name} "
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
                            f"Exception raised in receiver {self.name} "
                            f"on_state_change callback:\n"
                            f"{traceback.format_exc()}"
                        )

                self.prev_state = new_state
