#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Iterative divisor allocator, based on [DorfleitnerKlein:1997]_.

:ref:`References <interregnum_biblio>`
--------------------------------------

* [DorfleitnerKlein:1997]_
* [Zachariasen:2006]_

----
"""
from __future__ import annotations
from typing import (
    Generic,
    Callable,
)
from dataclasses import dataclass, field
from collections import defaultdict
from functools import partial
import math
import enum
import heapq
from fractions import Fraction
from ..types import (
    Candidate,
    AnyName,
    check_seats,
    Score,
    Result,
    Allocator,
    allocators,
    Input,
    Summary,
    CalculationState,
)
from .. import events as evt
from ...divisors import Divisor
from ...rounding import (
    signposts,
    RoundingWithSignpost,
    ScoreWithInf,
    is_finite,
)
from .highest_averages import HAResultData
from .. import inputs as ipt


class Discrepancy(enum.IntEnum):
    """Mark for seats discrepancies."""

    INCREMENTABLE = 1
    "A candidate can win one more seat"
    DECREMENTABLE = -1
    "A candidate can lose one seat"
    EXACT = 0
    "A candidate can not lose or wine seats"


@dataclass
class IDResultData(HAResultData, Generic[AnyName]):
    """Result data for Iterative Divisor Allocator."""

    ties: dict[AnyName, Discrepancy] = field(
        default_factory=lambda: defaultdict(lambda: Discrepancy.EXACT)
    )
    "Candidates with ties (incrementable or decrementable)"


def or_inf(val: ScoreWithInf) -> Score | float:
    """Return val if is finite, otherwise return Infinity."""
    if not is_finite(val):
        return math.inf
    return val


Priority = tuple[Score | float, Score, AnyName]
"Anything representing a priority for a candidate"


def priority_inc(round_f: RoundingWithSignpost, cand: Candidate[AnyName]) -> Priority:
    """Priority for incrementation."""
    val = round_f.incrementation(cand.seats, cand.votes)
    return or_inf(val), -cand.votes, cand.name


def priority_dec(round_f: RoundingWithSignpost, cand: Candidate[AnyName]) -> Priority:
    """Priority for decrementation."""
    val = round_f.decrementation(cand.seats, cand.votes)
    return -or_inf(val), cand.votes, cand.name


@allocators.register("iterative_divisor")
class IterativeDivisorAllocator(Allocator[AnyName, IDResultData[AnyName]]):
    """Iterative divisor method.

    See [DorfleitnerKlein:1997]_ and [Zachariasen:2006]_

    :data:`.allocators` collection keys:

    - `iterative_divisor`
    - `iterative-divisor`
    """

    def __init__(self, signpost_f: str | RoundingWithSignpost):
        """Create an iterative divisor allocator.

        Args
        ----
        `signpost_f`
            round function with signpost (collection :data:`.signposts`).
        """
        super().__init__(
            Input.SEATS | Input.CANDIDATES,
            Input.EXCLUDE_CANDIDATES,
        )
        self.signpost_f = signpost_f

    def calc(
        self, candidates: ipt.ICandidates, seats: int, exclude_candidates: ipt.INames | None = None
    ) -> Result[AnyName, IDResultData[AnyName]]:
        """Allocate `candidates` to `seats`.

        Initial candidate seats are ignored. All won seats will be logged by :class:`.SeatsEvent`.

        Args
        ----
        candidates
            list of candidates
        seats
            allocatable seats
        exclude_candidates
            list of candidates excluded from allocation


        Examples
        --------
        >>> # use the Jefferson method
        >>> jefferson = IterativeDivisorAllocator("jefferson")
        """
        check_seats(seats)
        initial_seats = {cand.name: cand for cand in Candidate.make_input(candidates)}

        excluded: Summary[AnyName] = Summary.build(
            initial_seats[name] for name in exclude_candidates or [] if name in initial_seats
        )

        state = CalculationState()
        data: IDResultData[AnyName] = IDResultData()
        data.log.extend(
            evt.IneligibleEvent(target=name, criterion="initial_exclusion")
            for name in excluded.names
        )

        if excluded.seats > 0:
            seats -= excluded.seats
            check_seats(seats)

        eligible = sorted(
            [x for x in initial_seats.values() if x.name not in excluded.names],
            key=lambda x: (-x.votes, x.name),
        )
        total_votes = sum(x.votes for x in eligible)
        if not eligible:
            return state.make_result([], data)

        quota = Fraction(total_votes, seats)

        round_f = signposts.get(self.signpost_f)

        # multiplier step

        allocated = 0
        for idx, cand in enumerate(eligible):
            weight = cand.votes / quota
            new_cand = cand.with_seats(round_f(weight))
            allocated += new_cand.seats
            eligible[idx] = new_cand

        # discrepancy loop
        discrepancy = allocated - seats

        priority_f: Callable[[Candidate[AnyName]], tuple[Score | float, Score, AnyName]]
        if discrepancy < 0:
            diff = Discrepancy.INCREMENTABLE
            priority_f = partial(priority_inc, round_f)
        else:
            diff = Discrepancy.DECREMENTABLE
            priority_f = partial(priority_dec, round_f)

        heap = [(priority_f(c), c) for c in eligible]
        heapq.heapify(heap)

        while discrepancy != 0:
            try:
                _, cand = heapq.heappop(heap)
            except IndexError:
                break

            allocated += diff
            cand = cand.add_seats(diff)

            heapq.heappush(heap, (priority_f(cand), cand))

            discrepancy = allocated - seats

        # multiple solutions step
        min_inc = min(or_inf(round_f.incrementation(c.seats, c.votes)) for _, c in heap)
        max_dec = max(or_inf(round_f.decrementation(c.seats, c.votes)) for _, c in heap)

        data.remaining_seats = seats - allocated

        if min_inc == max_dec:
            for _, cand in heap:
                if min_inc == or_inf(round_f.incrementation(cand.seats, cand.votes)):
                    data.ties[cand.name] = Discrepancy.INCREMENTABLE
                elif max_dec == or_inf(round_f.decrementation(cand.seats, cand.votes)):
                    data.ties[cand.name] = Discrepancy.DECREMENTABLE

        data.log.extend(
            evt.SeatsEvent(
                target=cand.name,
                seats=cand.seats,
                criterion="quota",
            )
            for _, cand in heap
            if cand.seats
        )

        if data.ties:
            data.log.append(evt.TieEvent(candidates=tuple(data.ties)))

        # calc quotas
        def calc_quota(votes: Score, seats: int) -> Divisor:
            if votes <= 0:
                return 0
            signpost = round_f.unbounded_signpost(seats)
            if signpost <= 0:
                return math.inf
            return Fraction(votes, signpost)

        d_min: Divisor = max(
            x for x in (calc_quota(x.votes, x.seats) for _, x in heap if x.votes > 0)
        )
        d_max: Divisor = min(
            x for x in (calc_quota(x.votes, x.seats - 1) for _, x in heap if x.votes > 0)
        )

        assert (d_min is not None) and (d_max is not None) and (d_min <= d_max), (d_min, d_max)

        data.min_quota = d_min
        data.max_quota = d_max

        elected = [x for _, x in heap]

        return state.make_result(elected, data)
