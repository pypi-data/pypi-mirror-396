#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Compensatory systems."""

from __future__ import annotations
from typing import (
    Any,
    Literal,
    Sequence,
    Mapping,
)
import dataclasses as dt
import enum
from pathlib import Path

from typing_extensions import override

from ..types import ifnone, parse_enum
from ..methods.types import PreconditionError, Input, Allocator
from ..methods.compensatory.additional_member import AdditionalMemberAdapter
from ..methods.compensatory.mixed_member import MixedMemberAdapter, OverhangMode
from ..methods.adapters.initialseats import DEFAULT_RESUME_ALLOCATION
from ..methods import inputs as ipt
from .contenders import GroupBy
from .counting import TotalVotes, Counting
from . import node as nd
from . import district as ds
from . import serialize as sr
from .references import unserialize_groupable_reference


class CompensatoryType(enum.Enum):
    """Types of compensatory systems."""

    ADDITIONAL_MEMBER = enum.auto()
    "Resume allocation from the seats won by first vote"

    MIXED_MEMBER = enum.auto()
    """Allocate and subtract the seats won by first vote. Any party with overhang seats will
    will get no new seat."""

    ABSORB_OVERHANG = enum.auto()
    """Allocate and subtract the seats won by first vote. The allocated seats are incremented
    until no overhang seats exist"""

    EXCLUDE_OVERHANG_PARTIES = enum.auto()
    "Subtract the overhang seats and exclude those parties from the compensatory allocation."

    SUBTRACT_OVERHANG_SEATS = enum.auto()
    """Allocate and subtract the already won seats. Any party with overhang seats
    will win negative seats in order to compensate the overhang seats"""

    @classmethod
    def parse(cls, value: str | CompensatoryType | None) -> CompensatoryType | None:
        """Parse from string format."""
        if isinstance(value, CompensatoryType):
            return value
        value = (value or "").strip()
        if not value:
            return None
        return parse_enum(cls, value)

    def to_mode(self) -> OverhangMode:
        """Return an associated mode for the allocator."""
        if self == CompensatoryType.ABSORB_OVERHANG:
            return OverhangMode.ABSORB
        if self == CompensatoryType.EXCLUDE_OVERHANG_PARTIES:
            return OverhangMode.EXCLUDE_PARTIES
        if self == CompensatoryType.SUBTRACT_OVERHANG_SEATS:
            return OverhangMode.SUBTRACT_SEATS
        return OverhangMode.IGNORE

    def __str__(self) -> str:
        """Return the attribute as a string key."""
        return self.name.lower()


sr.serializer(CompensatoryType)(str)


