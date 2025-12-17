#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

r"""Re-apportionment from one node to others.

:ref:`References <interregnum_biblio>`
--------------------------------------

* [Denmark:2011]_
* [Iceland:2013]_
* [Norway:2023]_
* [Germany:2025]_

----
"""

from __future__ import annotations
from typing import (
    Any,
    Sequence,
    Literal,
    Mapping,
    Iterator,
    Iterable,
)
import dataclasses as dt
import itertools
from pathlib import Path
from collections import defaultdict
from fractions import Fraction
import enum
from typing_extensions import override

from ..types import parse_enum
from ..methods.types import (
    Allocator,
    PreconditionError,
    Input,
    Candidate,
    Result,
    Score,
)
from ..methods.compensatory.additional_member import AdditionalMemberAdapter
from ..methods.adapters.maxseats import RuleSet
from ..methods.events import EventLog, QuotaWinnerEvent
from . import serialize as sr
from . import node as nd
from . import contenders as tp
from . import counting as ct
from . import references as rf
from . import district as ds


class ParallelReapportionmentError(PreconditionError):
    """Raised when the parallel strategy can't be used."""


@dt.dataclass
class CompositeResultData(EventLog):
    """A result that stores several allocation steps."""

    #: result for each allocation step
    steps: list[Result] | None = None


class RelativeDivisor(enum.Enum):
    """Divisor that will be used as a divisor for party/district score."""

    VOTES = enum.auto()
    """Use district votes.

    Iceland ([Iceland:2013]_): votes / constituency votes"""

    QUOTA = enum.auto()
    """use district votes quota

    Norway ([Norway:2023]_): votes / (constituency votes / number of constituency seats)"""

    @classmethod
    def parse(cls, value: str) -> RelativeDivisor:
        """Parse from string format."""
        return parse_enum(cls, value)

    def __str__(self):
        """Return a formatted string."""
        return self.name.lower()


sr.serializer(RelativeDivisor)(str)


