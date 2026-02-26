from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional

from .format_config import FormatConfig

_OME_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)

_CHANNEL_KEYS = ("biomarker", "fluorophore", "display_name", "description", "exposure", "wavelength")


def _strip_xml_comments(text: str) -> str:
    return _OME_COMMENT_RE.sub("", text).strip()


def _empty_channel(index: int, raw_xml: Optional[str] = None) -> Dict[str, Any]:
    return {
        "index": index,
        "biomarker": None,
        "fluorophore": None,
        "display_name": None,
        "description": None,
        "exposure": None,
        "wavelength": None,
        "raw_xml": raw_xml,
    }


class PerPageParser:
    """Parses per-page XML descriptions (e.g. QPTIFF)."""

    def __init__(self, config: FormatConfig, tif) -> None:
        self.config = config
        self.tif = tif

    def parse(self) -> List[Dict[str, Any]]:
        results = []
        pages = self.tif.series[0].pages
        for idx, page in enumerate(pages):
            raw = getattr(page, "description", None)
            ch = _empty_channel(idx, raw)
            if raw:
                try:
                    root = ET.fromstring(raw)
                    self._extract_fields(root, ch)
                except ET.ParseError:
                    pass
            results.append(ch)
        return results

    def _extract_fields(self, root: ET.Element, ch: Dict[str, Any]) -> None:
        for field_name in _CHANNEL_KEYS:
            xpath_spec = self.config.channel_fields.get(field_name)
            if xpath_spec is None:
                continue
            # biomarker may be a list of XPaths (first match wins)
            if isinstance(xpath_spec, list):
                for xpath in xpath_spec:
                    elem = root.find(xpath)
                    if elem is not None and elem.text:
                        ch[field_name] = elem.text.strip()
                        break
            elif isinstance(xpath_spec, str):
                elem = root.find(xpath_spec)
                if elem is not None and elem.text:
                    ch[field_name] = elem.text.strip()


class FileLevelParser:
    """Parses file-level XML (e.g. OME-TIFF): reads channel nodes from page 0 description."""

    def __init__(self, config: FormatConfig, tif) -> None:
        self.config = config
        self.tif = tif

    def parse(self) -> List[Dict[str, Any]]:
        raw = getattr(self.tif.series[0].pages[0], "description", None)
        if not raw:
            return []

        cleaned = _strip_xml_comments(raw)
        try:
            root = ET.fromstring(cleaned)
        except ET.ParseError:
            return []

        # Build namespace map for XPath if namespace is present
        ns_map: Dict[str, str] = {}
        xml_ns = self.config.detection.xml_namespace
        if xml_ns:
            ns_map["ome"] = xml_ns

        xpath = self.config.channel_list_xpath or ""
        if not xpath:
            return []

        channel_nodes = root.findall(xpath, ns_map)

        results = []
        for idx, node in enumerate(channel_nodes):
            ch = _empty_channel(idx, raw_xml=None)
            self._extract_fields(node, ch)
            results.append(ch)

        return results

    def _extract_fields(self, node: ET.Element, ch: Dict[str, Any]) -> None:
        for field_name in _CHANNEL_KEYS:
            spec = self.config.channel_fields.get(field_name)
            if spec is None:
                continue
            if isinstance(spec, dict):
                # Should not happen for FileLevelParser, skip
                continue
            if isinstance(spec, str):
                # Try attribute first, then child element text
                value = node.get(spec)
                if value is None:
                    child = node.find(spec)
                    if child is not None:
                        value = child.text
                if value is not None:
                    ch[field_name] = value.strip() if value else value


class ImageJParser:
    """Parses ImageJ metadata from tif.imagej_metadata dict."""

    def __init__(self, config: FormatConfig, tif) -> None:
        self.config = config
        self.tif = tif

    def parse(self) -> List[Dict[str, Any]]:
        meta = getattr(self.tif, "imagej_metadata", None) or {}

        # Gather channel names via imagej_key fields
        biomarker_key = self._imagej_key("biomarker")
        fluorophore_key = self._imagej_key("fluorophore")

        names = self._split_labels(meta.get(biomarker_key) if biomarker_key else None)
        flu_names = self._split_labels(meta.get(fluorophore_key) if fluorophore_key else None)

        count = len(names) or len(flu_names)
        results = []
        for idx in range(count):
            ch = _empty_channel(idx)
            if idx < len(names):
                ch["biomarker"] = names[idx]
            if idx < len(flu_names):
                ch["fluorophore"] = flu_names[idx]
            results.append(ch)

        return results

    def _imagej_key(self, field_name: str) -> Optional[str]:
        spec = self.config.channel_fields.get(field_name)
        if isinstance(spec, dict):
            return spec.get("imagej_key")
        return None

    @staticmethod
    def _split_labels(value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [s.strip() for s in value.split("\n") if s.strip()]
        if isinstance(value, (list, tuple)):
            return [str(v).strip() for v in value if str(v).strip()]
        return []
