from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

_CACHE: Optional[List["FormatConfig"]] = None


@dataclass
class FormatDetection:
    xml_root_tag: Optional[str]
    xml_namespace: Optional[str]
    tifffile_flag: Optional[str]


@dataclass
class FormatConfig:
    id: str
    name: str
    detection: FormatDetection
    metadata_scope: str
    channel_fields: Dict[str, Any]
    channel_list_xpath: Optional[str] = None


def _parse_format(entry: Dict[str, Any]) -> FormatConfig:
    for key in ("id", "name", "detection", "metadata_scope", "channel_fields"):
        if key not in entry:
            raise ValueError(
                f"formats.json entry is missing required key '{key}': {entry}"
            )

    det = entry["detection"]
    detection = FormatDetection(
        xml_root_tag=det.get("xml_root_tag"),
        xml_namespace=det.get("xml_namespace"),
        tifffile_flag=det.get("tifffile_flag"),
    )

    return FormatConfig(
        id=entry["id"],
        name=entry["name"],
        detection=detection,
        metadata_scope=entry["metadata_scope"],
        channel_fields=entry["channel_fields"],
        channel_list_xpath=entry.get("channel_list_xpath"),
    )


def load_formats(path: Optional[str] = None) -> List[FormatConfig]:
    """Load and return format configs.

    If *path* is None the bundled formats.json is loaded via importlib.resources.
    Results are cached after the first call for a given path=None invocation.
    Passing an explicit path bypasses the cache and loads directly.
    """
    global _CACHE

    if path is None:
        if _CACHE is not None:
            return _CACHE

        try:
            from importlib.resources import files  # Python 3.9+
            data = files("mxtifffile").joinpath("formats.json").read_text(encoding="utf-8")
        except AttributeError:
            # Python 3.8 fallback
            import importlib.resources as pkg_resources
            data = pkg_resources.read_text("mxtifffile", "formats.json")

        configs = _parse_json(data, source="bundled formats.json")
        _CACHE = configs
        return _CACHE

    import os
    if not os.path.exists(path):
        raise FileNotFoundError(f"formats config not found: {path}")

    with open(path, encoding="utf-8") as fh:
        data = fh.read()

    return _parse_json(data, source=path)


def _cache_clear() -> None:
    global _CACHE
    _CACHE = None


load_formats.cache_clear = _cache_clear  # type: ignore[attr-defined]


def _parse_json(data: str, source: str) -> List[FormatConfig]:
    raw = json.loads(data)
    if "formats" not in raw:
        raise ValueError(f"'{source}' must have a top-level 'formats' key")
    return [_parse_format(entry) for entry in raw["formats"]]
