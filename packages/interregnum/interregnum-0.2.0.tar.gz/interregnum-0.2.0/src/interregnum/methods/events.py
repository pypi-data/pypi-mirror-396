#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Common allocation log events."""
from __future__ import annotations
from typing import (
    Sequence,
    Any,
    ClassVar,
)
from dataclasses import (
    dataclass,
    field,
)
from ..types import Score
from ..divisors import Divisor


@dataclass
class Event:
    """Log event data."""

    EVENT: ClassVar[str]
    "Event type"


@dataclass
class EventLog:
    """Data with event log info."""

    log: list[Event] = field(default_factory=list)
    "An event list"


@dataclass
class TieEvent(Event):
    """Tie event."""

    EVENT = "tie"
    candidates: Sequence
    "Candidates affected by the tie"
    condition: Any | None = None
    "Condition related to the tie"


@dataclass
class WinnerEvent(Event):
    """Winner event."""

    EVENT = "winner"
    target: Any
    "Winner"
    criterion: str
    "Criterion that triggered the event"


@dataclass
class QuotaWinnerEvent(WinnerEvent):
    """Winner event for quota reached."""

    quota: Divisor
    "Quota reached by the winner"


@dataclass
class IneligibleEvent(Event):
    """Ineligible candidate event."""

    EVENT = "ineligible"
    target: Any
    "Ineligible candidate"
    criterion: str
    "Criterion that caused the event."
    condition: Any | None = None
    "Condition related to the tie."


@dataclass
class TransferredVotesEvent(Event):
    """Transferred votes event."""

    EVENT = "transferred votes"
    source: Any
    "Source candidate"
    target: Any
    "Target candidate"
    votes: Score
    "Transferred votes"


@dataclass
class SeatsEvent(Event):
    """Seats allocated event."""

    EVENT = "seats"
    target: Any
    "Seats winner"
    seats: int
    "Allocated seats"
    criterion: str
    "Allocation criterion"


@dataclass
class NewAllocationEvent(Event):
    """A new allocation is needed to fulfill requirements."""

    EVENT = "new allocation"
    criterion: str
    "Criterion for re-allocation"
    data: Any | None = None
    "Additional data"
