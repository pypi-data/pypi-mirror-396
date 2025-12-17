#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Basic district."""
from __future__ import annotations
from typing import (
    Any,
    Sequence,
    Iterable,
    Iterator,
    Literal,
    Mapping,
    TypeVar,
    Callable,
    cast,
)
import dataclasses as dt
from pathlib import Path
from typing_extensions import override

from ..types import ifnone
from ..methods.preferential.types import Preference
from ..methods.types import (
    PreconditionError,
    Input,
    Allocator,
)
from ..methods.events import Event
from ..methods.filters import ContenderSetFilter
from ..methods.adapters.maxseats import MaxSeatsAdapter, RuleSet
from ..methods.adapters.initialseats import (
    InitialSeatsAdapter,
    DEFAULT_RESUME_ALLOCATION,
)
from ..methods import inputs as ipt
from ..logging import logger
from .counting import (
    Counting,
    Ballots,
    TotalVotes,
    InitialSeatsSource,
)
from .contenders import (
    Contender,
    Alliance,
    ContenderId,
    GroupBy,
)
from .references import (
    GroupableReference,
    ReferenceSet,
    unserialize_groupable_reference,
)
from . import serialize as sr
from . import io
from . import node as nd


Inputs = ipt.InputDict[ContenderId, Event]
BipropInputs = ipt.BipropInputDict[ContenderId, Event, str | None, tuple[str, str]]


@dt.dataclass
class Filters:
    """Exclusion filters provider."""

    context: nd.AllocationContext
    "electoral system allocation context"

    node: nd.NodeContext
    "working node local context"

    key: str
    "working node id"

    lists: tuple[set[ContenderId], set[ContenderId]] | None = None
    "exlusion list and inclusion list"

    def _compute(self) -> tuple[set[ContenderId], set[ContenderId]]:
        if not self.lists:
            blacklist = None
            whitelist = None
            if self.node.exclude:
                blacklist = self.context.resolve_threshold(self.key)
            if self.node.include:
                whitelist = self.context.resolve_threshold(self.key, include=True)
            self.lists = blacklist or set(), whitelist or set()
        return self.lists

    def get_filter_f(self) -> ContenderSetFilter[ContenderId, Event]:
        """Return a candidate filter using the combination of exclusion and inclusion lists."""
        return ContenderSetFilter(self.get_exclude_candidates())

    def get_exclude_candidates(self) -> set[ContenderId]:
        """Return the combination of exclusion and inclusion lists."""
        blacklist, whitelist = self._compute()
        return blacklist.difference(whitelist)


