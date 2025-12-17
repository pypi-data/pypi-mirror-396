#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

r"""Bi-proportional seats allocation (alternate scaling method).

Consider this implementation as experimental.
For a realiable reference implementation,
please use `Bazi <https://www.math.uni-augsburg.de/htdocs/emeriti/pukelsheim/bazi/>`_.


:ref:`References <interregnum_biblio>`
--------------------------------------

* [Zachariasen:2006]_
* [Pukelsheim:2013]_
* [Oelbermann:2016]_

----
"""

from __future__ import annotations
from typing import (
    Iterable,
    Generic,
    Sequence,
    Callable,
)
from collections import OrderedDict
from dataclasses import dataclass, field
import itertools
from functools import partial

from typing_extensions import TypedDict

from ...rounding import RoundingWithSignpost
from ...quotas import QuotaResolver
from ..singlevote.iterative_divisor import (
    IterativeDivisorAllocator,
)
from ..events import EventLog
from ..types import (
    Allocator,
    CalculationState,
    Candidate,
    PreconditionError,
    allocators,
    Input,
    AnyName,
)
from .. import inputs as ipt
from .table import (
    Table,
    DivisorRange,
)
from .tally import (
    BPTallyBoard,
    PartyName,
    DistrictName,
)


class Divisors(TypedDict, Generic[AnyName]):
    """Divisor range for single-proportional candidate."""

    name: AnyName
    divisor: DivisorRange


@dataclass
class BAPResultData(EventLog, Generic[PartyName, DistrictName]):
    """Result data for bi-proportional allocations."""

    rounds: int = 0
    transfers: int = 0
    party_divisors: Sequence[Divisors[PartyName]] = field(default_factory=list)
    district_divisors: Sequence[Divisors[DistrictName]] = field(default_factory=list)


def _sort_parties(
    party_seats: dict[PartyName, int],
    candidates: Sequence[Candidate[tuple[PartyName, DistrictName]]],
) -> OrderedDict[PartyName, int]:
    votes = sorted((c.name[0], c.votes) for c in candidates)
    l_votes = []
    for party_name, group in itertools.groupby(votes, key=lambda x: x[0]):
        party_votes = sum(v for p, v in group)
        l_votes.append((party_votes, party_seats[party_name], party_name))
    l_votes = sorted(l_votes, reverse=True)
    return OrderedDict((p, s) for (v, s, p) in l_votes)


def _make_table(
    votes: Sequence[Candidate[tuple[PartyName, DistrictName]]],
    party_seats: dict[PartyName, int],
    district_seats: dict[DistrictName, int],
    sort_parties: bool,
) -> Table[DistrictName, PartyName]:

    if sum(party_seats.values()) != sum(district_seats.values()):
        raise PreconditionError("total party seats must be equal to total district seats")

    if sort_parties:
        party_seats = _sort_parties(party_seats, votes)

    data: Table[DistrictName, PartyName] = Table(district_seats, party_seats)
    for cand in votes:
        party, district = cand.name
        if district not in district_seats:
            raise PreconditionError(f"district '{district}' not found int district_seats")
        if party not in party_seats:
            raise PreconditionError(f"party '{party}' not found in party_seats")
        data.matrix[district, party].votes = cand.votes
    return data


def extract_party_name(contender):
    """Get party name from a contender."""
    return contender[0]


def extract_district_name(contender):
    """Get district name from a contender."""
    return contender[-1]


def ident(item):
    """Return the same."""
    return item


def contender2tuple_f(
    party_f: Callable[[AnyName], PartyName],
    district_f: Callable[[AnyName], DistrictName],
    contender: AnyName,
) -> tuple[PartyName, DistrictName]:
    """Convert a contender to (party, district)."""
    return (party_f(contender), district_f(contender))


