#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Convert from old format."""

from typing import Any
import sys
from pathlib import Path
import yaml

KEYS0 = [
    "name",
    "method",
    "method_params",
    "compensatory",
    "alliance",
    "votes",
    "key",
    "type",
    "mode",
    "seats",
    "meta",
    "max_seats",
    "threshold",
    "quota",
]

KEYS1 = [
    "first_vote",
    "second_vote",
    "divisions",
    "candidates",
    "preferences",
    "districts",
]


counter = 100
CACHE = {}

for idx, k in enumerate(KEYS0):
    CACHE[k] = idx

for idx, k in enumerate(KEYS1):
    CACHE[k] = idx + 200


def sort_key(item: tuple[str, Any]) -> int:
    """Return a key for sorting."""
    key, _value = item
    global counter
    if key not in CACHE:
        CACHE[key] = counter
        counter += 1
    return CACHE[key]


def convert_item(data):
    """Convert an item."""
    if isinstance(data, dict):
        if "candidates" in data:
            data["meta"] = data.get("meta", {})
            data["meta"]["test"] = True
        data = dict(sorted([(k, convert_item(v)) for k, v in data.items()], key=sort_key))
    elif isinstance(data, list):
        data = [convert_item(x) for x in data]
    return data


def convert(path: Path):
    """Convert a file."""
    with open(path, encoding="utf8") as fd:
        data = yaml.safe_load(fd)

    data = convert_item(data)

    with open(path, "wt", encoding="utf8") as fd:
        yaml.safe_dump(data, fd, sort_keys=False, allow_unicode=True, default_flow_style=False)


def main():
    """Main function."""  # noqa: D401
    for path in sys.argv[1:]:
        convert(Path(path))


if __name__ == "__main__":
    main()
