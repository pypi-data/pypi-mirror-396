#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Adapters are allocators that modifies the behaviour of base methods."""

from typing import TypeVar
from ...types import SortHash


CandLike = TypeVar("CandLike", bound=SortHash)
"any valid candidate"