@dt.dataclass
class BallotsNode(nd.Node):
    """A node with ballots."""

    candidates: Sequence[Contender] | ReferenceSet[GroupableReference] | None = None
    "votes for candidates"

    alliances: Sequence[Alliance] | None = None
    "alliances definitions"

    preferences: (
        Sequence[Preference[str]]
        | Callable[[Callable[[str], ContenderId]], Iterator[Preference[ContenderId]]]
        | ReferenceSet[GroupableReference]
        | None
    ) = None
    "list of preferential ballots"

    @override
    def __call__(self, context: nd.AllocationContext, local_context: nd.NodeContext):
        raise NotImplementedError()

    def _clear_data(self) -> None:
        if not isinstance(self.candidates, ReferenceSet):
            self.candidates = None
        self.alliances = None
        if not isinstance(self.preferences, ReferenceSet):
            self.preferences = None

    @override
    def local_candidates(self) -> Ballots | ReferenceSet[GroupableReference] | None:
        if (self.candidates is None) or isinstance(self.candidates, nd.ReferenceSet):
            return self.candidates
        return Ballots.build(self.candidates)

    @override
    def local_candidates_references(self) -> nd.ReferenceSet[GroupableReference] | bool:
        if isinstance(self.candidates, nd.ReferenceSet):
            return self.candidates
        return self.candidates is not None

    @override
    def local_preferences(
        self, candidates: Iterable[ContenderId]
    ) -> Iterator[Preference[ContenderId]] | nd.ReferenceSet[nd.GroupableReference] | None:
        mapping: dict[str, ContenderId] = {}
        for cand in candidates:
            if cand.name in mapping:
                raise ValueError(
                    f"candidate {cand} can't be represented by name: "
                    f"it conflicts with {mapping[cand.name]}"
                )
            mapping[cand.name] = cand

        def converter(name: str) -> ContenderId:
            if name in mapping:
                return mapping[name]
            mapping[name] = ContenderId(name=name, alliance=name)
            return mapping[name]

        if (self.preferences is None) or isinstance(self.preferences, nd.ReferenceSet):
            return self.preferences

        if self.preferences and callable(self.preferences):
            return self.preferences(converter)

        return (pref.transform(converter) for pref in self.preferences)

    @override
    def local_preferences_references(self) -> ReferenceSet[GroupableReference] | bool:
        if isinstance(self.preferences, ReferenceSet):
            return self.preferences
        return self.preferences is not None

    @override
    def local_alliances(self) -> Sequence[Alliance] | nd.ReferenceSet[nd.GroupableReference] | None:
        if self.alliances:
            return self.alliances
        refs = self.local_candidates_references()
        if isinstance(refs, nd.ReferenceSet):
            return refs
        return None

    @override
    def update_candidates(self, candidates: Sequence[Contender]) -> None:
        self.candidates = candidates

    def _get_counting(self, context: nd.AllocationContext) -> Counting:
        return Counting(
            candidates=context.flatten_candidates(self),
            alliances=context.flatten_alliances(self),
        )

    def _get_initial_seats(
        self,
        contexts: tuple[nd.AllocationContext, nd.NodeContext],
        method: Allocator,
        counting: Counting,
        results: nd.ReferenceSet | Any,
    ) -> tuple[Allocator, dict[ContenderId, int]]:
        """Get the initial seats from the specified origin."""
        context, local_context = contexts
        initial_seats: dict[ContenderId, int] = {}
        cont_seats = ifnone(local_context.resume_allocation, DEFAULT_RESUME_ALLOCATION)
        add_seats = ifnone(local_context.skip_initial_seats, ipt.DEFAULT_SKIP_INITIAL_SEATS)
        if isinstance(local_context.initial_seats, InitialSeatsSource):
            if local_context.initial_seats == InitialSeatsSource.MIN_SEATS:
                initial_seats = (
                    {
                        cont.get_id(): cont.min_seats
                        for cont in counting.candidates.ballots or []
                        if cont.min_seats is not None and cont.min_seats != 0
                    }
                    if counting.candidates
                    else {}
                )
            elif InitialSeatsSource.RESULT and isinstance(self.candidates, ReferenceSet):
                initial_seats = {
                    c.name: c.seats
                    for c in context.group_result(get_candidates(results, GroupBy.CANDIDATE))
                }
            else:
                raise PreconditionError(
                    f"unexpected value for initial_seats: {local_context.initial_seats}"
                )
        elif (local_context.initial_seats != 0) or (cont_seats != DEFAULT_RESUME_ALLOCATION):
            # an adapter is required
            method = InitialSeatsAdapter(
                method,
                local_context.initial_seats,
                resume_allocation=cont_seats,
                skip_initial_seats=add_seats,
            )

        return method, initial_seats

    def _add_candidates_input(
        self,
        context: nd.AllocationContext,
        filters: Filters,
        method: Allocator,
        counting: Counting,
        inputs: Inputs,
    ) -> Filters:
        """Add required allocator inputs related to candidates."""
        logger.debug("adding ballots and restrictions to inputs for '%s'", self.get_id())
        # filter
        if input_required(method, inputs, Input.FILTER_F) and (filter_f := filters.get_filter_f()):
            if filter_f.exclusion_list() or Input.FILTER_F in method.required_input:
                inputs["filter_f"] = filter_f
        # candidates
        if input_required(method, inputs, Input.CANDIDATES):
            if (counting.candidates is None) or (counting.candidates.ballots is None):
                if Input.CANDIDATES in method.required_input:
                    raise ValueError(f"no candidates found for district {self.name}")
            else:
                candidates = [x.candidate(0) for x in counting.candidates.ballots]
                inputs["candidates"] = candidates
        # exclude candidates
        if input_required(method, inputs, Input.EXCLUDE_CANDIDATES) and (
            excl_cand := filters.get_exclude_candidates()
        ):
            inputs["exclude_candidates"] = excl_cand
        # candidate list
        if input_required(method, inputs, Input.CANDIDATE_LIST):
            if counting.candidates and counting.candidates.ballots:
                inputs["candidate_list"] = [x.get_id() for x in counting.candidates.ballots]
        # preferences
        if input_required(method, inputs, Input.PREFERENCES):
            if prefs := context.flatten_preferences(self):
                counting.preferences = list(prefs)
                logger.debug(
                    "[node: %s] number of preferences: %d", self.name, len(counting.preferences)
                )
            if counting.preferences is None:
                if Input.PREFERENCES not in method.required_input:
                    raise ValueError(f"no preferences found for district {self.name}")
            else:
                inputs["preferences"] = counting.preferences

        return filters


