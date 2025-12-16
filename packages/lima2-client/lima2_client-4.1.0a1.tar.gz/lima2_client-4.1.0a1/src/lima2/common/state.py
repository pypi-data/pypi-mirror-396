# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Lima2 acquisition system state classes."""

import logging
from enum import Enum, IntFlag, auto

logger = logging.getLogger(__name__)


class DeviceState(Enum):
    """State of an individual lima2 device

    Values *must* match `enum class acq_state_enum`.
    """

    IDLE = 0
    PREPARED = 1
    RUNNING = 2
    STOPPED = 3
    FAULT = 4
    TERMINATE = 5
    OFFLINE = 6


class RunState(IntFlag):
    """Represents the current runstate, a light client-side state flag.

    This state has two main purposes: to prevent invalid user commands,
    and to keep track of whether acquisition and processing are done.

    Since acquisition and processing can finish in either order, it is
    necessary to have orthogonal states for those two cases, to present
    a valid picture.
    """

    IDLE = auto()
    """Not running."""
    RUNNING = auto()
    """Running."""

    ACQ_DONE = auto()
    """Once acquisition is done on all receivers."""
    PROC_DONE = auto()
    """Once processing is done on all receivers."""

    ACQ_EXCEPTION = auto()
    """An exception occurred in the acquisition thread."""
    PROC_EXCEPTION = auto()
    """An exception occurred in the processing pipeline."""

    # Composite states, used for better clarity of the state

    DONE = RUNNING | ACQ_DONE | PROC_DONE

    WAITING_FOR_ACQ = RUNNING | PROC_DONE
    WAITING_FOR_PROC = RUNNING | ACQ_DONE

    ACQ_FAILED = RUNNING | ACQ_EXCEPTION
    PROC_FAILED = RUNNING | PROC_EXCEPTION

    FAULT = ACQ_EXCEPTION | PROC_EXCEPTION
    """Upon error in the acquisition or processing."""

    ACQUISITION_DONE_BUT_PROCESSING_FAILED = RUNNING | PROC_EXCEPTION | ACQ_DONE
    PROCESSING_DONE_BUT_ACQUISITION_FAILED = RUNNING | ACQ_EXCEPTION | PROC_DONE

    def __str__(self) -> str:
        return self.name or f"UNKNOWN ({self.value})"


class State(Enum):
    """System-wide aggregated state of the acquisition system.

    This state corresponds to the aggregation of all device states.
    It is not meant to be kept around, but only computed punctually
    to determine whether an action is possible at the current instant.
    """

    IDLE = auto()
    """All devices are IDLE or STOPPED, or in a mix of IDLE and PREPARED."""
    PREPARED = auto()
    """All devices are PREPARED."""
    RUNNING = auto()
    """All devices are RUNNING, or in a mix of RUNNING and IDLE."""
    FAULT = auto()
    """At least one device is FAULT."""
    UNKNOWN = auto()
    """
    In an inconsistent mix of states, which cannot be resolved.
    Usually requires a server restart.
    """
    DISCONNECTED = auto()
    """At least one device is offline."""

    @staticmethod
    def from_device_states(states: list[DeviceState]) -> "State":
        """Compute the system-wide state from individual DeviceStates."""

        control = states[0]

        if all(s == control for s in states):
            match control:
                case DeviceState.IDLE | DeviceState.STOPPED:
                    return State.IDLE
                case DeviceState.PREPARED:
                    return State.PREPARED
                case DeviceState.RUNNING:
                    return State.RUNNING
                case DeviceState.FAULT | DeviceState.TERMINATE:
                    return State.FAULT
                case _:
                    raise NotImplementedError(f"Unexpected device state {control}")

        elif all(s in [DeviceState.IDLE, DeviceState.PREPARED] for s in states):
            # Tolerate a mix of prepared and idle devices. In this case,
            # the global state shall be IDLE (forcing user to prepare again).
            return State.IDLE

        elif all(s in [DeviceState.RUNNING, DeviceState.IDLE] for s in states):
            # Tolerate a mix of running and idle devices. In this case,
            # the global state shall be RUNNING.
            return State.RUNNING

        elif any(s == DeviceState.FAULT for s in states):
            logger.warning(
                f"At least one device in FAULT state -> system is {State.FAULT}"
            )
            return State.FAULT

        else:
            logger.warning(
                f"Inconsistent server states ({states}) -> system is {State.UNKNOWN}"
            )
            return State.UNKNOWN
