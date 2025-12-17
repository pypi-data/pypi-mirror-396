#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Information for districts or constituencies."""

from __future__ import annotations
from typing import (
    Any,
    Sequence,
    Iterator,
    Iterable,
    Callable,
    Generator,
    Mapping,
    TypeVar,
    ClassVar,
    Union,
)
import itertools
from functools import partial
from collections import defaultdict
import dataclasses as dt

from ..dfs import depth_first_search
from ..exceptions import PreconditionError
from ..methods.preferential.types import Preference
from ..methods import allocators
from ..methods.types import (
    Result,
    Allocator,
    Candidate,
)
from . import restriction as rst
from .counting import (
    Votes,
    TotalVotes,
    Ballots,
    InitialSeatsSource,
)
from .contenders import (
    Contender,
    GroupBy,
    Alliance,
    merge_candidates,
    group_candidates,
    group_preferences,
    ContenderId,
)
from .references import (
    Reference,
    GroupableReference,
    ReferenceSet,
)

from ..logging import logger


__all__ = [
    # "merge_preferences",
    "NodeContext",
    "NodeOffset",
    "Node",
    "AllocationContext",
    "MethodDef",
]


MethodDef = Union[str, Callable[..., Allocator]]
"a method definition"


T = TypeVar("T")


def _merge_field(this: T | None, parent: T | None) -> T | None:
    """Use this value, or parent value in case this is None."""
    if this is None:
        return parent
    return this


def _apply_alliances(contenders: Ballots, alliances: Sequence[Alliance] | None) -> Ballots:
    if not contenders.ballots or not alliances:
        return contenders
    allis = {a.name: a for a in alliances if a.groups}
    out = []
    for cont in contenders.ballots:
        if cont.get_alliance() in allis:
            out.append(cont.add_groups(*allis[cont.get_alliance()].groups))
        else:
            out.append(cont)
    return dt.replace(contenders, ballots=out)


@dt.dataclass(kw_only=True)
class NodeContext:
    """Inherited node context.

    Set of attributes inherited from parent context.

    If a node defines any of these attribute, the own node attribute is used.
    Otherwise, the inherited value for the attribute from parents is used.
    """

    total_votes: TotalVotes | None = None
    "how to calculate total votes"

    resume_allocation: bool | None = None
    "resume allocation from the initial seats"

    skip_initial_seats: bool | None = None
    "add initial seats to result"

    exclude: rst.RestrictionList | None = None
    "rules for excluding contenders from allocation"

    include: rst.RestrictionList | None = None
    """rules for including contenders in allocation (even if the contender
    is present in the exclusion list)"""

    initial_seats: int | InitialSeatsSource = InitialSeatsSource.MIN_SEATS
    "how to calculate total votes"

    method: MethodDef | None = None
    "allocation method"

    method_params: dict[str, Any] | None = None
    "arguments for the allocation method (only used if method is defined in the same node)"

    random_seed: int | None = None
    "random number generator seed passed to allocators"

    @staticmethod
    def unserialize_dict(**data) -> dict:
        """Unserialize a node context attributes from arguments."""
        if val := data.get("total_votes"):
            data["total_votes"] = TotalVotes.parse(val)
        if val := data.get("exclude"):
            data["exclude"] = rst.parse_restrictions(val)
        if val := data.get("include"):
            data["include"] = rst.parse_restrictions(val)
        val = data.get("initial_seats") or InitialSeatsSource.MIN_SEATS
        try:
            data["initial_seats"] = InitialSeatsSource.parse(val)
        except ValueError:
            assert not isinstance(val, InitialSeatsSource)
            data["initial_seats"] = int(val)
        return data

    def get_method(self) -> Callable[[], Allocator] | None:
        """Resolve method and return an allocator factory."""
        if not self.method:
            return None
        func = allocators.get(self.method)
        if not self.method_params:
            return func
        return partial(func, **self.method_params)

    def merge_context(self, parent: NodeContext) -> NodeContext:
        """Merge this context with the parent context.

        Local values will take precedence, and it will use the parent
        value as a fallback value.
        """
        changes: dict[str, Any] = {
            "total_votes": _merge_field(self.total_votes, parent.total_votes),
            "resume_allocation": _merge_field(self.resume_allocation, parent.resume_allocation),
            "exclude": _merge_field(self.exclude, parent.exclude),
            "include": _merge_field(self.include, parent.include),
            "initial_seats": _merge_field(self.initial_seats, parent.initial_seats),
            "random_seed": _merge_field(self.random_seed, parent.random_seed),
            "skip_initial_seats": _merge_field(self.skip_initial_seats, parent.skip_initial_seats),
        }
        changes = {k: v for k, v in changes.items() if v is not None}
        if self.method is not None:
            changes["method"] = self.method
            changes["method_params"] = self.method_params
        elif parent.method is not None:
            changes["method"] = parent.method
            changes["method_params"] = parent.method_params
        if changes:
            return NodeContext(**changes)
        return self


