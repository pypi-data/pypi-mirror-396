# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT license. See LICENSE for more info.

"""XPCS pipeline subclass."""

import logging
from typing import Any


from lima2.common.pipelines import xpcs
from lima2.conductor.processing.pipeline import Pipeline
from lima2.conductor.topology import DynamicDispatch, Topology

# Create a logger
logger = logging.getLogger(__name__)


class Xpcs(Pipeline):
    TANGO_CLASS = xpcs.class_name

    FRAME_SOURCES = xpcs.frame_sources
    """Available frame sources."""

    REDUCED_DATA_SOURCES = xpcs.reduced_data_sources
    """Available static reduced data sources."""

    PROGRESS_INDICATOR = xpcs.progress_indicator
    """Name of the main progress counter."""


def finalize_params(
    proc_params: dict[str, Any],
    receiver_idx: int,
    topology: Topology,
) -> None:
    """Finalize pipeline-specific parameters.

    NOTE: any param change which breaks the validation will prevent the
    acquisition prepare() call, in a way the user has no control over.
    """

    # Assign unique filename rank per receiver
    for source in xpcs.frame_sources.values():
        if source.saving_channel is not None:
            proc_params[source.saving_channel]["filename_rank"] = receiver_idx

    if type(topology) is DynamicDispatch:
        logger.info(
            "Dynamic dispatch: force 'frame_idx_enabled' "
            f"and 'saving*/include_frame_idx' to True on receiver {receiver_idx}"
        )

        proc_params["frame_idx_enabled"] = True
        for source in xpcs.frame_sources.values():
            if source.saving_channel is not None:
                proc_params[source.saving_channel]["include_frame_idx"] = True