def unserialize_ballotsnode_dict(data: Mapping[str, Any], cwd: Path | None) -> dict[str, Any]:
    """Unserialize fields for a BallotsNode node."""
    data = nd.Node.unserialize_dict(**data)
    if val := data.get("candidates"):
        if isinstance(val, str):
            val = nd.ReferenceSet(list(GroupableReference.parse(val)))
        elif not isinstance(val, ReferenceSet):
            val = Contender.make(val)
        data["candidates"] = val
    if val := data.get("alliances"):
        if isinstance(val, str):
            val = nd.ReferenceSet(list(GroupableReference.parse(val)))
        elif not isinstance(val, ReferenceSet):
            val = Alliance.make(val)
        data["alliances"] = val
    if val := data.get("preferences"):
        if isinstance(val, str):
            val = nd.ReferenceSet(list(GroupableReference.parse(val)))
        elif isinstance(val, Mapping):
            val = io.unserialize_preferences_file(val, cwd)
        elif not isinstance(val, ReferenceSet):
            val = list(Preference.make(val))
        data["preferences"] = val
    return data


_Ref = TypeVar("_Ref", bound=nd.Reference)


def expand_nodes(node: nd.Node | Iterable[_Ref] | None) -> Iterator[nd.Node | _Ref]:
    """Iterate nodes or references."""
    if node is None:
        return
    if isinstance(node, nd.Node):
        yield node
        return
    yield from node


def get_candidates(district: nd.Node | nd.ReferenceSet | None, by: GroupBy) -> nd.ReferenceSet:
    """Return a reference for a district.

    If district is already a reference, return as is.
    Otherwise, compose a groupable reference.
    """
    if isinstance(district, nd.ReferenceSet):
        return district
    assert district is not None
    return nd.ReferenceSet(
        references=[
            nd.GroupableReference(
                groupby=by,
                ref=district.get_id(),
                # level=-1
            )
        ]
    )


def unsupported_input(allocator: Allocator, inputs: Inputs, flag: Input) -> bool:
    """Return True if `allocator` does not allow `flag` as an input."""
    return flag.param_name in inputs and flag not in allocator.admitted_input


def adapt_allocator(allocator: Allocator, inputs: Inputs, **kwargs) -> Allocator:
    """Add adapters to allocator so that all inputs can be processed."""
    if unsupported_input(allocator, inputs, Input.INITIAL_SEATS) or unsupported_input(
        allocator, inputs, Input.SKIP_INITIAL_SEATS
    ):
        allocator = InitialSeatsAdapter(
            allocator,
            min_seats=0,
            resume_allocation=ifnone(
                kwargs.get("resume_allocation"),
                DEFAULT_RESUME_ALLOCATION,
            ),
            skip_initial_seats=ifnone(
                kwargs.get("skip_initial_seats"), ipt.DEFAULT_SKIP_INITIAL_SEATS
            ),
        )
    if unsupported_input(allocator, inputs, Input.CONSTRAINTS):
        allocator = MaxSeatsAdapter(allocator)
    return allocator