@dt.dataclass
class Reapportionment(ds.BallotsNode):
    """Re-apportionment system.

    Use to project adjustment seats allocated by compensatory systems to final
    districts which already have initial seats, using the votes provided by the field `candidates`.

    Negative levelling seats are supported.

    See [Denmark:2011]_, [Iceland:2013]_, [Norway:2023]_, [Germany:2025]_.
    """

    type: Literal["reapportionment"] = "reapportionment"
    strategy: Literal["parallel"] | tp.GroupBy = tp.GroupBy.DISTRICT
    """how to split allocations:

    - `parallel` ([Iceland:2013]_) will allocate each compensatory seat in
       the order it was won (requires a method that produces :class:`.WinnerEvent` for each seat)
    - :class:`.GroupBy`: split the allocations by the given criterion (for example,
       party names or districts)"""

    relative: RelativeDivisor | None = None
    """reference numbers (score used as votes for the allocation):

    - `None`: use absolute votes for party and district
    - `RelativeDivisor`: make a relative score using this divisor"""

    adjustment: nd.Node | rf.ReferenceSet[rf.GroupableReference] | None = None
    "adjustment seats that will be projected to the new districts"

    first_vote: nd.Node | rf.ReferenceSet[rf.GroupableReference] | None = None
    "districts where the seats will be projected"

    @override
    def get_seats(self) -> Literal[0]:
        return 0

    @override
    def grouping(self) -> Literal[tp.GroupBy.CANDIDATE]:
        return tp.GroupBy.CANDIDATE

    @override
    def local_divisions(self) -> Sequence[nd.Node | nd.Reference] | None:
        out: list[nd.Node | nd.Reference] = []
        out.extend(ds.expand_nodes(self.adjustment))
        out.extend(ds.expand_nodes(self.first_vote))
        return out or None

    def _calc_additive(
        self,
        context: nd.AllocationContext,
        base_method: Allocator,
        counting: ds.Counting,
        filters: ds.Filters,
    ) -> tuple[list[Candidate[tp.ContenderId]], list[Result]]:

        if not (counting.candidates and counting.candidates.ballots):
            raise PreconditionError("no candidates found for additive reapportionment")
        state = ReapportionmentState(
            candidates=[x.candidate(0) for x in counting.candidates.ballots or []],
            rules=counting.seat_rules(),
            excluded=filters.get_exclude_candidates(),
        )
        if self.relative:
            state.compute_relative_score(context, self.relative, self.total_votes)

        # seats to reapportion
        state.adjustment_seats = {
            c.name: c.seats
            for c in context.group_result(ds.get_candidates(self.adjustment, tp.GroupBy.CANDIDATE))
            if c.seats > 0
        }
        if not state.adjustment_seats:
            # nothing to allocate
            return [], []
        state.initial_seats = {
            c.name: c.seats
            for c in context.group_result(ds.get_candidates(self.first_vote, tp.GroupBy.CANDIDATE))
            if c.seats
        }
        state.pair_districts(context)

        # district constraints
        state.add_district_constraints(context)

        # party constraints
        if self.strategy != "parallel":
            state.add_party_constraints()

        # remove candidates not present in adjustment_seats
        state.clean_candidates()

        allocation: list[Candidate[tp.ContenderId]] = []
        steps = []
        for seats, contenders in self._iter_allocations(context, state):
            if not seats or not contenders:
                continue
            result = self._allocate_step(base_method, state, seats, contenders)
            steps.append(result)
            allocation.extend(result.allocation)
            allocation = list(nd.merge_candidates(allocation))
            for cand in result.allocation:
                if cand.name not in state.initial_seats:
                    state.initial_seats[cand.name] = 0
                state.initial_seats[cand.name] += cand.seats
        return allocation, steps

    def _calc_subtractive(
        self,
        context: nd.AllocationContext,
        base_method: Allocator,
        counting: ds.Counting,
        filters: ds.Filters,
    ) -> tuple[list[Candidate[tp.ContenderId]], list[Result]]:

        assert counting.candidates and counting.candidates.ballots
        state = ReapportionmentState(
            candidates=[
                x.candidate(0).with_votes(-(x.votes or 0))
                for x in counting.candidates.ballots or []
            ],
            rules=[],
            excluded=filters.get_exclude_candidates(),
        )
        if self.relative:
            state.compute_relative_score(context, self.relative, self.total_votes)
        # shift votes to positive
        min_score = min(c.votes for c in state.candidates)
        state.candidates = [c.with_votes(c.votes - min_score) for c in state.candidates]

        # seats to reapportion
        state.adjustment_seats = {
            c.name: c.seats
            for c in context.group_result(ds.get_candidates(self.adjustment, tp.GroupBy.CANDIDATE))
            if c.seats < 0
        }
        if not state.adjustment_seats:
            # nothing to allocate
            return [], []
        state.initial_seats = {
            c.name: c.seats
            for c in context.group_result(ds.get_candidates(self.first_vote, tp.GroupBy.CANDIDATE))
            if c.seats
        }
        state.pair_districts(context)

        # party constraints
        state.rules.extend((seats, [cand]) for cand, seats in state.initial_seats.items())

        # remove candidates not present in adjustment_seats
        state.clean_candidates()
        # reset initial seats
        state.initial_seats = {}

        allocation: list[Candidate[tp.ContenderId]] = []
        steps = []
        for seats, contenders in self._iter_allocations(context, state):
            if not seats or not contenders:
                continue
            result = self._allocate_step(base_method, state, -seats, contenders)
            steps.append(result)
            allocation.extend(result.allocation)
            allocation = list(nd.merge_candidates(allocation))
            for cand in result.allocation:
                if cand.name not in state.initial_seats:
                    state.initial_seats[cand.name] = 0
                state.initial_seats[cand.name] += cand.seats
        return ([cand.with_seats(-cand.seats) for cand in allocation], steps)

    @override
    def __call__(self, context: nd.AllocationContext, local_context: nd.NodeContext):
        if not (method_f := local_context.get_method()):
            raise PreconditionError(
                f"Leaf district '{self.name}' could not inherit a voting method"
            )
        base_method = method_f()

        counting = ds.Counting(
            candidates=context.flatten_candidates(self),
            alliances=context.flatten_alliances(self),
        )
        filters = ds.Filters(context, local_context, self.get_id())

        allocation, steps = self._calc_additive(context, base_method, counting, filters)
        neg_alloc, neg_steps = self._calc_subtractive(context, base_method, counting, filters)
        allocation.extend(neg_alloc)
        steps.extend(neg_steps)

        if len(steps) == 1:
            self.result = steps[0]
        else:
            self.result = Result(allocation, CompositeResultData(steps=steps))

    def _iter_allocations(
        self,
        context: nd.AllocationContext,
        state: ReapportionmentState,
    ) -> Iterator[tuple[int, Sequence[Candidate[tp.ContenderId]]]]:
        if self.strategy == "parallel":
            try:
                yield from self._iter_parallel_allocations(context, state)
                return
            except ParallelReapportionmentError:
                if sum(state.adjustment_seats.values()) >= 0:
                    raise
                # negative reapportionment, try non-parallel
        groups = defaultdict(list)
        sources = defaultdict(set)
        for cand in state.candidates:
            # source candidate
            source = cand.name.with_district(state.district_map[cand.name.district], force=True)
            key: tp.ContenderId | None
            if self.strategy != tp.GroupBy.DISTRICT:
                key = source.transform(
                    self.strategy if self.strategy != "parallel" else tp.GroupBy.ID
                )
            else:
                key = None
            groups[key].append(cand)
            sources[key].add(source)
        for key, group in groups.items():
            yield (sum(state.adjustment_seats.get(source, 0) for source in sources[key]), group)

    def _iter_parallel_allocations(
        self,
        context: nd.AllocationContext,
        state: ReapportionmentState,
    ) -> Iterator[tuple[int, Sequence[Candidate[tp.ContenderId]]]]:
        assert self.adjustment
        comp_nodes = _resolve_node_reference(context, self.adjustment)
        assert len(comp_nodes) == 1
        result = comp_nodes[0].result
        assert result
        # find seat allocation events
        log = check_event_log(result.data).log
        # filter by adjustment_seats
        events = [
            evt
            for evt in log
            if isinstance(evt, QuotaWinnerEvent) and evt.target in state.adjustment_seats
        ]
        if len(events) != abs(sum(state.adjustment_seats.values())):
            raise ParallelReapportionmentError(
                "parallel re-apportionment: no event found for some winners"
            )
        for evt in events:
            # find compatible candidates
            yield 1, _filter_candidates(state.candidates, evt.target)

    def _allocate_step(
        self,
        base_method: Allocator,
        state: ReapportionmentState,
        seats: int,
        contenders: Sequence[Candidate[tp.ContenderId]],
    ) -> Result:
        inputs: ds.Inputs = {}
        if ds.input_required(base_method, inputs, Input.RANDOM_SEED):
            inputs["random_seed"] = self.random_seed
        inputs["seats"] = seats
        inputs["candidates"] = contenders
        inputs["initial_seats"] = [
            (c.name, state.initial_seats[c.name])
            for c in contenders
            if state.initial_seats.get(c.name)
        ]
        inputs["skip_initial_seats"] = True
        # reduce rules
        step_rules: RuleSet[tp.ContenderId] = RuleSet(state.rules, validate=False)
        contender_names = {c.name for c in contenders}
        for cand in state.candidates:
            if cand.name not in contender_names:
                step_rules.remove_name(cand.name, state.initial_seats.get(cand.name, 0))
        if rules_items := list(step_rules):
            inputs["constraints"] = rules_items
        method = ds.adapt_allocator(base_method, inputs)
        method = AdditionalMemberAdapter(method)
        if ds.input_required(method, inputs, Input.TOTAL_VOTES):
            inputs["total_votes"] = sum(c.votes for c in contenders)
        return method(**ds.clean_inputs(method, inputs))

    @override
    def update_candidates(self, candidates: Sequence[ct.Contender]) -> None:
        raise PreconditionError(
            f"node {self.get_id()} does not have local candidates. "
            "Update nodes for 'target' or 'adjustment'."
        )


