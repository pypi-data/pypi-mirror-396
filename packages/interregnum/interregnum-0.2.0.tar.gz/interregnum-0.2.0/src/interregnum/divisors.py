#!/usr/bin/source python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

r"""Divisors for Highest-Averages method.

:ref:`References <interregnum_biblio>`
--------------------------------------

* [Gallagher:1992]_
* [Denmark:2011]_
* [Norway:2023]_
* [KohlerZeh:2012]_
* [Reitzig:2014]_

----
"""

from typing import (
    Union,
    Iterator,
    Callable,
    TypeVar,
    Generic,
)
import math
from fractions import Fraction
from .collections import FunctionCollection
from .exceptions import PreconditionError


Divisor = Union[int, float, Fraction]
"Allowed types for divisors"

DivisorFunction = Callable[[int], Divisor]
"Functions that return a divisor for a number of seats"

divisors: FunctionCollection[DivisorFunction] = FunctionCollection()
"Collection of divisor functions"


_Divisor = TypeVar("_Divisor", bound=Divisor)


class DivisorIterator(Generic[_Divisor]):
    """A wrapper for a divisor sequence iterator."""

    def __init__(self, divisor_f: Callable[[int], _Divisor]):
        """Create this iterator from `divisor_f`."""
        self._divisor_f_ = divisor_f

    @staticmethod
    def _check_seats(seats: int):
        if seats < 0:
            raise PreconditionError(f"step [{seats}] is not a non-negative integer")

    def divisor(self, seats: int = 0) -> _Divisor:
        """Return a divisor for `seats`.

        Raises
        ------
        PreconditionError
            When seats is less than 0.
        """
        self._check_seats(seats)
        return self._divisor_f_(seats)

    def sequence(self, seats: int = 0) -> Iterator[_Divisor]:
        """Return a divisor iterator starting from `seats`.

        Raises
        ------
        PreconditionError
            When seats is less than 0.
        """
        self._check_seats(seats)
        return self._sequence(seats)

    def __call__(self, *args, **kwargs) -> Iterator[_Divisor]:
        """Return a divisor iterator."""
        return self.sequence(*args, **kwargs)

    def _sequence(self, seats: int) -> Iterator[_Divisor]:
        while True:
            yield self._divisor_f_(seats)
            seats += 1


CallDivisorIterator = Callable[[], DivisorIterator[Divisor]]
"A function that returns a divisor iterator"


# Collection of divisor sequences
divisor_iterators: FunctionCollection[CallDivisorIterator] = FunctionCollection()
"Collection of divisor iterators"


@divisors.register(
    "dhondt",
    "d'hondt",
    "jefferson",
    "greatest_divisors",
    "greatest-divisors",
)
def dhondt_divisor(seats: int) -> int:
    r"""D'Hondt / Jefferson divisor / Greatest divisors.

    :math:`d(seats) = seats + 1`

    Sequence: 1, 2, 3, 4, ... for :math:`seats \in \{0, 1, 2, 3, \dots\}`

    See [Gallagher:1992]_ and [Reitzig:2014]_

    Args
    ----
    seats
        assigned seats

    Return
    ------
    :
        divisor for the next unassigned seat


    :data:`.divisors` collection keys:

    - `dhondt`
    - `d'hondt`
    - `jefferson`
    - `greatest_divisors`
    - `greatest-divisors`
    """
    return seats + 1


@divisor_iterators.register("dhondt", "d'hondt", "jefferson")
class DhondtDivisorIterator(DivisorIterator[int]):
    """Iterator for the d'Hondt divisor.

    :data:`.divisor_iterators` collection keys:

    - `dhondt`
    - `d'hondt`
    - `jefferson`
    """

    def __init__(self):
        """Create a D'Hondt divisor iterator."""
        super().__init__(dhondt_divisor)

    def _sequence(self, seats: int) -> Iterator[int]:
        divisor = self._divisor_f_(seats)
        while True:
            yield divisor
            divisor += 1


@divisors.register("sainte_lague", "sainte-lague", "sainte_laguë", "sainte-laguë", "webster")
def sainte_lague_divisor(seats: int) -> int:
    r"""Sainte-Laguë / Webster divisor.

    :math:`d(seats) = 2 seats + 1`

    Sequence: 1, 3, 5, 7, ... for :math:`seats \in \{0, 1, 2, 3, \dots\}`

    See [Gallagher:1992]_

    Args
    ----
    seats
        assigned seats

    Return
    ------
    :
        divisor for the next unassigned seat


    :data:`.divisors` collection keys:

    - `sainte_lague`
    - `sainte-lague`
    - `sainte_laguë`
    - `sainte-laguë`
    - `webster`
    """
    return 2 * seats + 1


