#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Function collections."""

from __future__ import annotations
from typing import (
    Generic,
    TypeVar,
    Callable,
)

AnyCallable = TypeVar("AnyCallable", bound=Callable)
"Any type for callables"


class FunctionCollection(Generic[AnyCallable]):
    """Collection of named functions.

    It allows to register or retrieve function by names.

    A registered function can have more than one associated name.
    """

    def __init__(self, transform_f: Callable[[str], str] | None = None) -> None:
        """Create a collection."""
        self.transform_f = transform_f or key_normalizer
        self.items: dict[str, AnyCallable] = {}

    def __getitem__(self, key: str) -> AnyCallable:
        """Get a function identified by some `key`."""
        return self.items[self.transform_f(key)]

    def get(self, key_or_function: str | AnyCallable) -> AnyCallable:
        """Get a function associated to a key.

        If a function is provided, return the same function
        """
        if isinstance(key_or_function, str):
            return self[key_or_function]
        return key_or_function

    def __contains__(self, key: str):
        """Return `True` if `key` is in this collection."""
        return self.transform_f(key) in self.items

    def add(self, key: str, item: AnyCallable):
        """Add a new function identified by `key`."""
        self.items[self.transform_f(key)] = item

    def register(self, *keys: str):
        """Register a new function identified by the given keys.

        Decorator for adding functions to the collection.
        """

        def decorator(func):
            for key in keys:
                self.add(key, func)
            return func

        return decorator


def key_normalizer(key: str) -> str:
    """Transform a key to a canonical form."""
    return key.strip().replace(" ", "_").replace("-", "_").lower()