@dt.dataclass
class ReapportionmentState:
    """Internal state for reapportionment node."""

    # target candidates
    candidates: list[tp.Candidate[tp.ContenderId]]
    # adjustment seats that will be injected to target
    adjustment_seats: dict[tp.ContenderId, int] = dt.field(default_factory=dict)
    # seats already allocated in target
    initial_seats: dict[tp.ContenderId, int] = dt.field(default_factory=dict)
    district_map: dict[str | None, str | None] = dt.field(default_factory=dict)
    rules: list[tuple[int, Sequence[tp.ContenderId]]] = dt.field(default_factory=list)
    excluded: set[tp.ContenderId] = dt.field(default_factory=set)

    def compute_relative_score(
        self,
        context: nd.AllocationContext,
        relative: RelativeDivisor,
        total_votes: ct.TotalVotes | None,
    ) -> None:
        """Compute relative score (reference number) using a divisor (votes, quota)."""
        total_votes = total_votes or ct.TotalVotes.CANDIDATES
        district_votes: dict[str | None, Score] = defaultdict(lambda: 0)
        for cand in self.candidates:
            if cand.name.district not in district_votes:
                district_votes[cand.name.district] = 0
        for district in district_votes:
            if not district:
                raise PreconditionError("district field can not be empty")
            stats = context.build_stats(rf.Reference(district), False)
            district_votes[district] = d_votes = stats.usable_votes(total_votes)
            if relative == RelativeDivisor.QUOTA:
                district_votes[district] = Fraction(d_votes, stats.seats)

        self.candidates = [
            cand.with_votes(Fraction(cand.votes, district_votes[cand.name.district]))
            for cand in self.candidates
        ]

    def pair_districts(self, context: nd.AllocationContext) -> None:
        """Map districts from the compensatory system to the destination districts."""
        self.district_map.clear()
        source_nodes = frozenset(c.district for c in self.adjustment_seats)
        target_nodes = frozenset(c.name.district for c in self.candidates)
        for source_node in source_nodes:
            descendants = (
                target_nodes.intersection(context.children(source_node))
                if source_node
                else target_nodes
            )
            self.district_map.update((t, source_node) for t in descendants)

    def add_district_constraints(self, context: nd.AllocationContext) -> None:
        """Add constraints for districts that do no allow undetermined adjustment seats."""
        for district, group in itertools.groupby(
            sorted(self.candidates, key=_get_district), _get_district
        ):
            if not district:
                continue
            node = context.keys[district].node
            if node.max_adjustment_seats:
                group_ = [c.name for c in group]
                node_seats = sum(self.initial_seats.get(name, 0) for name in group_)
                self.rules.append((node_seats + node.max_adjustment_seats, group_))

    def add_party_constraints(self) -> None:
        """Add constraints for parties based on the number of adjustment seats."""
        for source_cand, group in itertools.groupby(
            sorted(self.candidates, key=self._get_source_candidate), self._get_source_candidate
        ):
            group_ = [c.name for c in group]
            adjustment_seats = self.adjustment_seats.get(source_cand, 0)
            rule_seats = sum(self.initial_seats.get(name, 0) for name in group_)
            if adjustment_seats >= 0:
                rule_seats += adjustment_seats
            self.rules.append((rule_seats, group_))

    def _get_source_candidate(self, cand: tp.Candidate[tp.ContenderId]) -> tp.ContenderId:
        return cand.name.with_district(self.district_map[cand.name.district], force=True)

    def clean_candidates(self) -> None:
        """Remove candidates not present in adjustment_seats."""
        step_rules: RuleSet[tp.ContenderId] = RuleSet(self.rules)
        for idx, cand in reversed(list(enumerate(self.candidates))):
            removable = cand.name.district not in self.district_map
            if not removable:
                removable = (
                    cand.name.with_district(self.district_map[cand.name.district], force=True)
                    not in self.adjustment_seats
                    or cand.name in self.excluded
                )
            if removable:
                step_rules.remove_name(cand.name, self.initial_seats.get(cand.name, 0))
                self.candidates.pop(idx)
        self.rules = list(step_rules)


