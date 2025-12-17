#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Serialization tools."""
from __future__ import annotations
from typing import (
    Mapping,
    Callable,
    Any,
)
from fractions import Fraction
from pathlib import Path
import dataclasses as dt
from collections import defaultdict

from ..methods import events as evt
from . import node as nd
from . import references as rf
from . import counting as ct
from . import restriction as rst
from . import io
from . import contenders as cd


DictHandler = Callable[[Mapping[str, Any], Path | None], dict[str, Any]]
NodeFactory = Callable[..., nd.Node]


def serialize_fraction(obj: Fraction, decimals: int | None) -> str | int:
    """Serialize fraction as a string or an integer.

    Args
    ----
    obj
        a :class:`Fraction`
    decimals
        number of decimals `obj` will be rounded to
    """
    if obj.denominator == 1:
        return obj.numerator
    if decimals is None:
        return format(obj)
    div = round(obj.numerator / obj.denominator, decimals + 1)
    fmt = f".{decimals}f"
    return format(div, fmt)


_dict_unserializers: dict[str, tuple[NodeFactory, DictHandler]] = {}
_serializers: dict[type, Callable[[Any], Any]] = {
    rf.Reference: str,
    rf.ReferenceSet: str,
    rst.Restriction: str,
    rst.RestrictionList: str,
    ct.TotalVotes: str,
    ct.InitialSeatsSource: str,
    cd.GroupBy: str,
    Path: str,
}


def serialize_to_str(obj) -> str:
    """Serialize anything to a string."""
    return str(obj)


def unserializer(key: str, factory: NodeFactory) -> Callable[[DictHandler], DictHandler]:
    """Register node unserializers.

    Used as a decorator.

    Args
    ----
    key
        node type
    factory
        factory function for creating that type of node
    """

    def decorator(func: DictHandler) -> DictHandler:
        _dict_unserializers[key] = (factory, func)
        return func

    return decorator


def serializer(*object_types: type):
    """Register a function as a serializer (decorator)."""

    def decorator(func: Callable[[Any], Any]):
        for otype in object_types:
            _serializers[otype] = func
        return func

    return decorator


def unserialize_dict(kwargs: Mapping[str, Any], cwd: Path | None) -> dict[str, Any]:
    """Unserialize node fields from a mapping.

    Args
    ----
    cwd
        working directory for opening files
    """
    type_ = kwargs.get("type", "district")
    return _dict_unserializers[type_][1](kwargs, cwd)


def unserialize_node(
    data: Mapping[str, Any] | str, cwd: Path | None, groupby: bool = False
) -> nd.Node | rf.ReferenceSet:
    """Convert a mapping to a node.

    The field ``fill_candidates`` will be interpreted as
    a :class:`~.io.CandidatesFile` and rows
    will be injected to nodes.

    Args
    ----
    data
        source data: if `data` is a string instead of a mapping, a reference will be returned
    cwd
        working directory. Used by file readers.
    groupby
        use :class:`.GroupableReference` instead of :class:`.Reference`
    """
    if isinstance(data, str):
        return (
            rf.unserialize_groupable_reference(data) if groupby else rf.unserialize_reference(data)
        )
    type_ = data.get("type", "district")
    fill_candidates: io.CandidatesFile | None = None
    if "fill_candidates" in data:
        data = dict(data)
        fill_candidates = io.CandidatesFile(**data.pop("fill_candidates"), cwd=cwd)
    factory, handler = _dict_unserializers[type_]
    args = handler(data, cwd)
    node = factory(**args)
    if fill_candidates:
        fill_node_candidates(node, fill_candidates)
    return node


def to_serializable(data, decimals: int | None):
    """Serialize objects.

    Args
    ----
    decimals
        rounding precision
    """
    for key, converter in _serializers.items():
        if isinstance(data, key):
            return converter(data)
    if isinstance(data, Fraction):
        return serialize_fraction(data, decimals)
    if isinstance(data, evt.Event):
        data = _serialize_event(data)
    elif dt.is_dataclass(data):
        data = _serialize_dataclass(data)
    if isinstance(data, Mapping):
        return {to_serializable(k, decimals): to_serializable(v, decimals) for k, v in data.items()}
    if isinstance(data, (list, tuple, set, frozenset)):
        return [to_serializable(v, decimals) for v in data]
    return data


def _serialize_dataclass(data) -> dict:
    return {
        field.name: getattr(data, field.name)
        for field in dt.fields(data)
        if not field.name.startswith("_") and getattr(data, field.name) is not None
    }


def _serialize_event(data: evt.Event) -> dict:
    out = {"EVENT": data.EVENT}
    out.update(_serialize_dataclass(data))
    return out


def fill_node_candidates(node: nd.Node, data: io.CandidatesFile) -> None:
    """Populate nodes with lists of candidates read from file.

    Args
    ----
    node
        root node
    """
    ignore = set()
    sequences = defaultdict(list)
    nodes = {}
    for target_id, contender in data():
        if target_id in ignore:
            continue
        if target_id not in nodes:
            target = node.find_district(target_id or node.get_id())
            if not target:
                ignore.add(target_id)
                continue
            nodes[target_id] = target
        sequences[target_id].append(contender)

    for target_id, sequence in sequences.items():
        nodes[target_id].update_candidates(sequence)
