#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Group of electoral districts."""
from __future__ import annotations
from typing import (
    Iterable,
    Sequence,
    Literal,
    Any,
    Mapping,
)
import dataclasses
from pathlib import Path
from typing_extensions import override

from ..exceptions import PreconditionError
from ..methods.types import Result
from . import node as nd
from .contenders import (
    Contender,
    ContenderId,
    GroupBy,
    group_candidates,
)
from . import serialize as sr
from .references import ReferenceSet


@dataclasses.dataclass
class Group(nd.Node):
    """A group of electoral districts."""

    type: Literal["group"] = "group"
    aggregate: bool = False
    "if True, aggregate children results as this node result"

    groupby: GroupBy | None = None
    "candidate id transformation applied to this node results"

    divisions: Sequence[nd.Node] = dataclasses.field(default_factory=list)
    "list of children nodes"

    def _clear_data(self) -> None:
        pass

    @override
    def get_seats(self) -> Literal[0]:
        """Return 0 (no seats are associated to groups)."""
        return 0

    @override
    def grouping(self) -> GroupBy:
        """Return a grouping criterion for this node (default: :attr:`.GroupBy.CANDIDATE`)."""
        return self.groupby or GroupBy.CANDIDATE

    @override
    def local_candidates(self) -> Literal[None]:
        return None

    @override
    def local_candidates_references(self) -> Literal[False]:
        return False

    @override
    def local_preferences(self, candidates: Iterable[ContenderId]) -> Literal[None]:
        return None

    @override
    def local_preferences_references(self) -> Literal[False]:
        return False

    @override
    def local_alliances(self) -> Literal[None]:
        return None

    @override
    def local_divisions(self) -> Sequence[nd.Node]:
        return self.divisions

    @override
    def __call__(self, context: nd.AllocationContext, local_context: nd.NodeContext):
        if not self.aggregate:
            return
        groupby = self.grouping()
        groups = {}
        ignored = self.ignore_compute_dependency() or []
        for node_id in context.nested_results(self.get_id()):
            if node_id in ignored:
                continue
            node = context.keys[node_id].node
            if not node.result:
                raise PreconditionError(f"node '{node_id}' must produce a result")
            groups[node_id] = node.result.allocation
        self.result = Result(allocation=list(group_candidates(groupby, groups)))

    @override
    def update_candidates(self, candidates: Sequence[Contender]) -> None:
        raise ValueError(f"node {self.get_id()} does not have local candidates.")


@sr.unserializer("group", Group)
def unserialize_group_dict(data: Mapping[str, Any], cwd: Path | None) -> dict[str, Any]:
    """Serialize Group fields."""
    data = nd.NodeContext.unserialize_dict(**data)
    if val := data.get("groupby"):
        data["groupby"] = GroupBy.parse(val)
    divs: list[nd.Node] = []
    for item in data["divisions"]:
        node = sr.unserialize_node(item, cwd)
        assert not isinstance(node, ReferenceSet)
        divs.append(node)
    data["divisions"] = divs
    return data
