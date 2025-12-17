#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Test for mixed-member methods."""

from __future__ import annotations
import pytest
from ..methods.singlevote.highest_averages import HighestAveragesAllocator
from ..methods.compensatory.mixed_member import (
    MixedMemberAdapter,
    OverhangMode,
)
from ..methods.types import Input


@pytest.fixture(name="ignore_allocator")
def fixture_ignore_allocator():
    """Return an allocator that will ignore parties with overhang seats."""
    method = HighestAveragesAllocator("dhondt")
    return MixedMemberAdapter(OverhangMode.IGNORE, method)


@pytest.fixture(name="absorb_allocator")
def fixture_absorb_allocator():
    """Return an allocator that will increment seats to absorb overhang seats."""
    method = HighestAveragesAllocator("dhondt")
    return MixedMemberAdapter(OverhangMode.ABSORB, method)


@pytest.fixture(name="method", params=["ignore_allocator", "absorb_allocator"])
def fixture_method(request):
    """Return a mixed-member allocator."""
    return request.getfixturevalue(request.param)


@pytest.fixture(name="input_type")
def fixture_input_type(method: MixedMemberAdapter):
    """Return input types for an allocator."""
    return method.admitted_input


# test inputs
def test_input_initial_seats(input_type):
    """A mixed member method should admit initial_seats."""
    assert Input.INITIAL_SEATS in input_type


def test_input_skip_initial_seats(input_type):
    """A mixed member method should admit skip_initial_seats."""
    assert Input.SKIP_INITIAL_SEATS in input_type


def test_input_seats(input_type):
    """A mixed member method should admit seats."""
    assert Input.SEATS in input_type


def test_input_max_seats(input_type):
    """A mixed member method should admit max_seats."""
    assert Input.MAX_SEATS in input_type


def test_input_inner_initial_seats(input_type):
    """A mixed member method should admit inner_initial_seats."""
    assert Input.INNER_INITIAL_SEATS in input_type


@pytest.fixture(name="votes")
def fixture_votes():
    """Return votes and seats from first-vote."""
    return {
        "candidates": [
            ["A", 340_000],
            ["B", 280_000],
            ["C", 160_000],
            ["D", 60_000],
            ["E", 15_000],
        ],
        "initial_seats": [
            ["A", 2],
            ["B", 2],
            ["C", 1],
            ["D", 1],
            ["E", 1],
        ],
        "skip_initial_seats": True,
    }


# test mixed member
def test_allocator_dont_absorb_overhang(ignore_allocator: MixedMemberAdapter, votes: dict):
    """Test result for ignore_allocator.

    A 6
    B 5
    C 2
    D 1
    """
    ref = {("A", 4), ("B", 3), ("C", 1)}
    result = ignore_allocator(**votes)

    app = {(x.name, x.seats) for x in result.allocation if x.seats}
    print(app)
    print(result)
    assert result.data
    overhang = {item["name"]: item["seats"] for item in result.data.overhang}
    assert overhang.get("E", 0) == 1
    assert ref == app


# test mixed member absorb overhang
def test_allocator_absorb_overhang_max_seats_16(absorb_allocator: MixedMemberAdapter, votes: dict):
    """Test result for absorb_allocator with max_seats==16.

    A 7
    B 5
    C 3
    D 1
    """
    ref = {("A", 5), ("B", 3), ("C", 2)}
    result = absorb_allocator(**votes, max_seats=16)

    app = {(x.name, x.seats) for x in result.allocation if x.seats}
    print(app)
    print(result)
    assert result.data
    overhang = {item["name"]: item["seats"] for item in result.data.overhang}
    assert overhang.get("E", 0) == 1
    assert ref == app


def test_allocator_absorb_overhang_max_seats_none(
    absorb_allocator: MixedMemberAdapter, votes: dict
):
    """Test result for absorb_allocator with max_seats==None.

    A 22
    B 18
    C 10
    D 4
    E 1
    """
    ref = {("A", 20), ("B", 16), ("C", 9), ("D", 3)}
    result = absorb_allocator(**votes)

    app = {(x.name, x.seats) for x in result.allocation if x.seats}
    print(app)
    print(result)
    assert result.data and not result.data.overhang
    assert ref == app