def input_required(method: Allocator, inputs: Inputs, flag: Input) -> bool:
    """Return True if `flag` is required for `method`."""
    return flag in method.admitted_input and flag.param_name not in inputs


@dt.dataclass
class District(BallotsNode):
    """An electoral district or constituency.

    This node supports methods, candidates and preferences.
    """

    type: Literal["district"] = "district"
    seats: int | ReferenceSet[GroupableReference] | None = None
    "number of seats to allocate (default = 1)"

    party_seats: nd.Node | ReferenceSet[GroupableReference] | None = None
    "seats allocated by party (used by bi-proportional methods), extracted from a node result"

    district_seats: nd.Node | ReferenceSet[GroupableReference] | None = None
    "seats allocated by district (used by bi-proportional methods), extracted from a node result"

    @override
    def grouping(self) -> Literal[GroupBy.CANDIDATE]:
        return GroupBy.CANDIDATE

    @override
    def local_divisions(self) -> Sequence[nd.Node | nd.Reference] | None:
        out: list[nd.Node | nd.Reference] = []
        out.extend(expand_nodes(self.party_seats))
        out.extend(expand_nodes(self.district_seats))
        return out or None

    @override
    def get_seats(self) -> int | ReferenceSet[GroupableReference]:
        if isinstance(self.seats, ReferenceSet):
            return self.seats
        return self.seats or 1

    @override
    def __call__(self, context: nd.AllocationContext, local_context: nd.NodeContext):
        method_f = local_context.get_method()
        if not method_f:
            raise PreconditionError(
                f"Leaf district '{self.name}' could not inherit a voting method"
            )
        old_method = method_f()
        inputs: BipropInputs = {}

        logger.debug("counting ballots at '%s'", self.get_id())
        counting = self._get_counting(context)
        filters = Filters(context, local_context, self.get_id())
        logger.debug("getting initial seats at '%s'", self.get_id())
        old_method, initial_seats = self._get_initial_seats(
            (context, local_context), old_method, counting, self.candidates
        )

        logger.debug("getting seats constraints at '%s'", self.get_id())
        if rules := counting.seat_rules():
            inputs["constraints"] = rules

        logger.debug("adding required input ('%s')", self.get_id())
        method: Allocator | None = None
        while method is not old_method:
            method = method or old_method

            if input_required(method, inputs, Input.SKIP_INITIAL_SEATS):
                inputs["skip_initial_seats"] = ifnone(
                    local_context.skip_initial_seats, ipt.DEFAULT_SKIP_INITIAL_SEATS
                )

            if input_required(method, inputs, Input.INITIAL_SEATS):
                inputs["initial_seats"] = initial_seats.items()

            if input_required(method, inputs, Input.RANDOM_SEED):
                inputs["random_seed"] = self.random_seed

            if input_required(method, inputs, Input.SEATS):
                inputs["seats"] = context.resolve_seats(self)

            if input_required(method, inputs, Input.TOTAL_VOTES):
                inputs["total_votes"] = counting.total_votes().usable_votes(
                    local_context.total_votes or TotalVotes.CANDIDATES
                )

            self._add_candidates_input(
                context,
                filters,
                method,
                counting,
                inputs,
            )

            if input_required(method, inputs, Input.DISTRICT_SEATS):
                inputs["district_seats"] = [
                    (cand.name, cand.seats)
                    for cand in context.group_result(
                        get_candidates(self.district_seats, GroupBy.CANDIDATE)
                    )
                ]
            if input_required(method, inputs, Input.PARTY_SEATS):
                inputs["party_seats"] = [
                    (cand.name, cand.seats)
                    for cand in context.group_result(
                        get_candidates(self.party_seats, GroupBy.CANDIDATE)
                    )
                ]

            inputs = _prepare_biproportional(method, clean_inputs(method, inputs))
            old_method = method
            method = adapt_allocator(
                method,
                inputs,
                resume_allocation=local_context.resume_allocation,
                skip_initial_seats=local_context.skip_initial_seats,
            )

        logger.debug("invoking allocation method ('%s')", self.get_id())
        assert method
        self.result = method(**inputs)