@divisor_iterators.register(
    "sainte_lague", "sainte-lague", "sainte_laguë", "sainte-laguë", "webster"
)
class SainteLagueDivisorIterator(DivisorIterator[int]):
    """Iterator for the Sainte-Laguë divisor.

    :data:`.divisor_iterators` collection keys:

    - `sainte_lague`
    - `sainte-lague`
    - `sainte_laguë`
    - `sainte-laguë`
    - `webster`
    """

    def __init__(self):
        """Create a Sainte-Laguë divisor iterator."""
        super().__init__(sainte_lague_divisor)

    def _sequence(self, seats: int) -> Iterator[int]:
        divisor = self._divisor_f_(seats)
        while True:
            yield divisor
            divisor += 2


@divisors.register("sainte_lague_1.4", "sainte-lague-1.4", "sainte_laguë_1.4", "sainte-laguë-1.4")
def sainte_lague_14_divisor(seats: int) -> Divisor:
    r"""Sainte-Laguë divisor with 1.4 for the first seat.

    :math:`d(0) = 1.4`

    :math:`d(seats) = 2 seats + 1` for :math:`seats > 0`

    Sequence: 1.4, 3, 5, 7, ... for :math:`seats \in \{0, 1, 2, 3, \dots\}`

    See [Norway:2023]_ and [Reitzig:2014]_

    Args
    ----
    seats
        assigned seats

    Return
    ------
    :
        divisor for the next unassigned seat


    :data:`.divisors` collection keys:

    - `sainte_lague_1.4`
    - `sainte-lague-1.4`
    - `sainte_laguë_1.4`
    - `sainte-laguë-1.4`
    """
    if seats == 0:
        return Fraction("1.4")
    return 2 * seats + 1


@divisor_iterators.register(
    "sainte_lague_1.4", "sainte-lague-1.4", "sainte_laguë_1.4", "sainte-laguë-1.4"
)
class SainteLague14DivisorIterator(DivisorIterator[int]):
    """Iterator for the Sainte-Laguë 1.4 divisor.

    :data:`.divisor_iterators` collection keys:

    - `sainte_lague_1.4`
    - `sainte-lague-1.4`
    - `sainte_laguë_1.4`
    - `sainte-laguë-1.4`
    """

    def __init__(self):
        """Create a Sainte-Laguë divisor iterator with 1.4 as first divisor."""
        super().__init__(sainte_lague_14_divisor)

    def _sequence(self, seats: int) -> Iterator[int]:
        divisor = self._divisor_f_(seats)
        if seats == 0:
            yield divisor
            divisor = self._divisor_f_(1)
        while True:
            yield divisor
            divisor += 2


@divisors.register("imperiali")
def imperiali_divisor(seats: int) -> int:
    r"""Imperiali divisor.

    :math:`d(seats) = seats + 2`

    Sequence: 2, 3, 4, 5, ... for :math:`seats \in \{0, 1, 2, 3, \dots\}`

    See [Reitzig:2014]_

    Args
    ----
    seats
        assigned seats

    Return
    ------
    :
        divisor for the next unassigned seat


    :data:`.divisors` collection keys:

    - `imperiali`
    """
    return seats + 2


@divisor_iterators.register("imperiali")
class ImperialiDivisorIterator(DivisorIterator[int]):
    """Iterator for the Imperiali divisor.

    :data:`.divisor_iterators` collection keys:

    - `imperiali`
    """

    def __init__(self):
        """Create an Imperiali divisor iterator."""
        super().__init__(imperiali_divisor)

    def _sequence(self, seats: int) -> Iterator[int]:
        divisor = self._divisor_f_(seats)
        while True:
            yield divisor
            divisor += 1


@divisors.register(
    "belgian-imperiali",
    "belgian_imperiali",
)
def belgian_imperiali_divisor(seats: int) -> Fraction:
    r"""Belgian Imperiali divisor.

    :math:`d(seats) = \frac{seats + 1}{2}`

    Sequence: 1, 1.5, 2, 2.5, ... for :math:`seats \in \{0, 1, 2, 3, \dots\}`

    See [Gallagher:1992]_


    Args
    ----
    seats
        assigned seats

    Return
    ------
    :
        divisor for the next unassigned seat


    :data:`.divisors` collection keys:

    - `belgian-imperiali`
    - `belgian_imperiali`
    """
    return Fraction(seats + 1, 2)


@divisor_iterators.register("belgian-imperiali", "belgian_imperiali")
class BelgianImperialiDivisorIterator(DivisorIterator[Fraction]):
    """Iterator for the Imperiali divisor.

    :data:`.divisor_iterators` collection keys:

    - `imperiali`
    """

    def __init__(self):
        """Create a Belgian Imperiali divisor iterator."""
        super().__init__(imperiali_divisor)

    def _sequence(self, seats: int) -> Iterator[Fraction]:
        delta = Fraction(1, 2)
        divisor = self._divisor_f_(seats)
        while True:
            yield divisor
            divisor += delta


@divisors.register("danish")
def danish_divisor(seats: int) -> int:
    r"""Danish divisor.

    :math:`d(seats) = 3 seats + 1`

    Sequence: 1, 4, 7, 10, 13, ... for :math:`seats \in \{0, 1, 2, 3, \dots\}`

    See [Denmark:2011]_, [Gallagher:1992]_ and [Reitzig:2014]_

    Args
    ----
    seats
        assigned seats

    Return
    ------
    :
        divisor for the next unassigned seat


    :data:`.divisors` collection keys:

    - `danish`
    """
    return 3 * seats + 1


