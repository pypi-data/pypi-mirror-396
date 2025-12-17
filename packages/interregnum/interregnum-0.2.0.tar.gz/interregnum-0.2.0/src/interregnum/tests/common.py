# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Common functions and fixtures for testing."""

from typing import Callable
from pathlib import Path
import json
import yaml

import pytest


def iter_problem_filenames(path: Path, rglob=False):
    """Iterate filenames with problem definitions."""
    path = Path(__file__).parent / path
    if not rglob:
        yield from path.glob("*.yaml")
        yield from path.glob("*.json")
    else:
        yield from path.rglob("*.yaml")
        yield from path.rglob("*.json")


def read_data(path: Path):
    """Read data from a problem definition file."""
    read_f: Callable
    if path.suffix == ".json":
        read_f = json.load
    elif path.suffix == ".yaml":
        read_f = yaml.safe_load
    else:
        raise ValueError(f"file type not supported: {path}")
    with open(path, encoding="utf-8") as fddata:
        data = read_f(fddata)
    return data


@pytest.fixture(name="problem")
def fixture_problem(request):
    """Fixture for problem definitions."""
    return read_data(request.param)
