#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Quota bisection process."""
from fractions import Fraction
from .quotas import hare_quota
from .types import Score


class QuotaBisect:
    """Find the best quota using binary search."""

    def __init__(self, quota: Score, votes: Score, seats: int, step: Score = 1):
        """Start with a `quota` calculated for `votes` and `seats`.

        `step` defines the quota increment at each step.

        Args
        ----

        quota
            initial quota
        votes
            number of votes
        seats
            number of seats
        step
            move the quota by using this step
        """
        self._step = step
        self._lower = quota
        self._upper = quota + hare_quota(votes, seats).reference - quota
        if self._lower > self._upper:
            self._lower, self._upper = self._upper, self._lower
        self._split()

    def _split(self) -> None:
        midpoint = Fraction(self._upper - self._lower, 2)
        self._pivot = self._lower + midpoint

    def guess(self) -> Score:
        """Get current tentative quota."""
        return self._pivot

    def bad(self) -> None:
        """Mark current quota as a bad quota.

        A bad quota will allocate more seats than the allowed amount.
        """
        self._lower = self._pivot + self._step
        self._split()

    def good(self) -> None:
        """Mark current quota as a good quota.

        A good quota will allocate the allowed amount or seats, or less.
        """
        self._upper = self._pivot - self._step
        self._split()

    def has_more(self):
        """Return True if there are values yet to explore."""
        return self._lower < self._upper
