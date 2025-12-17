#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""
Preferential vote allocators.

A preferential vote allocator needsan input
:attr:`preferences <interregnum.methods.inputs.InputDict.preferences>`.
"""

from .borda_count import BordaCountAllocator
from .condorcet import (
    CondorcetCopelandAllocator,
    CondorcetMinimaxAllocator,
    CondorcetRankedPairsAllocator,
)
from .transferable_vote import (
    SingleTransferableVoteAllocator,
    InstantRunOffAllocator,
    transfers,
)
from .types import Preference
from ..types import allocators


__all__ = [
    "allocators",
    "transfers",
    "Preference",
    "BordaCountAllocator",
    "CondorcetCopelandAllocator",
    "CondorcetMinimaxAllocator",
    "CondorcetRankedPairsAllocator",
    "SingleTransferableVoteAllocator",
    "InstantRunOffAllocator",
]
