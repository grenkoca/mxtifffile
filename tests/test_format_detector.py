from unittest.mock import MagicMock
import pytest
import tifffile

from mxtifffile.format_config import load_formats
from mxtifffile.format_detector import detect_format, _strip_xml_comments, _page0_root_tag


def test_detect_format_ome_tiff(ome_tiff_path):
    configs = load_formats()
    with tifffile.TiffFile(str(ome_tiff_path)) as tif:
        result = detect_format(tif, configs)
    assert result is not None
    assert result.id == "ome-tiff"


def test_detect_format_ome_tiff_2(ome_tiff_path_2):
    configs = load_formats()
    with tifffile.TiffFile(str(ome_tiff_path_2)) as tif:
        result = detect_format(tif, configs)
    assert result is not None
    assert result.id == "ome-tiff"


def test_detect_format_qptiff(qptiff_path):
    configs = load_formats()
    with tifffile.TiffFile(str(qptiff_path)) as tif:
        result = detect_format(tif, configs)
    assert result is not None
    assert result.id == "qptiff"


def test_detect_format_returns_none_for_unknown():
    configs = load_formats()
    mock_tif = MagicMock()
    mock_tif.series = []
    mock_tif.is_ome = False
    mock_tif.is_qpi = False
    mock_tif.is_imagej = False
    result = detect_format(mock_tif, configs)
    assert result is None


def test_detect_format_prefers_ome_over_imagej():
    configs = load_formats()
    mock_tif = MagicMock()
    mock_tif.is_ome = True
    mock_tif.is_imagej = True
    mock_tif.is_qpi = False
    # Make page0_root_tag return "OME"
    mock_page = MagicMock()
    mock_page.description = "<!-- comment --><OME></OME>"
    mock_tif.series = [MagicMock()]
    mock_tif.series[0].pages = [mock_page]
    result = detect_format(mock_tif, configs)
    assert result is not None
    assert result.id == "ome-tiff"


def test_strip_xml_comments():
    result = _strip_xml_comments("<!-- comment -->text")
    assert result == "text"


def test_page0_root_tag_empty_pages():
    mock_tif = MagicMock()
    mock_tif.series = [MagicMock()]
    mock_tif.series[0].pages = []
    result = _page0_root_tag(mock_tif)
    assert result is None
