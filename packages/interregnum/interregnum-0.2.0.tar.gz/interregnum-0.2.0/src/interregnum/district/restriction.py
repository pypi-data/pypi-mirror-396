#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Restrictions to rule the inclusion or exclusion of candidates."""
from __future__ import annotations
from typing import (
    Iterator,
    TypeVar,
    Mapping,
    Container,
)
import dataclasses as dt
from decimal import Decimal
from fractions import Fraction
from collections import defaultdict
import enum
import re

from ..types import enum_from_string
from ..methods import types as tp
from .. import quotas as qt
from . import contenders as cd
from . import counting as ct
from . import references as rf


__all__ = [
    "Attribute",
    "ContenderStats",
    "NodeStats",
    "Restriction",
    "RestrictionList",
    "AnyRestriction",
    "parse_restrictions",
]

# group -> #nombre
# level -> int
# key ->

# votes
# seats
# districts (quorum) -> district_seats

# any()
# all()


class Attribute(enum.Flag):
    """Restriction attribute.

    Candidates and alliances can be compare against these attributes.
    """

    # source
    COUNTING_ = enum.auto()
    RESULTS_ = enum.auto()
    # contender
    ALLIANCE_ = enum.auto()
    CANDIDATE_ = enum.auto()
    # primary concept
    VOTES_ANY_ = enum.auto()
    VOTES_ = enum.auto()
    VALID_VOTES_ = enum.auto()
    TOTAL_VOTES_ = enum.auto()
    SEATS_ = enum.auto()
    DISTRICTS_ = enum.auto()
    QUORUM_ = enum.auto()
    RANK_ = enum.auto()
    GROUP_ = enum.auto()
    VOTES = COUNTING_ | CANDIDATE_ | VOTES_ANY_ | VOTES_
    """
    **Criterion**
        party votes
    **Total**
        the sum of party votes
    """
    VALID_VOTES = COUNTING_ | CANDIDATE_ | VOTES_ANY_ | VALID_VOTES_
    """
    **Criterion**
        party votes
    **Total**
        the sum of party votes and blank votes
    """
    TOTAL_VOTES = COUNTING_ | CANDIDATE_ | VOTES_ANY_ | TOTAL_VOTES_
    """
    **Criterion**
        party votes
    **Total**
        the sum of party votes, blank votes and void votes
    """
    ALLIANCE_VOTES = COUNTING_ | ALLIANCE_ | VOTES_ANY_ | VOTES_
    """
    **Criterion**
        alliance votes
    **Total**
        the sum of alliance votes
    """
    ALLIANCE_VALID_VOTES = COUNTING_ | ALLIANCE_ | VOTES_ANY_ | VALID_VOTES_
    """
    **Criterion**
        alliance votes
    **Total**
        the sum of alliance votes and blank votes
    """
    ALLIANCE_TOTAL_VOTES = COUNTING_ | ALLIANCE_ | VOTES_ANY_ | TOTAL_VOTES_
    """
    **Criterion**
        alliance votes
    **Total**
        the sum of alliance votes, blank votes and void votes
    """
    SEATS = RESULTS_ | CANDIDATE_ | SEATS_
    """
    **Criterion**
        party seats
    **Total**
        the sum of party seats
    """
    ALLIANCE_SEATS = RESULTS_ | ALLIANCE_ | SEATS_
    """
    **Criterion**
        alliance seats
    **Total**
        the sum of alliance seats
    """
    QUORUM = RESULTS_ | CANDIDATE_ | QUORUM_
    """
    **Criterion**
        party quorum (number of districts where the party won seats)
    **Total**
        number of districts
    """
    ALLIANCE_QUORUM = RESULTS_ | ALLIANCE_ | QUORUM_
    """
    **Criterion**
        alliance quorum (number of districts where the alliance won seats)
    **Total**
        number of districts
    """
    DISTRICTS = COUNTING_ | CANDIDATE_ | DISTRICTS_
    """
    **Criterion**
        number of districts where the party contends
    **Total**
        number of districts
    """
    ALLIANCE_DISTRICTS = COUNTING_ | ALLIANCE_ | DISTRICTS_
    """
    **Criterion**
        number of districts where the alliance contends
    **Total**
        number of districts
    """
    RANK = COUNTING_ | CANDIDATE_ | RANK_
    """
    **Criterion**
        party rank in order of votes
    **Total**
        not applicable
    """
    ALLIANCE_RANK = COUNTING_ | ALLIANCE_ | RANK_
    """
    **Criterion**
        alliance rank in order of votes
    **Total**
        not applicable
    """
    GROUP = COUNTING_ | CANDIDATE_ | GROUP_
    """
    **Criterion**
        the party contains the group tag
    **Total**
        not applicable
    """
    ALLIANCE_GROUP = COUNTING_ | ALLIANCE_ | GROUP_
    """
    **Criterion**
        the alliance contains the group tag
    **Total**
        not applicable
    """

    @classmethod
    def parse(cls, text: str) -> Attribute:
        """Parse value from text."""
        key = enum_from_string(text)
        item: Attribute | None = None
        try:
            item = cls[key]
        except KeyError:
            item = None
        if item and not (item.name or "").endswith("_"):
            return item
        raise ValueError(f"could not parse as a restriction attribute: {text}")

    def requires_results(self) -> bool:
        """Return `True` if this attribute depends on results."""
        return Attribute.RESULTS_ in self

    def __str__(self) -> str:
        """Return string representation."""
        assert self.name
        return self.name.lower()


