#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Tests for additional member methods."""

from __future__ import annotations
import pytest
from ..methods.singlevote.highest_averages import HighestAveragesAllocator
from ..methods.compensatory.additional_member import AdditionalMemberAdapter
from ..methods.types import Input


@pytest.fixture(name="allocator")
def fixture_allocator():
    """Return a method."""
    method = HighestAveragesAllocator("dhondt")
    return AdditionalMemberAdapter(method)


@pytest.fixture(name="input_type")
def fixture_input_type(allocator: AdditionalMemberAdapter):
    """Return admitted inputs."""
    return allocator.admitted_input


# test inputs
def test_input_initial_seats(input_type):
    """Initial seats should be admitted."""
    assert Input.INITIAL_SEATS in input_type


def test_input_candidates(input_type):
    """Candidates should be admitted."""
    assert Input.CANDIDATES in input_type


def test_input_seats(input_type):
    """Seats should be admitted."""
    assert Input.SEATS in input_type


def test_input_inner_initial_seats(input_type):
    """Inner initial seats should be admitted."""
    assert Input.INNER_INITIAL_SEATS in input_type


@pytest.fixture(name="votes")
def fixture_votes():
    """Return a problem."""
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


@pytest.fixture(name="data1")
def fixture_data1(votes: dict):
    """Return a result for votes."""
    votes["seats"] = 5
    result = {
        ("A", 2),
        ("B", 2),
        ("C", 1),
        ("D", 0),
        ("E", 0),
    }
    return votes, result


# test additional member result
def test_result(allocator: AdditionalMemberAdapter, data1):
    """Test calc.

    Check that the result is correct.
    """
    data, ref = data1
    result = allocator(**data)
    assert ref == {(x.name, x.seats) for x in result.allocation}
