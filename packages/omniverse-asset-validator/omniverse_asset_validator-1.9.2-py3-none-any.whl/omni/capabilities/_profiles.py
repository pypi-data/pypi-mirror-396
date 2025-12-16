# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

from dataclasses import dataclass
from enum import Enum

from ._capabilities import Capability, Capabilities


@dataclass(frozen=True)
class Profile:
    """
    Args:
        id: The id of the profile
        version: The version of the profile
        path: The path to the profile
        capabilities: The capabilities of the profile
    """
    id: str
    version: str
    path: str
    capabilities: list[Capability]


class Profiles(Profile, Enum):
    """
    An enumeration of all profiles.
    """
    