@dt.dataclass
class Compensatory(ds.BallotsNode):
    """A node for compensatory systems."""

    type: Literal["compensatory"] = "compensatory"
    seats: int | nd.ReferenceSet[nd.GroupableReference] | None = None
    "levelling seats"

    mode: CompensatoryType = CompensatoryType.ADDITIONAL_MEMBER
    "allocation mode"

    max_seats: int | None = None
    "max number of seats the allocation can use (for growing allocations)"

    first_vote: nd.Node | nd.ReferenceSet[nd.GroupableReference] | None = None
    "child node or reference where the first vote is extracted from"

    subtract_excluded_candidates: bool = False
    "exclude seats for excluded candidates due to restrictions"

    propagate_initial_seats: bool = False
    "propagate candidates' initial seats to the inner method"

    @override
    def get_seats(self) -> int | nd.ReferenceSet[nd.GroupableReference]:
        if isinstance(self.seats, nd.ReferenceSet):
            return self.seats
        return self.seats or 1

    @override
    def grouping(self) -> Literal[GroupBy.CANDIDATE]:
        return GroupBy.CANDIDATE

    @override
    def local_divisions(self) -> Sequence[nd.Node | nd.Reference] | None:
        return list(ds.expand_nodes(self.first_vote)) or None

    def _add_required_inputs(
        self,
        contexts: tuple[nd.AllocationContext, nd.NodeContext],
        filters: ds.Filters,
        counting: Counting,
        method: Allocator,
        inputs: ds.Inputs,
    ):
        context, local_context = contexts

        if ds.input_required(method, inputs, Input.RANDOM_SEED):
            inputs["random_seed"] = self.random_seed

        if self.max_seats and ds.input_required(method, inputs, Input.MAX_SEATS):
            inputs["max_seats"] = self.max_seats

        if ds.input_required(method, inputs, Input.TOTAL_VOTES):
            inputs["total_votes"] = counting.total_votes().usable_votes(
                local_context.total_votes or TotalVotes.CANDIDATES
            )

        if ds.input_required(method, inputs, Input.SEATS):
            inputs["seats"] = context.resolve_seats(self)

        # threshold
        self._add_candidates_input(
            context,
            filters,
            method,
            counting,
            inputs,
        )

    @override
    def __call__(self, context: nd.AllocationContext, local_context: nd.NodeContext):
        method_f = local_context.get_method()
        if not method_f:
            raise PreconditionError(
                f"Leaf district '{self.name}' could not inherit a voting method"
            )
        old_method = method_f()
        inputs: ds.Inputs = {}

        counting = self._get_counting(context)
        old_method, candidates_initial_seats = self._get_initial_seats(
            (context, local_context), old_method, counting, self.candidates
        )

        filters = ds.Filters(context, local_context, self.get_id())

        if rules := counting.seat_rules():
            inputs["constraints"] = rules

        skip_initial_seats = ifnone(
            local_context.skip_initial_seats, ipt.DEFAULT_SKIP_INITIAL_SEATS
        )
        resume_allocation = ifnone(local_context.resume_allocation, DEFAULT_RESUME_ALLOCATION)

        method: Allocator | None = None
        while method is not old_method:
            method = method or old_method

            self._add_required_inputs((context, local_context), filters, counting, method, inputs)

            if ds.input_required(method, inputs, Input.INITIAL_SEATS):
                inputs["initial_seats"] = list(candidates_initial_seats.items())

            inputs = ds.clean_inputs(method, inputs)
            old_method = method
            method = ds.adapt_allocator(
                method,
                inputs,
                resume_allocation=resume_allocation,
                skip_initial_seats=skip_initial_seats,
            )
        assert method

        # set mode
        if self.mode == CompensatoryType.ADDITIONAL_MEMBER:
            method = AdditionalMemberAdapter(method, skip_initial_seats=skip_initial_seats)
        else:
            method = MixedMemberAdapter(
                overhang_mode=self.mode.to_mode(),
                allocator_f=method,
                subtract_excluded_candidates=self.subtract_excluded_candidates,
                skip_initial_seats=skip_initial_seats,
            )

        if "initial_seats" in inputs:
            if self.propagate_initial_seats and ds.input_required(
                method, inputs, Input.INNER_INITIAL_SEATS
            ):
                inputs["inner_initial_seats"] = inputs["initial_seats"]
            del inputs["initial_seats"]

        # convert first vote to initial_seats
        if ds.input_required(method, inputs, Input.INITIAL_SEATS):
            inputs["initial_seats"] = [
                (c.name, c.seats)
                for c in context.group_result(ds.get_candidates(self.first_vote, GroupBy.CANDIDATE))
                if c.seats
            ]

        if self.max_seats and ds.input_required(method, inputs, Input.MAX_SEATS):
            inputs["max_seats"] = self.max_seats

        inputs = ds.clean_inputs(method, inputs)
        self.result = method(**inputs)


@sr.unserializer("compensatory", Compensatory)
def unserialize_compensatory_dict(data: Mapping[str, Any], cwd: Path | None) -> dict[str, Any]:
    """Unserialize Compensatory fields."""
    # mode: CompensatoryType = CompensatoryType.ADDITIONAL_MEMBER
    # first_vote: Node | str | None = None
    # second_vote: Node | str | None = None
    data = ds.unserialize_ballotsnode_dict(data, cwd)
    if val := data.get("mode"):
        data["mode"] = CompensatoryType.parse(val)
    if val := data.get("first_vote"):
        data["first_vote"] = sr.unserialize_node(val, cwd, groupby=True)
    if (val := data.get("seats")) is not None:
        if not isinstance(val, int):
            val = unserialize_groupable_reference(val)
        data["seats"] = val
    return data
