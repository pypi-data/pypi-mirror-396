#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Allocation with max seats constraints."""
from __future__ import annotations
from typing import (
    Generic,
    Sequence,
    Collection,
    Mapping,
    Any,
    Iterator,
    Iterable,
    cast,
    NamedTuple,
)
from collections import (
    ChainMap,
    defaultdict,
)
import dataclasses as dt
import warnings

from ..types import (
    AnyName,
    check_seats,
    Allocator,
    CalculationState,
    Result,
    Score,
    Candidate,
    Input,
    PreconditionError,
    Data,
    CandidateFilter,
)
from ...exceptions import PreconditionWarning
from ..filters import (
    ChainCandidateFilter,
)
from ..events import EventLog, Event, SeatsEvent
from .. import inputs as ipt
from .initialseats import InitialSeatsAdapter


@dt.dataclass
class MaxSeatsReachedEvent(Event):
    """Event: max seats reached."""

    EVENT = "max seats reached"
    candidates: Sequence[Candidate]
    "candidates affected by the restriction"
    max_seats: int
    "restriction max seats"


@dt.dataclass
class MaxSeatsResultData(EventLog, Generic[AnyName]):
    """Result data for MaxSeatsAdapter."""

    remaining_seats: int = 0
    remaining_votes: Score = 0
    steps: Sequence[Result[AnyName, EventLog]] = dt.field(default_factory=list)


class MaxVotesFilter(CandidateFilter[AnyName, MaxSeatsReachedEvent]):
    """Candidate filter which excludes candidates that do not meet max seats constraints."""

    def __init__(self, rules: Sequence[tuple[int, Sequence[AnyName]]]):
        """List of max seats `rules`."""
        self.rules = rules
        self._rules = list(rules)
        self._status: dict[AnyName, int] = defaultdict(lambda: 0)
        self._excluded: set[AnyName] = set()

    def start(self) -> Sequence[MaxSeatsReachedEvent]:
        """Initialize this filter.

        Logged events
        -------------
        :class:`.MaxSeatsReachedEvent` when the initial seats of candidates reach
        constraints.
        """
        self._rules = list(self.rules)
        self._status.clear()
        self._excluded.clear()
        # initial check for seats==0
        contenders = {name for _, allies in self._rules for name in allies}
        events: list[MaxSeatsReachedEvent] = []
        for name in contenders:
            events.extend(self.update(Candidate(name=name, votes=0)))
        return events

    def update(self, cand: Candidate[AnyName]) -> Sequence[MaxSeatsReachedEvent]:
        """Update information with new seats added to a candidate."""
        if not self.is_valid(cand.name):
            return []
        events = []
        self._status[cand.name] = cand.seats
        violated = []
        for idx, (max_seats, allies) in enumerate(self._rules):
            if cand.name not in allies:
                continue
            seats = sum(self._status[name] for name in allies)
            if seats >= max_seats:
                self._excluded.update(allies)
                violated.append(idx)
                events.append(
                    MaxSeatsReachedEvent(
                        max_seats=max_seats,
                        candidates=tuple(
                            Candidate(name=name, votes=0, seats=self._status[name])
                            for name in allies
                        ),
                    )
                )
        for idx in reversed(violated):
            self._rules.pop(idx)

        return events

    def is_valid(self, name: AnyName) -> bool:
        """Return True if a candidate is valid (it doesn't have reached its max seats)."""
        return name not in self._excluded

    def exclusion_list(self) -> Collection[AnyName]:
        """Return the current excluded candidates."""
        return self._excluded


class TriggeredRule(NamedTuple):
    """A rule violation."""

    rule_index: int
    rule_seats: int
    assigned_seats: int

    def is_valid(self) -> bool:
        """Return True if the assigned seats are in the allowed range."""
        return self.assigned_seats <= self.rule_seats


Rule = tuple[int, Sequence[AnyName]]
"A max seats rule."


