#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""
Single votes allocators.

A single vote allocator needs an input
:attr:`candidates <interregnum.methods.inputs.InputDict.candidates>`.
"""

from .highest_averages import HighestAveragesAllocator
from .iterative_divisor import IterativeDivisorAllocator
from .largest_remainder import LargestRemainderAllocator
from .limited_voting import LimitedVotingAllocator
from .winner_takes_all import WinnerTakesAllAllocator

from ..types import allocators


__all__ = [
    "HighestAveragesAllocator",
    "IterativeDivisorAllocator",
    "LargestRemainderAllocator",
    "LimitedVotingAllocator",
    "WinnerTakesAllAllocator",
    "allocators",
]
