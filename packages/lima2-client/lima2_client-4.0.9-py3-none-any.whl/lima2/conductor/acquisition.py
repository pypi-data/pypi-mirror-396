# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Lima2 acquisition state.

Contains state logic for running acquisitions.
"""

import asyncio
import logging
import time
import traceback
import weakref
from dataclasses import dataclass
from enum import Enum, auto
from typing import Awaitable, Callable

from lima2.common.exceptions import Lima2BackendError
from lima2.common.types import FrameInfo
from lima2.conductor.processing import pipeline_classes
from lima2.conductor.processing.master_file import (
    FrameSavingChannel,
    MasterFileMetadata,
)
from lima2.conductor.processing.reduced_data import RoiParams
from lima2.conductor.tango.container import TangoProcessingGroup
from lima2.conductor.tango.processing import ProcessingErrorEvent, TangoProcessing
from lima2.conductor.tango.utils import format_exception
from lima2.conductor.utils import naturaltime

logger = logging.getLogger(__name__)


class AcquisitionEvent(Enum):
    """Events that can occur during the acquisition run."""

    ACQ_DEVICE_DONE = auto()
    """One acquisition device finished successfully."""
    PROC_DEVICE_DONE = auto()
    """One processing device finished successfully."""
    ACQ_DEVICE_FAILED = auto()
    """One acquisition device failed."""
    ACQ_DEVICE_DISCONNECTED = auto()
    """One acquisition device went offline (backend crash)."""
    PROC_DEVICE_FAILED = auto()
    """One processing device failed."""
    ACQ_FINISHED = auto()
    """All acquisition devices finished (successfully or not)."""
    PROC_FINISHED = auto()
    """All processing devices finished (successfully or not)."""
    FAILURE = auto()
    """A device failed."""
    FINISHED = auto()
    """All devices are done or failed.

    NOTE: this event has two effects: it marks the acquisition state as
    'finished', and stops the event loop. Any events queued after this one will
    not be handled.
    """


@dataclass
class SuccessFlag:
    success: bool


OnEndCallback = Callable[[SuccessFlag], Awaitable[None]]
"""Signature of the on_end() callback."""

OnFailureCallback = Callable[[], Awaitable[None]]
"""Signature of the on_failure() callback."""


class AcquisitionState:
    """Represents the state of a running acquisition.

    Keeps track of how many devices have reported success or failure so far.

    When start() is called, an event loop starts to process events enqueued via
    enqueue() and process(), and the internal state is updated in consequence.

    When specific events occur, callbacks passed to the constructor are called.
    E.g. when all receivers finish their acquisition, on_end() is called.

    Given the number of receivers, it is thus able to tell whether the
    acquisition is still running (some devices haven't reported back yet) or
    finished (all devices have finished successfully or with errors).
    """

    def __init__(
        self,
        num_receivers: int,
        on_end: OnEndCallback,
        on_failure: OnFailureCallback,
    ) -> None:
        self.num_receivers = num_receivers

        self.on_end = on_end
        """Called when all devices are done (successfully or not)."""
        self.on_failure = on_failure
        """Called when any device fails, but only once."""

        # Substate: we need to keep track of how many receivers and processing
        # devices are done, whether some failed, whether failure has already
        # occurred, etc.
        self.started: bool = False
        self.num_rcv_done: int = 0
        self.num_proc_done: int = 0
        self.acq_finished: bool = False
        self.rcv_failed: bool = False
        """True if a receiver failed to acquire a frame."""
        self.proc_finished: bool = False
        self.proc_failed: bool = False
        """True if a processing device failed to process a frame."""
        self.failed_once: bool = False
        """True if at least one FAILURE event was handled."""
        self.finished: bool = False
        """True when the FINISHED event is handled."""

        ###
        # Event loop
        self.event_queue: asyncio.Queue[
            tuple[AcquisitionEvent, asyncio.Future[None]]
        ] = asyncio.Queue()
        self.lock = asyncio.Lock()
        """
        Ensures events are processed one by one, preventing one event from being
        processed before the previous one is completely handled (including
        executing remote commands).
        """
        self.loop: asyncio.Task[None] | None = None

    def running(self) -> bool:
        """Returns True if the acquisition is running."""
        return self.started and not self.finished

    def failed(self) -> bool:
        """Returns True if the acquisition failed.

        NOTE: this is orthogonal to running(): some devices might have stopped,
        but others might still be running. In this case, both running() and
        failed() will return True.
        """
        return self.rcv_failed or self.proc_failed

    def describe(self) -> str:
        return (
            f"running={self.running()}, "
            f"failed={self.failed()}, "
            f"num_rcv_done={self.num_rcv_done}, "
            f"num_proc_done={self.num_proc_done}, "
            f"acq_finished={self.acq_finished}, "
            f"rcv_failed={self.rcv_failed}, "
            f"proc_finished={self.proc_finished}, "
            f"proc_failed={self.proc_failed}, "
            f"failed_once={self.failed_once}, "
            f"finished={self.finished}"
        )

    def start(self) -> None:
        """Mark the acquisition as running and start processing events."""
        self.started = True
        self.loop = asyncio.create_task(
            self._loop(), name="AcquisitionState event loop"
        )

    def detach(self) -> None:
        """Stop processing events."""
        if self.loop:
            self.loop.cancel()

    async def enqueue(self, event: AcquisitionEvent) -> asyncio.Future[None]:
        """Enqueue an event and return immediately.

        If other events are already in the queue, they will be processed first.

        The returned future can be awaited to pause until the event has been
        processed.
        """
        fut: asyncio.Future[None] = asyncio.Future()
        await self.event_queue.put((event, fut))
        return fut

    async def _handle(self, event: AcquisitionEvent) -> list[AcquisitionEvent]:
        """Handle an event.

        Returns all events generated as byproducts.
        """
        events: list[AcquisitionEvent] = []
        match event:
            case AcquisitionEvent.ACQ_DEVICE_DONE:
                self.num_rcv_done += 1

                if self.num_rcv_done == self.num_receivers:
                    events.append(AcquisitionEvent.ACQ_FINISHED)

            case AcquisitionEvent.ACQ_DEVICE_FAILED:
                self.num_rcv_done += 1
                self.rcv_failed = True

                events.append(AcquisitionEvent.FAILURE)

                if self.num_rcv_done == self.num_receivers:
                    events.append(AcquisitionEvent.ACQ_FINISHED)

            case AcquisitionEvent.ACQ_DEVICE_DISCONNECTED:
                events.append(AcquisitionEvent.ACQ_DEVICE_FAILED)
                # Assume the processing is unrecoverable: the processing device died
                # (honorably) with the receiver. This will allow us to clean up
                # regardless.
                events.append(AcquisitionEvent.PROC_DEVICE_DONE)
                events.append(AcquisitionEvent.PROC_DEVICE_FAILED)

            case AcquisitionEvent.ACQ_FINISHED:
                self.acq_finished = True

                if self.proc_finished:
                    events.append(AcquisitionEvent.FINISHED)

            case AcquisitionEvent.PROC_DEVICE_DONE:
                # NOTE(mdu) Unlike acquisition exceptions, processing "done"
                # events can arrive even though the device also failed. So, for
                # each processing device, we expect there to be one "done" event
                # and one potential "error" event.
                self.num_proc_done += 1

                if self.num_proc_done == self.num_receivers:
                    events.append(AcquisitionEvent.PROC_FINISHED)

            case AcquisitionEvent.PROC_DEVICE_FAILED:
                self.proc_failed = True
                events.append(AcquisitionEvent.FAILURE)

            case AcquisitionEvent.PROC_FINISHED:
                self.proc_finished = True

                if self.acq_finished:
                    events.append(AcquisitionEvent.FINISHED)

            case AcquisitionEvent.FINISHED:
                if not self.rcv_failed:
                    logger.info("✅ All frames received")
                else:
                    logger.error("🔥 Acquisition finished with errors: see above 🔥")

                if not self.proc_failed:
                    logger.info("✅ Pipeline finished without errors")
                else:
                    logger.info("🔥 Pipeline finished with errors: see above 🔥")

                try:
                    await self.on_end(
                        SuccessFlag(success=not (self.rcv_failed or self.proc_failed))
                    )
                except BaseException:
                    logger.warning(
                        f"Exception in on_end() callback: {traceback.format_exc()}"
                    )

                self.finished = True

            case AcquisitionEvent.FAILURE:
                if not self.failed_once:
                    self.failed_once = True
                    try:
                        await self.on_failure()
                    except BaseException:
                        logger.warning(
                            f"Exception in on_failure() callback: "
                            f"{traceback.format_exc()}"
                        )
                else:
                    pass

            case _:
                raise ValueError(f"Invalid event value {event}")

        return events

    async def _loop(self) -> None:
        """Handles events sequentially in the order they were enqueued.

        Uses the lock to prevent concurrent handling of events: one event is
        processed at a time until its handling is complete.

        If an exception is raised in the handler, it is logged and the
        processing continues. The exception is placed in the future, so if the
        event was queued with process(), the exception is raised in the caller's
        context.
        """
        while True:
            async with self.lock:
                evt, fut = await self.event_queue.get()
                logger.debug(f"Handling {evt}")
                try:
                    events = await self._handle(event=evt)
                    for ev in events:
                        await self.enqueue(ev)
                    fut.set_result(None)
                except BaseException as e:
                    logger.error(
                        f"Error while handling {evt}: {traceback.format_exc()}"
                    )
                    fut.set_exception(e)

                # NOTE: break condition
                if evt is AcquisitionEvent.FINISHED:
                    break


class Acquisition:
    """Prepared acquisition, ready to start.

    Holds an internal state, a set of processing devices, and a Pipeline instance.

    Listens to events from all devices in order to update its state and properly manage
    local tasks.
    """

    def __init__(
        self,
        processing_devices: TangoProcessingGroup,
        on_end: OnEndCallback,
        on_failure: OnFailureCallback,
        num_frames: int,
        frame_infos: dict[str, FrameInfo],
        roi_params: RoiParams,
        saving_channels: dict[str, FrameSavingChannel],
        masterfile_metadata: MasterFileMetadata,
    ) -> None:
        self.uuid = processing_devices.uuid
        self.state = AcquisitionState(
            num_receivers=len(processing_devices),
            on_end=on_end,
            on_failure=on_failure,
        )
        self.proc_group = processing_devices
        """Processing device group."""

        # Instantiate a Pipeline
        pipeline_class = pipeline_classes[self.proc_group.class_name]
        self.pipeline = pipeline_class(
            devices=processing_devices,
            num_frames=num_frames,
            frame_infos=frame_infos,
            roi_params=roi_params,
            saving_channels=saving_channels,
            masterfile_metadata=masterfile_metadata,
        )
        """Processing pipeline."""

        self.processing_errors: list[str] = []
        """Holds processing error messages that occurred during the run, if any."""

        self.done_devices: set[TangoProcessing] = set()
        """Set of processing devices that have finished (successfully or not)."""

    def __del__(self) -> None:
        logger.debug(f"Acquisition instance {self.uuid} destroyed")

    def running(self) -> bool:
        return self.state.running()

    def failed(self) -> bool:
        return self.state.failed()

    def start(self) -> None:
        """Start the pipeline subtasks and listen for device events."""
        self.pipeline.start()
        self.state.start()

    @staticmethod
    async def attach(
        processing_devices: TangoProcessingGroup,
        on_end: OnEndCallback,
        on_failure: OnFailureCallback,
        num_frames: int,
        frame_infos: dict[str, FrameInfo],
        roi_params: RoiParams,
        saving_channels: dict[str, FrameSavingChannel],
        masterfile_metadata: MasterFileMetadata,
    ) -> "Acquisition":
        """
        Instantiate a complete Acquisition instance listening to processing device
        events.
        """
        instance = Acquisition(
            processing_devices=processing_devices,
            on_end=on_end,
            on_failure=on_failure,
            num_frames=num_frames,
            frame_infos=frame_infos,
            roi_params=roi_params,
            saving_channels=saving_channels,
            masterfile_metadata=masterfile_metadata,
        )

        await instance.listen()

        return instance

    def detach(self) -> None:
        """Stop listening to events."""
        self.state.detach()

    async def notify(self, event: AcquisitionEvent) -> None:
        """Enqueue an event in the AcquisitionState and return."""
        await self.state.enqueue(event=event)

    async def listen(self) -> None:
        """Listen to processing device events to update the AcquisitionState.

        Should be called just after instantiating the Acquisition instance.
        """

        # NOTE: Using weakref in event handlers is necessary to allow the
        # garbage collector to destroy the Pipeline object.
        # This is CRUCIAL for proper cleanup of the tango DeviceProxy
        # instances.
        # See https://gitlab.esrf.fr/limagroup/lima2-client/-/issues/90.
        wself = weakref.ref(self)

        async def on_device_finished(device: TangoProcessing) -> None:
            """Adds a processing device to the done_devices set.

            When the set is complete, call the on_finished callback registered to
            this pipeline instance (see constructor).
            """
            logger.info(f"Processing device {device.name} is done")

            self_ref = wself()
            if self_ref is None:
                return

            await self_ref.notify(event=AcquisitionEvent.PROC_DEVICE_DONE)

            self_ref.done_devices.add(device)
            if self_ref.done_devices == set(self_ref.proc_group):
                logger.info("Closing pipeline")
                await self_ref.pipeline.close()

        async def on_device_error(evt: ProcessingErrorEvent) -> None:
            """Reports a processing error to the registered callback."""
            self_ref = wself()
            if self_ref is None:
                return

            err_msg = format_exception(
                where=evt.device_name,
                when="while processing frames",
                what=evt.what,
                info=evt.info,
            )
            logger.warning(err_msg)
            self_ref.processing_errors.append(err_msg)

            await self_ref.notify(event=AcquisitionEvent.PROC_DEVICE_FAILED)

        reg_t0 = time.perf_counter()

        results = await self.proc_group.listen(
            on_finished=on_device_finished, on_error=on_device_error
        )

        errors = [res for res in results if res is not None]
        if len(errors) > 0:
            raise Lima2BackendError(
                "Couldn't register event handlers on some processing devices:\n- "
                + "\n- ".join([str(err) for err in errors])
            )

        logger.info(
            f"Registered to processing device events in "
            f"{naturaltime(time.perf_counter() - reg_t0)}"
        )
