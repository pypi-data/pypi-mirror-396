#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Candidate filters used to exclude candidates by allocators that allocate one seat at a time."""
from __future__ import annotations
from typing import (
    Sequence,
    Collection,
    cast,
)
from typing_extensions import Never, override
from ..methods import inputs as ipt
from .types import (
    AnyName,
    AnyEvent,
    Candidate,
    Allocator,
    Input,
    PreconditionError,
    CandidateFilter,
)


class ChainCandidateFilter(CandidateFilter[AnyName, AnyEvent]):
    """Compose a candidate filter using several chained filters."""

    def __init__(self, *filters: CandidateFilter[AnyName, AnyEvent]):
        """
        Create a chain filter from a list of `filters`.

        Args
        ----
        filters
            list of filters
        """
        self.filters = filters

    @override
    def start(self) -> Sequence[AnyEvent]:
        """Start the filter."""
        events: list[AnyEvent] = []
        for fil in self.filters:
            events.extend(fil.start())
        return events

    @override
    def update(self, cand: Candidate[AnyName]) -> Sequence[AnyEvent]:
        """Update candidate seats."""
        events: list[AnyEvent] = []
        for fil in self.filters:
            events.extend(fil.update(cand))
        return events

    @override
    def is_valid(self, name: AnyName) -> bool:
        """Check if a candidate can continue in the allocation."""
        return all(fil.is_valid(name) for fil in self.filters)

    @override
    def exclusion_list(self) -> Collection[AnyName]:
        """Return the list of excluded candidates at the current allocation stage."""
        out: set[AnyName] = set()
        for fil in self.filters:
            out.update(fil.exclusion_list())
        return out


class ContenderSetFilter(CandidateFilter[AnyName, AnyEvent]):
    """Simple candidate filter based on an exclusion list."""

    def __init__(self, contenders: Collection[AnyName]):
        """Create a contender set filter from a collection of contenders.

        Everyone in the collection will be excluded from allocation.

        Args
        ----
        contenders
            list of excluded contenders
        """
        self.contenders = contenders

    @override
    def start(self) -> Sequence[Never]:
        return []

    @override
    def update(self, cand: Candidate[AnyName]) -> Sequence[Never]:
        return []

    @override
    def is_valid(self, name: AnyName) -> bool:
        return name not in self.contenders

    @override
    def exclusion_list(self) -> Collection[AnyName]:
        return self.contenders


def exclude_candidates(
    allocator: Allocator, params: ipt.InputDict[AnyName, AnyEvent], exclusion: ipt.INames
) -> ipt.InputDict[AnyName, AnyEvent]:
    """Add standard arguments to `params` for excluding candidates in `exclusion`.

    Args
    ----
    allocator
        an allocator where the inputs will be used
    params
        current inputs
    exclusion
        list of candidates excluded from allocation

    Return
    ------
    :
        updated inputs
    """
    new_params = cast(ipt.InputDict[AnyName, AnyEvent], dict(params))
    if Input.EXCLUDE_CANDIDATES in allocator.admitted_input:
        cands = set(params.get("exclude_candidates", []))
        cands.update(exclusion)
        new_params["exclude_candidates"] = cands
    elif Input.FILTER_F in allocator.admitted_input:
        # chain
        filter_f: CandidateFilter[AnyName, AnyEvent] = ContenderSetFilter(frozenset(exclusion))
        if old_filter_f := params.get("filter_f"):
            filter_f = ChainCandidateFilter(old_filter_f, filter_f)
        new_params["filter_f"] = filter_f
    else:
        raise PreconditionError(
            "unable to exclude candidates: the allocator does not allow "
            "params 'filter_f' or 'exclude_candidates'"
        )
    return new_params
