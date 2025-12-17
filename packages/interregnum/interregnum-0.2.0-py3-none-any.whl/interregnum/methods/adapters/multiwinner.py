# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

# #!/usr/bin/env python
"""Adapters to convert single-winner methods to multi-winner methods."""
from __future__ import annotations
from typing import (
    Callable,
    TypeVar,
    Iterable,
    Generic,
    Any,
)
import dataclasses as dt
from typing_extensions import override

from ..types import (
    check_seats,
    NonDeterministicAllocator,
    NonDeterministicState,
    Result,
    Score,
    Candidate,
    Input,
    PreconditionError,
    CandidateFilter,
)
from ..events import (
    EventLog,
    TieEvent,
    QuotaWinnerEvent,
    IneligibleEvent,
)

from ...random import RandomSeed
from .ranking import (
    Ranking,
    RankingList,
    break_tie_ranking,
)
from . import CandLike


@dt.dataclass
class MultiWinnerResultData(EventLog):
    """Multi-winner result data."""

    threshold: Score = 0
    remaining_seats: int = 0
    rounds: int = 0


MultiDataT = TypeVar("MultiDataT", bound=MultiWinnerResultData)


@dt.dataclass
class MultiWinnerState(NonDeterministicState, Generic[MultiDataT]):
    """A calculation state from multi-winner-adapter."""

    data: MultiDataT

    def break_tie(self, candidates: Iterable[Candidate[CandLike]], ascending: bool):
        """Break ties based on a ranking list, or choose randomly if not possible."""
        return break_tie_ranking(
            RankingList(candidates, ascending),
            limit=self.data.remaining_seats,
            fallback=self.random_tie_break,
        )


# get winners from a ranking function
class MultiWinnerAdapter(NonDeterministicAllocator[CandLike, MultiDataT]):
    """Create a multi-winner allocator from a single-winner allocator.

    Given N seats, this method will give each seat for the most ranked candidate
    in succesive rounds,
    """

    def __init__(
        self,
        make_input_f,
        ranking_f: Callable[..., Ranking[CandLike]],
        required_input: Input,
        optional_input: Input,
    ):
        """Create a multi-winner adapter.

        Args
        ----
        make_input_f
            input data formatter
        ranking_f
            a ranking method
        required_input
            declaration of required inputs for the calc method
        optional_input
            declaration of optional inputs for the calc method
        """
        super().__init__(required_input, optional_input)
        self._make_input_f = make_input_f
        self._ranking_f = ranking_f

    def _init_data(self):
        return MultiWinnerResultData()

    def _reset(self, random_seed) -> MultiWinnerState[MultiDataT]:
        return MultiWinnerState(random_seed=random_seed, data=self._init_data())

    def _base_ranking_kwargs(self) -> dict[str, Any]:
        return {}

    def _build_input(self, data, **ranking_args):
        return self._make_input_f(data, **ranking_args)

    def _build_ranking(self, state: MultiWinnerState[MultiDataT], candidates, **ranking_args):
        ranking_args.update(self._base_ranking_kwargs())
        return self._ranking_f(candidates, **ranking_args)

    def _build_result(self, state: MultiWinnerState[MultiDataT], elected):
        return state.make_result(elected, state.data)

    def _check_precondition(self, score):
        pass

    def _calc(
        self,
        data,
        seats: int,
        random_seed: RandomSeed | None = None,
        filter_f: CandidateFilter | None = None,
        **ranking_args,
    ) -> tuple[MultiWinnerState[MultiDataT], Result[CandLike, MultiDataT]]:
        check_seats(seats)
        state: MultiWinnerState[MultiDataT] = self._reset(random_seed)

        state.data.remaining_seats = seats
        elected = []

        scores = self._build_ranking(state, self._build_input(data), **ranking_args)
        if filter_f:
            for name in filter_f.exclusion_list():
                scores.remove_name(name)
                state.data.log.append(IneligibleEvent(target=name, criterion="initial_exclusion"))

        self._check_precondition(scores)

        state.data.rounds = 0
        while state.data.remaining_seats and not scores.empty():
            # get scores
            winners = scores.winners()
            state.data.threshold = winners[0].votes

            if len(winners) > state.data.remaining_seats:
                # tie
                state.data.log.append(
                    TieEvent(
                        candidates=tuple(elem.name for elem in winners),
                        condition={"best_score": state.data.threshold},
                    )
                )
                # log
                batches = state.break_tie(winners, scores.ascending())
            else:
                batches = {"best_score": winners}

            for criterion, items in batches.items():
                for cand in items:
                    elected.append(cand.with_seats(1))
                    state.data.log.append(
                        QuotaWinnerEvent(
                            target=cand.name, quota=state.data.threshold, criterion=criterion
                        )
                    )
                    state.data.remaining_seats -= 1
                    if state.data.remaining_seats:
                        scores.remove(cand)
                    if filter_f:
                        state.data.log.extend(filter_f.update(elected[-1]))

            if filter_f:
                for name in filter_f.exclusion_list():
                    scores.remove_name(name)

            state.data.rounds += 1

        return state, self._build_result(state, elected)


# winner-takes-all form a ranking function
class WinnerTakesAllAdapter(MultiWinnerAdapter[CandLike, MultiDataT]):
    """Winner Takes All Adapter using a ranking list."""

    def __init__(
        self,
        make_input_f,
        ranking_f: Callable[..., Ranking[CandLike]],
        required_input: Input,
        optional_input: Input,
    ):
        """Create a Winner Takes All adapter.

        Args
        ----
        make_input_f
            input data formatter
        ranking_f
            a ranking method
        required_input
            declaration of required inputs for the calc method
        optional_input
            declaration of optional inputs for the calc method
        """
        super().__init__(
            make_input_f,
            ranking_f=ranking_f,
            required_input=required_input,
            optional_input=optional_input,
        )

    def _call_calc(
        self, data, **kwargs
    ) -> tuple[MultiWinnerState[MultiDataT], Result[CandLike, MultiDataT]]:
        return super()._calc(data, **kwargs)

    @override
    def _calc(
        self,
        data,
        seats: int = 1,
        random_seed: RandomSeed | None = None,
        filter_f: CandidateFilter | None = None,
        **kwargs,
    ) -> tuple[MultiWinnerState[MultiDataT], Result[CandLike, MultiDataT]]:
        if filter_f:
            if seats > 1:
                raise PreconditionError("filter_f is not supported")
            kwargs["filter_f"] = filter_f
        check_seats(seats)
        state, result = self._call_calc(data, seats=1, random_seed=random_seed, **kwargs)
        if seats == 1:
            return state, result
        elected = [x.with_seats(seats) for x in result.allocation]
        assert result.data
        return state, state.make_result(elected, result.data)