@dt.dataclass
class ContenderStats:
    """Statistics for contenders used when applying restrictions."""

    votes: tp.Score = 0
    "contender votes"
    seats: int = 0
    "seats won by the contender"
    districts: set[str] = dt.field(default_factory=set)
    "districts where the contender appears"
    quorum: set[str] = dt.field(default_factory=set)
    "districts where the contender won at least one seat"
    rank: int = 0
    "contender rank in order of seats won"

    tags: set[str] = dt.field(default_factory=set)
    "tags or groups associated to the contender"

    def value(self, attribute: Attribute) -> tp.Score:
        """Return the value associated to the `attribute`.

        Raises
        ------
        ValueError
            if the attribute has no numeric value associated to it
        """
        if Attribute.VOTES_ANY_ in attribute:
            return self.votes
        if Attribute.SEATS_ in attribute:
            return self.seats
        if Attribute.DISTRICTS_ in attribute:
            return len(self.districts)
        if Attribute.QUORUM_ in attribute:
            return len(self.quorum)
        if Attribute.RANK_ in attribute:
            return self.rank
        raise ValueError(f"{attribute} is not supported")


T = TypeVar("T")


@dt.dataclass
class NodeStats:
    """Statistics for nodes used when applying restrictions."""

    candidates_votes: tp.Score = 0
    "total votes associated to any candidate"
    valid_votes: tp.Score = 0
    "total valid votes (associated to any candidate or not)"
    total_votes: tp.Score = 0
    "total votes, including invalid or null votes"
    seats: tp.Score = 0
    "total seats allocated by the node"
    districts: set[str] = dt.field(default_factory=set)
    "districts associated to candidates"
    candidates: dict[cd.ContenderId, ContenderStats] = dt.field(
        default_factory=lambda: defaultdict(ContenderStats)
    )
    "candidates statistics"
    alliances: dict[str, ContenderStats] = dt.field(
        default_factory=lambda: defaultdict(ContenderStats)
    )
    "alliances statistics"

    def usable_votes(self, usable: ct.TotalVotes) -> tp.Score:
        """Return usable votes given a criterion.

        Args
        ----
        usable
            criterion of inclusion (valid, invalid, etc...)
        """
        if usable == ct.TotalVotes.VALID_VOTES:
            return self.valid_votes
        if usable == ct.TotalVotes.ALL:
            return self.total_votes
        if usable == ct.TotalVotes.CANDIDATES:
            return self.candidates_votes
        raise ValueError(f"unknown criterion: {usable}")


