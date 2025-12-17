#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Tests for Single Transferable Vote methods."""

from __future__ import annotations
from typing import Final
from fractions import Fraction

import pytest

from ..methods.preferential.transferable_vote.transfer_functions import (
    CandidateParcels,
    Parcel,
    Preference,
    inclusive_gregory_transfer,
    gregory_transfer,
)


# Tests: Miragliotta2002
#
# Ira has been elected having received a total of 925 votes.
# The quota is 650 which means that Ira has 275 surplus votes.
# Ira's vote is made up of the following subparcels of ballot papers assigned
# to him during the course of the count, in the following order:
#
# - 475 first preference votes
# - 160 votes received follwing Rhonda's election which represent 1600 ballot papers
# - 290 votes received at full value, as a result of Carla's exclusion from the count.
#
# There is still one vacancy to be filled following Ira's election and two candidates remaining:
# George, with 520 votes
# Sandie, with 500 votes
#
# Preference rankings:
#
# Ira (1/1) -      475, George 95,  Sandie 380
# Rhonda (1/10) - 1600, George 640, Sandie 960
# Carla (1/1) -   290,  George 232, Sandie  58

DATA: Final[dict[str, CandidateParcels]] = {
    "Ira": CandidateParcels(
        votes=925,
        parcels=[
            # Ira's parcel
            Parcel(
                votes=475,
                group_id=0,
                batches=[
                    Preference(95, ("George", "Sandie")),
                    Preference(380, ("Sandie", "George")),
                ],
            ),
            # Rhonda's parcel
            Parcel(
                votes=1600,
                group_id=1,
                weight=Fraction(1, 10),
                batches=[
                    Preference(640, ("George", "Sandie")),
                    Preference(960, ("Sandie", "George")),
                ],
            ),
            # Carla's parcel
            Parcel(
                votes=290,
                group_id=2,
                batches=[
                    Preference(232, ("George", "Sandie")),
                    Preference(58, ("Sandie", "George")),
                ],
            ),
        ],
    ),
}
DATA_SURPLUS: Final = 275


@pytest.fixture(name="gregory_transfers", scope="module")
def fixture_gregory_transfer():
    """Return transfer Ira's parcels using the Gregory transfer method."""
    return gregory_transfer(int, DATA, "Ira", DATA_SURPLUS)


@pytest.fixture(name="inclusive_gregory_transfers", scope="module")
def fixture_inclusive_gregory_transfer():
    """Return transfer Ira's parcels using the Inclusive Gregory transfer method."""
    return inclusive_gregory_transfer(False, int, DATA, "Ira", DATA_SURPLUS)


@pytest.fixture(name="weighted_inclusive_gregory_transfers", scope="module")
def fixture_weighted_inclusive_gregory_transfer():
    """Return transfer Ira's parcels using the Inclusive Gregory transfer method."""
    return inclusive_gregory_transfer(True, round, DATA, "Ira", DATA_SURPLUS)


@pytest.mark.parametrize(
    "transfers,transferred,votes",
    [
        # 275/290 * Carla's ballot papers for each of Sandie and George
        # Carla's parcel (Last parcel):
        #   Sandie: (275/290) * 58 -> 55
        #   George: (275/290) * 232 -> 220
        ("gregory_transfers", "Sandie", 55),
        ("gregory_transfers", "George", 220),
        # 275/2365 * for each parcel
        # 2365 -> total number of Ira's ballot papers
        # Ira's Parcel
        #   Sandie: (275/2365) * 380 -> 44.186 (1900/43)
        #   George: (275/2365) * 95 -> 11.0465 (475/43)
        # Rhonda's Parcel
        #   Sandie: (275/2365) * 960 -> 111.6279 (4800/43)
        #   George: (275/2365) * 640 -> 74.4186 (3200/43)
        # Carla's Parcel
        #   Sandie: (275/2365) * 58 -> 6.7441 (290/43)
        #   George: (275/2365) * 232 -> 26.9767 (1160/43)
        # Total:
        #   Sandie: int((1900/43)+(4800/43)+(290/43)) -> 162
        #   George: int((475/43)+(3200/43)+(1160/43)) -> 112
        ("inclusive_gregory_transfers", "Sandie", 162),
        ("inclusive_gregory_transfers", "George", 112),
        # ("inclusive_gregory_transfers", "Sandie", 0, 44),
        # ("inclusive_gregory_transfers", "George", 0, 11),
        # ("inclusive_gregory_transfers", "Sandie", 1, 111),
        # ("inclusive_gregory_transfers", "George", 1, 74),
        # ("inclusive_gregory_transfers", "Sandie", 2, 6),
        # ("inclusive_gregory_transfers", "George", 2, 26),
        # 275/295 * Ira's ballot papers (transfer value=1)
        # 275/295 * Carla's ballot papers (transfer value=1)
        # 275/295 * transfer value of Rhonda's ballot papers
        # Ira's parcel
        #   Sandie: (275/925) * 380 -> 112.9729 (4180/37)
        #   George: (275/925) * 95 -> 28.24324 (1045/37)
        # Rhonda's parcel
        #   Sandie: (275/925)*(1/10) * 960 -> 28.5405 (1056/37)
        #   George: (275/925)*(1/10) * 640 -> 19.027 (704/37)
        # Carla's parcel
        #   Sandie: (275/925) * 58 -> 17.2432 (638/37)
        #   George: (275/925) * 232 -> 68.9729 (2552/37)
        # Total:
        #   Sandie: round((4180/37)+(1056/37)+(638/37)) -> 159
        #   George: round((1045/37)+(704/37)+(2552/37)) -> 116
        ("weighted_inclusive_gregory_transfers", "Sandie", 159),
        ("weighted_inclusive_gregory_transfers", "George", 116),
        # ("weighted_inclusive_gregory_transfers", "Sandie", 0, 113),
        # ("weighted_inclusive_gregory_transfers", "George", 0, 28),
        # ("weighted_inclusive_gregory_transfers", "Sandie", 1, 29),
        # ("weighted_inclusive_gregory_transfers", "George", 1, 19),
        # ("weighted_inclusive_gregory_transfers", "Sandie", 2, 17),
        # ("weighted_inclusive_gregory_transfers", "George", 2, 69),
    ],
)
def test_transferred_votes(request, transfers, transferred: str, votes):
    """Check votes transferred to a candidate in a parcel."""
    batch: dict[str, CandidateParcels] = request.getfixturevalue(transfers)
    target = batch[transferred]
    assert target.votes == votes