@dt.dataclass
class NodeOffset:
    """Location offset of a node from the root tree."""

    key: str
    "node key"

    level: int
    "positive offset from the root"

    reverse_level: int
    "negative offset from the leaf"

    context: NodeContext
    "computed node context"

    node: Node
    "node reference"

    @classmethod
    def walk(cls, node: Node, parent_level=-1) -> Iterator[NodeOffset]:
        """Walk nodes from `node`.

        Args
        ----
        parent_level
            parent's computed root offset
        """
        root = cls(
            key=node.get_id(), level=parent_level + 1, reverse_level=-1, context=node, node=node
        )
        leaf = True
        for division in node.local_children():
            for child in cls.walk(division, root.level):
                child.context = child.context.merge_context(root.context)
                yield child
                root.reverse_level = min(root.reverse_level, child.reverse_level)
                leaf = False
        if not leaf:
            root.reverse_level -= 1
        yield root


@dt.dataclass
class Node(NodeContext):
    """An electoral node.

    A node represents an allocation unit in an electoral system.
    """

    _cseq_id: ClassVar[int] = 0
    type: str

    name: str | None = None
    "type of node"

    key: str | None = None
    "human readable node name (must be unique)"

    _: dt.KW_ONLY

    groups: Sequence[str] | None = None
    "tags useful for finding node groups"

    result: Result[ContenderId, Any] | None = None
    "allocation result"

    max_adjustment_seats: int | None = None
    """maximum number of additional seats this node can win in systems with
    adjustment seats (such as levelling seats or mixed-member systems)"""

    ignore: Sequence[str] | None = None
    "ignore these node when computing dependencies on results"

    map_districts: Mapping[str | None, str | None] | None = None
    "map for changing district names when collecting candidates"

    meta: dict[str, Any] | None = None
    "additional data"

    _seq_id: int = dt.field(init=False)

    def clear_data(self) -> None:
        """Clear results, ballots and meta."""
        self.result = None
        self.meta = None
        self._clear_data()
        for node in self.local_children():
            node.clear_data()

    def _clear_data(self) -> None:
        """Clear results and ballots in this node."""
        raise NotImplementedError()

    def __post_init__(self):
        """Update sequential id."""
        self._seq_id = self._cseq_id
        self._cseq_id += 1

    def get_id(self) -> str:
        """Return a unique identifier for this node.

        If a key is present, use it.
        Otherwise, use name or return a generated id.
        """
        return self.key or self.name or f"__node_{self._seq_id}"

    def grouping(self) -> GroupBy:
        """Return a grouping criterion for this node."""
        raise NotImplementedError()

    def get_seats(self) -> int | ReferenceSet[GroupableReference]:
        """Return seats to allocate."""
        raise NotImplementedError()

    def local_candidates(self) -> Ballots | ReferenceSet[GroupableReference] | None:
        """Return node local candidates or None."""
        raise NotImplementedError()

    def local_candidates_references(self) -> ReferenceSet[GroupableReference] | bool:
        """Return references to local candidates defined elsewhere.

        If no references but local candidates exist, return True
        """
        raise NotImplementedError()

    def local_preferences(
        self, candidates: Iterable[ContenderId]
    ) -> Iterator[Preference[ContenderId]] | ReferenceSet[GroupableReference] | None:
        """Return node local preferential votes or None."""
        raise NotImplementedError()

    def local_preferences_references(self) -> ReferenceSet[GroupableReference] | bool:
        """Return references to local preferences defined elsewhere.

        If no references but local preferences exist, return True
        """
        raise NotImplementedError()

    def local_alliances(self) -> Sequence[Alliance] | ReferenceSet[GroupableReference] | None:
        """Return node alliances or None."""
        raise NotImplementedError()

    def local_divisions(self) -> Sequence[Node | Reference] | None:
        """Return node divisions or None."""
        raise NotImplementedError()

    def local_children(self) -> Iterator[Node]:
        """Return local divisions that are not references."""
        for child in self.local_divisions() or []:
            if not isinstance(child, Node):
                continue
            yield child

    def __iter__(self) -> Iterator[NodeOffset]:
        """Iterate district keys and indices.

        yield NodeOffset
        """
        yield from NodeOffset.walk(self)

    def iter_leaves(self) -> Iterator[Node]:
        """Iterate leaf nodes."""
        if not (divisions := self.local_divisions()):
            yield self
        else:
            for child in divisions:
                if not isinstance(child, Node):
                    continue
                yield from child.iter_leaves()

    def build(self) -> AllocationContext:
        """Build an allocation context."""
        return AllocationContext.build(self)

    def calculate(self) -> None:
        """Build an allocation context from this node and calculate."""
        self.build()()

    def __call__(self, context: AllocationContext, local_context: NodeContext):
        """Compute allocation for this tree given a context."""
        raise NotImplementedError()

    def find_district(self, district_id: str) -> Node | None:
        """Find a district by identifier and return a reference to it.

        District(id) or None
        """
        if district_id == self.get_id():
            return self
        if divisions := self.local_children():
            for child in divisions:
                out = child.find_district(district_id)
                if out:
                    return out
        return None

    def find_level(self, level: int) -> Iterator[Node]:
        """Iterate nodes at a given level from this node.

        Positive levels will look levels from this node.
        Negative levels will look levels from a leaf node.
        """
        if level < 0:
            yield from self._find_reverse_level(level)
            return
        if level == 0:
            yield self
            return
        for child in self.local_children():
            yield from child.find_level(level - 1)

    def _find_reverse_level(self, level: int) -> Iterator[Node]:
        for info in self:
            if info.reverse_level == level:
                yield info.node

    def ignore_compute_dependency(self) -> Sequence[str] | None:
        """Ignore these nodes when computing result."""
        return self.ignore

    def update_candidates(self, candidates: Sequence[Contender]) -> None:
        """Set these candidates as local candidates."""
        raise NotImplementedError()

    def transform_contender(self, contender: Contender) -> Contender:
        """Transform `contender` using the district mapping."""
        if self.map_districts and (contender.district in self.map_districts):
            return dt.replace(contender, district=self.map_districts[contender.district])
        return contender

    def transform_contender_id(self, contender_id: ContenderId) -> ContenderId:
        """Transform `contender_id` using the district mapping."""
        if self.map_districts and (contender_id.district in self.map_districts):
            return contender_id.with_district(self.map_districts[contender_id.district], force=True)
        return contender_id