@dt.dataclass
class Restriction:
    """A non-composite restriction definition.

    String format
    -------------
    .. code-block:: text

        <attribute><opt><threshold>
        <attribute><opt><threshold>%
        <attribute><opt><threshold> => <groupby>
        <attribute><opt><threshold>% => <groupby>
        <target>.<attribute><opt><threshold>
        <target>.<attribute><opt><threshold>%
        <target>.<attribute><opt><threshold> => <groupby>
        <target>.<attribute><opt><threshold>% => <groupby>

    Where:

    ``<attribute>``
        an :class:`.Attribute` value as string (lower or upper-cased)
    ``<opt>``
        an operator (see :class:`~interregnum.quotas.Inequality`)
    ``<threshold>``
        a numeric threshold (it can be a percentage if the attribute supports total),
        or a string if the attribute is `group` or `alliance_group`
    ``<target>``
        a :class:`~.references.Reference` to the nodeset where the restriction is to be computed
    ``<groupby>``
        a transformation expression applied to filtered candidates
        (see :class:`~.contenders.GroupBy`)

    Examples
    --------
    a) Get candidates with at least 5% of the total votes:

        .. code-block:: text

            valid_votes>=5%

    b) Get candidates who won more than 2 seats at Paris district and transform
       their names removing the district name:

        .. code-block:: text

            Paris.alliance_seats>2 => id

    c) Get candidates within the group 'minority':

        .. code-block:: text

            group=minority
    """

    inequality: qt.Inequality
    "(in)equality operator"
    threshold: Decimal
    "reference value for the inequality"
    percentage: bool
    "treat values as percentages"
    target: rf.Reference | None
    "node reference where the attribute is retrieved from"
    attribute: Attribute
    "attribute for retrieving the value to compare"
    groupby: cd.GroupBy = cd.GroupBy.CANDIDATE
    "transformation that will be applied to the filtered candidates"
    tag: str | None = None
    "check that the candidate is associated to this tag instead of doing a numerical comparison"

    def __str__(self) -> str:
        """Return the restriction formatted as as string."""
        val = f"{self.attribute if not self.tag else 'group'} {self.inequality} {self.threshold}"
        if self.percentage:
            val = val + "%"
        if self.target:
            val = f"{self.target}.{val}"
        if self.groupby != cd.GroupBy.CANDIDATE:
            val = f"{val} => {self.groupby}"
        return val

    def walk(self) -> Iterator[Restriction]:
        """Yield this restriction.

        Yields
        ------
        self
        """
        yield self

    def dependencies(self) -> Iterator[tuple[rf.Reference | None, Attribute]]:
        """Iterate over dependencies on targets and attributes.

        Yields
        ------
        (target reference, attribute)
        """
        yield (self.target, self.attribute)

    def check_any(self, target: rf.Reference | None, ref: str, attribute: Attribute) -> bool:
        """Check if this restriction depends on `target` and `attribute`.

        If the restriction has no target, use `ref` instead.
        """
        return target in (self.target, ref) and attribute in self.attribute

    def _resolve_threshold(
        self, context: Mapping[rf.Reference | None, NodeStats]
    ) -> set[cd.ContenderId]:
        stats = context[self.target]
        # resolve threshold
        threshold = Fraction(self.threshold)

        if self.percentage:
            if Attribute.VOTES_ in self.attribute:
                total = stats.candidates_votes
            elif Attribute.VALID_VOTES_ in self.attribute:
                total = stats.valid_votes
            elif Attribute.TOTAL_VOTES_ in self.attribute:
                total = stats.total_votes
            elif Attribute.SEATS_ in self.attribute:
                total = stats.seats
            elif Attribute.QUORUM_ in self.attribute:
                total = len(stats.districts)
            elif Attribute.DISTRICTS_ in self.attribute:
                total = len(stats.districts)
            else:
                raise ValueError(f"{self.attribute} could not be resolved using a percentage")

            threshold = threshold * total / 100

        if Attribute.CANDIDATE_ in self.attribute:
            return {
                cand_id.transform(self.groupby)
                for cand_id, cont in stats.candidates.items()
                if self.inequality(cont.value(self.attribute), threshold)
            }
        if Attribute.ALLIANCE_ in self.attribute:
            out = set()
            for cand_id, _cont in stats.candidates.items():
                alli = stats.alliances[cand_id.alliance]
                if self.inequality(alli.value(self.attribute), threshold):
                    out.add(cand_id.transform(self.groupby))
            return out

        raise ValueError(f"{self.attribute} could not be resolved")

    def resolve(self, context: Mapping[rf.Reference | None, NodeStats]) -> set[cd.ContenderId]:
        """Resolve this restriction for a context and return the compliant contenders.

        Args
        ----
        context
            A context composed of statistics computed for nodes.
            It should contain stats for each possible node.

        Raises
        ------
        ValueError
            When the operator does not support the threshold or when the attribute
            could not be resolved for the context

        Return
        ------
        :
            The set of filtered contenders ids
        """
        stats = context[self.target]
        if Attribute.GROUP_ not in self.attribute:
            return self._resolve_threshold(context)

        if self.inequality == qt.Inequality.EQ:

            def operator(tags: Container[str]) -> bool:
                return self.tag in tags

        elif self.inequality == qt.Inequality.NE:

            def operator(tags: Container[str]) -> bool:
                return self.tag not in tags

        else:
            raise ValueError(f"operator {self.inequality} not supported for groups")

        if Attribute.CANDIDATE_ in self.attribute:
            return {
                cand_id.transform(self.groupby)
                for cand_id, cont in stats.candidates.items()
                if operator(cont.tags)
            }
        if Attribute.ALLIANCE_ in self.attribute:
            out = set()
            for cand_id, _cont in stats.candidates.items():
                alli = stats.alliances[cand_id.alliance]
                if operator(alli.tags):
                    out.add(cand_id.transform(self.groupby))
            return out
        raise ValueError(f"{self.attribute} could not be resolved")


