# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Test quota functions."""

from fractions import Fraction
import pytest

from .. import quotas


def check_quota_function(quota_f, votes, seats, value, expected):
    """Check rank function."""
    result = quota_f(votes, seats).reached(value)
    assert result == expected, {
        "votes": votes,
        "seats": seats,
        "value": value,
        "expected": expected,
    }


def test_hare_quota_zero_division():
    """Check that a Hare quota for 0 seats should raise an exception."""
    with pytest.raises(ZeroDivisionError):
        quotas.hare_quota(1, 0)


@pytest.mark.parametrize(
    "votes,seats,value,expected",
    [
        (100, 1, 100, False),
        (100, 1, 101, True),
        (100, 1, 100.1, True),
        (100, 1, 99, False),
        (100, 2, 50, False),
        (100, 2, 50.1, True),
        (100, 2, 51, True),
        (100, 3, Fraction(100, 3), False),
        (100, 3, Fraction(100, 3) + Fraction(1, 1000), True),
        (100, 3, 33, False),
        (100, 3, 34, True),
        (100, 4, 25, False),
        (100, 4, 26, True),
        (100, 5, 20, False),
        (100, 5, 21, True),
        (100, 100, 1, False),
        (100, 100, 2, True),
        (100, 101, Fraction(100, 101), False),
        (100, 101, Fraction(100, 101) + Fraction(1, 1000), True),
    ],
)
def test_hare_quota(votes, seats, value, expected):
    """Check results for Hare quota."""
    check_quota_function(quotas.hare_quota, votes, seats, value, expected)


@pytest.mark.parametrize(
    "votes,seats,value,expected",
    [
        (100, 1, 50, False),
        (100, 1, 51, True),
        (100, 2, 50, False),
        (100, 2, 51, True),
        (100, 3, 50, False),
        (100, 3, 51, True),
        (50, 1, 25, False),
        (50, 1, 26, True),
        (47, 1, Fraction(47, 2), False),
        (47, 1, 24, True),
    ],
)
def test_majority_quota(votes, seats, value, expected):
    """Check results for majority quota."""
    check_quota_function(quotas.majority_quota, votes, seats, value, expected)


@pytest.mark.parametrize(
    "votes,seats,value,expected",
    [
        (100, 0, 101, True),
        (100, 0, 100, False),
        (100, 1, 51, True),
        (100, 1, 50, False),
        (100, 2, 34, True),
        (100, 2, 33, False),
        (100, 3, 26, True),
        (100, 3, 25, False),
        (100, 4, 21, True),
        (100, 4, 20, False),
        (100, 5, 17, True),
        (100, 5, 16, False),
        (100, 100, 1, True),
        (100, 101, 0, False),
    ],
)
def test_droop_quota(votes, seats, value, expected):
    """Check results for Droop quota."""
    check_quota_function(quotas.droop_quota, votes, seats, value, expected)


@pytest.mark.parametrize(
    "votes,seats,value,expected",
    [
        (100, 0, 100, False),
        (100, 0, 100.1, True),
        (100, 1, 50, False),
        (100, 1, 50.1, True),
        (100, 2, Fraction(100, 3), False),
        (100, 2, Fraction(100, 3) + 0.1, True),
        (100, 3, 25, False),
        (100, 3, 25.1, True),
        (100, 4, 20, False),
        (100, 4, 20.1, True),
        (100, 5, Fraction(50, 3), False),
        (100, 5, Fraction(50, 3) + 0.1, True),
        (100, 100, Fraction(100, 101), False),
        (100, 100, Fraction(100, 101) + 0.1, True),
        (100, 101, Fraction(50, 51), False),
        (100, 101, Fraction(50, 51) + 0.1, True),
    ],
)
def test_hagenbach_bischoff_quota(votes, seats, value, expected):
    """Check results for Hagenbach-Bischoff quota."""
    check_quota_function(quotas.hagenbach_bischoff_quota, votes, seats, value, expected)


@pytest.mark.parametrize(
    "votes,seats,value,expected",
    [
        (100, 0, 50, False),
        (100, 0, 50.1, True),
        (100, 1, Fraction(100, 3), False),
        (100, 1, Fraction(100, 3) + 0.1, True),
        (100, 2, 25, False),
        (100, 2, 25.1, True),
        (100, 3, 20, False),
        (100, 3, 20.1, True),
        (100, 4, Fraction(50, 3), False),
        (100, 4, Fraction(50, 3) + 0.1, True),
        (100, 5, Fraction(100, 7), False),
        (100, 5, Fraction(100, 7) + 0.1, True),
        (100, 100, Fraction(50, 51), False),
        (100, 100, Fraction(50, 51) + 0.1, True),
        (100, 101, Fraction(100, 103), False),
        (100, 101, Fraction(100, 103) + 0.1, True),
    ],
)
def test_imperiali_quota(votes, seats, value, expected):
    """Check results for Imperiali quota."""
    check_quota_function(quotas.imperiali_quota, votes, seats, value, expected)


@pytest.mark.parametrize(
    "votes,seats,value,expected",
    [
        (100, 0, Fraction(100, 3), False),
        (100, 0, Fraction(100, 3) + 0.1, True),
        (100, 1, 25, False),
        (100, 1, 25.1, True),
        (100, 2, 20, False),
        (100, 2, 20.1, True),
        (100, 3, Fraction(50, 3), False),
        (100, 3, Fraction(50, 3) + 0.1, True),
        (100, 4, Fraction(100, 7), False),
        (100, 4, Fraction(100, 7) + 0.1, True),
        (100, 5, Fraction(25, 2), False),
        (100, 5, Fraction(25, 2) + 0.1, True),
        (100, 100, Fraction(100, 103), False),
        (100, 100, Fraction(100, 103) + 0.1, True),
        (100, 101, Fraction(25, 26), False),
        (100, 101, Fraction(25, 26) + 0.1, True),
    ],
)
def test_imperiali_3_quota(votes, seats, value, expected):
    """Check results for Imperiali-3 quota."""
    check_quota_function(quotas.imperiali_3_quota, votes, seats, value, expected)
