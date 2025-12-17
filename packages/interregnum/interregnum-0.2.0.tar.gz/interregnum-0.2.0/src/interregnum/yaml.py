#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Yaml loader and dumper."""

from __future__ import annotations
from functools import partial
import yaml

try:
    from yaml import CSafeLoader as _Loader
    from yaml import CSafeDumper as _Dumper
except ImportError:
    from yaml import SafeLoader as _Loader  # type: ignore[assignment]
    from yaml import SafeDumper as _Dumper  # type: ignore[assignment]

safe_load = partial(yaml.load, Loader=_Loader)
"Safe-load a YAML using the available loader"

safe_dump = partial(yaml.dump, Dumper=_Dumper)
"Safe-dump a YAML using the available dumper"