@dt.dataclass
class RestrictionList:
    """A set of conjunctive or disjunctive restriction clauses.

    String formats
    --------------
    a) conjunctive: get every candidate returned by any of these restrictions

        .. code-block:: text

            any{<restriction 1>|...|<restriction N>}

    b) disjunctive: get candidates if they are returned by all of these restrictions

        .. code-block:: text

            all{<restriction 1>|...!<restriction N>}
    """

    items: list[AnyRestriction]
    "list of restrictions"
    disjunctive: bool = False
    "`True` for disjunctive, `False` for conjunctive"

    def __str__(self) -> str:
        """Return the restrictions list formatted as as string."""
        prefix = "all" if self.disjunctive else "any"
        items = "|".join(str(x) for x in self.items)
        return f"{prefix}{{{items}}}"

    def walk(self) -> Iterator[Restriction]:
        """Recursively iterate all restrictions in this list."""
        for item in self.items:
            yield from item.walk()

    def dependencies(self) -> Iterator[tuple[rf.Reference | None, Attribute]]:
        """Iterate dependencies on nodes and attributes."""
        for item in self.items:
            yield from item.dependencies()

    def check_any(self, target: rf.Reference | None, ref: str, attribute: Attribute) -> bool:
        """Check if this restriction depends on `target` and `attribute`.

        If the restriction has no target, use `ref` instead.
        """
        return any(r.check_any(target, ref, attribute) for r in self.items)

    def resolve(self, context: Mapping[rf.Reference | None, NodeStats]) -> set[cd.ContenderId]:
        """Resolve this restriction for a context and return the compliant contenders.

        Args
        ----
        context
            A context composed of statistics computed for nodes.
            It should contain stats for each possible node.

        Raises
        ------
        ValueError
            When the operator does not support the threshold or when the attribute
            could not be resolved for the context

        Return
        ------
        :
            The set of filtered contenders ids
        """
        parts = (x.resolve(context) for x in self.items)
        return set.union(*parts) if self.disjunctive else set.intersection(*parts)


AnyRestriction = Restriction | RestrictionList


_RX_RT = re.compile(
    r"\s*(?:(?P<TARGET>[^\|\{\}]+)\.)?(?P<ATTR>"
    r"(?:alliance_)?(?:valid_|total_)?votes"
    r"|(?:alliance_)?seats"
    r"|(?:alliance_)?quorum"
    r"|(?:alliance_)?districts"
    r"|(?:alliance_)?rank"
    r"|(?:alliance_)?group"
    r")\s*(?P<EQ>\>\=?|\<\=?|\!?==?|\<\>)\s*(?P<VAL>(?:\d+%?|[^\s=]+))"
    r"(?:\s+\=\>\s*(?P<GROUPBY>\w+(?:\s*\+\s*\w+)*))?"
)


def _parse_single(text: str) -> tuple[Restriction | None, str]:
    match_ = _RX_RT.match(text.strip())
    if not match_:
        return None, text
    end = match_.end(0)
    value = match_.group("VAL")
    target = match_.group("TARGET")
    attr = Attribute.parse(match_.group("ATTR"))
    out = Restriction(
        target=rf.Reference.parse_one(target.strip()) if target else None,
        attribute=attr,
        inequality=qt.Inequality.parse(match_.group("EQ")),
        threshold=Decimal(value.rstrip("%")) if Attribute.GROUP_ not in attr else Decimal(0),
        tag=value.strip() if Attribute.GROUP_ in attr else None,
        percentage=value.endswith("%"),
        groupby=cd.GroupBy.parse(match_.group("GROUPBY")) or cd.GroupBy.CANDIDATE,
    )
    return out, text[end:]


def _parse_list(text: str) -> tuple[list[AnyRestriction], str]:
    """Parse one restriction from a restriction list.

    <restriction>|...|<restriction>

    Return (AnyRestriction, rest of string expressions).
    """
    rest = text.strip()
    out: list[AnyRestriction] = []
    item: AnyRestriction | None
    while True:
        item, rest = _parse_group(rest)
        if not item:
            item, rest = _parse_single(rest)
        if item:
            out.append(item)
        rest = rest.strip()
        if not rest.startswith("|"):
            break
        rest = rest[1:].strip()
    return out, rest


def _parse_group(text: str) -> tuple[RestrictionList | None, str]:
    """Parse one group of restrictions from a restriction list.

    any(...)
    all(...)

    Return (RestrictionList, rest of string expressions).
    """
    rest = text.strip()
    prefix = text[:4].strip().lower()
    if prefix not in ("any{", "all{"):
        return None, rest
    rest = text[4:]
    items, rest = _parse_list(rest)
    rest = rest.strip()
    if items and rest.startswith("}"):
        return RestrictionList(items=items, disjunctive=prefix.startswith("any")), rest[1:]
    return None, rest


def parse_restrictions(text: str) -> Restriction | RestrictionList:
    """Parse restrictions from string expressions."""
    group, rest = _parse_group(text)
    if group:
        if rest.strip():
            raise ValueError("Cannot parse restrictions")
        return group
    item, rest = _parse_single(text)
    if not item or rest.strip():
        raise ValueError("Cannot parse restrictions")
    return item
