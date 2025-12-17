#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Largest remainder method.

:ref:`References <interregnum_biblio>`
--------------------------------------

* [Gallagher:1992]_
* [KohlerZeh:2012]_

----
"""
from __future__ import annotations
from typing import (
    Sequence,
    Iterable,
    Generic,
    Any,
)
import math
import dataclasses as dt
from fractions import Fraction

from ..types import (
    Candidate,
    AnyName,
    Score,
    NonDeterministicAllocator,
    NonDeterministicResult,
    NonDeterministicState,
    allocators,
    Input,
    check_seats,
    Summary,
)
from .. import events as evt
from ...random import (
    RandomSeed,
)
from ...quotas import (
    QuotaFunction,
    quotas,
)
from ...bisect import (
    QuotaBisect,
)
from ..adapters.ranking import RankingList, break_tie_ranking
from .. import inputs as ipt


@dt.dataclass
class CandidateState(Generic[AnyName]):
    """Candidate internal state."""

    candidate: Candidate[AnyName]
    "A candidate"
    remainder: Score | None = None
    "Votes remainder after applying quota"


@dt.dataclass
class LRResultData(evt.EventLog):
    """Additional result data for largest remainder methods."""

    quota: Score = 0
    "Current quota"
    remaining_seats: int = 0
    "Seats not allocated"
    first_quota: Score = dt.field(init=False)
    "Initial quota before adjustment"

    def __post_init__(self):
        """Initialize quota."""
        self.first_quota = self.quota


def apply_quota(
    seats: int, data: Iterable[Candidate[AnyName]], quota: Score
) -> tuple[int, list[CandidateState[AnyName]], list[evt.Event]]:
    """Apply quota to candidates.

    Args
    ----
    data
        candidates
    quota
        vote-seats quota

    Return
    ------
    :
        (remaining seats, remainders, log)
    """
    remaining_seats = seats

    remainders = []
    log: list[evt.Event] = []
    for candidate in data:
        quotient = Fraction(candidate.votes, quota)
        cand = candidate.with_seats(math.floor(quotient))
        remainders.append(
            CandidateState(
                candidate=cand,
                remainder=quotient - cand.seats,
            )
        )
        remaining_seats -= cand.seats
        log.append(evt.SeatsEvent(target=cand.name, seats=cand.seats, criterion="quota"))

    return remaining_seats, remainders, log


@dt.dataclass
class LRState(NonDeterministicState, Generic[AnyName]):
    """A calculation state for Largest Remainder Allocator."""

    data: LRResultData = dt.field(default_factory=LRResultData)
    "Result data"
    total_votes: Score = 0
    "Total number of votes"
    eligible: Sequence[Candidate[AnyName]] = dt.field(default_factory=list)
    "Eligible candidates"

    def break_tie(
        self, candidates: Sequence[CandidateState[AnyName]], limit: int
    ) -> dict[str, list[CandidateState[AnyName]]]:
        """Resolve a tie choosing `limit` candidates.

        Strategies are applied in the following order:

        - `tie_break_most_voted` Choose the candidate with most votes.
        - `tie_break_random` Choose a candidate randomly.
        """
        table = {x.candidate.name: x for x in candidates}

        score = sorted((cs.candidate for cs in candidates), key=lambda x: (-x.votes, x.name))

        batches = break_tie_ranking(
            RankingList(score, ascending=False),
            limit,
            fallback=self.random_tie_break,
            first_criterion="tie_break_most_voted",
        )

        return {crit: [table[x.name] for x in batch] for crit, batch in batches.items()}

    def resolve_tie_most_voted(
        self, candidates: Sequence[CandidateState[AnyName]]
    ) -> Sequence[CandidateState[AnyName]]:
        """Choose the most voted candidate."""
        max_votes = max(x.candidate.votes for x in candidates)
        candidates = [x for x in candidates if x.candidate.votes >= max_votes]
        return candidates

    def seats_by_remainders(
        self, remainders: Sequence[CandidateState[AnyName]]
    ) -> Sequence[CandidateState[AnyName]]:
        """Allocate seats by largest remainders."""
        while self.data.remaining_seats > 0:
            max_remainder = max(x.remainder for x in remainders if x.remainder is not None)
            rem_candidates = [
                x
                for x in remainders
                if (x.remainder is not None) and (x.remainder >= max_remainder)
            ]

            if len(rem_candidates) > self.data.remaining_seats:
                # tie
                self.data.log.append(
                    evt.TieEvent(
                        candidates=tuple(elem.candidate.name for elem in rem_candidates),
                        condition=("remainder", max_remainder),
                    )
                )
                winner_batches = self.break_tie(rem_candidates, self.data.remaining_seats)
            else:
                winner_batches = {"largest_remainder": rem_candidates}

            # add seats
            for criterion, winners in winner_batches.items():
                for winner in winners:
                    winner.remainder = None
                    winner.candidate = winner.candidate.add_seats(1)
                    self.data.remaining_seats -= 1

                    self.data.log.append(
                        evt.SeatsEvent(
                            target=winner.candidate.name,
                            seats=1,
                            criterion=f"remainder[{criterion}]",
                        )
                    )

        return remainders

    def remove_used_votes(self, quota_f: QuotaFunction, seats: int) -> None:
        """Remove votes used for initial seats."""
        old_seats = sum(cand.seats for cand in self.eligible)

        if old_seats <= 0:
            return

        old_quota = quota_f(self.total_votes, old_seats + seats).reference
        new_candidates = []

        for cand in self.eligible:
            if cand.seats > 0:
                used_votes = math.floor(cand.seats * old_quota)
                unused_votes = max(cand.votes - used_votes, 0)
                self.total_votes -= min(cand.votes, used_votes)
                new_candidates.append(Candidate(name=cand.name, votes=unused_votes))
            else:
                new_candidates.append(cand)

        self.eligible = new_candidates

    def seats_by_quota(
        self, seats: int, fix_overflow: bool, bisect_step: int
    ) -> list[CandidateState[AnyName]]:
        """Allocate seats by quota."""
        remaining_seats = -1

        if self.data.quota <= 0:
            return [CandidateState(candidate=cand, remainder=0) for cand in self.eligible]

        remaining_seats, remainders, log = apply_quota(seats, self.eligible, self.data.quota)

        if (remaining_seats >= 0) or not fix_overflow:
            self.data.log.extend(log)
            return remainders

        # find a suitable quota
        bisect = QuotaBisect(self.data.quota, self.total_votes, seats, step=bisect_step)

        first_quota = alt_quota = bisect.guess()

        while bisect.has_more():
            remaining_seats, remainders, log = apply_quota(seats, self.eligible, alt_quota)

            if remaining_seats < 0:
                bisect.bad()
            else:
                bisect.good()
            alt_quota = bisect.guess()

        self.data.log.extend(log)
        if remaining_seats >= 0:
            self.data.log.append(
                NewQuotaEvent(
                    quota=alt_quota,
                    old_quota=first_quota,
                    criterion="seats_overflow",
                )
            )
            self.data.quota = alt_quota

        return remainders


@dt.dataclass
class NewQuotaEvent(evt.Event):
    """A computed quota has changed."""

    EVENT = "new quota"
    quota: Score
    "current quota"
    criterion: str
    "criterion for choosing the quota"
    old_quota: Score | None = None
    "previous quota"
    data: Any | None = None
    "additional data"


@allocators.register("largest_remainder")
class LargestRemainderAllocator(NonDeterministicAllocator[AnyName, LRResultData]):
    """Largest remainder method.

    See [Gallagher:1992]_, [KohlerZeh:2012]_ and
    `<https://en.wikipedia.org/wiki/Largest_remainder_method>`_

    :data:`.allocators` collection keys:

    - `largest_remainder`
    - `largest-remainder`
    """

    def __init__(
        self,
        quota_f: str | QuotaFunction,
        fix_overflow: bool = True,
        bisect_step: int = 1,
        skip_initial_seats: bool = ipt.DEFAULT_SKIP_INITIAL_SEATS,
    ):
        """Create a largest remainder method using `quota_f` as the quota function.

        While the calculated quota allocates more than the avalaible seats
        and `fix_overflow` is `True`, the quota will be incremented by
        `bisect_step`. The remaining seats will be assigned to the candidates with
        the largest remainders.

        Args
        ----
        quota_f
            quota function or key in :py:data:`.quotas`
        fix_overflow
            adjust the quota if more seats than the required amount were allocated
        bisect_step
            step used at the quota adjustment process


        Examples
        --------
        >>> # Hare quota
        >>> hare = LargestRemainderAllocator("hare")

        >>> # Reinforced Imperiali quota, adjusting quota
        >>> # if the allocated seats are greater than required
        >>> imp3 = LargestRemainderAllocator("imperiali3")

        >>> # Reinforced Imperiali quota, do not adjust quota
        >>> imp3 = LargestRemainderAllocator("imperiali3", fix_overflow=False)
        """
        super().__init__(
            Input.SEATS | Input.CANDIDATES,
            Input.TOTAL_VOTES
            | Input.EXCLUDE_CANDIDATES
            | Input.RANDOM_SEED
            | Input.INITIAL_SEATS
            | Input.SKIP_INITIAL_SEATS,
        )
        self.quota_f = quota_f
        self.fix_overflow = fix_overflow
        self.bisect_step = bisect_step
        self.skip_initial_seats = skip_initial_seats

    def _skip_initial_seats(
        self, data: LRResultData, initial_seats: dict[AnyName, int], skip_initial_seats: bool | None
    ) -> bool:
        if skip_initial_seats is None:
            skip_initial_seats = self.skip_initial_seats

        if not skip_initial_seats:
            for name, seats in initial_seats.items():
                if seats:
                    data.log.append(
                        evt.SeatsEvent(target=name, seats=seats, criterion="initial_seats")
                    )

        return skip_initial_seats

    def calc(
        self,
        candidates: ipt.ICandidates,
        seats: int,
        random_seed: RandomSeed | None = None,
        total_votes: Score | None = None,
        exclude_candidates: ipt.INames | None = None,
        initial_seats: ipt.INamedSeats | None = None,
        skip_initial_seats: bool | None = None,
    ) -> NonDeterministicResult[AnyName, LRResultData]:
        """Allocates `candidates` to `seats`.

        If a candidate already has initial seats, the votes used for those seats
        are subtracted before the allocation.

        Distributed seats will be logged by :class:`.QuotaWinnerEvent`
        (seats by quota) and :class:`.SeatsEvent` (seats by remainders).

        If a quota is discarded because of overflow, a :class:`.NewQuotaEvent` will be logged.

        Args
        ----
        candidates
            list of candidates
        seats
            seats that will be computed, in addition to the initial seats
        random_seed
            used to break ties
        total_votes
            votes for the quota calculation, in the case it is greater
            than the sum of the candidates' votes
        initial_seats
            seats already allocated to candidates
        skip_initial_seats
            add initial seats to results. If `None`, the value from the constructor
            will be used
        """
        initial_seats_: dict[AnyName, int] = dict(initial_seats or {})
        initial_candidates = {
            c.name: (c if c.name not in initial_seats_ else c.with_seats(initial_seats_[c.name]))
            for c in Candidate.make_input(candidates)
        }
        check_seats(seats)
        state: LRState[AnyName] = LRState(
            random_seed=random_seed,
            total_votes=total_votes or 0,
        )
        data = state.data

        skip_initial_seats = self._skip_initial_seats(data, initial_seats_, skip_initial_seats)

        quota_f = quotas.get(self.quota_f)

        excluded: Summary[AnyName] = Summary.build(
            initial_candidates[name]
            for name in exclude_candidates or []
            if name in initial_candidates
        )
        state.total_votes = max(
            state.total_votes, sum(x.votes for x in initial_candidates.values())
        )
        state.total_votes -= excluded.votes

        state.eligible = [x for x in initial_candidates.values() if x.name not in excluded.names]

        # take account of already given seats
        state.remove_used_votes(quota_f, seats)

        data.quota = quota_f(state.total_votes, seats).reference

        if not state.eligible:
            return state.make_result([], data)

        # find fitting quota
        ######################

        state.data.log.extend(
            evt.IneligibleEvent(target=name, criterion="initial_exclusion")
            for name in excluded.names
        )

        remainders: Sequence[CandidateState[AnyName]] = state.seats_by_quota(
            seats, self.fix_overflow, self.bisect_step
        )

        data.remaining_seats = seats - sum(x.candidate.seats for x in remainders)

        # give the remaining seats according to the remainders
        #######################################################

        if data.remaining_seats > 0:
            remainders = state.seats_by_remainders(remainders)

        outcome = [x.candidate for x in remainders]
        if not skip_initial_seats:
            outcome = [c.add_seats(initial_seats_.get(c.name, 0)) for c in outcome]

        return state.make_result(outcome, data)

    def _apply_quota(
        self, seats: int, data: Iterable[Candidate[AnyName]], quota: Score
    ) -> tuple[int, list[CandidateState[AnyName]], list[evt.Event]]:
        remaining_seats = seats

        remainders = []
        log: list[evt.Event] = []
        for candidate in data:
            quotient = Fraction(candidate.votes, quota)
            cand = candidate.with_seats(math.floor(quotient))
            remainders.append(
                CandidateState(
                    candidate=cand,
                    remainder=quotient - cand.seats,
                )
            )
            remaining_seats -= cand.seats
            log.append(evt.SeatsEvent(target=cand.name, seats=cand.seats, criterion="quota"))

        return remaining_seats, remainders, log
