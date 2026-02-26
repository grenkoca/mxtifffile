from __future__ import annotations

import re
import warnings
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional

_OME_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)

ANCHOR_MARKER = "DAPI"


def _strip_comments(text: str) -> str:
    return _OME_COMMENT_RE.sub("", text).strip()


def _empty_channel(index: int) -> Dict[str, Any]:
    return {
        "index": index,
        "biomarker": None,
        "fluorophore": None,
        "display_name": None,
        "description": None,
        "exposure": None,
        "wavelength": None,
        "raw_xml": None,
    }


def _find_anchor_element(root: ET.Element, anchor: str) -> Optional[ET.Element]:
    """Return the first element whose text equals *anchor*."""
    for elem in root.iter():
        if elem.text and elem.text.strip() == anchor:
            return elem
    return None


def _find_name_element_for_structure(root: ET.Element, anchor_elem: ET.Element) -> Optional[str]:
    """
    Given that *anchor_elem* holds the anchor marker text, try to determine which
    XML tag name is used for channel names in this document structure.

    Strategy: if the parent of anchor_elem contains sibling elements with the same tag,
    those siblings likely hold other channel names. Return the tag name to use.
    If anchor_elem has no parent or siblings, fall back to its own tag.
    """
    anchor_tag = anchor_elem.tag

    # Look for the parent of the anchor element in the tree
    parent_map = {child: parent for parent in root.iter() for child in parent}
    parent = parent_map.get(anchor_elem)
    if parent is None:
        return anchor_tag

    # Check siblings with the same tag — indicates a repeating channel name element
    siblings = [c for c in parent if c.tag == anchor_tag]
    if len(siblings) > 1:
        return anchor_tag

    # anchor might be inside a channel block; look one level up
    grandparent = parent_map.get(parent)
    if grandparent is not None:
        # Check if parent's siblings (i.e. other channel blocks) share the same structure
        channel_blocks = [c for c in grandparent if c.tag == parent.tag]
        if len(channel_blocks) > 1:
            # Use the tag of the element within each block that matched
            return anchor_tag

    return anchor_tag


def _per_page_heuristic(tif) -> Optional[List[Dict[str, Any]]]:
    """Try to infer channel names from per-page XML descriptions."""
    import qptifffile as _pkg
    anchor = _pkg.ANCHOR_MARKER
    pages = tif.series[0].pages

    # Check page 0 for the anchor marker
    page0_desc = getattr(pages[0], "description", None) if pages else None
    if not page0_desc:
        return None

    try:
        root0 = ET.fromstring(page0_desc)
    except ET.ParseError:
        return None

    anchor_elem = _find_anchor_element(root0, anchor)
    if anchor_elem is None:
        return None

    # Determine tag used for channel name
    name_tag = _find_name_element_for_structure(root0, anchor_elem)

    results = []
    for idx, page in enumerate(pages):
        raw = getattr(page, "description", None)
        ch = _empty_channel(idx)
        ch["raw_xml"] = raw
        if raw:
            try:
                root = ET.fromstring(raw)
                for elem in root.iter():
                    if elem.tag == name_tag and elem.text and elem.text.strip():
                        ch["biomarker"] = elem.text.strip()
                        ch["fluorophore"] = elem.text.strip()
                        break
            except ET.ParseError:
                pass
        results.append(ch)

    return results


def _file_level_heuristic(tif) -> Optional[List[Dict[str, Any]]]:
    """Try to infer channel names from file-level XML (page 0 description)."""
    import qptifffile as _pkg
    anchor = _pkg.ANCHOR_MARKER
    pages = tif.series[0].pages
    if not pages:
        return None

    raw = getattr(pages[0], "description", None)
    if not raw:
        return None

    cleaned = _strip_comments(raw)
    try:
        root = ET.fromstring(cleaned)
    except ET.ParseError:
        return None

    # Search attributes and text for the anchor
    found = False
    for elem in root.iter():
        if anchor in (elem.text or ""):
            found = True
            break
        for val in elem.attrib.values():
            if anchor in val:
                found = True
                break
        if found:
            break

    if not found:
        return None

    # Fallback: collect all elements whose text looks like a channel name
    # by finding the element containing anchor and using its siblings/peers
    results = []
    # Simple approach: gather all unique text values of elements with the anchor's tag
    anchor_elem: Optional[ET.Element] = None
    for elem in root.iter():
        if elem.text and elem.text.strip() == anchor:
            anchor_elem = elem
            break
        for attr_val in elem.attrib.values():
            if attr_val.strip() == anchor:
                anchor_elem = elem
                break
        if anchor_elem is not None:
            break

    if anchor_elem is None:
        return None

    # Collect peers: all elements with the same tag as anchor_elem
    anchor_tag = anchor_elem.tag
    name_list: List[str] = []
    for elem in root.iter():
        if elem.tag == anchor_tag:
            text = (elem.text or "").strip() or elem.get("Name", "").strip()
            if text:
                name_list.append(text)

    if not name_list:
        # Try attribute
        for elem in root.iter():
            if elem.tag == anchor_elem.tag:
                val = elem.get("Name") or elem.get("name")
                if val:
                    name_list.append(val.strip())

    for idx, name in enumerate(name_list):
        ch = _empty_channel(idx)
        ch["biomarker"] = name
        ch["fluorophore"] = name
        results.append(ch)

    return results if results else None


def heuristic_detect(tif) -> Optional[List[Dict[str, Any]]]:
    """Attempt heuristic channel detection for unknown formats.

    Returns list[dict] on success, None if ANCHOR_MARKER not found anywhere.
    Emits a warning on success.
    """
    result = _per_page_heuristic(tif)
    if result is None:
        result = _file_level_heuristic(tif)

    if result is not None:
        warnings.warn(
            "MxTiffFile: format not recognized; channel names inferred heuristically",
            stacklevel=3,
        )

    return result