class RuleSet(Generic[AnyName]):
    """A set of max seats rules."""

    @staticmethod
    def validate(constraints: Sequence[Rule]) -> Iterator[Rule]:
        """Check if seats rules complies with alliances definitions.

        Constraints for defining restricted alliances must follow these conditions:

        - A candidate A must have one or none simple rule: A <= seats
        - A candidate A must be in one or none complex rule: A + B + C <= seats
        - If a candidate A verifies (A <= seats1) and (A + B + C <= seats2), seats2
          must be greater or equal than seats1.

        Yields
        ------
        :
            non-empty rules
        """
        simple_rules: dict[AnyName, int] = {}
        complex_rules: set[AnyName] = set()
        for seats, allies in sorted(constraints, key=lambda x: (len(x[1]), x[0])):
            if not allies:
                continue
            if len(allies) > 1:
                for name in allies:
                    if name in complex_rules:
                        raise PreconditionError(
                            f"candidate '{name}' has more than one alliance seats rule"
                        )
                    complex_rules.add(name)
                    if name in simple_rules:
                        if seats < simple_rules[name]:
                            raise PreconditionError(
                                f"alliance rule for candidate '{name}' is stricter"
                                " than the simple rule"
                            )
            else:
                name = allies[0]
                if name in simple_rules:
                    raise PreconditionError(
                        f"candidate '{name}' has more than one candidate seats rule"
                    )
                simple_rules[name] = seats
            yield (seats, allies)

    def __init__(self, constraints: Sequence[Rule], validate: bool = False):
        """Create a max seats rule set.

        Args
        ----
        constraints
            list of rules (<max seats>, [candidate names])
        validate
            if `True`, check if seats rule complies the following conditions:

            - A candidate A must have one or none simple rule: A <= seats
            - A candidate A must be in one or none complex rule: A + B + C <= seats
            - If a candidate A verifies (A <= seats1) and (A + B + C <= seats2),
              seats2 must be greater or equal than seats1.
        """
        self._members: set[AnyName] = set()
        self._items: list[tuple[int, list[AnyName]]] = []
        it_constraints: Iterator[Rule]
        if validate:
            it_constraints = self.validate(constraints)
        else:
            it_constraints = iter(constraints)
        for seats, allies in it_constraints:
            if not allies:
                continue
            self._items.append((seats, list(allies)))
            self._members.update(allies)

        self._items.sort(key=lambda x: (-len(x[1]), x[0]))

    def __getitem__(self, index: int) -> Rule:
        """Return rule at `index`."""
        return self._items[index]

    def __contains__(self, name: AnyName) -> bool:
        """Return True if a candidate name is in any rule."""
        return name in self._members

    def find(self, name: AnyName) -> Rule | None:
        """Find a candidate and return its main rule."""
        if name not in self:
            return None
        for idx, rule in enumerate(self._items):
            if name in rule[-1]:
                return idx, rule
        return None

    def check(
        self, seats: Mapping[AnyName, Candidate[AnyName]]
    ) -> dict[tuple[AnyName, ...], list[TriggeredRule]]:
        """Check if the provided setting violates any rule.

        Return a dictionary with the violated rules.

        (index, rule seats, assigned seats)
        """
        violated: dict[tuple[AnyName, ...], list[TriggeredRule]] = defaultdict(list)
        for idx_rule, (rule_seats, allied) in enumerate(self._items):
            if not allied:
                continue
            assigned = sum(seats[name].seats for name in allied if name in seats)
            if assigned >= rule_seats:
                value = TriggeredRule(idx_rule, rule_seats, assigned)
                if len(allied) > 1:
                    allied_k = tuple(allied)
                else:
                    key = self.find(allied[0])
                    if not key:
                        # insert
                        allied_k = (allied[0],)
                    else:
                        # append
                        _, (_seats, allied_list) = key
                        allied_k = tuple(allied_list)
                violated[allied_k].append(value)
        return violated

    def remove_name(self, name: AnyName, seats: int) -> None:
        """Simplify ruleset by removing a candidate with seats.

        Empty rules are not removed. Invoke :meth:`~RuleSet.compact` explicitly.
        """
        for idx, (rule_seats, alliance) in enumerate(self._items):
            if name not in alliance:
                continue
            alliance.remove(name)
            new_rule_seats = rule_seats - seats
            self._items[idx] = (new_rule_seats, alliance)
        if name in self._members:
            self._members.remove(name)

    def subset(self, index: int, redux: bool) -> Sequence[Rule]:
        """Return a subset with candidates from rule `index`.

        Args
        ----
        index
            rule id from where the valid candidates will be taken as reference
        redux
            exclude rule `index` if True.
        """
        _, valid = self._items[index]
        new_items = []
        for idx, (rule_seats, alliance) in enumerate(self._items):
            if redux and (idx == index):
                continue
            new_alliance = [x for x in alliance if x in valid]
            if not new_alliance:
                continue
            new_items.append((rule_seats, new_alliance))
        return new_items

    def __iter__(self) -> Iterator[Rule]:
        """Return an iterable over non empty rules."""
        for rule in sorted(
            (rule for rule in self._items if rule[1]),
            # more complex rules with lower seats take precedence
            key=lambda x: (-len(x[1]), x[0]),
        ):
            yield (rule[0], tuple(rule[1]))

    def compact(self) -> None:
        """Remove empty rules and sort by length and seats."""
        self._items = sorted(
            (rule for rule in self._items if rule[1]),
            # more complex rules with lower seats take precedence
            key=lambda x: (-len(x[1]), x[0]),
        )


