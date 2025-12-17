#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Files readers and writers."""

from __future__ import annotations
from pathlib import Path
import json
from .. import yaml

from ..district import node as nd
from ..district import serialize as sr


def normalize_extension(extension: str) -> str:
    """Normalize extensions."""
    extension = extension.strip().strip(".").lower()
    if extension == "yml":
        return "yaml"
    return extension


def read_dict_file(filename: Path, encoding: str = "utf-8"):
    """Read structured information from file."""
    extension = normalize_extension(filename.suffix)
    if extension == "json":
        with open(filename, encoding=encoding) as stream:
            return json.load(stream)
    if extension == "yaml":
        with open(filename, encoding=encoding) as stream:
            return yaml.safe_load(stream)
    raise ValueError(f"can't open file: {filename}. Unsupported format.")


def open_electoral_system(
    filename: Path,
    cwd: Path,
    encoding: str = "utf-8",
) -> nd.Node:
    """Open a serialized electoral system.

    Supported formats: .json, .yaml, .yml
    """
    data = sr.unserialize_node(read_dict_file(filename, encoding=encoding), cwd=cwd)
    assert isinstance(data, nd.Node)
    return data


def write_electoral_system(
    data: nd.Node,
    filename: Path,
    decimals: int | None,
    encoding: str = "utf-8",
) -> None:
    """Write an electoral system to file.

    Supported formats: .json, .yaml, .yml
    """
    extension = normalize_extension(filename.suffix)
    # json formatters
    if extension == "json":
        with open(filename, "wt", encoding=encoding) as stream:
            json.dump(
                sr.to_serializable(data, decimals),
                stream,
                indent=4,
                sort_keys=False,
            )
        return
    # yaml formatters
    if extension == "yaml":
        with open(filename, "wt", encoding=encoding) as stream:
            yaml.safe_dump(
                sr.to_serializable(data, decimals),
                stream,
                allow_unicode=True,
                sort_keys=False,
            )
        return
    raise ValueError(f"can't write file: {filename}. Unsupported format.")
