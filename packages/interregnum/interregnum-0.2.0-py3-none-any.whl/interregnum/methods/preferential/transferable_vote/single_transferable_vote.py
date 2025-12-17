#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Single transferable vote.

:ref:`References <interregnum_biblio>`
--------------------------------------

* [Gallagher:1992]_
* [EireSTV]_
* [AusProp]_
* [Miragliotta2002]_

----
"""
from __future__ import annotations
from typing import (
    Sequence,
    Generic,
)
import dataclasses as dt
import itertools
from collections import defaultdict

from ...types import (
    AnyName,
    Score,
    Result,
    NonDeterministicAllocator,
    NonDeterministicState,
    Candidate,
    check_seats,
    PreconditionError,
    allocators,
    Input,
    CandidateFilter,
)
from ....rounding import (
    RoundingFunction,
    roundings,
)
from ...events import (
    Event,
    QuotaWinnerEvent,
    TieEvent,
    IneligibleEvent,
    TransferredVotesEvent,
    EventLog,
)
from ....quotas import (
    quotas,
    QuotaFunction,
)
from ... import inputs as ipt

from ....random import (
    RandomSeed,
)
from ...adapters.ranking import (
    break_tie_ranking,
    RankingTable,
)
from ....bidimensional.dataframe import DataFrame
from .parcel import CandidateParcels
from .transfer_functions import (
    transfers,
    TTransferFunction,
)
from ..ties import PartialTieBreak


@dt.dataclass
class STVResultData(EventLog):
    """Single transferable vote result data."""

    threshold: Score = 0
    remaining_seats: int = 0
    rounds: int = 0


@dt.dataclass
class TallyBoard(NonDeterministicState, Generic[AnyName]):
    """Data needed for the tally."""

    transfer_f: TTransferFunction
    round_f: RoundingFunction
    filter_f: CandidateFilter[AnyName, Event] | None
    table: dict[AnyName, CandidateParcels[AnyName]]
    mode: PartialTieBreak
    elected: list[Candidate[AnyName]] = dt.field(default_factory=list)
    surplus: list[tuple[AnyName, Score]] = dt.field(default_factory=list)
    history: dict[AnyName, list[Score]] = dt.field(default_factory=lambda: defaultdict(list))
    data: STVResultData = dt.field(default_factory=STVResultData)

    def get_eligible_candidates(self) -> list[Candidate[AnyName]]:
        """List of eligible candidates.

        Elected and excluded candidates are not returned.
        """
        out = []
        for cand, info in self.table.items():
            if info.is_eligible():
                out.append(Candidate(name=cand, votes=info.votes))
                self.history[cand].append(info.votes)
            elif cand in self.history:
                del self.history[cand]

        return sorted(out, key=lambda x: (-x.votes, x.name))

    def compute_transfers(
        self, source: AnyName, surplus: Score | None = None
    ) -> dict[AnyName | None, CandidateParcels[AnyName]]:
        """Compute vote transfers from candidate 'source'.

        If not surplus given, transfer all 'source' votes
        """
        return self.transfer_f(  # type: ignore
            self.round_f,  # type: ignore
            self.table,  # type: ignore
            source,  # type: ignore
            surplus,
        )

    def apply_transfers(
        self, source: AnyName, deltas: dict[AnyName | None, CandidateParcels[AnyName]]
    ) -> None:
        """Apply transfers for `source`."""
        for target, bundle in deltas.items():
            target_data = self.table[target] if target else None

            for parcel in bundle.parcels:
                parcel.group_id = self.data.rounds
                if target_data:
                    target_data.parcels.append(parcel)
            if target_data:
                target_data.votes += bundle.votes

            self.data.log.append(
                TransferredVotesEvent(source=source, target=target, votes=bundle.votes)
            )

        # remove votes and parcels from source
        source_data = self.table[source]
        source_data.votes = 0
        source_data.parcels.clear()

        self.data.rounds += 1

    def break_tie(
        self, candidates: Sequence[Candidate[AnyName]], limit: int, ascending: bool = False
    ) -> dict[str, list[Candidate[AnyName]]]:
        """Break tie."""
        if self.mode == PartialTieBreak.RANDOM:
            return self.random_tie_break(candidates, limit)

        table: DataFrame[AnyName, Score] = DataFrame()
        for cand in candidates:
            table.insert_row(cand.name, self.history[cand.name][:-1])

        from_first = self.mode == PartialTieBreak.FROM_FIRST_VOTE

        return break_tie_ranking(
            RankingTable(table, limit, ascending=ascending, from_first=from_first),
            limit,
            fallback=self.random_tie_break,
            first_criterion="tie_break_partial_vote",
        )

    def add_winner(self, winners) -> list[Candidate[AnyName]]:
        """Add winner to elected and transfer votes."""
        if len(winners) > self.data.remaining_seats:
            self.data.log.append(
                TieEvent(
                    candidates=tuple(w.name for w in winners),
                    condition={"most_voted": self.data.threshold, "round": self.data.rounds},
                )
            )
            winner_batches = self.break_tie(winners, self.data.remaining_seats)
        else:
            winner_batches = {"most_voted": winners}

        for criterion, items in winner_batches.items():
            for winner in items:
                # TODO add round
                self.data.log.append(
                    QuotaWinnerEvent(
                        target=winner.name, quota=self.data.threshold, criterion=criterion
                    )
                )
                self.table[winner.name].elect()
                new_cand = winner.with_seats(1)
                self.elected.append(new_cand)
                if self.filter_f:
                    self.filter_f.update(new_cand)
                self.data.remaining_seats -= 1
                self.surplus.append((winner.name, winner.votes - self.data.threshold))

        return self.get_eligible_candidates()

    def filter_candidates(self, eligible: list[Candidate[AnyName]]) -> list[Candidate[AnyName]]:
        """Filter eligible candidates."""
        if not self.filter_f:
            return eligible
        out = []
        for cand in eligible:
            if self.filter_f.is_valid(cand.name):
                out.append(cand)
                break
            self.data.log.append(
                IneligibleEvent(
                    target=cand.name,
                    criterion="external_restriction",
                    condition={
                        "round": self.data.rounds,
                        "votes": cand.votes,
                    },
                )
            )
            self.surplus.append((cand.name, cand.votes))
        return out

    def remove_loser(
        self, losers: list[Candidate[AnyName]], lowest: Score
    ) -> list[Candidate[AnyName]]:
        """Remove loser from eligible and transfer votes."""
        criterion = "less_voted"
        if len(losers) > 1:
            self.data.log.append(
                TieEvent(
                    candidates=tuple(elem.name for elem in losers),
                    condition={"less_voted": lowest, "round": self.data.rounds},
                )
            )
            loser_batches = self.break_tie(losers, 1, ascending=True)
        else:
            loser_batches = {"less_voted": losers}

        for criterion, items in loser_batches.items():
            for loser in items:
                condition = {"votes": loser.votes, "threshold": lowest, "round": self.data.rounds}
                if criterion == "tie_break_partial_vote":
                    condition["partial_vote_position"] = loser.seats
                self.data.log.append(
                    IneligibleEvent(target=loser.name, criterion=criterion, condition=condition)
                )
                self.table[loser.name].exclude()
                deltas = self.compute_transfers(loser.name)

                # mark as excluded and remove parcels
                self.apply_transfers(loser.name, deltas)

        return self.get_eligible_candidates()

    def apply_surplus(self) -> list[Candidate[AnyName]]:
        """Get a pending surplus and transfer votes."""
        source, surplus = self.surplus.pop(0)
        deltas = self.compute_transfers(source, surplus)
        self.apply_transfers(source, deltas)

        return self.get_eligible_candidates()


@allocators.register("single_transferable_vote")
class SingleTransferableVoteAllocator(
    NonDeterministicAllocator[AnyName, STVResultData],
):
    """Single Transferable Vote method.

    - Each candidate that surpasses the calculated quota wins a seat. Their unused
      votes are moved to the next preference.
    - If no candidate reaches the quota, the less voted candidate is removed and
      his/her votes are moved to the next preference.

    The transfer of the surplus votes is calculated using
    different :mod:`transfer strategies <.transfer_functions>`.

    See `<https://en.wikipedia.org/wiki/Single_transferable_vote>`_,
    [Gallagher:1992]_, [EireSTV]_, [AusProp]_, [Miragliotta2002]_.

    :data:`.allocators` collection keys:

    - `single_transferable_vote`
    """

    def __init__(
        self,
        quota_f: str | QuotaFunction,
        transfer_f: str | TTransferFunction,
        round_f: str | RoundingFunction,
        tie_break: PartialTieBreak | str = "from_first_vote",
    ):
        """Create a Single Transferable Vote allocator.

        Args
        ----
        quota_f
            quota function to get the cost of a seat
        transfer_f
            transfer function or key in :data:`.transfers` collection
        round_f
            rounding function to apply to candidates batches
        tie_break
            strategy for breaking candidates ties
        """
        super().__init__(
            Input.PREFERENCES | Input.SEATS,
            Input.CANDIDATE_LIST | Input.TOTAL_VOTES | Input.RANDOM_SEED | Input.FILTER_F,
        )
        self.quota_f = quota_f
        self.transfer_f = transfer_f
        self.round_f = round_f
        self.tie_break_rule = tie_break

    def _reset(self, random_seed, filter_f) -> TallyBoard[AnyName]:
        return TallyBoard(
            random_seed=random_seed,
            transfer_f=transfers.get(self.transfer_f),
            round_f=roundings.get(self.round_f),
            filter_f=filter_f,
            table={},
            mode=PartialTieBreak.get_value(self.tie_break_rule),
        )

    def calc(
        self,
        preferences,
        seats: int,
        random_seed: RandomSeed | None = None,
        candidate_list: ipt.INames | None = None,
        total_votes: Score | None = None,
        filter_f: CandidateFilter[AnyName, Event] | None = None,
    ) -> Result:
        """Allocate seats to candidates.

        Args
        ----
        preferences
            list of grouped preferences ballots
        seats
            allocatable seats
        random_seed
            used to break ties
        candidate_list
            full list of allowed candidates
        total_votes
            total number of votes used to calculate quotas
        filter_f
            filter function to exclude candidates from getting seats
        """
        check_seats(seats)
        state = self._reset(random_seed, filter_f)
        quota_f = quotas.get(self.quota_f)
        state.table = CandidateParcels.collect(preferences, candidate_list)

        total_votes = total_votes or sum(x.votes for x in state.table.values())
        assert total_votes is not None
        quota = quota_f(total_votes, seats)
        state.data.threshold = quota.reference
        state.data.remaining_seats = seats

        # get first election
        # (name, votes)
        eligible = state.filter_candidates(state.get_eligible_candidates())
        if not eligible:
            raise PreconditionError("preferences list is empty and no candidates provided")

        state.data.rounds = 0
        while eligible and state.data.remaining_seats:
            if state.surplus:
                eligible = state.apply_surplus()

            # find winners
            if len(eligible) > state.data.remaining_seats:
                winners = list(itertools.takewhile(lambda x: quota.reached(x.votes), eligible))
            else:
                winners = eligible

            # add winner and transfer unused votes
            if winners:
                eligible = state.add_winner(winners)
            # otherwise, remove loser and transfer votes
            elif not state.surplus:
                lowest = eligible[-1].votes

                losers = list(itertools.takewhile(lambda x: x.votes <= lowest, reversed(eligible)))

                eligible = state.remove_loser(losers, lowest)

            eligible = state.filter_candidates(eligible)

        result = state.make_result(state.elected, state.data)
        return result