@allocators.register(
    "biproportional",
    "alternate_scaling",
    "alternate_scaling_tie_transfer",
)
class BiproportionalAllocator(Allocator[AnyName, BAPResultData[PartyName, DistrictName]]):
    """Bi-proportional allocator.

    Allocates seats based on two proportional allocations: one for parties and one for districts.

    See [Zachariasen:2006]_, [Pukelsheim:2013]_, [Oelbermann:2016]_

    :data:`.allocators` collection keys:

    - `biproportional`
    - `alternate_scaling`
    - `alternate_scaling_tie_transfer`
    """

    round_f: str | RoundingWithSignpost
    nice_quota: bool = True
    sort_parties: bool = False

    def __init__(
        self,
        round_f: str | RoundingWithSignpost,
        nice_quota: bool = True,
        sort_parties: bool = False,
    ):
        """Create a bi-proportional allocator.

        round_f
            round function with associated signpost sequence
        nice_quota
            when `True`, pick a human readable quota from the valid range
        sort_parties
            Sort parties for the sake of reproducibility.
        """
        super().__init__(
            Input.PARTY_SEATS | Input.DISTRICT_SEATS | Input.CANDIDATES,
            Input.PARTY_NAME_F
            | Input.DISTRICT_NAME_F
            | Input.CANDIDATE_NAME_F
            | Input.EXCLUDE_CANDIDATES,
        )
        self.round_f = round_f
        self.nice_quota = nice_quota
        self.sort_parties = sort_parties

    def calc(
        self,
        party_seats: Iterable[tuple[PartyName, int]],
        district_seats: Iterable[tuple[DistrictName, int]],
        candidates: ipt.ICandidates,
        exclude_candidates: ipt.INames | None = None,
        party_name_f: ipt.IPartyNameFunction = extract_party_name,
        district_name_f: ipt.IDistrictNameFunction = extract_district_name,
        candidate_name_f: ipt.INameFunction = ident,
    ):
        """Allocate seats to candidates.

        Args
        ----

        party_seats
            seats allocated to parties globally
        district_seats
            seats allocated to districts
        candidates
            list of candidates votes with names composed of party and district
        exclude_candidates
            exclude candidates in this list from winning seats
        party_name_f
            function to extract party names
        district_name_f
            function to extract district names
        candidate_name_f
            function to create a candidate name from party and district
        """
        initial_candidates = {c.name: c for c in Candidate.make_input(candidates)}
        contender2tuple = partial(contender2tuple_f, party_name_f, district_name_f)

        tally = BPTallyBoard(
            quota_f=QuotaResolver("midpoint", self.nice_quota),
            method_f=IterativeDivisorAllocator(self.round_f),
            tuple_f=contender2tuple,
            table=_make_table(
                [c.with_name(contender2tuple(c.name)) for c in initial_candidates.values()],
                OrderedDict(party_seats),
                OrderedDict(district_seats),
                sort_parties=self.sort_parties,
            ),
        )
        # exclude candidates
        tally.exclude(
            initial_candidates[name]
            for name in exclude_candidates or []
            if name in initial_candidates
        )

        public: BAPResultData[PartyName, DistrictName] = BAPResultData()

        is_row = True

        while True:
            # get discrepancies
            row_seats, _col_seats = tally.table.seats_by_axis()
            under, over = tally.table.row_discrepancies(row_seats)

            if not under and not over:
                # all cells have been properly allocated
                break

            public.rounds += 1

            # calculate rows
            tally.allocate_rows(under, over, is_row)

            # transfer
            public.transfers += tally.transfer_ties()

            # transpose
            tally.table = tally.table.transpose()

            is_row = not is_row

        tally.table = tally.table.original()

        if self.nice_quota:
            for _d_idx, data in tally.table.row_data.items():
                data.qrange.nice()
            for _p_idx, data in tally.table.col_data.items():
                data.qrange.nice()

        public.district_divisors = [
            {
                "name": d_idx,
                "divisor": data.qrange,
            }
            for d_idx, data in tally.table.row_data.items()
        ]

        public.party_divisors = [
            {
                "name": p_idx,
                "divisor": data.qrange,
            }
            for p_idx, data in tally.table.col_data.items()
        ]

        elected = [
            Candidate(name=candidate_name_f((party, district)), votes=cell.votes, seats=cell.seats)
            for (district, party), cell in tally.table.matrix
        ]

        return CalculationState().make_result(elected, public)
