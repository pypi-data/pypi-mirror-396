#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Compensatory systems.

A compensatory system adjust another allocation following certain rules.
First vote is provided by the input
:attr:`initial_seats <interregnum.methods.inputs.InputDict.initial_seats>`.
"""

from .additional_member import AdditionalMemberAdapter
from .mixed_member import MixedMemberAdapter

from ..types import allocators


__all__ = [
    "AdditionalMemberAdapter",
    "MixedMemberAdapter",
    "allocators",
]
