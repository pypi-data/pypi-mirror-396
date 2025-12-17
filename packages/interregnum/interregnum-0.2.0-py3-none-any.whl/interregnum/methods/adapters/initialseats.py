#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Allocator adapter that admits initial seats."""

from __future__ import annotations
from typing import (
    Any,
    Generic,
    cast,
    Sequence,
    Final,
)
import dataclasses as dt
from typing_extensions import TypedDict

from .. import types as tp
from .. import events as evt
from .. import inputs as ipt


DEFAULT_RESUME_ALLOCATION: Final[bool] = True


class _NamedSeat(TypedDict, Generic[tp.AnyName]):
    """Seats associated to a name."""

    name: tp.AnyName
    seats: int


@dt.dataclass
class InitialSeatsResultData(evt.EventLog, Generic[tp.AnyName, tp.Data]):
    """Initial seats adapter result data."""

    initial_seats: Sequence[_NamedSeat] = dt.field(default_factory=list)
    step: tp.Result[tp.AnyName, tp.Data] | None = None


class InitialSeatsAdapter(tp.Allocator[tp.AnyName, Any], Generic[tp.AnyName, tp.Data]):
    """Adapter that admits initial seats."""

    def __init__(
        self,
        allocator_f: tp.Allocator[tp.AnyName, tp.Data],
        min_seats: int,
        resume_allocation: bool = DEFAULT_RESUME_ALLOCATION,
        skip_initial_seats: bool = ipt.DEFAULT_SKIP_INITIAL_SEATS,
    ):
        """Create an initial seats adapter.

        Each non-excluded candidate will win at least `min_seats`.

        If `resume_allocation`, the allocation method will resume
        the process from the state provided from the already allocated seats
        (`allocator_f` must not ignore seats).

        Otherwise, the allocation is done as if no initial seats were present, and
        then the initial seats will be added to the final result.
        """
        super().__init__(
            allocator_f.required_input,
            allocator_f.optional_input
            | tp.Input.INITIAL_SEATS
            | tp.Input.EXCLUDE_CANDIDATES
            | tp.Input.CANDIDATE_LIST
            | tp.Input.SKIP_INITIAL_SEATS,
        )
        self.min_seats = min_seats
        self.resume_allocation = resume_allocation
        self.skip_initial_seats = skip_initial_seats
        self.allocator_f = allocator_f

    def _prepare_args(
        self,
        args: ipt.InputDict[tp.AnyName, evt.Event],
        initial_seats: ipt.INamedSeats | None = None,
        exclude_candidates: ipt.INames | None = None,
        candidate_list: ipt.INames | None = None,
    ) -> tuple[ipt.InputDict[tp.AnyName, evt.Event], dict[tp.AnyName, int]]:
        valid_cands: set[tp.AnyName] = set()
        # gather candidates
        if "candidates" in args:
            args["candidates"] = list(tp.Candidate.make_input(args["candidates"]))
            valid_cands.update(
                c.name for c in cast(list[tp.Candidate[tp.AnyName]], args["candidates"])
            )
        # gather candidate list
        if candidate_list is not None:
            candidate_list = list(candidate_list)
            valid_cands.update(candidate_list)
            if tp.Input.CANDIDATE_LIST in self.allocator_f.admitted_input:
                args["candidate_list"] = candidate_list
        # ignore excluded candidates
        if exclude_candidates is not None:
            exclude_candidates = list(exclude_candidates)
            valid_cands.difference_update(exclude_candidates)
            if tp.Input.EXCLUDE_CANDIDATES in self.allocator_f.admitted_input:
                args["exclude_candidates"] = exclude_candidates
        # excluded candidates
        #  only provided seats
        data_initial_seats = dict(initial_seats or [])
        # valid candidates
        #  initial seats or min seats
        data_initial_seats.update(
            (cand, max(data_initial_seats.get(cand, 0), self.min_seats)) for cand in valid_cands
        )
        return args, data_initial_seats

    def calc(
        self,
        initial_seats: ipt.INamedSeats | None = None,
        exclude_candidates: ipt.INames | None = None,
        candidate_list: ipt.INames | None = None,
        skip_initial_seats: bool | None = None,
        **method_args,
    ):
        """Allocate seats to candidates.

        The number of declared seats wil be pased to the allocator
        in addition to the allocated initial seats.

        Args
        ----
        initial_seats
            each candidate will start with the maximum of `initial_seats` or `min_seats`
        exclude_candidates
            candidates in this list will not receive seats
        candidate_list
            explicit list of candidates to take into account
        """
        state = tp.CalculationState()
        data: InitialSeatsResultData[tp.AnyName, tp.Data] = InitialSeatsResultData()
        args, data_initial_seats = self._prepare_args(
            cast(ipt.InputDict[tp.AnyName, evt.Event], method_args),
            initial_seats,
            exclude_candidates,
            candidate_list,
        )
        # add initial seats to result
        data.initial_seats = [{"name": k, "seats": v} for k, v in data_initial_seats.items()]

        if skip_initial_seats is None:
            skip_initial_seats = self.skip_initial_seats

        if (
            self.resume_allocation
            and (tp.Input.INITIAL_SEATS in self.allocator_f.admitted_input)
            and (tp.Input.SKIP_INITIAL_SEATS in self.allocator_f.admitted_input)
        ):
            # no need to use the adapter, pass to the original
            args["initial_seats"] = data_initial_seats.items()
            args["skip_initial_seats"] = skip_initial_seats
            return self.allocator_f(**args)

        if all(s == 0 for s in data_initial_seats.values()):
            # no initial seats, use the original allocator
            return self.allocator_f(**args)

        # initial seats are not taken into account for the allocation process
        seats = args.get("seats", 1)
        tp.check_seats(seats, threshold=0)
        if seats > 1:
            tp.check_inputs(tp.Input.SEATS, self.allocator_f.admitted_input)
            args["seats"] = seats

        if seats == 0:
            # seats == 0
            allocation = [
                c.with_seats(data_initial_seats.get(c.name, 0))
                for c in cast(list[tp.Candidate[tp.AnyName]], args["candidates"])
            ]
            data.log.extend(
                evt.SeatsEvent(target=name, seats=seats, criterion="initial_seats")
                for name, seats in data_initial_seats.items()
                if seats
            )
            return state.make_result(allocation, data)

        #               add=false       add=true
        # cont=true     res[0]          res[0] + seats
        # cont=false    res[0]          res[0] + seats
        log = []
        if not skip_initial_seats:
            for name, seats in data_initial_seats.items():
                if not seats:
                    continue
                log.append(evt.SeatsEvent(target=name, seats=seats, criterion="initial_seats"))
        result = self.allocator_f(**args)
        if result.data and isinstance(result.data, evt.EventLog):
            data.log = log + result.data.log
        if not skip_initial_seats:
            # add InitialSeatsAdapter
            d_alloc = dict(data_initial_seats)
            allocation = []
            for cand in result.allocation:
                allocation.append(cand.add_seats(d_alloc.get(cand.name, self.min_seats)))
                d_alloc.pop(cand.name, None)
            allocation.extend(
                tp.Candidate(name=name, votes=0, seats=seats) for name, seats in d_alloc.items()
            )
        else:
            allocation = list(result.allocation)
        data.step = result

        return state.make_result(allocation, data)
