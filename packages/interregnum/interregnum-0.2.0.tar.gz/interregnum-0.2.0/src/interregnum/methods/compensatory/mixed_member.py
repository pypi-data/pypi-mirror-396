#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

r"""Mixed-member systems.

Variants:

- increment seats to absorb overhang seats
- reduce seats to exclude overhang seats
- return overhang seats as negative seats

:ref:`References <interregnum_biblio>`
--------------------------------------

* [Norway:2023]_
* [Germany:2025]_

----
"""
from __future__ import annotations
from typing import (
    Generator,
    Generic,
    cast,
)
import enum
import dataclasses as dt
from collections import defaultdict

from typing_extensions import TypedDict

from ...exceptions import UnsolvableError
from ...types import parse_enum
from ..types import (
    AnyName,
    Input,
    check_seats,
    check_inputs,
    Allocator,
    CalculationState,
    Result,
    AnyResult,
    allocators,
    Candidate,
)
from ..filters import exclude_candidates
from .. import events as evt
from .. import inputs as ipt


class OverhangMode(enum.Enum):
    """How to solve overhang seats."""

    IGNORE = enum.auto()
    "do not adjust overhang seats"
    ABSORB = enum.auto()
    "add seats until the overhang seats are absorbed"
    EXCLUDE_PARTIES = enum.auto()
    "exclude parties with overhang seats from the compensatory allocation"
    SUBTRACT_SEATS = enum.auto()
    "return overhang seats as negative seats to be subtracted"

    @classmethod
    def parse(cls, value: str | OverhangMode) -> OverhangMode:
        """Return a value from a string."""
        if isinstance(value, OverhangMode):
            return value
        return parse_enum(cls, value)

    def __str__(self):
        """Return attribute as a key."""
        return self.name.lower()


class _NamedSeat(TypedDict, Generic[AnyName]):
    """Seats associated to a name."""

    name: AnyName
    seats: int


@dt.dataclass
class MMResultData(evt.EventLog, Generic[AnyName]):
    """Mixed member result data."""

    result: Result | None = None
    levelling_seats: int = 0
    overhang: list[_NamedSeat] = dt.field(default_factory=list)
    steps: list[Result] = dt.field(default_factory=list)


