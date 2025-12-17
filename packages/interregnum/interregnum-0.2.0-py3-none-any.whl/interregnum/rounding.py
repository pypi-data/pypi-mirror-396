#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Rounding and signpost sequence functions.

:ref:`References <interregnum_biblio>`
--------------------------------------

* [DorfleitnerKlein:1997]_
* [Zachariasen:2006]_

----
"""

from __future__ import annotations
from typing import (
    Callable,
    Final,
    Literal,
)
import math
from fractions import Fraction
from typing_extensions import TypeIs, override

from .types import Score
from .collections import FunctionCollection


RoundingFunction = Callable[[Score], Score]
"Any function that makes a rounding operation."


roundings: FunctionCollection[RoundingFunction] = FunctionCollection()
"Collection of rounding functions."

roundings.add("round", round)
roundings.add("int", int)
roundings.add("floor", math.floor)
roundings.add("ceil", math.ceil)


@roundings.register("noop", "none")
def noop(score: Score) -> Score:
    """Return the same `score`."""
    return score


FRAC_ZERO: Final[Fraction] = Fraction(0)
"Zero value as `Fraction`."

FRAC_INFTY: Final[Literal[None]] = None
"Infinity value for `Fraction` represented as `None`"


ScoreWithInf = Score | None
"A score with infinity values"


def is_finite(x: ScoreWithInf) -> TypeIs[Score]:
    """Return True if `x` is finite."""
    return x is not FRAC_INFTY


def as_fraction(numerator: Score, denominator: Score) -> ScoreWithInf:
    """Convert numerator and denominator into a fraction.

    Division by zero will return Infinity (FRAC_INFTY)
    """
    if denominator == FRAC_ZERO:
        return FRAC_INFTY
    return Fraction(numerator, denominator)


class RoundingWithSignpost:
    r"""Rounding function with associated signpost sequence.

    See [DorfleitnerKlein:1997]_ and [Zachariasen:2006]_:

    Rounding function: :math:`R(x)=k` for :math:`x \in [s_{k-1}, s_k)` and
    :math:`k \in \mathbb{N}_0` and a signpost sequence :math:`s_k \in [k, k+1]`.

    """

    def __call__(self, x: Score) -> int:
        """Convert `x` into a rounded integer value."""
        raise NotImplementedError()

    def incrementation(self, k: int, w: Score) -> ScoreWithInf:
        r"""Incrementation criterion.

        .. math::

            I(k, w) \rightarrow \frac{s_k}{w}
        """
        return as_fraction(self.unbounded_signpost(k), w)

    def decrementation(self, k: int, w: Score) -> ScoreWithInf:
        r"""Decrementation criterion.

        .. math::

            D(k, w) \rightarrow \frac{s_{k-1}}{w}
        """
        return as_fraction(self.unbounded_signpost(k - 1), w)

    def signpost(self, k: int) -> Score:
        r"""Bounded signpost sequence :math:`s_k`.

        :math:`s_k = 0` for :math:`k \leq 0`
        """
        return FRAC_ZERO if k <= 0 else self.unbounded_signpost(k)

    def unbounded_signpost(self, k: int) -> Score:
        """Unbounded signpost sequence :math:`s_k`."""
        raise NotImplementedError()


class ArithmeticMeanRoundingFunction(RoundingWithSignpost):
    r"""Arithmetic-mean rounding methods.

    See [DorfleitnerKlein:1997]_:

    .. math::

        s^{(q)}_k = (1-q)k+q(k+1) = k+q

    for :math:`q \in [0, 1]` and :math:`k \in \mathbb{N}_0`.
    """

    def __init__(self, q: Fraction):
        self.q = q

    @override
    def __call__(self, x: Score) -> int:
        return math.floor(x + 1 - self.q)

    @override
    def unbounded_signpost(self, k: int) -> Score:
        return k + self.q

    @override
    def signpost(self, k: int) -> Score:
        s = self.unbounded_signpost(k)
        if s <= 0:
            return FRAC_ZERO
        return s


signposts: FunctionCollection[RoundingWithSignpost] = FunctionCollection()
"Collection for rounding functions with signposts"

RND_ADAMS = ArithmeticMeanRoundingFunction(q=Fraction(0))
signposts.add("adams", RND_ADAMS)

RND_WEBSTER = ArithmeticMeanRoundingFunction(q=Fraction(1, 2))
RND_SAINTE_LAGUE = RND_WEBSTER
signposts.add("webster", RND_WEBSTER)
signposts.add("sainte_lague", RND_WEBSTER)
signposts.add("sainte_laguë", RND_WEBSTER)

RND_JEFFERSON = ArithmeticMeanRoundingFunction(q=Fraction(1))
RND_DHONDT = RND_JEFFERSON
signposts.add("jefferson", RND_JEFFERSON)
signposts.add("dhondt", RND_JEFFERSON)

for _key, _value in signposts.items.items():
    roundings.add(_key, _value)
