#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

r"""Transfer functions for Single Transferable Vote.

:ref:`References <interregnum_biblio>`
--------------------------------------

* [Gallagher:1992]_
* [EireSTV]_
* [AusProp]_
* [Miragliotta2002]_

----
"""

from __future__ import annotations
from typing import (
    Callable,
)
from collections import defaultdict
from fractions import Fraction
from functools import partial
from ...types import Score, AnyName
from ....rounding import RoundingFunction
from ....collections import FunctionCollection
from ..types import Preference
from .parcel import (
    Parcel,
    CandidateParcels,
)


TTransferFunction = Callable[
    [RoundingFunction, dict[AnyName, CandidateParcels[AnyName]], AnyName, Score | None],
    dict[AnyName | None, CandidateParcels[AnyName]],
]
"A transfer function"


transfers: FunctionCollection[TTransferFunction] = FunctionCollection()
"Collection of transfers"


def inclusive_gregory_transfer(
    weighted: bool,
    round_f: RoundingFunction,
    table: dict[AnyName, CandidateParcels[AnyName]],
    source: AnyName,
    surplus: Score | None = None,
) -> dict[AnyName | None, CandidateParcels[AnyName]]:
    """Weighted and Unweighted Inclusive Gregory transfer method.

    Args
    ----
    weighted
        choose either weighted or unweighted variable
    round_f
        rounding function to convert from transfer values to votes
    table
        parcels for each candidate
    source
        candidate who will transfer his/her votes
    surplus
        surplus to transfer. If None, transfer value weight will be set to 1


    See [EireSTV]_, [AusProp]_, [Miragliotta2002]_.

    :data:`.transfers` collection keys:

    unweighted:

    - `unweighted_gregory`
    - `inclusive_gregory`
    - `unweighted_gregory_transfer`

    weighted:

    - `weighted_gregory`
    - `weighted_inclusive_gregory`
    """
    removable = {source}
    removable.update(k for k, p in table.items() if not p.is_eligible())

    source_data = table[source]

    # unweighted inclusive gregory: total = number of ballot papers
    # weighted inclusive gregory: total = number of effective votes
    if surplus:
        total = source_data.total_ballot_papers() if not weighted else source_data.votes
        keep_value = Fraction(surplus, total)
    else:
        keep_value = Fraction(1)

    bundles: dict[AnyName | None, CandidateParcels[AnyName]] = defaultdict(CandidateParcels)
    for parcel in source_data.parcels:
        for owner, batches in parcel.group_by_next_preference(removable).items():
            subparcel = Parcel(
                batches=Preference.compact_preferences(batches, skip_empty=False),
                weight=keep_value * parcel.weight,
            )
            subparcel.votes = keep_value * sum(x.votes for x in subparcel.batches)
            if weighted:
                subparcel.votes *= parcel.weight
            if not subparcel.votes:
                continue
            bundle = bundles[owner]
            bundle.parcels.append(subparcel)
            bundle.votes += subparcel.votes

    for bundle in bundles.values():
        bundle.votes = round_f(bundle.votes)

    return bundles


unweighted_gregory_transfer = partial(inclusive_gregory_transfer, False)
transfers.add("unweighted_gregory", unweighted_gregory_transfer)
transfers.add("inclusive_gregory", unweighted_gregory_transfer)
transfers.add("unweighted_inclusive_gregory", unweighted_gregory_transfer)

weighted_gregory_transfer = partial(inclusive_gregory_transfer, True)
transfers.add("weighted_gregory", weighted_gregory_transfer)
transfers.add("weighted_inclusive_gregory", weighted_gregory_transfer)


@transfers.register(
    "gregory",
    "last_parcel",
)
def gregory_transfer(
    round_f: RoundingFunction,
    table: dict[AnyName, CandidateParcels[AnyName]],
    source: AnyName,
    surplus: Score | None = None,
) -> dict[AnyName | None, CandidateParcels[AnyName]]:
    """Gregory transfer method ("Last Parcel").

    Args
    ----
    round_f
        rounding function to convert from transfer values to votes
    table
        parcels for each candidate
    source
        candidate who will transfer his/her votes
    surplus
        surplus to transfer. If None, transfer value weight will be set to 1


    See [EireSTV]_, [AusProp]_, [Miragliotta2002]_.

    :data:`.transfers` collection keys:

    - gregory
    - last_parcel
    """
    removable = {source}
    removable.update(k for k, p in table.items() if not p.is_eligible())

    source_data = table[source]
    if not source_data.parcels:
        return {}

    group_id = source_data.parcels[-1].group_id
    parcels = [p for p in source_data.parcels if p.group_id == group_id]

    total = sum(x.total_ballot_papers() for x in parcels)

    if surplus:
        keep_value = Fraction(min(surplus, total), total)
    else:
        keep_value = Fraction(1)

    bundles: dict[AnyName | None, CandidateParcels[AnyName]] = defaultdict(CandidateParcels)

    for parcel in parcels:
        for owner, batches in parcel.group_by_next_preference(removable).items():
            subparcel = Parcel(
                batches=Preference.compact_preferences(batches, skip_empty=False),
                weight=keep_value * parcel.weight,
            )
            subparcel.votes = keep_value * sum(x.votes for x in subparcel.batches)
            if not subparcel.votes:
                continue
            bundle = bundles[owner]
            bundle.parcels.append(subparcel)
            bundle.votes += subparcel.votes

    for bundle in bundles.values():
        bundle.votes = round_f(bundle.votes)

    return bundles
