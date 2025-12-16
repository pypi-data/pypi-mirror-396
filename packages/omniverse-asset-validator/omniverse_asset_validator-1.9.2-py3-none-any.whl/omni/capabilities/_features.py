# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

from dataclasses import dataclass
from enum import Enum


from ._requirements import Requirement, Requirements


@dataclass(frozen=True)
class Feature:
    """
    Args:
        id: The id of the feature
        version: The version of the feature
        path: The path to the feature
        requirements: The requirements of the feature
    """
    id: str
    version: str
    path: str
    requirements: list[Requirement]

class Features(Feature, Enum):
    """
    An enumeration of all features.
    """
    MINIMAL_PLACEABLE_VISUAL = (
        "minimal_placeable_visual", 
        "1.0.0",
        "features/minimal_placeable_visual.html",
        [
            Requirements.HI_001,
            Requirements.HI_004,
            Requirements.HI_003,
            Requirements.UN_006,
            Requirements.UN_007,
            Requirements.VG_002,
            Requirements.VG_024,
            Requirements.VG_025,
            Requirements.VG_028,
            Requirements.VG_027,
            Requirements.VG_014,
            Requirements.VG_029,
            Requirements.VG_MESH_001,
        ]
    )
    