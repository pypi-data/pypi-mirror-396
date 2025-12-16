# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from importlib.resources import files


class ExampleResult(str, Enum):
    """
    Args:
        SUCCESS: The example succeeded.
        FAILURE: The example failed.
    """

    SUCCESS = "success"
    FAILURE = "failure"


class ExampleSnippetLanguage(str, Enum):
    """
    Args:
        PYTHON: The example snippet is in Python.
        USD: The example snippet is in USD.
    """

    PYTHON = "python"
    USD = "usd"


@dataclass(frozen=True)
class ExampleSnippet:
    """
    Args:
        language: The language of the example snippet.
        content: The content of the example snippet (lazy-loaded from file).
    """

    language: ExampleSnippetLanguage
    content_file: str

    @cached_property
    def content(self) -> str:
        resource_files = files(__package__) / "resources" / "examples" / self.content_file
        return resource_files.read_text(encoding='utf-8')


@dataclass(frozen=True)
class Example:
    """
    Args:
        snippet: The snippet of code in a specific language.
        name: The name of the example.
        result: The result of the example.
    """

    snippet: ExampleSnippet
    display_name: str
    result: ExampleResult


class Examples(Example, Enum):
    """
    An enumeration of all examples.
    """
    
    NO_METERSPERUNIT_SPECIFIED_NOK = (
        ExampleSnippet(
            language=ExampleSnippetLanguage.USD,
            content_file="a80e5ec526a5.usd",
        ),
        "No metersPerUnit specified",
        ExampleResult.FAILURE,
    )
    
    METERSPERUNIT_NOT_SET_TO_1_0_NOK = (
        ExampleSnippet(
            language=ExampleSnippetLanguage.USD,
            content_file="f564eeaf18ff.usd",
        ),
        "metersPerUnit not set to 1.0",
        ExampleResult.FAILURE,
    )
    
    METERSPERUNIT_1_0_OK = (
        ExampleSnippet(
            language=ExampleSnippetLanguage.USD,
            content_file="4a04f5d9b830.usd",
        ),
        "metersPerUnit = 1.0",
        ExampleResult.SUCCESS,
    )
    
    MANY_CHILDREN_UNDER_A_SINGLE_PRIM_NOK = (
        ExampleSnippet(
            language=ExampleSnippetLanguage.USD,
            content_file="e275f2eb715e.usd",
        ),
        "Many children under a single prim",
        ExampleResult.FAILURE,
    )
    
    CHILDREN_DISTRIBUTED_AMONG_MULTIPLE_PRIMS_OK = (
        ExampleSnippet(
            language=ExampleSnippetLanguage.USD,
            content_file="99385cc5bdb5.usd",
        ),
        "Children distributed among multiple prims",
        ExampleResult.SUCCESS,
    )
    
    UNNECESSARY_EMPTY_LEAF_PRIMS_NOK = (
        ExampleSnippet(
            language=ExampleSnippetLanguage.USD,
            content_file="fc3b97f9b696.usd",
        ),
        "Unnecessary, empty leaf prims",
        ExampleResult.FAILURE,
    )
    
    PRIM_HIERARCHY_WITHOUT_UNNECESSARY_LEAF_PRIMS_OK = (
        ExampleSnippet(
            language=ExampleSnippetLanguage.USD,
            content_file="0a19ac9d7a5d.usd",
        ),
        "Prim hierarchy without unnecessary leaf prims",
        ExampleResult.SUCCESS,
    )
    
    TRIANGLE_WITH_INCONSISTENT_WINDING_ORDER_AND_NORMALS_NOK = (
        ExampleSnippet(
            language=ExampleSnippetLanguage.USD,
            content_file="c334b91c9672.usd",
        ),
        "Triangle with inconsistent winding order and normals",
        ExampleResult.FAILURE,
    )
    
    NON_MANIFOLD_EDGE_DUE_TO_INCONSISTENT_WINDING_NOK = (
        ExampleSnippet(
            language=ExampleSnippetLanguage.USD,
            content_file="3d5baf1c77b8.usd",
        ),
        "Non-manifold edge due to inconsistent winding",
        ExampleResult.FAILURE,
    )
    
    MANIFOLD_MESH_OK = (
        ExampleSnippet(
            language=ExampleSnippetLanguage.USD,
            content_file="90b35f9ae887.usd",
        ),
        "Manifold mesh",
        ExampleResult.SUCCESS,
    )
    
    INCONSISTENT_WINDING_ORDER_NOK = (
        ExampleSnippet(
            language=ExampleSnippetLanguage.USD,
            content_file="7dfd94ef0098.usd",
        ),
        "Inconsistent winding order",
        ExampleResult.FAILURE,
    )
    