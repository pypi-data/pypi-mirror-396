#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Structures and functions to store and manipulate election contenders."""
from __future__ import annotations
from typing import (
    Any,
    Iterable,
    Generator,
    Mapping,
    Sequence,
)
import enum
import json
import dataclasses as dt
from ..types import parse_flag
from ..methods.types import Score
from ..methods.types import Candidate
from ..methods.preferential.types import Preference


__all__ = [
    "GroupBy",
    "ContenderId",
    "Contender",
    "Alliance",
    "merge_candidates",
    "group_candidates",
    "transform_preferences",
    "group_preferences",
]


class GroupBy(enum.Flag):
    """Grouping criterion for contenders transformation."""

    NAME = enum.auto()
    "keep the field `name`"

    ALLIANCE = enum.auto()
    "keep the field `alliance`"

    DISTRICT = enum.auto()
    "get the field `district`"

    ID = NAME | ALLIANCE
    "keep the fields `name` and `alliance`"

    CANDIDATE = ID | DISTRICT
    "keep all the fields"

    ALLIANCE_ID = ALLIANCE | DISTRICT
    "keep the fields `alliance` and `district`"

    def __str__(self) -> str:
        """Return string attribute representation."""
        assert self.name
        return self.name.lower()

    @classmethod
    def parse(cls, text: str | None, sep="+") -> GroupBy | None:
        """Parse GroupBy from string format.

        Examples
        --------
        ``alliance`` -> :attr:`ALLIANCE`

        ``name+district`` -> :attr:`NAME` | :attr:`DISTRICT`
        """
        return parse_flag(cls, text or "", sep=sep)


_MIN_CONTENDER_PARTS = 2


@dt.dataclass(frozen=True, eq=True, order=True)
class ContenderId:
    """Identifier for contenders."""

    name: str
    "contender's name"

    alliance: str
    "collective name for all the contender's allies"

    district: str | None = None
    "district where the contender's candidature is registered or associated to"

    def __contains__(self, other) -> bool:
        """Return `True` if this is equal or a more general definition of `other`'s.

        Examples
        --------
        >>> ContenderId("A", "PARTY", "DISTRICT") in ContenderId("A", "PARTY")
        True
        """
        return (
            isinstance(other, ContenderId)
            and (self.name == other.name)
            and (self.alliance == other.name)
            and ((self.district == other.district) or not self.district)
        )

    def with_district(self, district: str | None, force=False) -> ContenderId:
        """Return this with the specified district.

        If there is already a district, it will not be replaced unless `force` is `True`

        Args
        ----
        district
            new district name
        force
            replace district always (even when the field is not empty)
        """
        if district == self.district:
            return self
        return ContenderId(
            name=self.name,
            alliance=self.alliance,
            district=self.district or district if not force else district,
        )

    def transform(self, required: GroupBy) -> ContenderId:
        """Transform this by removing parts not specified in the required elements.

        Examples
        --------
        >>> ContenderId(
        >>>     "A", "PARTY", "DISTRICT"
        >>> ).transform(GroupBy.ALLIANCE_ID)
        ContenderId(name="PARTY", alliance="DISTRICT", district=None)
        """
        if GroupBy.CANDIDATE in required:
            return self
        parts: list[str | None] = []
        if GroupBy.NAME in required:
            parts.append(self.name)
        if GroupBy.ALLIANCE in required:
            parts.append(self.alliance)
        if GroupBy.DISTRICT in required:
            parts.append(self.district)
        out = [x for x in parts if x is not None]
        del parts
        size = len(out)
        assert size
        if size < _MIN_CONTENDER_PARTS:
            out.append(out[0])
        return ContenderId(*out)

    def matches(self, other: ContenderId, criterion: GroupBy) -> bool:
        """Return `True` if `other` matches this using a given transformation `criterion`.

        Examples
        --------
        >>> ContenderId("A", "PARTY").matches(
        >>>     ContenderId("B", "PARTY"),
        >>>     GroupBy.ALLIANCE
        >>> )
        True
        """
        return self.transform(criterion) == other.transform(criterion)


BLANK_PREFIX = "?"
"prefix for blank votes"

VOID_PREFIX = "!"
"prefix for void/null votes"


def _clean_field(field: str | None) -> str | None:
    return (field or "").strip() or None


