#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

r"""Highest averages method for proportional apportionments.

:ref:`References <interregnum_biblio>`
--------------------------------------

* [Gallagher:1992]_
* [KohlerZeh:2012]_
* [Loreg:1985]_
* [Denmark:2011]_

----
"""

from __future__ import annotations
from typing import (
    Sequence,
    Iterator,
    Generic,
)
import math
import dataclasses as dt
from fractions import Fraction
from typing_extensions import override

from ..types import (
    Candidate,
    AnyName,
    NonDeterministicAllocator,
    check_seats,
    allocators,
    Input,
    CandidateFilter,
    Result,
    NonDeterministicState,
)

from ...divisors import DivisorFunction, DivisorIterator, Divisor, divisor_iterators, divisors
from ..events import (
    Event,
    EventLog,
    QuotaWinnerEvent,
    TieEvent,
    SeatsEvent,
)
from ..adapters.ranking import RankingList, break_tie_ranking
from ...random import (
    RandomSeed,
)
from .. import inputs as ipt


def division(num: Divisor, den: Divisor):
    """Make a fraction or a float division."""
    if isinstance(den, float) or isinstance(num, float):
        return num / den
    return Fraction(num, den)


@dt.dataclass
class CandidateState(Generic[AnyName]):
    """Candidate internal state."""

    candidate: Candidate[AnyName]
    divisor: Iterator[Divisor]
    quotient: Divisor
    last_tie_victory: int = -1

    def update(self) -> None:
        """Update quotient and divisor."""
        self.quotient = division(self.candidate.votes, next(self.divisor))

    @classmethod
    def init(cls, candidate: Candidate[AnyName], div_f: DivisorIterator) -> CandidateState:
        """Init a candidate state."""
        seq = div_f.sequence(candidate.seats)
        quotient = division(candidate.votes, next(seq))

        return cls(
            candidate=candidate,
            divisor=seq,
            quotient=quotient,
        )

    def tie_state(self) -> Candidate[AnyName]:
        """Get a candidate with the same votes and the last tie victory."""
        return self.candidate.with_seats(self.last_tie_victory)


@dt.dataclass
class HAResultData(EventLog):
    """Additional result data for highest averages methods."""

    max_quota: Divisor = -math.inf
    "Maximum allowed quota"
    min_quota: Divisor = math.inf
    "Minimum allowed quota"
    remaining_seats: int = 0
    "Seats not allocated yet"

    def new_seat(self, criterion, winner: CandidateState):
        """Log new seat allocated to `winner` by `criterion`."""
        self.log.append(
            QuotaWinnerEvent(
                target=winner.candidate.name, quota=winner.quotient, criterion=criterion
            )
        )
        self.min_quota = min(self.min_quota, winner.quotient)
        self.max_quota = max(self.max_quota, winner.quotient)


@dt.dataclass
class HAState(NonDeterministicState):
    """Calculation state for Highest Average Allocator."""

    data: HAResultData = dt.field(default_factory=HAResultData)

    def break_tie_ttl(
        self, candidates: Sequence[Candidate[AnyName]], limit: int = 1
    ) -> dict[str, list[Candidate[AnyName]]]:
        """Resolve a tie based on the less recent victory.

        The candidates that won a random tie-breaking
        more time ago than the others will have priority.

        If not possible, fall back to random tie-break.

        Return winners grouped by criterion

        Args
        ----
        candidates
            tied candidates
        limit
            number of winners

        Return
        ------
        :
            winners grouped by criterion
        """
        score = sorted((Candidate(x.name, x.seats) for x in candidates), key=lambda x: x.votes)

        return break_tie_ranking(
            RankingList(score, ascending=True),
            limit,
            fallback=self.random_tie_break,
            first_criterion="tie_break_older_random_winner",
        )

    def break_tie(
        self, candidates: Sequence[CandidateState[AnyName]]
    ) -> dict[str, list[CandidateState[AnyName]]]:
        """Resolve a tie affecting `candidates`.

        Three strategies are applied in the following order ([Loreg:1985]_):

        - `tie_break_most_voted` Choose the candidate with most votes.
        - `tie_break_older_random_winner` Choose the candidate the older non
          deterministic tie-winning candidate.
        - `tie_break_random` Choose a candidate randomly.

        Args
        ----
        candidates
            tied candidates

        Return
        ------
        :
            Winners grouped by criterion.
        """
        table = {x.candidate.name: x for x in candidates}
        score = sorted((x.tie_state() for x in candidates), key=lambda x: x.votes, reverse=True)

        batches = break_tie_ranking(
            RankingList(score, ascending=False),
            1,
            fallback=self.break_tie_ttl,
            first_criterion="tie_break_most_voted",
        )

        return {crit: [table[x.name] for x in batch] for crit, batch in batches.items()}


