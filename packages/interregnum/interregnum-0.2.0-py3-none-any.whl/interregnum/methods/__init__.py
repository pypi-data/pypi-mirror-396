#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""
Methods allocate seats from votes.

- Inputs: each allocator defines which types of input admits. See :class:`.types.Input`
  and :mod:`.inputs` for a detailed list of inputs.
- Output: an allocator returns a :class:`.types.Result`, which contains the seats
  allocation and other additional information.
- Events provide information about what the allocator internally did (:mod:`.events`).
- Filters (:class:`.types.CandidateFilter`, :mod:`.filters`) are useful to add constraints
  to the allocation process (for example, when some contenders can't win more
  than a limited number of seats).

Allocators are grouped by their main input's type:

- Single vote (:mod:`interregnum.methods.singlevote`)
- Preferential vote (:mod:`interregnum.methods.preferential`)
- Bi-proportional system (:mod:`interregnum.methods.biproportional`)
- Compensatory systems (:mod:`interregnum.methods.compensatory`)
- Adapters (:mod:`interregnum.methods.compensatory`)

Creating new methods
--------------------

New methods should inherit the classes :class:`.types.Allocator` or
:class:`.types.NonDeterministicAllocator`. Then, that method can be added to the
:data:`.allocators` collection.

-----
"""

from __future__ import annotations
from .biproportional import BiproportionalAllocator
from .compensatory import (
    AdditionalMemberAdapter,
    MixedMemberAdapter,
)
from .preferential import (
    BordaCountAllocator,
    CondorcetCopelandAllocator,
    CondorcetMinimaxAllocator,
    CondorcetRankedPairsAllocator,
    SingleTransferableVoteAllocator,
    InstantRunOffAllocator,
)
from .singlevote import (
    HighestAveragesAllocator,
    IterativeDivisorAllocator,
    LargestRemainderAllocator,
    LimitedVotingAllocator,
    WinnerTakesAllAllocator,
)

from .types import (
    allocators,
    Allocator,
    CalculationState,
    Result,
    AnyName,
    Input,
    Candidate,
)
from . import events as evt
from . import inputs as ipt


__all__ = [
    "BiproportionalAllocator",
    "AdditionalMemberAdapter",
    "MixedMemberAdapter",
    "BordaCountAllocator",
    "CondorcetCopelandAllocator",
    "CondorcetMinimaxAllocator",
    "CondorcetRankedPairsAllocator",
    "SingleTransferableVoteAllocator",
    "InstantRunOffAllocator",
    "HighestAveragesAllocator",
    "IterativeDivisorAllocator",
    "LargestRemainderAllocator",
    "LimitedVotingAllocator",
    "WinnerTakesAllAllocator",
    "NoopAllocator",
    "allocators",
]


@allocators.register("noop", "no-op", "nop", "copy")
class NoopAllocator(Allocator[AnyName, evt.EventLog]):
    """Do nothing.

    Generate result from the input.

    :data:`.allocators` collection keys:

    - `noop`
    - `no-op`
    - `nop`
    - `copy`
    """

    def __init__(self, skip_initial_seats: bool = ipt.DEFAULT_SKIP_INITIAL_SEATS):
        """Create a noop allocator."""
        super().__init__(
            Input.CANDIDATES,
            Input.EXCLUDE_CANDIDATES | Input.SEATS | Input.INITIAL_SEATS | Input.SKIP_INITIAL_SEATS,
        )
        self.skip_initial_seats = skip_initial_seats

    def calc(
        self,
        candidates: ipt.ICandidates,
        initial_seats: ipt.INamedSeats | None = None,
        exclude_candidates: ipt.INames | None = None,
        seats: int = 0,
        skip_initial_seats: bool | None = None,
    ) -> Result[AnyName, evt.EventLog]:
        """Return a result with the provided `candidates`.

        Seats in `initial_seats` will be preserved.

        Candidates in `exclude_candidates` will win no seats.
        """
        state = CalculationState()
        data = evt.EventLog()
        allocated_seats = dict(initial_seats or [])
        if skip_initial_seats is None:
            skip_initial_seats = self.skip_initial_seats

        out: list[Candidate[AnyName]] = list(Candidate.make_input(candidates))

        # log excluded candidates
        exclusion = frozenset(exclude_candidates or [])
        data.log.extend(
            evt.IneligibleEvent(target=cand.name, criterion="initial_exclusion")
            for cand in exclusion
        )
        if not skip_initial_seats:
            out = [
                cand.with_seats(
                    allocated_seats.get(cand.name, 0) if cand.name not in exclusion else 0
                )
                for cand in out
            ]
            data.log.extend(
                evt.SeatsEvent(target=cand.name, seats=cand.seats, criterion="initial_seats")
                for cand in out
                if cand.seats
            )

        return state.make_result(out, data)
