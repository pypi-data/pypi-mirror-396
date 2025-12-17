#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""References to nodes."""
from __future__ import annotations
from typing import (
    Iterator,
    Generator,
    TypeVar,
    Generic,
    Sequence,
)
import dataclasses as dt
from .contenders import GroupBy

__all__ = [
    "parse_reference",
    "Reference",
    "GroupableReference",
    "ReferenceSet",
    "unserialize_reference",
    "unserialize_groupable_reference",
]


def parse_reference(text: str) -> tuple[str | None, int | None]:
    """Parse a single reference from `text`.

    Args
    ----
    text
        A text reference expression, following the format:

        .. code-block:: text

            <node>
            #<group>
            <node>:<level>
            #<group>:<level>

        Where ``<node>`` is a node id, ``<group>`` is a group tag, and ``<level>`` is the
        offset from the level of ``<node>`` or ``<group>``. Level can be positive
        (counting from start) or negative (counting from leaves).

    Return
    ------
    :
        (``<node>`` or ``<group>``, ``<level>``)
    """
    ref: str | None = None
    level: int | None = None
    text = text.strip()
    if ":" in text:
        level_str: str | None
        ref, _, level_str = text.rpartition(":")
        ref = ref.strip()
        level_str = level_str.strip() or None
        if level_str is not None:
            level = int(level_str)
        if not ref and level:
            ref, level = level_str, None
    else:
        ref = text
    return ref, level


@dt.dataclass(frozen=True)
class Reference:
    """A reference to a node or a set of nodes.

    Examples
    --------
    a) Point to node 'Cádiz':

        >>> Reference("Cádiz")

    b) Use 'Andalucía' as reference, and get its direct child nodes:

        >>> Reference("Andalucía", 1)

    c) Use 'Andalucía' as reference, and get its leaf nodes:

        >>> Reference("Andalucía", -1)

    d) Point to any node in the group 'constituency':

        >>> Reference("#constituency")
    """

    ref: str | None = None
    "Node or group of nodes"

    level: int | None = None
    "Numerical offset counting from :attr:`ref` (level=0). Can be positive or negative"

    def __str__(self) -> str:
        """Return as a formatted string."""
        if self.ref and self.level is not None:
            return f"{self.ref}:{self.level}"
        return f"{self.ref or self.level}"

    @classmethod
    def parse(cls, text: str) -> Generator[Reference]:
        """Iterate references separated by ``|`` in `text`.

        Args
        ----
        text
            text references expression: references parseables by
            :func:`parse_reference` separated by ``|``.

        Examples
        --------
        Input examples:

        .. code-block:: text

            node
            node:<level>
            #group
            #group:<level>
            node:<level>|#group:<level>
        """
        seen = set()
        if not text:
            return
        for part in text.split("|"):
            ref_str, level = parse_reference(part)
            if not ref_str:
                continue
            ref = Reference(ref_str, level)
            if ref:
                part = str(ref)
                if part not in seen:
                    yield ref
                    seen.add(part)

    @classmethod
    def parse_one(cls, text: str) -> Reference:
        """Parse one reference from `text`.

        Args
        ----
        text
            references expression: references parseables by
            :func:`parse_reference` separated by ``|``.

        Examples
        --------
        Input examples:

        .. code-block:: text

            node
            node:<level>
            #group
            #group:<level>
            node:<level>|#group:<level>

        Raises
        ------
        ValueError
            when `text` could not be parsed
        """
        ref_str, level = parse_reference(text)
        if not ref_str:
            raise ValueError(f"could not parse as a reference: {text}")
        return Reference(ref_str, level)


@dt.dataclass(frozen=True)
class GroupableReference(Reference):
    """A reference with an associated grouping criterion."""

    groupby: GroupBy = GroupBy.CANDIDATE
    "Candidate name transformation"

    def __str__(self) -> str:
        """Return a groupable reference in string format."""
        body = super().__str__()
        if self.groupby != GroupBy.CANDIDATE:
            body = f"{self.groupby}[{body}]"
        return body

    @classmethod
    def parse_item(cls, text: str) -> GroupableReference | None:
        """Parse a groupable reference from `text`.

        Args
        ----
        text
            reference expression with the following format:

            .. code-block: text

                <groupby>[<reference>]
                <reference>

        Raises
        ------
        ValueError
            when `text` could not be parsed

        Examples
        --------
        Get candidates from leaf nodes in Calabria and transform them to get only their alliance id.

        .. code-block:: text

            alliance[Calabria:-1]


        Get candidates identified by name and district from constituencies.

        .. code-block:: text

            name+district[#constituencies]

        Get candidates from constituencies without any transformation.

        .. code-block:: text

            #constituencies
        """
        text = text.strip()
        if text.endswith("]") and "[" in text:
            group, _, text = text[:-1].partition("[")
            groupby = GroupBy.parse(group) or GroupBy.CANDIDATE
        else:
            groupby = GroupBy.CANDIDATE
        ref, level = parse_reference(text)
        if not ref:
            return None
        return cls(ref, level, groupby)

    @classmethod
    def parse(cls, text: str) -> Generator[GroupableReference]:
        """Iterate groupable references separated by ``|`` in `text`.

        Args
        ----
        text
            a references expression

        Raises
        ------
        ValueError
            when `text` could not be parsed
        """
        seen = set()
        if not text:
            return
        for part in text.split("|"):
            ref = cls.parse_item(part)
            if not ref:
                continue
            if ref:
                part = str(ref)
                if part not in seen:
                    yield ref
                    seen.add(part)


_Ref = TypeVar("_Ref", bound=Reference)


@dt.dataclass
class ReferenceSet(Generic[_Ref]):
    """An iterable reference set."""

    references: Sequence[_Ref] = dt.field(default_factory=list)
    "list of references"

    def __iter__(self) -> Iterator[_Ref]:
        """Iterate references."""
        return iter(self.references)

    def __str__(self) -> str:
        """Return the reference set as a text expression."""
        return "|".join(str(x) for x in self.references)


def unserialize_reference(node: dict | str) -> ReferenceSet[Reference]:
    """Unserialize a reference set from a string or a mapping."""
    if isinstance(node, str):
        return ReferenceSet(list(Reference.parse(node)))
    return ReferenceSet([Reference(**x) for x in node])


def unserialize_groupable_reference(node: dict | str) -> ReferenceSet[GroupableReference]:
    """Unserialize a groupable reference set from a string or a mapping."""
    if isinstance(node, str):
        return ReferenceSet(list(GroupableReference.parse(node)))
    return ReferenceSet([GroupableReference(**x) for x in node])
