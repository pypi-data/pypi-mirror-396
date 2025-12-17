#!/usr/bin/source python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Test divisor functions."""

from fractions import Fraction
import pytest
from .. import divisors


def check_divisor_function(divisor_f, seats, expected):
    """Check divisor function."""
    value = divisor_f(seats)
    assert value == expected, {"seats": seats, "expected": expected, "value": value}


def check_float_divisor_function(divisor_f, seats, expected):
    """Check divisor function."""
    value = divisor_f(seats)
    assert pytest.approx(value, rel=1e-3) == expected


@pytest.mark.parametrize("seats,divisor", enumerate(list(range(1, 11))))
def test_dhondt_divisor(seats, divisor):
    """Test D'Hondt divisor function."""
    check_divisor_function(divisors.dhondt_divisor, seats, divisor)


@pytest.mark.parametrize("seats,divisor", enumerate([1, 3, 5, 7, 9, 11, 13, 15, 17, 19]))
def test_sainte_lague_divisor(seats, divisor):
    """Test Sainte-Lague divisor function."""
    check_divisor_function(divisors.sainte_lague_divisor, seats, divisor)


@pytest.mark.parametrize(
    "seats,divisor", enumerate([Fraction("1.4"), 3, 5, 7, 9, 11, 13, 15, 17, 19])
)
def test_sainte_lague_14_divisor(seats, divisor):
    """Test Sainte-Lague 1.4 divisor function."""
    check_divisor_function(divisors.sainte_lague_14_divisor, seats, divisor)


@pytest.mark.parametrize("seats,divisor", enumerate(list(range(2, 12))))
def test_imperiali_divisor(seats, divisor):
    """Test Imperiali divisor function."""
    check_divisor_function(divisors.imperiali_divisor, seats, divisor)


@pytest.mark.parametrize("seats,divisor", enumerate([1, 4, 7, 10, 13, 16, 19, 22, 25]))
def test_danish_divisor(seats, divisor):
    """Test Danish divisor function."""
    check_divisor_function(divisors.danish_divisor, seats, divisor)


@pytest.mark.parametrize("seats,divisor", enumerate([0, 1.414, 2.449, 3.464, 4.472]))
def test_huntington_hill_divisor(seats, divisor):
    """Test Huntington-Hill divisor function."""
    check_float_divisor_function(divisors.huntington_hill_divisor, seats, divisor)
