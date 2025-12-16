# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

from dataclasses import dataclass
from enum import Enum


class ParameterType(str, Enum):
    """Valid parameter types for requirements."""
    INT = "int"
    BOOL = "bool"
    FLOAT = "float"
    ENUM = "enum"


@dataclass(frozen=True)
class Parameter:
    """
    Args:
        display_name: The display name of the parameter
        type: The type of the parameter (int, bool, float, or enum)
        assigned_value: The assigned value of the parameter
        enum_values: The possible enum values (only for enum type)
    """
    display_name: str
    type: ParameterType
    assigned_value: int | bool | float | str | None = None
    enum_values: tuple[str, ...] | None = None


class Parameters(Parameter, Enum):
    """
    An enumeration of all unique parameters used across requirements.
    Each enum value is a tuple of (display_name, type, assigned_value, enum_values) that corresponds to a Parameter.
    """
    TRANSFORM_TOLERANCE = (
        "TRANSFORM_TOLERANCE",
        ParameterType.FLOAT,
        0.0001,
        None,
    )
