#!/usr/bin/env python

# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Tools for reading ballots info."""
from __future__ import annotations
from typing import (
    Literal,
    Callable,
    Mapping,
    Generator,
    Any,
    Iterable,
)
import dataclasses as dt
from pathlib import Path
import csv
import json
from .. import yaml
from .contenders import Contender, ContenderId
from ..methods.types import Candidate
from ..methods.preferential.types import Preference
from ..methods.preferential.io import read_preferences


@dt.dataclass
class File:
    """A resource file definition."""

    path: Path
    "file path"

    format: str
    "file format"

    encoding: str = "utf-8"
    "char encoding"

    cwd: Path | None = None
    "working directory"

    def __post_init__(self) -> None:
        """Normalize format string."""
        self.path = Path(self.path)
        if self.cwd:
            self.cwd = Path(self.cwd)
        self.format = self._normalize_format(self.format)

    def _normalize_format(self, tag: str) -> str:
        """Normalize a format string to a canonical form."""
        raise NotImplementedError()

    def _resolve_path(self) -> Path:
        if not self.path.is_absolute() and self.cwd:
            return self.cwd / self.path
        return self.path


@dt.dataclass
class PreferencesFile(File):
    """A file with preferences.

    Formats:

    - `pref`
    - `yaml`: should be compatible with the preference converter
    - `json`: should be compatible with the preference converter
    """

    type: Literal["preferences-file"] = "preferences-file"

    def _normalize_format(self, tag: str):
        tag = (tag or "").strip().lower()
        if tag not in ("pref", "yaml", "json"):
            raise ValueError(f"unknown format {format:r}")
        return tag

    def __call__(
        self, converter: Callable[[str], ContenderId]
    ) -> Generator[Preference[ContenderId]]:
        """Read file and convert candidates names using `converter`."""
        if self.format == "pref":
            return self._read_pref(converter)
        if self.format == "yaml":
            return self._read_yaml(converter)
        if self.format == "json":
            return self._read_json(converter)
        raise ValueError(f"unknown format {self.format:r}")

    def _read_pref(
        self, converter: Callable[[str], ContenderId]
    ) -> Generator[Preference[ContenderId]]:
        with open(self._resolve_path(), encoding=self.encoding) as stream:
            for row in read_preferences(stream, converter):
                yield Preference(row[0], tuple(row[1]))

    def _read_yaml(
        self, converter: Callable[[str], ContenderId]
    ) -> Generator[Preference[ContenderId]]:
        with open(self._resolve_path(), encoding=self.encoding) as stream:
            for row in yaml.safe_load(stream):
                yield Preference(row[0], tuple(row[1])).transform(converter)

    def _read_json(
        self, converter: Callable[[str], ContenderId]
    ) -> Generator[Preference[ContenderId]]:
        with open(self._resolve_path(), encoding=self.encoding) as stream:
            for row in json.load(stream):
                yield Preference(row[0], tuple(row[1])).transform(converter)

    @classmethod
    def from_path(cls, path: Path, cwd: Path | None) -> PreferencesFile:
        """Create a PreferencesFile from a path."""
        return cls(path=path, format=path.suffix.lstrip("."), cwd=cwd)


