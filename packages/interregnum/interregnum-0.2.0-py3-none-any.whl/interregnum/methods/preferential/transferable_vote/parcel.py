#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""A parcel of preferential votes."""

from __future__ import annotations
from typing import (
    Container,
    Iterable,
    Sequence,
    Generic,
)
import enum
from dataclasses import dataclass, field
from collections import defaultdict
from fractions import Fraction
from ...types import (
    Score,
    AnyName,
)
from ... import inputs as ipt
from ..types import Preference, check_untied, as_tuple


@dataclass
class Parcel(Generic[AnyName]):
    """A parcel of votes transferable to another candidate.

    Args
    ----

    batches
        batches of transferred preferences
    votes
        representative votes for the new owner
    weight
        ratio of the votes transferred to the new owner
    group_id
        round id for this parcel
    """

    batches: list[Preference[AnyName]]
    votes: Score = 0
    weight: Fraction = field(default_factory=lambda: Fraction(1))
    group_id: int = 0

    def total_ballot_papers(self):
        """Total number of ballot papers."""
        return sum(x.votes for x in self.batches)

    def group_by_next_preference(
        self, ignore: Container[AnyName]
    ) -> dict[AnyName | None, list[Preference[AnyName]]]:
        """Group batches by sources.

        ignore
            exclude candidates in this list
        """
        useful_batches: dict[AnyName | None, list[Preference[AnyName]]] = defaultdict(list)
        for batch in self.batches:
            # if not no_tie_in_pref(batch.preference):
            #     raise PreconditionError("ties in preferences are not allowed")
            preference: list[AnyName] = [
                check_untied(x) for x in batch.preference if x not in ignore
            ]
            owner = preference[0] if preference else None
            if batch.votes:
                useful_batches[owner].append(
                    Preference(votes=batch.votes, preference=as_tuple(preference[1:]))
                )
        return useful_batches


class CandidateState(enum.Enum):
    """A possible state for a Candidate."""

    ELIGIBLE = enum.auto()
    "the candidate can win seats"
    ELECTED = enum.auto()
    "the candidate already won seats"
    EXCLUDED = enum.auto()
    "the candidate has been discarded"


@dataclass
class CandidateParcels(Generic[AnyName]):
    """List of a candidate's parcels.

    Args
    ----

    votes
        total value of the candidate's votes
    parcels
        list of parcels
    state
        candidate tally state
    """

    votes: Score = 0
    parcels: list[Parcel[AnyName]] = field(default_factory=list)
    state: CandidateState = CandidateState.ELIGIBLE

    def total_ballot_papers(self) -> Score:
        """Return the score associated to the owned ballots."""
        return sum(x.total_ballot_papers() for x in self.parcels)

    def elect(self) -> None:
        """Set state as elected."""
        self.state = CandidateState.ELECTED

    def exclude(self) -> None:
        """Set state as excluded."""
        self.state = CandidateState.EXCLUDED

    def is_eligible(self) -> bool:
        """Return True if the candidate can win seats."""
        return self.state == CandidateState.ELIGIBLE

    @classmethod
    def collect(
        cls, batches: Iterable[Sequence], candidate_list: ipt.INames | None
    ) -> dict[AnyName, CandidateParcels[AnyName]]:
        """Collect parcels for all the candidates.

        Args
        ----

        batches
            list of grouped preference ballots
        candidate_list
            full list of allowed candidates
        """
        candidates: dict[AnyName, Score] = defaultdict(lambda: 0)
        if candidate_list:
            candidates.update((x, 0) for x in candidate_list)

        ballots: dict[AnyName, list[Preference[AnyName]]] = defaultdict(list)

        for batch in batches:
            pref: Preference[AnyName] = Preference.convert(batch, allow_ties=False)
            if not pref.preference:
                continue
            # register known candidates
            for cand in pref.preference[1:]:
                candidates.setdefault(check_untied(cand), 0)
            # first preference owns the batch
            owner = check_untied(pref.preference[0])
            pref = pref.remove([owner])
            candidates[owner] += pref.votes
            ballots[owner].append(pref)

        return {
            cand: CandidateParcels(
                votes=votes,
                parcels=[
                    Parcel(
                        batches=Preference.compact_preferences(ballots[cand], skip_empty=False),
                        votes=votes,
                    ),
                ],
            )
            for cand, votes in candidates.items()
        }
