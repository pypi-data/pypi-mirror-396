# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT license. See LICENSE for more info.

"""Failing pipeline subclass."""

import logging
from typing import Any

from lima2.common.exceptions import Lima2ValueError
from lima2.common.pipelines import failing
from lima2.conductor.processing.pipeline import Pipeline
from lima2.conductor.topology import DynamicDispatch, Topology

logger = logging.getLogger(__name__)


class Failing(Pipeline):
    TANGO_CLASS = failing.class_name

    FRAME_SOURCES = failing.frame_sources
    """Available frame sources."""

    REDUCED_DATA_SOURCES = failing.reduced_data_sources
    """Available static reduced data sources."""

    PROGRESS_INDICATOR = failing.progress_indicator
    """Name of the main progress counter."""


def finalize_params(proc_params: dict[str, Any], topology: Topology) -> None:
    """Finalize pipeline-specific parameters.

    NOTE: any param change which breaks the validation will prevent the
    acquisition prepare() call, in a way the user has no control over.
    """

    if type(topology) is DynamicDispatch:
        raise Lima2ValueError(
            "Can't use failing pipeline with dynamic dispatch: "
            "frame_idx stream isn't supported"
        )
