#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

r"""Adapter for additional member systems.

:ref:`References <interregnum_biblio>`
--------------------------------------

* [Denmark:2011]_
* [Iceland:2013]_
* [Scotland:2024]_

----
"""
from __future__ import annotations
import dataclasses as dt
from typing import (
    Generic,
    cast,
)

from ..types import (
    AnyName,
    allocators,
    Input,
    check_seats,
    Allocator,
    AnyResult,
    check_inputs,
)
from ..events import Event
from .. import inputs as ipt
from ..adapters.initialseats import InitialSeatsAdapter


@allocators.register("additional_member", "levelling_seats")
class AdditionalMemberAdapter(Generic[AnyName, AnyResult], Allocator[AnyName, AnyResult]):
    """Additional member system.

    Used to allocated levelling seats resuming a previous allocation with different votes.

    See [Denmark:2011]_, [Iceland:2013]_, [Scotland:2024]_.

    :data:`.allocators` collection keys:

    - `additional_member`
    - `levelling_seats`
    """

    def __init__(
        self,
        allocator_f: Allocator[AnyName, AnyResult],
        skip_initial_seats: bool = ipt.DEFAULT_SKIP_INITIAL_SEATS,
    ):
        """Create an additional member adapter.

        Args
        ----
        allocator_f:
            A method to allocate seats. It must admit initial seats.
        skip_initial_seats
            If `True`, return new seats summed to old seats, otherwise return new seats only.
        """
        if Input.INITIAL_SEATS not in allocator_f.admitted_input:
            allocator_f = InitialSeatsAdapter(allocator_f, min_seats=0, resume_allocation=True)
        check_inputs(
            Input.SEATS | Input.INITIAL_SEATS | Input.SKIP_INITIAL_SEATS, allocator_f.admitted_input
        )
        super().__init__(
            allocator_f.required_input | Input.INITIAL_SEATS | Input.SEATS,
            allocator_f.optional_input | Input.INNER_INITIAL_SEATS | Input.SKIP_INITIAL_SEATS,
        )
        self.allocator_f = allocator_f
        self.skip_initial_seats = skip_initial_seats

    def calc(
        self,
        initial_seats: ipt.INamedSeats,
        seats: int,
        inner_initial_seats: ipt.INamedSeats | None = None,
        skip_initial_seats: bool | None = None,
        **method_args,
    ):
        """Allocate seats to candidates.

        Args
        ----
        initial_seats
            seats won by the first vote allocation
        seats
            number of levelling seats
        inner_initial_seats
            initial seats to pass to the inner allocation
        """
        check_seats(seats)
        if skip_initial_seats is None:
            skip_initial_seats = self.skip_initial_seats
        initial_seats_: dict[AnyName, int] = dict(initial_seats)
        c_initial_seats: dict[AnyName, int] = dict(inner_initial_seats or {})
        init_candidates = frozenset(initial_seats_.keys()).union(c_initial_seats.keys())
        args = cast(ipt.InputDict[AnyName, Event], method_args)
        args["seats"] = seats
        args["initial_seats"] = [
            (name, initial_seats_.get(name, 0) + c_initial_seats.get(name, 0))
            for name in init_candidates
        ]
        supports_add_is = Input.SKIP_INITIAL_SEATS in self.allocator_f.admitted_input
        if supports_add_is:
            args["skip_initial_seats"] = skip_initial_seats
        result = self.allocator_f(**args)

        if not skip_initial_seats and not supports_add_is:
            # the default behaviour is not including initial seats
            result = dt.replace(
                result,
                allocation=tuple(
                    cand.add_seats(initial_seats_.get(cand.name, 0)) for cand in result.allocation
                ),
            )
        return result
