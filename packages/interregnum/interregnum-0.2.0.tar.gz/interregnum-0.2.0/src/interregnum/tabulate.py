#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Utils for showing tabulated data."""

from __future__ import annotations
from typing import Sequence


def tabulate(
    rows: Sequence[Sequence[str]],
    colsep: str = " ",
    rowsep: str = "\n",
    headersep: str | None = None,
) -> str:
    """Return a displayable representation of bidimensional data.

    Useful for debugging.

    Args
    ----
    rows:
        bidimensional data
    colsep:
        columns separator
    rowsep:
        rows separator
    headersep:
        if this separator exists, will be printed after the first row.
    """
    n_cols = max(len(cols) for cols in rows)
    col_size = [0] * n_cols
    for cols in rows:
        for idx_c, col in enumerate(cols):
            col_size[idx_c] = max(col_size[idx_c], len(col))

    out = []
    for idx_r, cols in enumerate(rows):
        if (idx_r == 1) and headersep:
            out.append(colsep.join((headersep * n)[:n] for n in col_size))
        out.append(colsep.join(x.rjust(col_size[idx]) for idx, x in enumerate(cols)))
    return rowsep.join(out) + "\n"
