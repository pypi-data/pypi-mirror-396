#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Utils for random numbers operations."""

from __future__ import annotations
from typing import (
    Any,
    Union,
)
import random


RandomSeed = Union[int, random.Random]
"Type for random generators' seeds"


class Dice:
    """Wrapper for a random number generator.

    It keeps a usage counter.
    """

    _seed: int | None
    _original_state: Any | None
    _rng: random.Random

    def __init__(self, rng: RandomSeed | None = None):
        """Create a dice from `rng`.

        Args
        ----

        rng
            A random seed. When None, a random number generator with a randomly
            chosen seed is used.
        """
        if isinstance(rng, random.Random):
            self._rng = rng
            self._original_state = rng.getstate()
            self._seed = None
        else:
            self._seed = rng
            if self._seed is None:
                self._seed = random.randint(0, 2**32 - 1)
            self._rng = random.Random(self._seed)
            self._original_state = None
        self._uses = 0

    @property
    def deterministic(self) -> bool:
        """Return True if the dice has not been used."""
        return self._uses == 0

    def __call__(self) -> random.Random:
        """Increment the randomg generator usage and return it."""
        self._uses += 1
        return self._rng

    def state(self) -> dict[str, Any]:
        """Return a serializable state."""
        if self.deterministic:
            return {}
        return {
            "deterministic": self.deterministic,
            "uses": self._uses,
            "seed": self._seed,
            "original_state": self._original_state,
        }
