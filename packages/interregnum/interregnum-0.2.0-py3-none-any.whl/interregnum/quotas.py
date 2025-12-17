#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Utils for the calculation of votes/seats quotas.

:ref:`References <interregnum_biblio>`
--------------------------------------

* [Gallagher:1992]_

----
"""

from __future__ import annotations
from typing import (
    Callable,
)
from dataclasses import dataclass
import enum
import operator

import math
from fractions import Fraction

from .types import Score
from .collections import FunctionCollection
from .exceptions import PreconditionError


class Inequality(enum.Enum):
    r"""Represents an (in)equality relation."""

    EQ = enum.auto()
    "(:math:`=`) equal"

    LT = enum.auto()
    "(:math:`<`) less than"

    LE = enum.auto()
    r"(:math:`\leq`) less or equal"

    GT = enum.auto()
    "(:math:`>`) greater than"

    GE = enum.auto()
    r"(:math:`\geq`) greater or equal"

    NE = enum.auto()
    r"(:math:`\neq`) not equal"

    TRUE = enum.auto()
    "Always `True`"

    FALSE = enum.auto()
    "Always `False`"

    def __str__(self) -> str:
        """Human representation for the operator."""
        if self == self.TRUE:
            return "true"
        if self == self.FALSE:
            return "false"
        if self == self.LT:
            op = "<"
        elif self == self.LE:
            op = "<="
        elif self == self.GT:
            op = ">"
        elif self == self.GE:
            op = ">="
        elif self == self.NE:
            op = "!="
        else:
            op = "="
        return op

    def __call__(self, first, second) -> bool:
        """Evaluate this inequality: `first` <op> `second`."""
        return self.check(first, second)

    def check(self, first, second) -> bool:
        """Check if `first` <self> `second`."""
        if self == self.TRUE:
            return True
        if self == self.FALSE:
            return False
        if self == self.LT:
            op = operator.lt
        elif self == self.LE:
            op = operator.le
        elif self == self.GT:
            op = operator.gt
        elif self == self.GE:
            op = operator.ge
        elif self == self.NE:
            op = operator.ne
        else:
            op = operator.eq
        return op(first, second)

    @classmethod
    def parse(cls, text: str) -> Inequality:
        """Parse inequality from string.

        Raises
        ------
        ValueError
            When `text` could not be parsed.
        """
        text = text.strip()
        if text == "<=":
            return cls.LE
        if text == "<":
            return cls.LT
        if text == ">=":
            return cls.GE
        if text == ">":
            return cls.GT
        if text in ("!=", "!==", "<>"):
            return cls.NE
        if text in ("=", "=="):
            return cls.EQ
        raise ValueError("Could not parse inequality")

    def __invert__(self) -> Inequality:
        """Negate this inequality."""
        return self.negate()

    def negate(self) -> Inequality:
        """Return the negated inequality."""
        neg: Inequality
        if self == Inequality.TRUE:
            neg = Inequality.FALSE
        elif self == Inequality.FALSE:
            neg = Inequality.TRUE
        elif self == Inequality.LT:
            neg = Inequality.GE
        elif self == Inequality.LE:
            neg = Inequality.GT
        elif self == Inequality.GT:
            neg = Inequality.LE
        elif self == Inequality.GE:
            neg = Inequality.LT
        elif self == Inequality.NE:
            neg = Inequality.EQ
        else:
            neg = Inequality.NE
        return neg


@dataclass
class Comparison:
    """An inequality `operator` and a `reference` value.

    <`operator`> `reference`
    """

    operator: Inequality
    "An inequality operator"

    reference: Score
    "A reference value (right side of the operator)"

    def reached(self, value) -> bool:
        """Return True if 'value' <op> <reference>."""
        return self.operator.check(value, self.reference)

    def __contains__(self, value):
        """Return True if value evaluates to True."""
        return self.reached(value)


Quota = Comparison
"A quota comparator"

QuotaFunction = Callable[[Score, Score], Quota]
"A function that returns a quota comparator"


quotas: FunctionCollection[QuotaFunction] = FunctionCollection()
"Collection for quota comparators"


def proportional_quota(pct: Score, votes: Score, *_args) -> Fraction:
    r"""Proportional quota.

    pct
        a percent value (N%)

    :math:`q = votes\frac{pct}{100}`
    """
    return Fraction(pct * votes, 100)


@quotas.register("hare")
def hare_quota(votes: Score, seats: Score) -> Comparison:
    r"""Hare quota comparison.

    :math:`q=[>]\frac{votes}{seats}`

    See [Gallagher:1992]_

    Collection keys:

    - `hare`
    """
    return Comparison(Inequality.GT, Fraction(votes, seats))


@quotas.register("majority")
def majority_quota(votes: Score, *_args) -> Comparison:
    r"""Absolute Majority quota.

    :math:`q=[>]\frac{votes}{2}`

    Collection keys:

    - `majority`
    """
    return Comparison(Inequality.GT, Fraction(votes, 2))


@quotas.register("hagenbach_bischoff", "hagenbach-bischoff", "droop_fractional")
def hagenbach_bischoff_quota(votes: Score, seats: Score) -> Comparison:
    r"""Hagenbach Bischoff quota (Droop fractional).

    :math:`q=[>]\frac{votes}{seats + 1}`

    Collection keys:

    - `hagenbach_bischoff`
    - `hagenbach-bischoff`
    - `droop_fractional`
    """
    return Comparison(Inequality.GT, Fraction(votes, seats + 1))


@quotas.register("droop")
def droop_quota(votes: Score, seats: Score) -> Comparison:
    r"""Droop quota.

    :math:`q=[\geq]1 + \lfloor \frac{votes}{seats + 1} \rfloor`

    See [Gallagher:1992]_

    Collection keys:

    - `droop`
    """
    return Comparison(Inequality.GE, 1 + math.floor(Fraction(votes, seats + 1)))


@quotas.register("imperiali")
def imperiali_quota(votes: Score, seats: Score) -> Comparison:
    r"""Imperali quota.

    :math:`q=[>]\frac{votes}{seats + 2}`

    See [Gallagher:1992]_

    Collection keys:

    - `imperiali`
    """
    return Comparison(Inequality.GT, Fraction(votes, seats + 2))


@quotas.register(
    "imperiali3",
    "imperiali_3",
)
def imperiali_3_quota(votes: Score, seats: Score) -> Comparison:
    r"""Reinforced Imperiali quota.

    :math:`q=[>]\frac{votes}{seats + 3}`

    Collection keys:

    - `imperiali3`
    - `imperiali_3`
    """
    return Comparison(Inequality.GT, Fraction(votes, (seats + 3)))


@quotas.register("infinity")
def infinity(_votes: Score, _seats: Score) -> Comparison:
    """Return a contradiction, impossible to satisfy.

    (for testing)

    Collection keys:

    - `infinity`
    """
    return Comparison(Inequality.FALSE, 0)


class QuotaStatus(enum.Enum):
    """Validity status for a quota."""

    OVER = enum.auto()
    EXACT = enum.auto()
    UNDER = enum.auto()


class QuotaResolverType(enum.Enum):
    """Type of quota resolver."""

    EXTREME = enum.auto()
    "find a quota at the range boundary"

    MIDPOINT = enum.auto()
    "find a quota in the middle of the range"

    @classmethod
    def parse(cls, key: str) -> QuotaResolverType:
        """Parse enum from a string."""
        key = key.strip().lower()
        if key == "extreme":
            return cls.EXTREME
        return cls.MIDPOINT


def _check_range(name: str, value):
    if value < 0:
        raise PreconditionError(f"{name} [{value}] must be >= 0")


class QuotaResolver:
    """Find a representative for a quota range."""

    def __init__(self, strategy: str | QuotaResolverType = "midpoint", nice_quota: bool = True):
        """Create a resolve using a `strategy`.

        If `nice_quota` is `True`, find a value with the least number of digits as possible.
        """
        if not isinstance(strategy, QuotaResolverType):
            self.strategy = QuotaResolverType.parse(strategy)
        else:
            self.strategy = strategy
        self.nice_quota = nice_quota

    def find(self, min_quota: Score, max_quota: float | Score, status: QuotaStatus) -> Score:
        """Get a quota using the resolver strategy."""
        _check_range("min_quota", min_quota)
        _check_range("max_quota", max_quota)
        if min_quota == max_quota:
            return min_quota
        if self.strategy == QuotaResolverType.EXTREME:
            return self.quota_extreme(min_quota, max_quota, status)
        return self.quota_midpoint(min_quota, max_quota)

    def quota_midpoint(self, min_quota: Score, max_quota: float | Score) -> Score:
        """Get a quota in the middle of the range."""
        if isinstance(max_quota, float):
            try:
                max_quota = Fraction(max_quota)
            except OverflowError:
                # inf
                max_quota = min_quota + 2
        quota = Fraction(min_quota + max_quota, 2)
        return quota

    def quota_extreme(
        self, min_quota: Score, max_quota: float | Score, status: QuotaStatus
    ) -> Score:
        """Get a quota at the range boundary."""
        if status == QuotaStatus.OVER:
            # min multiplier -> max quota
            if isinstance(max_quota, float):
                try:
                    max_quota = Fraction(max_quota)
                except OverflowError:
                    # inf
                    return min_quota + 1
            return max_quota
        if status == QuotaStatus.UNDER:
            # max multiplier -> min quota
            return min_quota
        return self.quota_midpoint(min_quota, max_quota)

    @staticmethod
    def nice(quota: Score, min_quota: Score, max_quota: float | Score) -> Score:
        """Try to get a nice quota number."""
        if (quota < min_quota) or (quota > max_quota):
            raise PreconditionError(
                f"quota ({quota}) is not within the provided range [{min_quota}, {max_quota}]"
            )
        n_digits: int = -math.floor(math.log10(quota))
        while True:
            output = round(quota, n_digits)
            assert isinstance(output, (int, Fraction))
            if min_quota <= output <= max_quota:
                break
            n_digits += 1
        return output
