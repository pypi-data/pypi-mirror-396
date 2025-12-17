#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Common structures for allocation methods."""

from __future__ import annotations
import dataclasses as dt
from typing import (
    Any,
    Sequence,
    Callable,
    Iterable,
    Iterator,
    TypeVar,
    Generic,
    Collection,
    cast,
)
import enum
import warnings

from ..random import (
    Dice,
    RandomSeed,
)
from ..types import SortHash, Score
from ..exceptions import PreconditionError, PreconditionWarning
from ..collections import FunctionCollection
from ..logging import logger


AnyName = TypeVar("AnyName", bound=SortHash)
"A type for names"

AnotherName = TypeVar("AnotherName", bound=SortHash)
"Alternative type for names"

AnyEvent = TypeVar("AnyEvent")
"Alternative type for events"


CandTuple = tuple[AnyName, Score] | tuple[AnyName, Score, int]
"A tuple with candidate information (name, votes, and ocassionally, initial seats)"


@dt.dataclass(frozen=True, eq=True, order=True)
class Candidate(Generic[AnyName]):
    """A candidate for allocations based on single votes."""

    name: AnyName
    "Candidate identifier"

    votes: Score
    "Candidate received votes"

    seats: int = 0
    "Candidate allocated seats"

    def with_seats(self, seats: int) -> Candidate[AnyName]:
        """Return the same candidate with the provided `seats`.

        Args
        ----
        seats
            new number of seats
        """
        if seats == self.seats:
            return self
        return dt.replace(self, seats=seats)

    def with_name(self, name: AnotherName) -> Candidate[AnotherName]:
        """Return the same candidate with a different `name`.

        Args
        ----
        name
            new name
        """
        if self.name == name:
            return cast(Candidate[AnotherName], self)
        return Candidate(name=name, votes=self.votes, seats=self.seats)

    def with_votes(self, votes: Score) -> Candidate[AnyName]:
        """Return the same candidate with a different number of `votes`.

        Args
        ----
        votes
            new number of votes
        """
        return dt.replace(self, votes=votes)

    def add_seats(self, increment: int) -> Candidate[AnyName]:
        """Return a candidate with :obj:`seats` plus `increment`.

        Args
        ----
        increment
            seats increment relative to the current :obj:`seats`.
        """
        return self.with_seats(self.seats + increment)

    @classmethod
    def make_input(
        cls, candidates: Iterable[CandTuple | Candidate[AnyName]], initialized: bool = False
    ) -> Sequence[Candidate[AnyName]]:
        """Make candidates from an iterable of iterables.

        Args
        ----
        candidates
            Iterable of structures compatible with :class:`.Candidate`.
        initialized
            If `False`, a warning will be emitted if any candidate has seats
        """
        output = [cls(*cast(CandTuple, x)) if not isinstance(x, cls) else x for x in candidates]
        if not initialized and any(c.seats for c in output):
            warnings.warn(
                PreconditionWarning("Already allocated seats will be ignored"), stacklevel=2
            )
        # if not output:
        #     raise PreconditionError("candidate list is empty")
        return output

    def merge(self, other: Candidate[AnyName]) -> Candidate[AnyName]:
        """Return this candidate with the votes and seats summed to `other`.

        Args
        ----
        other
            second candidate
        """
        return Candidate(
            name=self.name,
            votes=self.votes + other.votes,
            seats=self.seats + other.seats,
        )


CandLike = CandTuple | Candidate[AnyName]
"A :class:`.Candidate` or something convertible to a candidate."


class CandidateFilter(Generic[AnyName, AnyEvent]):
    """Candidate filter for restrictions in methods that allocate one seat at a time."""

    def start(self) -> Sequence[AnyEvent]:
        """Start this filter.

        Return
        ------
        :
            A sequence of events associated to this action.
        """
        raise NotImplementedError()

    def update(self, cand: Candidate[AnyName]) -> Sequence[AnyEvent]:
        """Update candidate seats.

        Return
        ------
        :
            A sequence of events associated to this action.
        """
        raise NotImplementedError()

    def is_valid(self, name: AnyName) -> bool:
        """Check if a candidate can continue in the allocation.

        Args
        ----
        name
            A candidate name

        Return
        ------
        :
            Return `True` if the candidate identified by `name` is not excluded from the allocation.
        """
        raise NotImplementedError()

    def exclusion_list(self) -> Collection[AnyName]:
        """Return the list of excluded candidates at the current allocation stage."""
        raise NotImplementedError()