class MaxSeatsAdapter(Allocator[AnyName, Any], Generic[AnyName, Data]):
    """Adapt an allocator ensuring all max seats constraints are met.

    If the inner allocator does not support `filter_f` or `exclude_candidates`,
    the original allocation will be returned.
    """

    def __init__(
        self,
        allocator_f: Allocator[AnyName, Data],
    ):
        """Create an adapter using `allocator_f` as inner allocator."""
        req_input = allocator_f.required_input | Input.SEATS | Input.CONSTRAINTS
        opt_input = allocator_f.optional_input
        if Input.EXCLUDE_CANDIDATES in allocator_f.admitted_input:
            opt_input |= Input.INITIAL_SEATS
        super().__init__(req_input, opt_input)
        self.allocator_f = allocator_f

    def _calc_filter(
        self,
        params: ipt.InputDict[AnyName, Event],
        constraints: Sequence[tuple[int, Sequence[AnyName]]],
    ):
        filter_f: CandidateFilter = MaxVotesFilter(constraints)
        if Input.FILTER_F.param_name in params:
            filter_f = ChainCandidateFilter(params["filter_f"], filter_f)

        params["filter_f"] = filter_f

        return self.allocator_f(**params)

    # FIXME result:
    # FIXME - OriginalData
    # FIXME - maxresultdata
    def _calc_iterative(
        self, seats: int, params: ipt.InputDict[AnyName, Event], constraints: Sequence[Rule]
    ) -> Result[AnyName, EventLog]:
        """Allocation based on exclude_candidates.

        When a rule is violated, non compliant candidates will be included on a new
        partial allocation.
        """
        # ensure initial seats can be skipped
        allocator_f = InitialSeatsAdapter(
            self.allocator_f, min_seats=0, resume_allocation=True, skip_initial_seats=True
        )

        data: MaxSeatsResultData[AnyName] = MaxSeatsResultData()

        params["exclude_candidates"] = list(params.get("exclude_candidates") or [])
        if "skip_initial_seats" in params:
            del params["skip_initial_seats"]

        state = MaxSeatsState(
            rules=RuleSet(constraints, validate=True),
            excluded=list(params["exclude_candidates"]),
        )
        state.initial_seats.update(params.get("initial_seats") or {})

        # import pudb; pu.db

        surplus = max(seats - sum(state.initial_seats.values()), 0)
        first = True
        while first or surplus:
            first = False
            params["exclude_candidates"] = state.excluded_candidates()
            params["initial_seats"] = state.initial_seats.items()
            params["seats"] = surplus
            result = allocator_f(**params)
            state.steps.append(result)

            state.update(result.allocation)

            affected: set[AnyName] = set()
            for alliance, rule_ids in state.triggered_rules().items():
                affected.update(alliance)
                triggered = rule_ids[0]
                if len(alliance) == 1:
                    # add candidate and truncate seats
                    data.log.extend(state.rule_1(triggered, alliance[0]))
                elif triggered.is_valid() and (len(rule_ids) == 1):
                    # x + y + z == N and there is no other dependent rule
                    data.log.extend(state.rule_n_exact(triggered, alliance))
                else:
                    # x + y + z >= N
                    # x <= M (M <= N)
                    data.log.extend(state.rule_n_surplus(self, triggered, alliance, params))

            state.validate_seats(affected)

            if not state.reusable:
                break

            current_surplus = max(seats - sum(state.initial_seats.values()), 0)
            if current_surplus >= surplus:
                break
            surplus = current_surplus

        for name, cand in state.reusable.items():
            if cand.seats:
                data.log.append(SeatsEvent(target=name, seats=cand.seats, criterion="allocation"))
            state.elected.append(cand)

        if (len(state.steps) == 1) and not data.log:
            return state.steps[0]
        data.steps = state.steps
        return state.make_result(state.elected, data)

    def calc(self, seats: int, constraints: ipt.IConstraints, **params):
        """Allocate seats to candidates.

        Args
        ----
        seats
            seats to allocate
        total_votes
            total number of votes
        constraints
            list of max seats rules
        """
        check_seats(seats)

        # a more complex rule with less seats takes priority
        constraints = sorted((c for c in constraints if c[1]), key=lambda x: (-len(x[1]), x[0]))

        if Input.SEATS in self.allocator_f.admitted_input:
            params[Input.SEATS.param_name] = seats

        if not constraints or all(not names for _, names in constraints):
            # no constraints, use original
            return self.allocator_f(**params)

        if Input.FILTER_F in self.allocator_f.admitted_input:
            return self._calc_filter(cast(ipt.InputDict[AnyName, Event], params), constraints)
        if Input.EXCLUDE_CANDIDATES in self.allocator_f.admitted_input:
            return self._calc_iterative(
                seats, cast(ipt.InputDict[AnyName, Event], params), constraints
            )
        if constraints:
            warnings.warn(
                PreconditionWarning(
                    "the allocator is not compatible and the result will ignore "
                    "the provided max seats constraints"
                ),
                stacklevel=2,
            )
        return self.allocator_f(**params)