@allocators.register("highest_averages")
class HighestAveragesAllocator(NonDeterministicAllocator[AnyName, HAResultData]):
    """Highest averages allocator ([Gallagher:1992]_, [KohlerZeh:2012]_).

    Implementation based on divisor series which allocates one seat at a time.

    Tie-breaking follows the rules defined by the Spanish law from 1985 ([Loreg:1985]_).

    :data:`.allocators` collection keys:

    - `highest_averages`
    - `highest-averages`
    """

    def __init__(
        self,
        divisor_f: str | DivisorFunction | DivisorIterator,
        skip_initial_seats: bool = ipt.DEFAULT_SKIP_INITIAL_SEATS,
    ):
        """Create a highest averages allocator using a divisor function or a divisor sequence.

        Args
        ----
        divisor_f
            A divisor function, a divisor iterator or a key in the :data:`.divisors` collection.

        Examples
        --------
        >>> # use the d'Hondt divisor
        >>> dhondt = HighestAveragesAllocator("dhondt")
        """
        super().__init__(
            Input.SEATS | Input.CANDIDATES,
            Input.FILTER_F | Input.RANDOM_SEED | Input.INITIAL_SEATS | Input.SKIP_INITIAL_SEATS,
        )
        self.divisor_f = divisor_f
        self.skip_initial_seats = skip_initial_seats

    def _init_quotient(
        self, candidate: Candidate[AnyName], divisor_f: DivisorIterator
    ) -> CandidateState[AnyName]:
        return CandidateState.init(candidate, divisor_f)

    def _resolve_divisor_f(self) -> DivisorIterator:
        """Resolve a divisor iterator from a key or a function."""
        divisor_f: DivisorIterator
        if isinstance(self.divisor_f, DivisorIterator):
            divisor_f = self.divisor_f
        elif isinstance(self.divisor_f, str) and (self.divisor_f in divisor_iterators):
            divisor_f = divisor_iterators.get(self.divisor_f)()
        else:
            divisor_f = DivisorIterator(divisors.get(self.divisor_f))
        return divisor_f

    def _skip_initial_seats(
        self, data: HAResultData, initial_seats: dict[AnyName, int], skip_initial_seats: bool | None
    ) -> bool:
        if skip_initial_seats is None:
            skip_initial_seats = self.skip_initial_seats

        if not skip_initial_seats:
            for name, seats in initial_seats.items():
                if seats:
                    data.log.append(SeatsEvent(target=name, seats=seats, criterion="initial_seats"))

        return skip_initial_seats

    @override
    def calc(
        self,
        candidates: ipt.ICandidates,
        seats: int,
        random_seed: RandomSeed | None = None,
        filter_f: CandidateFilter[AnyName, Event] | None = None,
        initial_seats: ipt.INamedSeats | None = None,
        skip_initial_seats: bool | None = None,
    ) -> Result[AnyName, HAResultData]:
        """Allocate `candidates` to `seats`.

        If a candidate has initial seats, the initial divisor will be adjusted
        considering those seats at a starting point ([Denmark:2011]_).

        Distributed seats will be logged by a :py:class:`.QuotaWinnerEvent`.

        Args
        ----
        candidates
            list of candidates with votes. Only candidates in this list will be considered.
        seats
            seats that will be computed, in addition to the initial seats
        random_seed
            used to break ties
        filter_f
            restrict allocation to filtered candidates
        initial_seats
            seats already allocated to candidates
        skip_initial_seats
            add initial seats to results. If `None`, the value from the constructor
            will be used
        """
        check_seats(seats)
        state = HAState(random_seed=random_seed)
        data = state.data
        data.remaining_seats = seats
        if filter_f:
            data.log.extend(filter_f.start())

        initial_seats_: dict[AnyName, int] = dict(initial_seats or {})

        divisor_f = self._resolve_divisor_f()
        skip_initial_seats = self._skip_initial_seats(
            data,
            initial_seats_,
            skip_initial_seats,
        )

        # canonical form
        eligible = sorted(
            (
                (c if c.name not in initial_seats_ else c.with_seats(initial_seats_[c.name]))
                for c in Candidate.make_input(candidates)
            ),
            key=lambda x: (x.votes, x.name),
            reverse=True,
        )

        # initialize quotients
        # (candidate,votes, seats), quotient, divisor
        table = [self._init_quotient(x, divisor_f) for x in eligible]
        if filter_f:
            for cand in eligible:
                if cand.seats:
                    data.log.extend(filter_f.update(cand))
        table_ref = list(table)

        while data.remaining_seats > 0:
            table = [x for x in table_ref if not filter_f or filter_f.is_valid(x.candidate.name)]
            if not table:
                break

            best_quotient = max(table, key=lambda x: x.quotient).quotient

            chosen = [elem for elem in table if elem.quotient == best_quotient]

            if len(chosen) > 1:
                # tie
                data.log.append(
                    TieEvent(
                        candidates=tuple(elem.candidate.name for elem in chosen),
                        condition=("quotient", best_quotient),
                    )
                )
                # resolving tie
                winner_batches = state.break_tie(chosen)
            else:
                winner_batches = {"best_quotient": [chosen[0]]}

            for criterion, winners in winner_batches.items():
                for winner in winners:
                    winner.candidate = winner.candidate.add_seats(1)
                    data.remaining_seats -= 1
                    data.new_seat(criterion, winner)
                    if criterion == "tie_break_random":
                        winner.last_tie_victory = seats - data.remaining_seats
                    if filter_f:
                        data.log.extend(filter_f.update(winner.candidate))

            # update quotient
            winner.update()

        if skip_initial_seats:
            allocation = [
                elem.candidate.add_seats(-initial_seats_.get(elem.candidate.name, 0))
                for elem in table_ref
            ]
        else:
            allocation = [elem.candidate for elem in table_ref]

        return state.make_result(allocation, data)
