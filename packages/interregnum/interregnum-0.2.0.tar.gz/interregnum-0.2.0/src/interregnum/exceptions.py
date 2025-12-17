#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Custom exception."""


class PreconditionError(Exception):
    """Raised when an operation can not be computed for not meeting all the pre-conditions."""


class PreconditionWarning(UserWarning):
    """Emitted when a pre-condition failed by the process continues."""


class UnsolvableError(Exception):
    """Raised when an allocator can't resolve the allocation."""