@dt.dataclass
class MaxSeatsState(CalculationState, Generic[AnyName]):
    """A calculation state for max seats adapter."""

    rules: RuleSet[AnyName]
    elected: list[Candidate[AnyName]] = dt.field(default_factory=list)
    excluded: list[AnyName] = dt.field(default_factory=list)
    initial_seats: dict[AnyName, int] = dt.field(default_factory=lambda: defaultdict(lambda: 0))
    "valid seats already assigned to candidates"
    reusable: dict[AnyName, Candidate[AnyName]] = dt.field(default_factory=dict)
    "provisional seats for non-elected candidates"
    steps: list[Result[AnyName, Any]] = dt.field(default_factory=list)

    def elect_candidate(self, candidate: Candidate[AnyName]) -> None:
        """Set a candidate as elected."""
        self.elected.append(candidate)
        del self.reusable[candidate.name]
        self.initial_seats[candidate.name] = candidate.seats

    def rule_1(self, triggered: TriggeredRule, name: AnyName) -> Iterator[Event]:
        """Treat rules with only 1 element.

        Rules
        -----
        x <= N

        Triggers
        --------
        x = N -> accept and remove from reusable
        x > N -> trim and remove from reusable
        """
        # add candidate and truncate seats
        cand = self.reusable[name]
        yield MaxSeatsReachedEvent(
            candidates=(cand,),
            max_seats=triggered.rule_seats,
        )
        cand = cand.with_seats(triggered.rule_seats)
        yield SeatsEvent(
            target=cand.name,
            seats=triggered.rule_seats,
            criterion="allocation" if triggered.is_valid() else "max_seats_reached",
        )
        self.rules.remove_name(cand.name, triggered.rule_seats)
        self.elect_candidate(cand)

    def rule_n_exact(
        self, triggered: TriggeredRule, alliance: Sequence[AnyName]
    ) -> Iterator[Event]:
        """Treat rules with more than one candidate and no seats surplus.

        Rules
        -----
        x + y + z <= N
        no other dependent rule

        Triggers
        --------
        x + y + z = N -> accept and remove from reusable
        """
        yield MaxSeatsReachedEvent(
            candidates=tuple(self.reusable[name] for name in self.rules[triggered.rule_index][1]),
            max_seats=triggered.rule_seats,
        )
        # self.rules.remove_rule(triggered.rule_index)
        for name in alliance:
            cand = self.reusable[name]
            self.rules.remove_name(name, cand.seats)
            self.elect_candidate(cand)
            if cand.seats:
                yield SeatsEvent(target=cand.name, seats=cand.seats, criterion="allocation")

    def rule_n_surplus(
        self,
        adapter: MaxSeatsAdapter,
        triggered: TriggeredRule,
        alliance: Sequence[AnyName],
        params: ipt.InputDict[AnyName, Event],
    ) -> Iterator[Event]:
        """Treat rules with more than one candidate and seats surplus.

        Rules
        -----
        x + y + z <= N
        x <= A (A <= N)
        y <= B (B <= N)
        z <= C (C <= N)

        Triggers
        --------
        x + y + z >= N -> distribute for (x, y, z) and N seats
        """
        # get a rule subset for alliance
        rule_subset = self.rules.subset(triggered.rule_index, redux=True)
        subset_params = dict(params)
        # emit an event for the trigger
        yield MaxSeatsReachedEvent(
            candidates=tuple(cand for name, cand in self.reusable.items() if name in alliance),
            max_seats=triggered.rule_seats,
        )
        # exclude anyone but the alliance
        subset_exclude: list[AnyName] = [
            name for name, cand in self.reusable.items() if name not in alliance
        ]
        subset_exclude.extend(self.excluded_candidates())
        subset_params["exclude_candidates"] = subset_exclude
        subset_params["initial_seats"] = self.initial_seats.items()
        subset_params["seats"] = triggered.rule_seats - sum(
            self.initial_seats[name] for name in alliance
        )
        subset = adapter(constraints=rule_subset, **subset_params)
        self.steps.append(subset)
        if subset.data and isinstance(subset.data, MaxSeatsResultData):
            yield from subset.data.log
        # this rule and its dependent rules have been resolved
        # self.rules.remove_rule(triggered.rule_index)
        for cand in subset.allocation:
            if cand.seats:
                yield SeatsEvent(
                    target=cand.name, seats=cand.seats, criterion="rule_inner_allocation"
                )
            absolute_cand = cand.add_seats(self.initial_seats[cand.name])
            self.rules.remove_name(cand.name, absolute_cand.seats)
            self.elect_candidate(absolute_cand)
            # self.initial_seats[cand.name] += cand.seats

    def excluded_candidates(self) -> list[AnyName]:
        """Compute a list of excluded candidates.

        A candidate is excluded if it's already elected or in an explicit exclusion list.
        """
        return [c.name for c in self.elected] + self.excluded

    def update(self, allocation: Iterable[Candidate[AnyName]]):
        """Update seats from the last general allocation."""
        self.reusable.clear()
        excluded = self.excluded_candidates()
        for cand in allocation:
            if cand.name in excluded:
                continue
            absolute_cand = cand.add_seats(self.initial_seats[cand.name])
            # initial seats are not updated for cands in rules
            self.reusable[cand.name] = absolute_cand
        self.rules.compact()

    def validate_seats(self, affected: set[AnyName]):
        """Validate seats for non-affected candidates."""
        for name, cand in self.reusable.items():
            if name not in affected:
                self.initial_seats[name] = cand.seats

    def triggered_rules(self) -> dict[tuple[AnyName, ...], list[TriggeredRule]]:
        """Return rules triggered for the new distribution."""
        return self.rules.check(ChainMap(self.reusable, {cand.name: cand for cand in self.elected}))