@dt.dataclass
class Summary(Generic[AnyName]):
    """A summary for an allocation list."""

    names: set[AnyName]
    "Set of contenders' ids"

    votes: Score
    "Total number of votes"

    seats: int
    "Total number of seats"

    @classmethod
    def build(cls, candidates: Iterable[CandLike] | None = None) -> Summary[AnyName]:
        """Build a summary for `candidates`.

        Args
        ----
        candidates
            list of candidates
        """
        names = set()
        votes: Score = 0
        seats = 0
        if candidates is not None:
            try:
                for cand in Candidate.make_input(candidates):
                    seats += cand.seats
                    votes += cand.votes
                    names.add(cand.name)
            except PreconditionError:
                pass
        return cls(names=names, votes=votes, seats=seats)


Data = TypeVar("Data")
"A type for data"


@dt.dataclass
class Result(Generic[AnyName, Data]):
    """Result information returned by an allocation method."""

    allocation: Sequence[Candidate[AnyName]]
    "Allocation result"

    data: Data | None = None
    "Additional data"


AnyResult = TypeVar("AnyResult", bound=Result)
"A result type"


@dt.dataclass
class NonDeterministicResult(Result[AnyName, Data]):
    """Result data for non deterministic allocators."""

    deterministic: bool = True
    "`True` if the allocation result was deterministic"

    random_state: Any | None = None
    "Initial random state used by the random generator"


class Input(enum.Flag):
    """Standard input arguments for methods."""

    NONE = 0
    RANDOM_SEED = enum.auto()
    SEATS = enum.auto()
    CANDIDATES = enum.auto()
    CANDIDATE_LIST = enum.auto()
    PREFERENCES = enum.auto()
    PARTY_SEATS = enum.auto()
    DISTRICT_SEATS = enum.auto()
    INITIAL_SEATS = enum.auto()
    INNER_INITIAL_SEATS = enum.auto()
    SKIP_INITIAL_SEATS = enum.auto()
    FILTER_F = enum.auto()
    TOTAL_VOTES = enum.auto()
    EXCLUDE_CANDIDATES = enum.auto()
    MAX_SEATS = enum.auto()
    CONSTRAINTS = enum.auto()
    PARTY_NAME_F = enum.auto()
    DISTRICT_NAME_F = enum.auto()
    CANDIDATE_NAME_F = enum.auto()
    MAX_BALLOTS_SIZE = enum.auto()

    @property
    def param_name(self) -> str:
        """Get the associated param name."""
        assert self.name
        return self.name.lower()


def check_inputs(required: Input, flags: Input):
    """Raise a :exc:`.PreconditionError` if `flags` does not contain `required`."""
    if required not in flags:
        raise PreconditionError(f"required input not found: {required}")


allocators: FunctionCollection[Callable[..., Allocator]] = FunctionCollection()
"Allocators collection"


