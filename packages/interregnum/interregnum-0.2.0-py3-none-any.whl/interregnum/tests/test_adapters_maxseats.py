# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

from typing import Any
import pytest
from ..methods.singlevote.highest_averages import HighestAveragesAllocator
from ..methods.singlevote.largest_remainder import LargestRemainderAllocator
from ..methods.adapters.maxseats import MaxSeatsAdapter, MaxSeatsResultData
from ..methods.types import Result


@pytest.fixture(name="dhondt")
def fixture_dhondt():
    """Return a d'Hondt allocator."""
    return HighestAveragesAllocator("dhondt")


@pytest.fixture(name="hare")
def fixture_hare():
    """Return a Hare allocator."""
    return LargestRemainderAllocator("hare")


# TODO: imperiali 3


@pytest.fixture(name="sample1")
def fixture_sample1():
    """Vote result."""
    return (
        [
            ("A", 340_000),
            ("B", 280_000),
            ("C", 160_000),
            ("D", 60_000),
            ("E", 15_000),
        ],
        7,
    )


def check_result(
    result: Result[str, Any], samples: tuple[list[tuple[str, int]], int], expected: dict[str, int]
):
    """Test result."""
    print(result)
    if isinstance(result.data, MaxSeatsResultData):
        for idx, evt in enumerate(result.data.steps):
            print(f"result {idx}: ", evt.allocation)
            if evt.data and evt.data.log:
                for log in evt.data.log:
                    print("\t", log)
    allocated = {cand.name: cand.seats for cand in result.allocation}
    for c_name, _ in samples[0]:
        if c_name not in allocated:
            allocated[c_name] = 0
        if c_name not in expected:
            expected[c_name] = 0
    assert sum(allocated.values()) == sum(
        expected.values()
    ), "number of allocated seats differs from required"
    assert allocated == expected, "candidates seats differs from expected"


def test_dhondt1(dhondt: HighestAveragesAllocator[str], sample1):
    """Test Dhondt with a candidate restriction restriction.

    A <= 2
    """
    data, seats = sample1
    adapter = MaxSeatsAdapter(dhondt)
    res = adapter.calc(seats, [(2, ["A"])], candidates=data)
    check_result(
        res,
        sample1,
        {
            "A": 2,
            "B": 3,
            "C": 2,
        },
    )


def test_dhondt2(dhondt: HighestAveragesAllocator, sample1):
    """Test Dhondt with a candidate restriction and an alliance restriction.

    A <= 3
    A + C <= 2
    """
    data, seats = sample1
    adapter = MaxSeatsAdapter(dhondt)
    res = adapter.calc(
        seats,
        [
            (3, ["A"]),
            (2, ["A", "C"]),
        ],
        candidates=data,
    )
    # A = 1 1 0
    # B = 1 1 1 1
    # C = 0
    # D = 1
    check_result(
        res,
        sample1,
        {
            "A": 2,
            "B": 4,
            "C": 0,
            "D": 1,
        },
    )


def test_hare1(hare: LargestRemainderAllocator, sample1):
    """Test Hare with a candidate restriction.

    A <= 1
    """
    data, seats = sample1
    # import pudb; pu.db
    adapter = MaxSeatsAdapter(hare)
    res = adapter.calc(seats, [(1, ["A"])], candidates=data)
    # A == 1
    # B == 3
    # C == 1 + 1
    # D == 0 + 1
    # E == 0
    check_result(
        res,
        sample1,
        {
            "A": 1,
            "B": 3,
            "C": 2,
            "D": 1,
            "E": 0,
        },
    )


def test_hare2(hare: LargestRemainderAllocator, sample1):
    """Test Hare with an alliance restriction.

    A + B <= 3
    """
    data, seats = sample1
    adapter = MaxSeatsAdapter(hare)
    res = adapter.calc(seats, [(3, ["A", "B"])], candidates=data)
    # A=3, B=2, C=1, D=1

    # A == 3 -> 2 [<= 3]
    # B == 2 -> 1 [<= 3]
    # C == 1 -> 2 [+ 1]
    # D == 1 -> 2 [+ 1]
    # E == 0
    check_result(
        res,
        sample1,
        {
            "A": 2,
            "B": 1,
            "C": 3,
            "D": 1,
            "E": 0,
        },
    )


def test_hare3(hare: LargestRemainderAllocator, sample1):
    """Test Hare with two alliances restrictions.

    A + B <= 3
    C + D + E <= 2
    """
    data, seats = sample1
    adapter = MaxSeatsAdapter(hare)
    res = adapter.calc(
        seats,
        [
            (3, ["A", "B"]),
            (2, ["C", "D", "E"]),
        ],
        candidates=data,
    )
    # A=3, B=2, C=1, D=1

    # A == 3 -> 2 [<= 3]
    # B == 2 -> 1 [<= 3]
    # C == 1 -> 1 [<= 2]
    # D == 1 -> 1 [<= 2]
    # E == 0 -> 0 [<= 2]
    check_result(
        res,
        sample1,
        {
            "A": 2,
            "B": 1,
            "C": 1,
            "D": 1,
            "E": 0,
        },
    )


@pytest.fixture(
    name="divisor",
    params=[
        "dhondt",
        "sainte_lague",
        "imperiali",
    ],
)
def fixture_divisor(request):
    """Return a divisor key."""
    return request.param


@pytest.fixture(name="hag")
def fixture_method_hag(divisor):
    """Return a highest averages allocator."""
    return HighestAveragesAllocator(divisor)


def test_max_seats_adapter_filter(hag):
    """Test max seats adapter with two restrictions (method supporting filters)."""
    candidates = [["a", 1000], ["b", 900], ["c", 850], ["d", 200]]
    seats = 10

    v_constraint_1 = 2
    v_constraint_2 = 5

    adapter = MaxSeatsAdapter(hag)
    result = adapter(
        seats=seats,
        candidates=candidates,
        constraints=[
            (v_constraint_1, ("a",)),
            (v_constraint_2, ("a", "b")),
        ],
    )
    calc_seats = sum(x.seats for x in result.allocation)
    assert calc_seats == seats
    app = {c.name: c for c in result.allocation}
    assert app["a"].seats <= v_constraint_1
    assert (app["a"].seats + app["b"].seats) <= v_constraint_2


@pytest.fixture(name="quota", params=["hare", "droop"])
def fixture_quota(request):
    """Return a quota key."""
    return request.param


@pytest.fixture(name="lr")
def fixture_lr(quota):
    """Return a largest remainder allocator."""
    return LargestRemainderAllocator(quota)


def test_max_seats_adapter_exclude(lr):
    """Test max seats adapter with two restrictions (methods support exclusion list)."""
    # import pudb; pu.db
    candidates = [["a", 1000], ["b", 900], ["c", 850], ["d", 200]]
    seats = 10

    v_constraint_1 = 2
    v_constraint_2 = 5

    adapter = MaxSeatsAdapter(lr)
    result = adapter(
        seats=seats,
        candidates=candidates,
        constraints=[
            (v_constraint_1, ("a",)),
            (v_constraint_2, ("a", "b")),
        ],
    )
    calc_seats = sum(x.seats for x in result.allocation)
    assert calc_seats == seats
    app = {c.name: c for c in result.allocation}
    assert app["a"].seats <= v_constraint_1
    assert (app["a"].seats + app["b"].seats) <= v_constraint_2