@dt.dataclass(frozen=True)
class AllocationContext:
    """An electoral system allocation context.

    It stores information needed to access all data required at each step.
    """

    root: str
    "root node id"

    keys: Mapping[str, NodeOffset]
    "mapping of node ids and node offsets"

    groups: Mapping[str, set[str]]
    "translation of groups to sets of node ids"

    cand_cache: dict[str, Ballots] = dt.field(default_factory=dict)
    "cache for computed candidates at each node"

    alli_cache: dict[str, Sequence[Alliance]] = dt.field(default_factory=dict)
    "cache for computed alliances at each node"

    stats: dict[Reference, tuple[rst.NodeStats, bool]] = dt.field(default_factory=dict)
    "statistics computed for each references used by restrictions"

    @classmethod
    def build(cls, root: Node) -> AllocationContext:
        """Build a tree context."""
        logger.info("building allocation context for node '%s'", root.get_id())
        keys: dict[str, NodeOffset] = {}
        groups: dict[str, set[str]] = defaultdict(set)
        for info in root:
            if info.key in keys:
                raise PreconditionError(f"Duplicate district key: {info.key}")
            keys[info.key] = info
            groups[info.key].add(info.key)
            groups[f":{info.level}"].add(info.key)
            groups[f":{info.reverse_level}"].add(info.key)
            for group in info.node.groups or []:
                groups[f"#{group}"].add(info.key)
        # for group in groups.keys():
        #     if group in keys:
        #         raise ValueError(f"A group name conflicts with a district key: {group}")
        return cls(root=root.get_id(), keys=keys, groups=groups)

    def __call__(self) -> None:
        """Compute allocation for all nodes in the electoral system.

        Since dependencies are computed using depth first search, the
        electoral system must be a directed acyclic graph.
        """

        def edges(node_id: str) -> Iterator[str]:
            return iter(self.dependencies(node_id))

        def calc(node_id: str):
            logger.info("calculate node '%s'", node_id)
            info = self._get_info(node_id)
            info.node(self, info.context)
            logger.debug(
                "finished calculating node '%s' (result: %s)", node_id, info.node.result is not None
            )

        depth_first_search(edges, calc, self.root)

    def nested_results(self, key: str | Node) -> list[str]:
        """Return ids from nodes with results, considering `key` as the root."""
        root_id = self._get_info(key).key
        out = []

        def edges(node_id: str) -> Iterator[str]:
            node = self._get_info(node_id).node
            if not node.result:
                yield from self.dependencies(node_id, False)

        def calc(node_id: str):
            if node_id != root_id:
                out.append(node_id)

        depth_first_search(edges, calc, root_id)
        return out

    def _get_info(self, key: str | Node) -> NodeOffset:
        """Return a node offset from an id or a node."""
        if not isinstance(key, str):
            key = key.get_id()
        return self.keys[key]

    def _iter_reference(self, ref: Reference) -> Iterator[Node]:
        """Expand a reference to the referred nodes."""
        if not ref.ref:
            return
        for key in self.groups[ref.ref]:
            node = self.keys[key].node
            if ref.level is None:
                yield node
            else:
                yield from node.find_level(ref.level)

    def references(self, references: Iterable[Reference]) -> Iterator[Node]:
        """Iterate nodes referred by a list of `references`."""
        for ref in references:
            yield from self._iter_reference(ref)

    def _expand_refs(self, references: Iterable[Reference]) -> dict[GroupBy, list[Node]]:
        """Expand references to nodes by grouping by candidate id transformations."""
        groups: dict[GroupBy, list[Node]] = defaultdict(list)
        for ref in references:
            if isinstance(ref, GroupableReference):
                groupby = ref.groupby
            else:
                groupby = GroupBy.CANDIDATE
            collection = groups[groupby]
            for node in self._iter_reference(ref):
                if node not in collection:
                    collection.append(node)
        return groups

    def _find_edges(
        self, provider: Callable[[Node], bool | ReferenceSet[GroupableReference]], node_id: str
    ) -> Generator[str]:
        """Find dependent node ids from a reference provided.

        If the provided node does not have local data, the node divisions will be explored.
        """
        node = self._get_info(node_id).node
        cands = provider(node)
        if not isinstance(cands, bool):
            # candidates from references
            for ref in self.references(cands):
                yield ref.get_id()
        elif not cands and (divisions := node.local_divisions()):
            # candidates from divisions
            for div in divisions:
                if isinstance(div, Node):
                    yield self._get_info(div).key
                else:
                    for nref in self._iter_reference(div):
                        yield self._get_info(nref).key

    def flatten_candidates(self, key: str | Node) -> Ballots:
        """Compute candidates for a node identified by `key`.

        All references will be expanded, and candidates id will be transformed
        using the node names as districts.
        """
        root = self._get_info(key).node
        root_id = root.get_id()
        if root_id in self.cand_cache:
            return self.cand_cache[root_id]

        logger.debug("flattening candidates for node '%s'", root_id)

        def edges(node_id: str) -> Generator[str]:
            if node_id not in self.cand_cache:
                yield from self._find_edges(lambda n: n.local_candidates_references(), node_id)

        def append(node_id: str):
            # compute candidates for node_id
            node = self._get_info(node_id).node
            if node_id in self.cand_cache:
                return
            deps: dict[GroupBy, list[Node]]
            if candidates := node.local_candidates():
                if isinstance(candidates, Ballots):
                    if candidates.ballots:
                        candidates.ballots = [
                            node.transform_contender(c) for c in candidates.ballots
                        ]
                    self.cand_cache[node_id] = _apply_alliances(
                        candidates, self.flatten_alliances(node_id)
                    )
                    return
                deps = self._expand_refs(candidates)
            else:
                deps = {node.grouping(): list(node.local_children())}
            self._flatten_contenders(node, deps)

        depth_first_search(edges, append, root_id)

        return self.cand_cache[root_id]

    def _flatten_contenders(self, node: Node, groups: dict[GroupBy, list[Node]]):
        """Flatten ballots from groups of nodes."""
        ballots = Ballots()

        seen: set[str] = set()

        def children(items: Iterable[Node]) -> Iterator[tuple[Node, Ballots]]:
            for ch in items:
                ch_id = ch.get_id()
                if ch_id in seen:
                    raise PreconditionError(f"node {ch_id} cannot be used multiple times")
                seen.add(ch_id)
                c_ballots = self.cand_cache[ch_id]
                ballots.blank += c_ballots.blank
                ballots.void += c_ballots.void
                yield ch, c_ballots

        parts = []
        for groupby, nodes in groups.items():
            for ch, c_ballots in children(nodes):
                if GroupBy.DISTRICT in groupby:
                    contenders = (
                        dt.replace(cand, district=cand.district or ch.get_id())
                        for cand in c_ballots.ballots or []
                    )
                else:
                    contenders = (cand for cand in c_ballots.ballots or [])
                parts.append(Contender.merge_collection([contenders], by=groupby))
        ballots.ballots = [node.transform_contender(c) for c in Contender.merge_collection(parts)]
        self.cand_cache[node.get_id()] = _apply_alliances(
            ballots, self.flatten_alliances(node.get_id())
        )

    def flatten_alliances(self, key: str | Node) -> Sequence[Alliance] | None:
        """Compute alliances for a node identified by `key`.

        All references will be expanded, and alliances id will be transformed
        using the node names as districts.
        """
        root = self._get_info(key).node
        root_id = root.get_id()
        if root_id in self.alli_cache:
            return self.alli_cache[root_id]

        logger.debug("flattening alliances for node '%s'", root_id)

        def edges(node_id: str) -> Iterator[str]:
            if node_id in self.alli_cache:
                return
            node = self._get_info(node_id).node
            alliances = node.local_alliances()
            if isinstance(alliances, ReferenceSet):
                for ref in self.references(alliances):
                    yield ref.get_id()
            elif not alliances and (divisions := node.local_divisions()):
                # alliances from divisions
                for div in divisions:
                    if isinstance(div, Node):
                        yield self._get_info(div).key
                    else:
                        for nref in self._iter_reference(div):
                            yield self._get_info(nref).key

        def append(node_id: str):
            deps: dict[GroupBy, list[Node]]
            node = self._get_info(node_id).node
            if alliances := node.local_alliances():
                if not isinstance(alliances, ReferenceSet):
                    self.alli_cache[node_id] = alliances
                    return
                deps = self._expand_refs(alliances)
            else:
                deps = {node.grouping(): list(node.local_children())}
            self._flatten_alliances(node, deps)

        depth_first_search(edges, append, root_id)

        # return merge_alliances(parts)
        return self.alli_cache[root_id]

    def _flatten_alliances(self, node: Node, groups: dict[GroupBy, list[Node]]):
        """Flatten ballots from groups of nodes."""
        seen: set[str] = set()

        def children(items: Iterable[Node]) -> Iterator[tuple[Node, Sequence[Alliance]]]:
            for ch in items:
                ch_id = ch.get_id()
                if ch_id in seen:
                    raise PreconditionError(f"node {ch_id} cannot be used multiple times")
                seen.add(ch_id)
                c_allies = self.alli_cache[ch_id]
                yield ch, c_allies

        parts = []
        for groupby, nodes in groups.items():
            for ch, c_allies in children(nodes):
                alliances: Iterable[Alliance]
                if GroupBy.DISTRICT in groupby:
                    alliances = (
                        dt.replace(cand, district=cand.district or ch.get_id()) for cand in c_allies
                    )
                else:
                    alliances = (cand for cand in c_allies)
                parts.append(Alliance.merge_collection([alliances], by=groupby))
        self.alli_cache[node.get_id()] = Alliance.merge_collection(parts)

    def flatten_preferences(self, key: str | Node) -> list[Preference[ContenderId]] | None:
        """Compute preferences for a node identified by `key`.

        All references will be expanded, and preferences id will be transformed
        using the node names as districts.

        Preferences are not cached because of memory consumption.
        """
        node_cache: dict[str, list[Preference[ContenderId]] | None] = {}
        required: dict[str, int] = defaultdict(lambda: 0)

        def edges(node_id: str) -> Generator[str]:
            if node_id not in node_cache:
                for child_id in self._find_edges(
                    lambda n: n.local_preferences_references(), node_id
                ):
                    required[child_id] += 1
                    yield child_id

        def append(node_id: str):
            node = self._get_info(node_id).node
            if node_id in node_cache:
                return
            deps: dict[GroupBy, list[Node]]
            if preferences := self._get_preferences(node):
                if preferences:
                    if not isinstance(preferences, ReferenceSet):
                        node_cache[node_id] = list(preferences)
                        return
                    deps = self._expand_refs(preferences)
                else:
                    deps = {node.grouping(): list(node.local_children())}
            defs: list[tuple[GroupBy, str, list[Preference[ContenderId]]]] = []
            for groupby, nodes in deps.items():
                defs.extend(
                    (groupby, node.get_id(), node_cache[node.get_id()] or []) for node in nodes
                )
                for node in nodes:
                    child_id = node.get_id()
                    required[child_id] -= 1
            node_cache[node_id] = list(group_preferences(defs)) or None
            for child_id, is_required in required.items():
                if not is_required:
                    del node_cache[child_id]

        root_id = self._get_info(key).node.get_id()

        logger.debug("flattening preferences for node '%s'", root_id)

        required[root_id] += 2
        depth_first_search(edges, append, root_id)

        return node_cache[root_id]

    def _get_preferences(
        self, node: Node
    ) -> Iterator[Preference[ContenderId]] | ReferenceSet[GroupableReference] | None:
        if candidates := node.local_candidates():
            if isinstance(candidates, Ballots):
                ballots = candidates.ballots or []
            else:
                ballots = []
            mapping = frozenset(node.transform_contender_id(cand.get_id()) for cand in ballots)
        else:
            mapping = frozenset()
        return node.local_preferences(mapping)

    def resolve_seats(self, key: str | Node) -> int:
        """Resolve referenced seats.

        If the seats for a node depends on the result of other nodes, return the seats
        of the candidate with the same name as the node id. Otherwise return the node seats.
        """
        info = self._get_info(key)
        node_id = info.key

        seats = info.node.get_seats()
        if not isinstance(seats, ReferenceSet):
            return seats

        for cand in self.group_result(seats):
            if cand.name.name == node_id:
                return cand.seats
        raise KeyError(f"no seats found for node '{node_id}'")

    def group_result(self, reference: Iterable[Reference]) -> Sequence[Candidate[ContenderId]]:
        """Merge results from the referred nodes.

        Candidate-id transformations will be applied.
        """
        logger.debug("Grouping results for '%s'", reference)
        out: list[Candidate[ContenderId]] = []
        seen = set()
        for ref in reference:
            groups: dict[str, Iterable[Candidate[ContenderId]]] = {}
            for node in self._iter_reference(ref):
                node_id = node.get_id()
                if node_id in seen:
                    raise PreconditionError(f"node {node_id} cannot be used more than once")
                seen.add(node_id)
                if not node.result:
                    raise PreconditionError(f"node '{node_id}' must produce a result")
                groups[node_id] = node.result.allocation
            groupby = ref.groupby if isinstance(ref, GroupableReference) else GroupBy.CANDIDATE
            out.extend(group_candidates(groupby, groups))
        return list(merge_candidates(out))

    def dependencies(self, key: str | Node, restrictions: bool = True) -> frozenset[str]:
        """Return keys for nodes that must have a result before this node.

        Args
        ----
        key
            a node or a node id
        restrictions
            if True, include nodes referred in restrictions that need computed results.
        """
        info = self._get_info(key)
        logger.debug("computing dependencies for node '%s'", info.key)
        deps: set[str] = set()
        for div in info.node.local_divisions() or []:
            # divisions and references
            if isinstance(div, Node):
                deps.add(div.get_id())
            else:
                deps.update(r.get_id() for r in self._iter_reference(div))
        if info.context.initial_seats == InitialSeatsSource.RESULT:
            local_cands = info.node.local_candidates_references()
            if isinstance(local_cands, ReferenceSet):
                deps.update(r.get_id() for div in local_cands for r in self._iter_reference(div))

        # nodes referenced to get seats
        if isinstance(seats := info.node.get_seats(), ReferenceSet):
            deps.update(r.get_id() for ref in seats for r in self._iter_reference(ref))

        deps.difference_update(info.node.ignore_compute_dependency() or [])

        if restrictions:

            def add_restrictions(restrictions: Iterable[rst.Restriction]) -> None:
                for restriction in restrictions:
                    if restriction.target and restriction.attribute.requires_results():
                        deps.update(n.get_id() for n in self._iter_reference(restriction.target))

            # nodes referenced by thresholds
            if info.context.exclude:
                add_restrictions(info.context.exclude.walk())

            if info.context.include:
                add_restrictions(info.context.include.walk())

        return frozenset(deps)

    # restriction list
    def resolve_threshold(self, key: str | Node, include=False) -> set[ContenderId] | None:
        """Resolve restrictions for a node identified by `key`.

        Args
        ----
        include
            return restrictions from `include` instead of `exclude`
        """
        info = self._get_info(key)
        rlist = info.context.include if include else info.context.exclude
        if not rlist:
            return None
        node_id = info.node.get_id()
        logger.debug("resolving thresholds for node '%s': %s", node_id, rlist)
        node_ref = Reference(node_id)
        # build context
        # target | req_result | attrs*
        explorable: dict[Reference | None, bool] = {}
        for res_target, attrs in rlist.dependencies():
            target_key = res_target if node_id != res_target else None
            explorable[target_key] = explorable.get(target_key, False) or attrs.requires_results()
        context = {
            target: self.build_stats(target or node_ref, req_result)
            for target, req_result in explorable.items()
        }
        if None in context and node_ref not in context:
            context[node_ref] = context[None]

        # update ranks if needed
        for ref, stats in context.items():
            if rlist.check_any(ref, node_id, rst.Attribute.RANK):
                _update_ranks(stats.candidates)
            if rlist.check_any(ref, node_id, rst.Attribute.ALLIANCE_RANK):
                _update_ranks(stats.alliances)
        return rlist.resolve(context)

    def build_stats(self, targets: Reference, requires_results: bool) -> rst.NodeStats:
        """Compute statistics for nodes, candidates and alliances.

        This statistics are required for computing restrictions.

        Args
        ----
        requires_results
            compute statistics that requires previous results
        """
        # target = self._get_info(target).node
        with_votes = False
        with_results = False
        stats = rst.NodeStats()

        if targets in self.stats:
            stats, with_results = self.stats[targets]
            with_votes = True
            if not requires_results or with_results:
                return stats

        nodes = list(self._iter_reference(targets))
        if not with_votes:
            logger.debug("building vote stats for '%s'", targets)
            cand_districts: dict[ContenderId, set[str]] = defaultdict(set)
            alli_districts: dict[str, set[str]] = defaultdict(set)
            cand_groups: dict[ContenderId, set[str]] = defaultdict(set)
            alli_groups: dict[str, set[str]] = defaultdict(set)
            for target in nodes:
                target_id = target.get_id()
                # require results from referenced nodes
                stats.seats = self.resolve_seats(target)
                ballots = self.flatten_candidates(target_id)
                votes = Votes(0, ballots.blank, ballots.void)
                for cand in ballots.ballots or []:
                    district = cand.district or target_id
                    stats.districts.add(district)
                    cand_id = cand.get_id()
                    # add to candidate
                    s_can = stats.candidates[cand_id]
                    s_can.votes += cand.votes or 0
                    family = cand_id.transform(GroupBy.ID)
                    cand_groups[family].update(cand.groups)
                    cand_districts[family].add(district)
                    # add to alliance
                    s_alli = stats.alliances[cand_id.alliance]
                    s_alli.votes += cand.votes or 0
                    alli_groups[cand_id.alliance].update(cand.groups)
                    alli_districts[cand_id.alliance].add(district)
                    # global
                    votes.candidates += cand.votes or 0
                stats.candidates_votes += votes.candidates
                stats.valid_votes += votes.valid_votes()
                stats.total_votes += votes.all_votes()
            # update
            for cand_id in stats.candidates:
                family = cand_id.transform(GroupBy.ID)
                stats.candidates[cand_id].districts = cand_districts[family]
                stats.alliances[cand_id.alliance].districts = alli_districts[cand_id.alliance]
                stats.candidates[cand_id].tags = cand_groups[family]
                stats.alliances[cand_id.alliance].tags = alli_groups[cand_id.alliance]

        # gather from results
        if requires_results:
            logger.debug("building result stats for '%s'", targets)
            cand_quorum: dict[ContenderId, set[str]] = defaultdict(set)
            alli_quorum: dict[str, set[str]] = defaultdict(set)
            for target in nodes:
                if not target.result:
                    raise PreconditionError(f"node '{target_id}' must produce a result")

                for winner in target.result.allocation:
                    stats.seats += winner.seats
                    # candidate seats
                    s_can = stats.candidates[winner.name]
                    s_can.seats += winner.seats
                    # alliance seats
                    s_alli = stats.alliances[winner.name.alliance]
                    s_alli.seats += winner.seats
                    # quorum
                    if winner.seats > 0:
                        district = winner.name.district or target_id
                        cand_quorum[winner.name.transform(GroupBy.ID)].add(district)
                        alli_quorum[winner.name.alliance].add(district)
            for cand_id in stats.candidates:
                stats.candidates[cand_id].quorum.update(cand_quorum[cand_id.transform(GroupBy.ID)])
                stats.alliances[cand_id.alliance].quorum.update(alli_quorum[cand_id.alliance])

            with_results = True

        self.stats[targets] = stats, with_results

        return stats

    def children(self, key: str | Node) -> Iterator[str]:
        """Iterate `key`'s children node ids."""
        info = self._get_info(key)
        yield info.key
        for child in info.node.local_children():
            yield from self.children(child)


def _update_ranks(collection: dict[T, rst.ContenderStats]):
    ranked = sorted(collection.items(), key=lambda x: x[1].votes, reverse=True)
    for idx, (_, group) in enumerate(itertools.groupby(ranked, key=lambda x: x[1].votes), start=1):
        for c_id, _val in group:
            collection[c_id].rank = idx