@dt.dataclass
class CandidatesFile(File):
    """A file with candidates.

    - `yaml`, `json`: should be compatible with Contender
    - `csv`, `tsv`: the columns should be compatible with Contender's properties
    """

    type: Literal["candidates-file"] = "candidates-file"
    sep: str = ","

    def _normalize_format(self, tag: str):
        tag = (tag or "").strip().lower()
        if tag == "yml":
            return "yaml"
        if tag not in ("tsv", "csv", "yaml", "json"):
            raise ValueError(f"unsupported format {format:r}")
        return tag

    def __call__(self) -> Generator[tuple[str | None, Contender]]:
        """Return a list of contenders."""
        if self.format in "csv":
            return self._read_csv()
        if self.format == "yaml":
            return self._read_yaml()
        if self.format == "json":
            return self._read_json()
        raise ValueError(f"unsupported format {self.format:r}")

    def _read_csv(self) -> Generator[tuple[str | None, Contender]]:
        with open(self._resolve_path(), encoding=self.encoding, newline="") as stream:
            reader = csv.DictReader(stream, delimiter=self.sep)
            for row in reader:
                node = (row.pop("node", None) or "").strip() or None
                item = Contender.from_dict(row)
                yield node or item.district, item

    def _read_yaml(self) -> Generator[tuple[str | None, Contender]]:
        with open(self._resolve_path(), encoding=self.encoding) as stream:
            return self._read_structured(yaml.safe_load(stream))

    def _read_json(self) -> Generator[tuple[str | None, Contender]]:
        with open(self._resolve_path(), encoding=self.encoding) as stream:
            return self._read_structured(json.load(stream))

    def _read_structured(self, data) -> Generator[tuple[str | None, Contender]]:
        if isinstance(data, list):
            data = {None: data}
        assert isinstance(data, dict)
        for node, items in data.items():
            for item in items:
                yield node, Contender(**item)

    @classmethod
    def from_path(cls, path: Path, cwd: Path | None) -> CandidatesFile:
        """Create a CandidatesFile object from a path name."""
        out = cls(path=path, format=path.suffix.lstrip(".").lower(), cwd=cwd)
        if out.format == "tsv":
            out.format = "csv"
            out.sep = "\t"
        return out

    def write_data(self, nodes: Iterable[tuple[str, Iterable[Candidate | Contender]]]):
        """Write data to this file."""
        if self.format == "csv":
            return self._write_csv(nodes)
        if self.format == "yaml":
            return self._write_yaml(nodes)
        if self.format == "json":
            return self._write_json(nodes)
        raise ValueError(f"unknown format {self.format:r}")

    def _write_csv(self, nodes: Iterable[tuple[str, Iterable[Candidate[ContenderId] | Contender]]]):
        with open(self._resolve_path(), "w", encoding=self.encoding, newline="") as stream:
            fieldnames = [
                "node",
                "district",
                "name",
                "alliance",
                "votes",
                "seats",
                "min_seats",
                "max_seats",
                "groups",
                "meta",
            ]
            writer = csv.DictWriter(stream, fieldnames=fieldnames, delimiter=self.sep)

            writer.writeheader()
            for node, items in _iter_contenders(nodes):
                for item in items:
                    item["node"] = node
                    writer.writerow(item)

    def _write_yaml(self, nodes: Iterable[tuple[str, Iterable[Candidate | Contender]]]):
        with open(self._resolve_path(), "w", encoding=self.encoding) as stream:
            yaml.safe_dump(
                dict(_iter_contenders(nodes)), stream, allow_unicode=True, sort_keys=False
            )

    def _write_json(self, nodes: Iterable[tuple[str, Iterable[Candidate | Contender]]]):
        with open(self._resolve_path(), "w", encoding=self.encoding) as stream:
            json.dump(
                dict(_iter_contenders(nodes)),
                stream,
                sort_keys=False,
                indent=2,
            )


def _iter_contenders(
    nodes: Iterable[tuple[str, Iterable[Candidate[ContenderId] | Contender]]],
) -> Iterable[tuple[str, list[dict]]]:
    for node, items in nodes:
        out = []
        for item in items:
            if isinstance(item, Candidate):
                item = Contender.from_candidate(item)
            data = {k: v for k, v in dt.asdict(item).items() if v is not None}
            if not data["groups"]:
                data.pop("groups")
            out.append(data)
        yield node, out


def unserialize_file_object(data: Mapping[str, Any], path: Path | None) -> dict[str, Any]:
    """Unserialize File fields."""
    data = dict(data)
    data["path"] = Path(data["path"])
    if path:
        data["cwd"] = path
    return data


def unserialize_preferences_file(data: Mapping[str, Any], path: Path | None) -> PreferencesFile:
    """Unserialize PreferencesFile fields."""
    data = unserialize_file_object(data, path)
    if data["type"] != "preferences-file":
        raise ValueError(f"unknown type {data['type']}")
    data["path"] = Path(data["path"])
    return PreferencesFile(**data)
