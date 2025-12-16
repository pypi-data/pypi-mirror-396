# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Conductor client processing subpackage.

Contains functionality related to processing pipelines, reduced data handling
and master file generation.

Contains a specific class for each supported processing pipeline.
This file defines a dictionary of all supported pipelines by tango class name.

```
legacy_class = processing.pipeline_classes["LimaProcessingLegacy"]
legacy_pipeline = legacy_class(...)
```
"""


from lima2.conductor.processing.failing import Failing
from lima2.conductor.processing.legacy import Legacy
from lima2.conductor.processing.pipeline import Pipeline
from lima2.conductor.processing.smx import Smx
from lima2.conductor.processing.xpcs import Xpcs

# Dictionary of all pipelines supported by the client
pipeline_classes: dict[str, type[Pipeline]] = {
    "LimaProcessingLegacy": Legacy,
    "LimaProcessingSmx": Smx,
    "LimaProcessingXpcs": Xpcs,
    "LimaProcessingFailing": Failing,
}