@divisor_iterators.register("danish")
class DanishDivisorIterator(DivisorIterator[int]):
    """Iterator for Danish divisor.

    :data:`.divisor_iterators` collection keys:

    - `danish`
    """

    def __init__(self):
        """Create a Danish divisor iterator."""
        super().__init__(danish_divisor)

    def _sequence(self, seats: int) -> Iterator[int]:
        divisor = self._divisor_f_(seats)
        while True:
            yield divisor
            divisor += 3


@divisors.register("dean", "harmonic-mean", "harmonic_mean")
def dean_divisor(seats: int) -> Fraction:
    r"""Dean divisor.

    :math:`d(seats) = \frac{2 seats (seats + 1)}{2 seats + 1}`

    See [KohlerZeh:2012]_ and [Reitzig:2014]_

    Args
    ----
    seats
        assigned seats

    Return
    ------
    :
        divisor for the next unassigned seat


    :data:`.divisors` collection keys:

    - `dean`
    - `harmonic-mean`
    - `harmonic_mean`
    """
    return Fraction(2 * seats * (seats + 1), 2 * seats + 1)
    # :math:`d(seats) = \frac{2}{\frac{1}{seats} + \frac{1}{seats-1}}`
    # return Fraction(2, Fraction(1, seats) + Fraction(1, seats - 1))


@divisors.register(
    "huntington_hill",
    "huntington-hill",
    "equal-proportions",
    "equal_proportions",
)
def huntington_hill_divisor(seats: int) -> float:
    r"""Huntington-Hill / Equal proportions.

    :math:`d(seats) = \sqrt{seats (seats + 1)}`

    Sequence: 0, 1.414, 2.449, 3.464, 4.472, ... for :math:`seats \in \{0, 1, 2, 3, 4, \dots\}`

    See [KohlerZeh:2012]_, [Gallagher:1992]_ and [Reitzig:2014]_

    Args
    ----
    seats
        assigned seats

    Return
    ------
    :
        divisor for the next unassigned seat


    :data:`.divisors` collection keys:

    - `huntington_hill`
    - `huntington-hill`
    - `equal-proportions`
    - `equal_proportions`
    """
    return math.sqrt(seats * (seats + 1))


@divisors.register("huntington_hill1", "huntington-hill1")
def huntington_hill_1_divisor(seats: int) -> float:
    r"""Huntington-Hill + 1 / Equal proportions + 1.

    This version starts at 1.414.

    :math:`d(seats) = \sqrt{(seats + 1) (seats + 2)}`

    Sequence: 1.414, 2.449, 3.464, 4.472, ... for :math:`seats \in \{0, 1, 2, 3, \dots\}`

    Args
    ----
    seats
        assigned seats

    Return
    ------
    :
        divisor for the next unassigned seat


    :data:`.divisors` collection keys:

    - `huntington_hill1`
    - `huntington-hill1`
    """
    return huntington_hill_divisor(seats + 1)


@divisors.register(
    "modified-sainte-laguë",
    "modified_sainte_laguë",
    "modified-sainte-lague",
    "modified_sainte_lague",
)
def modified_sainte_lague_divisor(seats: int) -> Fraction:
    r"""Return a modified Sainte-Laguë divisor.

    :math:`d(0) = 1`

    :math:`d(seats) = \frac{10(seats + 1) - 5}{7}` for :math:`seats > 0`

    Sequence: 1, 2.14, 3.57, 5, 6.43 for :math:`seats \in \{0, 1, 2, 3, 4, \dots\}`

    See [Gallagher:1992]_

    :data:`.divisors` collection keys:

    - `modified-sainte-laguë`
    - `modified_sainte_laguë`
    - `modified-sainte-lague`
    - `modified_sainte_lague`
    """
    if seats == 0:
        return Fraction(1)
    return Fraction(10 * seats + 5, 7)


@divisors.register(
    "adams",
    "smallest_divisors",
    "smallest-divisors",
)
def adams_divisor(seats: int) -> int:
    r"""Adams divisor / Smallest divisors.

    :math:`d(seats) = seats`

    Sequence: 0, 1, 2, 3, 4, ... for :math:`seats \in \{0, 1, 2, 3, 4, \dots\}`

    See [Gallagher:1992]_

    :data:`.divisors` collection keys:

    - `adams`
    - `smallest-divisors`
    - `smallest_divisors`
    """
    return seats


@divisor_iterators.register("adams")
class AdamsDivisorIterator(DivisorIterator[int]):
    """Iterator for the Adams divisor.

    :data:`.divisor_iterators` collection keys:

    - `adams`
    """

    def __init__(self):
        """Create an Adams divisor iterator."""
        super().__init__(adams_divisor)

    def _sequence(self, seats: int) -> Iterator[int]:
        divisor = self._divisor_f_(seats)
        while True:
            yield divisor
            divisor += 1