@allocators.register("mixed_member")
class MixedMemberAdapter(Generic[AnyName, AnyResult], Allocator[AnyName, MMResultData]):
    """Mixed-member system adapter.

    See [Germany:2025]_, [Norway:2023]_.

    :data:`.allocators` collection keys:

    - `mixed_member`
    """

    def __init__(
        self,
        overhang_mode: OverhangMode | str,
        allocator_f: Allocator[AnyName, AnyResult],
        subtract_excluded_candidates: bool = False,
        skip_initial_seats: bool = ipt.DEFAULT_SKIP_INITIAL_SEATS,
    ):
        """Create a mixed-member system adapter.

        Args
        ----
        overhang_mode
            calculation variant
        subtract_excluded_candidates
            remove seats from excluded candidates
        skip_initial_seats
            return allocation seats instead of just the levelling seats
        """
        check_inputs(Input.SEATS, allocator_f.admitted_input)
        super().__init__(
            allocator_f.required_input | Input.INITIAL_SEATS | Input.SKIP_INITIAL_SEATS,
            allocator_f.optional_input | Input.SEATS | Input.INNER_INITIAL_SEATS | Input.MAX_SEATS,
        )
        self.allocator_f = allocator_f
        self.overhang_mode = OverhangMode.parse(overhang_mode)
        self.subtract_excluded_candidates = subtract_excluded_candidates
        self.skip_initial_seats = skip_initial_seats

    def calc(
        self,
        initial_seats: ipt.INamedSeats,
        seats: int | None = None,
        max_seats: int | None = None,
        inner_initial_seats: ipt.INamedSeats | None = None,
        skip_initial_seats: bool | None = None,
        **method_args,
    ):
        """Allocate seats to candidates.

        Args
        ----
        initial_seats
            seats from the first vote
        seats
            number of levelling seats (starting point)
        max_seats
            if defined, stop absorbing overhang when `max_seats` has been reached.
        inner_initial_seats
            initial seats for the inner allocator
        """
        # levelling seats
        if seats:
            check_seats(seats)

        if skip_initial_seats is None:
            skip_initial_seats = self.skip_initial_seats

        for param in (Input.CANDIDATES, Input.PREFERENCES, Input.DISTRICT_SEATS):
            if param.param_name in method_args:
                method_args[param.param_name] = list(method_args[param.param_name])

        args = cast(ipt.InputDict[AnyName, evt.Event], method_args)

        c_initial_seats = dict(inner_initial_seats or {})
        if c_initial_seats:
            args["initial_seats"] = [(c, seats) for c, seats in c_initial_seats.items() if seats]

        if self.overhang_mode != OverhangMode.EXCLUDE_PARTIES:
            return self._calc_absorb(
                mode=self.overhang_mode,
                initial_seats=dict(initial_seats),
                method_args=args,
                seats=seats,
                max_seats=max_seats,
                skip_initial_seats=skip_initial_seats,
            )
        return self._calc_reduce(
            initial_seats=dict(initial_seats),
            method_args=args,
            seats=seats,
            skip_initial_seats=skip_initial_seats,
        )

    def _calc_absorb(
        self,
        mode: OverhangMode,
        initial_seats: dict[AnyName, int],
        method_args: ipt.InputDict[AnyName, evt.Event],
        skip_initial_seats: bool,
        seats: int | None = None,
        max_seats: int | None = None,
    ):
        min_seats = sum(initial_seats.values())

        data: MMResultData[AnyName] = MMResultData(levelling_seats=seats or (min_seats * 2))
        if max_seats:
            data.levelling_seats = min(data.levelling_seats, max_seats)
        limit = max_seats or (data.levelling_seats * 10)
        check_seats(data.levelling_seats)

        # remove exclude candidates
        if self.subtract_excluded_candidates:
            self._subtract_excluded(data, initial_seats, method_args)

        finished = data.levelling_seats <= 0

        absorb_overhang = mode == OverhangMode.ABSORB
        allocation = []
        while not finished:
            overhang = 0
            method_args["seats"] = data.levelling_seats
            data.result = self.allocator_f(**method_args)
            assert data.result
            data.overhang.clear()
            for cand in data.result.allocation:
                diff = cand.seats - initial_seats.get(cand.name, 0)
                if diff < 0:
                    # overhang seats detected
                    overhang += abs(diff)
                    data.overhang.append(
                        {
                            "name": cand.name,
                            "seats": abs(diff),
                        }
                    )
                    allocation.append(
                        cand.with_seats(diff if mode == OverhangMode.SUBTRACT_SEATS else 0)
                    )
                else:
                    allocation.append(cand.with_seats(cand.seats - initial_seats.get(cand.name, 0)))

            new_levelling = data.levelling_seats + min(1, overhang)
            if max_seats:
                new_levelling = min(new_levelling, max_seats)
            finished = (new_levelling <= data.levelling_seats) or not absorb_overhang
            if not finished:
                data.log.append(
                    evt.NewAllocationEvent(
                        criterion="overhang_seats_not_allowed",
                        data={
                            "overhang_seats": overhang,
                            "seats": data.levelling_seats,
                            "initial_seats": min_seats,
                            "max_seats": max_seats,
                        },
                    )
                )
                data.steps.append(data.result)
                data.levelling_seats = new_levelling
                allocation = []

                if not finished and new_levelling > limit:
                    raise UnsolvableError(
                        "seats could not absorbed after an excessive "
                        f"growth (required seats > {limit})"
                    )

        assert data.result

        data.log.extend(_reinterpret_events(data.result.data, allocation))

        return CalculationState().make_result(
            allocation if skip_initial_seats else data.result.allocation, data
        )

    @staticmethod
    def _subtract_excluded(
        data: MMResultData[AnyName],
        initial_seats: dict[AnyName, int],
        method_args: ipt.InputDict[AnyName, evt.Event],
    ) -> set[AnyName]:
        # remove exclude candidates
        excluded: set[AnyName] = set()
        if Input.FILTER_F.param_name in method_args:
            excluded.update(method_args["filter_f"].exclusion_list())
        excluded.update(method_args.get("exclude_candidates", []))

        data.log.extend(
            evt.IneligibleEvent(target=cand, criterion="initial_exclusion") for cand in excluded
        )

        data.levelling_seats -= sum(initial_seats.get(excl, 0) for excl in excluded)

        return excluded

    def _calc_reduce(
        self,
        initial_seats: dict[AnyName, int],
        method_args: ipt.InputDict[AnyName, evt.Event],
        skip_initial_seats: bool,
        seats: int | None = None,
    ):
        # import pudb; pu.db
        min_seats = sum(initial_seats.values())

        data: MMResultData[AnyName] = MMResultData(levelling_seats=seats or (min_seats * 2))
        check_seats(data.levelling_seats)

        # remove exclude candidates
        excluded: set[AnyName] = set()
        if self.subtract_excluded_candidates:
            excluded = self._subtract_excluded(data, initial_seats, method_args)
        initial_excluded = len(excluded)

        finished = data.levelling_seats <= 0
        allocation: list[Candidate[AnyName]] = []
        data_overhang: dict[AnyName, int] = {}
        while not finished:
            allocation.clear()
            overhang = 0
            step_args = cast(ipt.InputDict[AnyName, evt.Event], dict(method_args))
            # remove candidates from method_args
            if len(excluded) > initial_excluded:
                step_args = exclude_candidates(self.allocator_f, method_args, excluded)
            step_args["seats"] = data.levelling_seats
            data.result = self.allocator_f(**step_args)
            assert data.result
            data_overhang.clear()
            for cand in data.result.allocation:
                if cand.name in excluded:
                    assert cand.seats == 0
                    allocation.append(cand)
                    continue
                diff = cand.seats - initial_seats.get(cand.name, 0)
                if diff < 0:
                    # overhang seats detected
                    overhang += abs(diff)
                    data_overhang[cand.name] = abs(diff)
                    allocation.append(cand.with_seats(0))
                else:
                    allocation.append(cand.with_seats(cand.seats - initial_seats.get(cand.name, 0)))

            if not (finished := not overhang or data.levelling_seats <= 0):
                data.log.append(
                    evt.NewAllocationEvent(
                        criterion="overhang_seats_not_allowed",
                        data={
                            "overhang_seats": overhang,
                            "seats": data.levelling_seats,
                            "initial_seats": min_seats,
                        },
                    )
                )
                data.steps.append(data.result)
                exclusion = (cand for cand in data.result.allocation if cand.name in data_overhang)
                for cand in exclusion:
                    data.levelling_seats -= initial_seats.get(cand.name, 0)
                    excluded.add(cand.name)
                    data.overhang.append(
                        {
                            "name": cand.name,
                            "seats": data_overhang.get(cand.name, 0),
                        }
                    )
                    data.log.append(
                        evt.IneligibleEvent(
                            target=cand.name,
                            criterion="overhang_seats",
                            condition={
                                "initial_seats": initial_seats.get(cand.name, 0),
                                "overhang": data_overhang.get(cand.name, 0),
                            },
                        )
                    )
                finished = finished or data.levelling_seats <= 0
                if overhang and data.levelling_seats <= 0:
                    # exhausted, can not allocate any more
                    allocation = []
                    data.result = None

                # recompute
                # remove candidates and substract from total_votes

        data.overhang.extend(
            [{"name": name, "seats": seats} for name, seats in data_overhang.items() if seats]
        )

        return CalculationState().make_result(
            (allocation if skip_initial_seats or not data.result else data.result.allocation), data
        )


def _reinterpret_events(
    data: evt.EventLog | None, allocation: list[Candidate[AnyName]]
) -> Generator[evt.Event]:
    logged_seats: dict[AnyName, int] = defaultdict(lambda: 0)
    if data:
        log: list[evt.Event] = []
        allocated_seats = {cand.name: cand.seats for cand in allocation}
        for event in reversed(data.log):
            if not isinstance(event, evt.WinnerEvent):
                continue
            logged = logged_seats[event.target]
            limit = allocated_seats[event.target]
            if limit > logged >= 0:
                log.append(dt.replace(event, criterion="levelling_seats"))
                logged_seats[event.target] += 1
            elif limit < logged <= 0:
                log.append(
                    evt.SeatsEvent(seats=-1, criterion="surplus_discarded", target=event.target)
                )
                logged_seats[event.target] -= 1
        yield from reversed(log)
    for cand in allocation:
        if (0 <= logged_seats[cand.name] < cand.seats) or (
            cand.seats < logged_seats[cand.name] <= 0
        ):
            yield evt.SeatsEvent(
                seats=cand.seats - logged_seats[cand.name],
                criterion="levelling_seats" if cand.seats > 0 else "surplus_discarded",
                target=cand.name,
            )