@sr.unserializer("district", District)
def unserialize_district_dict(data: Mapping[str, Any], cwd: Path | None) -> dict[str, Any]:
    """Unserialize District fields."""
    data = unserialize_ballotsnode_dict(data, cwd)
    if val := data.get("party_seats"):
        data["party_seats"] = sr.unserialize_node(val, cwd, groupby=True)
    if val := data.get("district_seats"):
        data["district_seats"] = sr.unserialize_node(val, cwd, groupby=True)
    if (val := data.get("seats")) is not None:
        if not isinstance(val, int):
            val = unserialize_groupable_reference(val)
        data["seats"] = val
    return data


def clean_inputs(method: Allocator, inputs: Inputs) -> Inputs:
    """Clean superfluous inputs.

    Max seats restrictions will be reduced to the subset of used candidates.
    """
    excluded: set[ContenderId] = set()
    if (inputs.get("random_seed") is None) and Input.RANDOM_SEED not in method.required_input:
        inputs.pop("random_seed", None)
    if not inputs.get("total_votes") and Input.TOTAL_VOTES not in method.required_input:
        inputs.pop("total_votes", None)
    if excl := inputs.get("exclude_candidates"):
        excluded.update(excl)
    elif Input.EXCLUDE_CANDIDATES not in method.required_input:
        inputs.pop("exclude_candidates", None)
    if filter_f := inputs.get("filter_f"):
        excluded.update(filter_f.exclusion_list())
    if excluded and (rules := inputs.get("constraints")):
        initial_seats = dict(inputs.get("initial_seats") or {})
        c_initial_seats = dict(inputs.get("inner_initial_seats") or {})
        ruleset: RuleSet[ContenderId] = RuleSet(rules, validate=False)
        for cand in excluded:
            ruleset.remove_name(cand, initial_seats.get(cand, 0))
            initial_seats.pop(cand, None)
            c_initial_seats.pop(cand, None)
        inputs["constraints"] = list(ruleset)
        if Input.INITIAL_SEATS.param_name in inputs:
            inputs["initial_seats"] = initial_seats.items()
        if Input.INNER_INITIAL_SEATS.param_name in inputs:
            inputs["initial_seats"] = c_initial_seats.items()
    if not inputs.get("constraints") and Input.CONSTRAINTS not in method.required_input:
        inputs.pop("constraints", None)
    return inputs


def to_party(contender: ContenderId) -> tuple[str, str]:
    """Return a party identifier from a contender id."""
    return (contender.name, contender.alliance)


def to_district(contender: ContenderId) -> str | None:
    """Return a district identifier from a contender id."""
    return contender.district


def to_biproportional_contender(contender: ContenderId) -> tuple[tuple[str, str], str | None]:
    """De-compose a contender in party and district ids."""
    return (to_party(contender), to_district(contender))


def from_biproportional_contender(contender: tuple[tuple[str, str], str | None]) -> ContenderId:
    """Compose a contender id from party and district ids."""
    return ContenderId(name=contender[0][0], alliance=contender[0][1], district=contender[1])


_ItSeats = Iterable[tuple[ContenderId, int]]


def _prepare_biproportional(method: Allocator, inputs: Inputs) -> BipropInputs:
    """Prepare inputs for bi-proportional methods."""
    inputs = cast(BipropInputs, inputs)
    if Input.CANDIDATE_NAME_F in method.admitted_input:
        inputs["candidate_name_f"] = from_biproportional_contender
    if Input.PARTY_NAME_F in method.admitted_input:
        inputs["party_name_f"] = to_party
    if Input.DISTRICT_NAME_F in method.admitted_input:
        inputs["district_name_f"] = to_district
    if district_seats := inputs.get("district_seats"):
        inputs["district_seats"] = [
            (cand.name, seats) for cand, seats in cast(_ItSeats, district_seats)
        ]
    if party_seats := inputs.get("party_seats"):
        inputs["party_seats"] = [
            (to_party(cand), seats) for cand, seats in cast(_ItSeats, party_seats)
        ]
    return inputs
