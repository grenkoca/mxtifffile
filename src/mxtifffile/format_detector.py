from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import List, Optional

from .format_config import FormatConfig

_OME_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def _strip_xml_comments(text: str) -> str:
    return _OME_COMMENT_RE.sub("", text).strip()


def _page0_root_tag(tif) -> Optional[str]:
    """Return the root element tag (local name only) of page 0's description XML."""
    try:
        pages = tif.series[0].pages
        if not pages:
            return None
        desc = pages[0].description
        if not desc:
            return None
        cleaned = _strip_xml_comments(desc)
        root = ET.fromstring(cleaned)
        tag = root.tag
        # Strip namespace if present: {ns}LocalName -> LocalName
        if tag.startswith("{"):
            tag = tag.split("}", 1)[1]
        return tag
    except Exception:
        return None


def detect_format(tif, configs: List[FormatConfig]) -> Optional[FormatConfig]:
    """Inspect *tif* and return the first matching FormatConfig, or None.

    Detection priority:
    1. tifffile_flag check (e.g. tif.is_ome)
    2. xml_root_tag match against page 0 description

    OME-TIFF takes priority over ImageJ for hybrid Bio-Formats files
    (tifffile sets both is_ome and is_imagej on such files).
    """
    root_tag = _page0_root_tag(tif)

    # Separate ome-tiff config so it can be checked before imagej
    ome_configs = [c for c in configs if c.id == "ome-tiff"]
    other_configs = [c for c in configs if c.id != "ome-tiff"]

    for config in ome_configs + other_configs:
        det = config.detection

        # Check tifffile_flag first
        if det.tifffile_flag:
            flag_value = getattr(tif, det.tifffile_flag, False)
            if flag_value:
                # Also validate xml_root_tag if set
                if det.xml_root_tag is None or root_tag == det.xml_root_tag:
                    return config

        # Fall back to xml_root_tag match
        if det.xml_root_tag and root_tag == det.xml_root_tag:
            return config

    return None
