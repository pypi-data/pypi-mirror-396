#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Strategies for breaking candidates ties."""
from __future__ import annotations
import enum

from ...types import enum_from_string


class PartialTieBreak(enum.Enum):
    """Tie break strategies using partial votes."""

    FROM_FIRST_VOTE = enum.auto()
    "explore partial scores from the first position to the last"
    FROM_LAST_VOTE = enum.auto()
    "explore partial scores from the last position to the first"
    RANDOM = enum.auto()
    "eplore partial scores randomly"

    @classmethod
    def get_value(cls, value: str | PartialTieBreak) -> PartialTieBreak:
        """Convert a value to a PartialTieBreak enum.

        Raises
        ------
        ValueError
            If value could not be parsed
        """
        if isinstance(value, PartialTieBreak):
            return value
        value = enum_from_string(value or "")
        if value in ("FROM_FIRST_VOTE", "FROM_FIRST", "FIRST_VOTE"):
            return cls.FROM_FIRST_VOTE
        if value in ("FROM_LAST_VOTE", "FROM_LAST", "LAST_VOTE"):
            return cls.FROM_LAST_VOTE
        if value == "RANDOM":
            return cls.RANDOM
        raise ValueError(f"unsupported value: {value}")