@dt.dataclass(frozen=True)
class Contender:
    """Information for a node contender."""

    name: str
    "contender's name"

    alliance: str | None = None
    "contender's alliance id"

    district: str | None = None
    "contender's electoral district"

    votes: Score | None = None
    "contender's votes"

    seats: int | None = None
    "seats the contender won (used mainly for testing)"

    min_seats: int | None = 0
    "minimum number of seats the contender can win"

    max_seats: int | None = None
    "maximum number of seats the contender can win"

    groups: tuple[str, ...] = dt.field(default_factory=tuple)
    "tags for diverse uses"

    meta: dict[str, Any] | None = None
    "a dictionary of additional information"

    @staticmethod
    def from_dict(items: Mapping[str, str | None]) -> Contender:
        """Create a contender from a mapping."""
        row: dict[str, Any] = dict(items)
        groups: tuple[str, ...] = tuple()
        if group := _clean_field(row.pop("group", None)):
            groups = (group,)
        if not isinstance(groups, tuple):
            groups = tuple(groups)
        if meta := row.get("meta", ""):
            if isinstance(meta, str):
                row["meta"] = json.loads(meta)
        for field in ("name", "alliance", "district"):
            if field in row:
                row[field] = (row[field] or "").strip() or None
        for field in ("votes", "seats", "min_seats", "max_seats"):
            if field in row:
                str_value = row[field] or ""
                if isinstance(str_value, str):
                    str_value = str_value.strip() or None
                row[field] = int(str_value) if str_value is not None else None
        return Contender(
            name=row["name"],
            alliance=row.get("alliance"),
            district=row.get("district"),
            votes=row.get("votes"),
            seats=row.get("seats"),
            min_seats=row.get("min_seats"),
            max_seats=row.get("max_seats"),
            groups=groups,
            meta=row.get("meta"),
        )

    @staticmethod
    def make(data: Iterable[Contender | Mapping]) -> list[Contender]:
        """Make contender objects from a sequence of items."""
        out = []
        for item in data:
            if isinstance(item, Contender):
                out.append(item)
            else:
                out.append(Contender.from_dict(item))
        return out

    def get_alliance(self) -> str:
        """Return the alliance id.

        If no alliance is defined, return the contender's name.
        """
        return self.alliance or (self.name if isinstance(self.name, str) else self.name[-1])

    def get_id(self) -> ContenderId:
        """Return the contender id (name, alliance, district)."""
        return ContenderId(self.name, self.get_alliance(), self.district)

    def with_id(self, cid: ContenderId) -> Contender:
        """Return a new contender replacing the contender id."""
        same = (
            (self.name == cid.name)
            and (self.district == cid.district)
            and (self.alliance == cid.alliance or not self.alliance and self.name == cid.alliance)
        )
        if same:
            return self
        alliance = None if cid.name == cid.alliance else cid.alliance
        return dt.replace(self, name=cid.name, alliance=alliance, district=cid.district)

    def add_groups(self, *groups: str) -> Contender:
        """Return a new contender with these `groups`."""
        if not groups:
            return self
        new_groups = frozenset(self.groups).union(groups)
        return dt.replace(self, groups=tuple(new_groups))

    def schema(self) -> Contender:
        """Return a contender without votes and seats."""
        return dt.replace(self, votes=None, seats=None)

    def candidate(self, initial_seats: int | None) -> Candidate[ContenderId]:
        """Return a :class:`.Candidate` object associated to this contender with `initial_seats`."""
        return Candidate(
            name=self.get_id(),
            votes=self.votes or 0,
            seats=self.min_seats or 0 if initial_seats is None else initial_seats,
        )

    def merge(self, other: Contender) -> Contender:
        """Merge this contender with another contender and return it as a new contender."""
        changes: dict[str, Any] = {}
        if self.votes is not None or other.votes is not None:
            changes["votes"] = (self.votes or 0) + (other.votes or 0)
        if self.seats is not None or other.seats is not None:
            changes["seats"] = (self.seats or 0) + (other.seats or 0)
        if self.min_seats is not None or other.min_seats is not None:
            changes["min_seats"] = (self.min_seats or 0) + (other.min_seats or 0)
        if self.max_seats is not None or other.max_seats is not None:
            # FIXME max_seats Inf ¿?
            changes["max_seats"] = (self.max_seats or 0) + (other.max_seats or 0)
        if self.groups or other.groups:
            changes["groups"] = tuple(frozenset(self.groups).union(other.groups))
        if not changes:
            return self
        return dt.replace(self, **changes)

    def is_blank(self) -> bool:
        """Return if this contender is storing blank votes.

        Names for blank votes are prefixed with ``?``
        """
        return self.name.startswith(BLANK_PREFIX)

    def is_void(self) -> bool:
        """Return if this contender is storing void/null votes.

        Names for void votes are prefixed with ``!``
        """
        return self.name.startswith(VOID_PREFIX)

    def is_special(self) -> bool:
        """Return `True` if this is a special contender (blank or void votes)."""
        return self.is_blank() or self.is_void()

    @staticmethod
    def merge_collection(
        batches: Iterable[Iterable[Contender]], by: GroupBy = GroupBy.CANDIDATE
    ) -> list[Contender]:
        """Merge contenders grouped on batches using a name transformation."""
        out = {}
        for batch in batches:
            for cand in batch:
                cid = cand.get_id().transform(by)
                if cid not in out:
                    out[cid] = cand.with_id(cid)
                else:
                    out[cid] = out[cid].merge(cand)

        return list(out.values())

    @classmethod
    def from_candidate(cls, candidate: Candidate[ContenderId], *groups: str) -> Contender:
        """Convert a Candidate object to a Contender."""
        return cls(
            name=candidate.name.name,
            alliance=candidate.name.alliance,
            district=candidate.name.district,
            votes=candidate.votes,
            seats=candidate.seats,
            groups=groups,
        )