class Allocator(Generic[AnyName, Data]):
    """Base class for seats allocators.

    An allocator creates an allocation result from the allowed inputs.

    It provides :meth:`__call__` as an alias to :meth:`calc`.
    """

    calc: Callable[..., Result[AnyName, Data]]
    "A method that returns an allocation result."

    def __init__(self, required_input: Input, optional_input: Input):
        """Allocator constructor.

        Its :meth:`calc` method requires `required_input` as arguments and admits `optional_input`.

        Args
        ----
        required_input
            Flags describing the types of inputs the method requires
        optional_input
            Flags describing the types of inputs the method optially admits
        """
        self._required_input = required_input
        self._optional_input = optional_input & ~required_input
        self._admitted_input = required_input | optional_input

    def __call__(self, *args, **kwargs) -> Result[AnyName, Data]:
        """Invoke the :meth:`calc` method."""
        logger.debug("calling allocator %s", self)
        return self.calc(*args, **kwargs)

    @property
    def required_input(self) -> Input:
        """Return required arguments for the method :meth:`calc`."""
        return self._required_input

    @property
    def optional_input(self) -> Input:
        """Return optional arguments for the method :meth:`calc`."""
        return self._optional_input

    @property
    def admitted_input(self) -> Input:
        """Return all the arguments that the method :meth:`calc` admits."""
        return self._admitted_input

    def get_model_params(self) -> Iterator[tuple[str, Any]]:
        """Return formal parameters."""
        for name, value in vars(self).items():
            if name.startswith("_") or name.endswith("_"):
                continue
            yield name, value

    def __repr__(self) -> str:
        """Return representation of the model with formal parameters."""
        name = self.__class__.__name__
        params = ", ".join(f"{k}={v}" for k, v in self.get_model_params())
        return f"<{name}({params}) at 0x{id(self):x}>"


_Tied = TypeVar("_Tied", bound=SortHash)


def choose_randomly(rng: Dice, candidates: Iterable[_Tied], limit: int) -> dict[str, list[_Tied]]:
    """Choose `limit` candidates randomly using the `rng` dice.

    Args
    ----
    rng
        a random generator
    candidates
        list of candidates
    limit
        number of candidates to be chosen

    Return
    ------
    :
        winners grouped by criterion
    """
    # normalize sorting by name for reproducibility
    winners = sorted(candidates)
    if limit == 1:
        out = [rng().choice(winners)]
    else:
        rng().shuffle(winners)
        out = winners[:limit]
    return {"tie_break_random": out}


class CalculationState:
    """A calculation state for an allocator."""

    def make_result(
        self, result: Sequence[Candidate[AnyName]], data: Data
    ) -> Result[AnyName, Data]:
        """Return a result structure with an allocation and additional info."""
        logger.debug("returning result (allocator %s)", self)
        return Result(allocation=result, data=data)


@dt.dataclass
class NonDeterministicState(CalculationState):
    """A calculation state for a non-deterministic allocator."""

    random_seed: dt.InitVar[RandomSeed | None] = dt.field(kw_only=True)
    rng: Dice = dt.field(init=False)

    def __post_init__(self, random_seed: RandomSeed | None):
        """Initialize random seed."""
        self.rng = Dice(random_seed)

    def make_result(
        self, result: Sequence[Candidate[AnyName]], data: Data
    ) -> NonDeterministicResult[AnyName, Data]:
        """Return a result stricture with an allocation and additional info.

        Information related to non-deterministic methods are included in the result.
        """
        return NonDeterministicResult(
            allocation=result,
            deterministic=self.rng.deterministic,
            random_state=self.rng.state(),
            data=data,
        )

    def random_tie_break(self, candidates: Iterable[_Tied], limit: int) -> dict[str, list[_Tied]]:
        """Choose candidates randomly.

        Args
        ----
        candidates
            list ofcandidates
        limit
            number of candidates to be chosen

        Return
        ------
        :
            Winners grouped by criterion
        """
        # normalize sorting by name for reproducibility
        return choose_randomly(self.rng, candidates, limit)


class NonDeterministicAllocator(Allocator[AnyName, Data]):
    """Non deterministic method."""

    rng: Dice
    "A random generator"

    def __init__(
        self,
        required_input: Input,
        optional_input: Input,
    ):
        super().__init__(required_input | Input.RANDOM_SEED, optional_input)


def check_seats(seats: int, threshold: int = 1):
    r"""Raise a :exc:`PreconditionError` if there is an invalid `seats` value.

    A `seats` value is considered invalid if :math:`seats \le 0`.
    """
    if seats < threshold:
        raise PreconditionError(f"the provided number of seats can't be allocated: {seats}")
