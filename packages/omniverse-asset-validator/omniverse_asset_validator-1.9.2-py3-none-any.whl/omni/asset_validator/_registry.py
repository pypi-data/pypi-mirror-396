# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from __future__ import annotations

from bisect import insort
from collections import defaultdict
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from functools import cached_property, total_ordering
from typing import Generic, TypeVar

from ._events import EventListener, EventStream, create_event_stream
from ._semver import SemVer

K = TypeVar("K")
V = TypeVar("V")


__all__ = [
    "Registry",
    "VersionedRegistry",
]


class Registry(Generic[K, V]):
    """
    A generic registry of key-value pairs.
    """

    def __init__(self):
        self._registry: dict[K, V] = {}

    def add(self, key: K, value: V) -> None:
        self._registry[key] = value
        self.event_stream.notify()

    def get(self, key: K, default: V | None = None) -> V | None:
        return self._registry.get(key, default)

    def clear(self) -> None:
        self._registry.clear()
        self.event_stream.notify()

    def __getitem__(self, key: K) -> V:
        return self._registry[key]

    def __delitem__(self, key: K) -> None:
        del self._registry[key]
        self.event_stream.notify()

    def __iter__(self) -> Iterator[V]:
        return iter(self._registry.values())

    def __len__(self) -> int:
        return len(self._registry)

    def keys(self) -> list[K]:
        return list(self._registry.keys())

    def values(self) -> list[V]:
        return list(self._registry.values())

    def items(self) -> list[tuple[K, V]]:
        return list(self._registry.items())

    @cached_property
    def event_stream(self) -> EventStream:
        return create_event_stream()

    def add_callback(self, callback: Callable[[], None]) -> EventListener:
        return self.event_stream.create_event_listener(callback)


@total_ordering
@dataclass(frozen=True)
class IdVersion:
    """
    A class to represent an ID and version.
    """

    id: str
    version: SemVer

    def __lt__(self, other: IdVersion) -> bool:
        return (self.id, self.version) < (other.id, other.version)


class VersionedRegistry(Registry[IdVersion, V]):
    """
    A registry of values with versioned keys.
    """

    def __init__(self, values: list[V] | None = None):
        super().__init__()
        self._registry_by_id: dict[str, list[IdVersion]] = defaultdict(list)
        if values:
            for value in values:
                self.add(value)

    def create_key(self, value: V) -> IdVersion:
        raise NotImplementedError("Subclass must implement this method")

    def add(self, value: V, overwrite: bool = False) -> None:
        key: IdVersion = self.create_key(value)
        if not overwrite and key in self._registry:
            raise ValueError(f"Value with key {key} already exists")
        super().add(key, value)
        insort(self._registry_by_id[key.id], key)

    def remove(self, value: V) -> None:
        """
        Remove a value from the registry.

        Args:
            value: The value to remove.

        Raises:
            ValueError: If the value is not found in the registry.
        """
        key: IdVersion = self.create_key(value)
        self._registry_by_id[key.id].remove(key)
        del self[key]

    def find(self, id: str, version: str | SemVer | None = None) -> V | None:
        """
        Find a value by ID and version.
        """
        keys = self._registry_by_id[id]
        if not keys:
            return None
        if not version or version == SemVer.LATEST:
            return self[keys[-1]]
        version = SemVer(version) if isinstance(version, str) else version
        for key in reversed(keys):
            if key.version.is_compatible(version):
                return self[key]
        return None

    def latest_keys(self) -> list[IdVersion]:
        return [values[-1] for values in self._registry_by_id.values() if values]

    def latest_values(self) -> list[V]:
        return [self[key] for key in self.latest_keys()]