@dt.dataclass(frozen=True)
class Alliance:
    """Alliance information."""

    name: str
    "alliance id"

    district: str | None = None
    "alliance district scope"

    max_seats: int | None = None
    "maximum number of seats the members of this allliance can win in `district`."

    groups: tuple[str, ...] = dt.field(default_factory=tuple)
    "tags"

    meta: dict[str, Any] | None = None
    "additional information"

    def merge(self, other: Alliance) -> Alliance:
        """Merge this alliance with another."""
        changes: dict[str, Any] = {}
        if self.max_seats is not None or other.max_seats is not None:
            changes["max_seats"] = (self.max_seats or 0) + (other.max_seats or 0)
        if not changes:
            return self
        return dt.replace(self, **changes)

    @staticmethod
    def make(data: Iterable[Alliance | Mapping]) -> list[Alliance]:
        """Construct a list of alliances from items."""
        out = []
        for item in data:
            if isinstance(item, Alliance):
                out.append(item)
            else:
                out.append(Alliance(**item))
        return out

    def get_id(self) -> ContenderId:
        """Return the alliance ContenderId."""
        return ContenderId(self.name, self.name, self.district)

    def with_id(self, cid: ContenderId) -> Alliance:
        """Return this alliance with a different ContenderId."""
        same = (
            (self.name == cid.name)
            and (self.district == cid.district)
            and (self.name == cid.alliance)
        )
        if same:
            return self
        return dt.replace(self, name=cid.alliance, district=cid.district)

    @staticmethod
    def merge_collection(
        batches: Iterable[Iterable[Alliance]], by: GroupBy | None = None
    ) -> list[Alliance]:
        """Merge a collection of collections of alliances using a name transformation."""
        if by:
            by = by & ~GroupBy.NAME
        cache = {}
        for batch in batches:
            for alli in batch:
                name = alli.get_id()
                if by:
                    name = name.transform(by)
                if name not in cache:
                    cache[name] = alli.with_id(name)
                else:
                    cache[name] = cache[name].merge(alli)

        return list(cache.values())


def merge_candidates(
    contenders: Iterable[Candidate[ContenderId]], groupby: GroupBy | None = None
) -> Generator[Candidate[ContenderId]]:
    """Merge candidates using a name transformation."""
    cache = {}
    for item in contenders:
        name = item.name
        if groupby:
            name = name.transform(groupby)
        if name not in cache:
            cache[name] = item.with_name(name)
        else:
            cache[name] = cache[name].merge(item)
    yield from cache.values()


def group_candidates(
    groupby: GroupBy, groups: Mapping[str, Iterable[Candidate[ContenderId]]]
) -> Generator[Candidate[ContenderId]]:
    """Merge candidates from district mapping using a name transformation.

    If there is only one group, district is omitted.
    """
    add_district = GroupBy.DISTRICT and len(groups) > 1
    contenders = (
        (item.name if not add_district else item.name.with_district(district), item)
        for district, items in groups.items()
        for item in items
    )

    cache = {}
    for name, item in contenders:
        name = name.transform(groupby)
        if name not in cache:
            cache[name] = item.with_name(name)
        else:
            cache[name] = cache[name].merge(item)
    yield from cache.values()


def transform_preferences(
    preferences: Iterable[Preference[ContenderId]],
    by: GroupBy = GroupBy.CANDIDATE,
    district: str | None = None,
) -> Generator[Preference[ContenderId]]:
    """Transform preferences by name and district."""
    mapping: dict[ContenderId, ContenderId] = {}

    def convert(name: ContenderId) -> ContenderId:
        if district:
            name = name.with_district(district)
        if name in mapping:
            return mapping[name]
        new_value = name.transform(by)
        mapping[name] = new_value
        return new_value

    for pref in preferences:
        yield pref.transform(convert)


def group_preferences(
    groups: Sequence[tuple[GroupBy, str, Iterable[Preference[ContenderId]]]],
) -> Generator[Preference[ContenderId]]:
    """Transform preferences using groupby and district.

    Args
    ----
    groups
        (GroupBy, district, preferences)
    """
    # add_district = GroupBy.DISTRICT and len(groups) > 1
    for groupby, district, ballots in groups:
        yield from transform_preferences(
            ballots, groupby, district=district  # if add_district else None
        )
