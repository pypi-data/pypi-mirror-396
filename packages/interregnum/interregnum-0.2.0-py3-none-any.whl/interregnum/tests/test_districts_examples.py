# /usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Test examples for district based systems."""

from __future__ import annotations
from typing import Final, Iterator, Any
from pathlib import Path

import pytest

from . import common as cmn
from ..district import unserialize_node, Node
from ..district.contenders import Contender
from ..district.counting import Ballots
from ..district import io


PROBLEM_DIR: Final = Path("examples")
RESTRICT: list[str] = []


def find_testables(node: dict[str, Any]) -> Iterator[tuple[str, str | list | None]]:
    """Return testable nodes from `node`."""
    if "name" not in node:
        return
    testable = node.get("meta", {}).get("test", False)
    node_name = node.get("key", node["name"])
    if testable:
        if isinstance(testable, (str, list)):
            # str - use candidates from referenced node
            # list - list of testing candidates
            yield node_name, testable
        else:
            yield node_name, None
    for field in node.values():
        if isinstance(field, dict) and "name" in field:
            # find testable children
            yield from find_testables(field)
        elif isinstance(field, list):
            # find testable children
            for item in field:
                if isinstance(item, dict) and "name" in item:
                    yield from find_testables(item)


def get_results():
    """Return results in directory."""
    filenames = list(cmn.iter_problem_filenames(PROBLEM_DIR, True))
    out = {}
    for path in filenames:
        if RESTRICT and path.name not in RESTRICT:
            continue
        data = cmn.read_data(path)
        out[str(path)] = list(find_testables(data))
    return out


@pytest.fixture(name="system", scope="module")
def fixture_system(request):
    """Return a system."""
    filename = Path(request.param)
    doc = cmn.read_data(filename)
    parent = filename.parent
    data = unserialize_node(doc, cwd=parent)
    data.build()()
    return data, parent


@pytest.mark.parametrize(
    "system,result_ref,test_ref",
    [(path,) + result for path, results in get_results().items() for result in results],
    indirect=["system"],
    ids=lambda x: x if not isinstance(x, list) else "meta",
)
def test_result(system: tuple[Node, Path], result_ref: str, test_ref: str | list | None):
    """Check results for a system."""
    root, cwd = system
    node = root.find_district(result_ref)
    assert node
    assert node.result
    ballots: Any
    if result_ref != test_ref:
        target = test_ref or result_ref
        if not isinstance(target, list):
            if target.startswith("file:"):
                data = io.CandidatesFile(path=Path(target[5:]), format="csv", cwd=cwd)
                ballots = Ballots(ballots=[cont for node_name, cont in data()])
            else:
                # node reference
                tnode = root.find_district(target)
                assert tnode
                ballots = tnode.local_candidates()
        else:
            ballots = Ballots(ballots=[Contender(**item) for item in target])
    else:
        ballots = node.local_candidates()
    # if not ballots:
    #     import pudb; pu.db
    assert ballots and isinstance(ballots, Ballots)
    ref = {
        (cand.get_id(), cand.seats)
        for cand in ballots.ballots or []
        if cand.seats and (cand.seats != 0)
    }
    val = {
        (cand.name, cand.seats)
        for cand in node.result.allocation
        if cand.seats and (cand.seats != 0)
    }
    assert ref == val