def _get_district(x: tp.Candidate[tp.ContenderId]) -> str:
    return x.name.district or ""


def _resolve_node_reference(
    context: nd.AllocationContext, reference: nd.Node | nd.ReferenceSet[nd.GroupableReference]
) -> list[nd.Node]:
    if not reference:
        return []
    if isinstance(reference, nd.Node):
        return [reference]
    return list(context.references(reference))


def _filter_candidates(
    candidates: Iterable[tp.Candidate[tp.ContenderId]], *refs: tp.ContenderId
) -> list[tp.Candidate[tp.ContenderId]]:
    return [
        cand for cand in candidates if any(cand.name.matches(ref, tp.GroupBy.ID) for ref in refs)
    ]


def check_event_log(data) -> EventLog:
    """Ensure that a result data is an instance of EventLog."""
    if isinstance(data, EventLog):
        return data
    raise PreconditionError(
        "parallel re-apportionment: the compensatory allocation does not have an event log"
    )


@sr.unserializer("reapportionment", Reapportionment)
def unserialize_reapportionment_dict(data: Mapping[str, Any], cwd: Path | None) -> dict[str, Any]:
    """Unserialize Reapportionment fields."""
    data = ds.unserialize_ballotsnode_dict(data, cwd)
    if (val := data.get("adjustment")) is not None:
        data["adjustment"] = sr.unserialize_node(val, cwd, groupby=True)
    if (val := data.get("first_vote")) is not None:
        data["first_vote"] = sr.unserialize_node(val, cwd, groupby=True)
    if (val := data.get("strategy")) is not None:
        if isinstance(val, str):
            val = val.strip().lower()
        if val != "parallel":
            val = tp.GroupBy.parse(val)
        data["strategy"] = val
    if (val := data.get("relative")) is not None:
        if not val:
            val = None
        else:
            val = RelativeDivisor.parse(val)
        data["relative"] = val
    return data
