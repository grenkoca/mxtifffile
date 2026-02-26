from unittest.mock import MagicMock
import pytest
import tifffile
import xml.etree.ElementTree as ET

from mxtifffile.format_config import load_formats
from mxtifffile.format_detector import detect_format
from mxtifffile.parsers import PerPageParser, FileLevelParser


def _get_config(format_id):
    configs = load_formats()
    return next(c for c in configs if c.id == format_id)


def test_per_page_parser_qptiff_returns_biomarkers(qptiff_path):
    config = _get_config("qptiff")
    with tifffile.TiffFile(str(qptiff_path)) as tif:
        parser = PerPageParser(config, tif)
        channels = parser.parse()
    assert len(channels) > 0
    for ch in channels:
        assert isinstance(ch.get("biomarker"), str) and len(ch["biomarker"]) > 0


def test_file_level_parser_ome_tiff_returns_biomarkers(ome_tiff_path):
    config = _get_config("ome-tiff")
    with tifffile.TiffFile(str(ome_tiff_path)) as tif:
        parser = FileLevelParser(config, tif)
        channels = parser.parse()
    assert len(channels) > 0
    for ch in channels:
        assert isinstance(ch.get("biomarker"), str) and len(ch["biomarker"]) > 0


def test_file_level_parser_ome_tiff_channel_count(ome_tiff_path):
    config = _get_config("ome-tiff")
    with tifffile.TiffFile(str(ome_tiff_path)) as tif:
        parser = FileLevelParser(config, tif)
        channels = parser.parse()
    assert len(channels) > 0


def test_no_channel_has_none_index(qptiff_path, ome_tiff_path):
    qptiff_config = _get_config("qptiff")
    ome_config = _get_config("ome-tiff")
    with tifffile.TiffFile(str(qptiff_path)) as tif:
        qptiff_channels = PerPageParser(qptiff_config, tif).parse()
    with tifffile.TiffFile(str(ome_tiff_path)) as tif:
        ome_channels = FileLevelParser(ome_config, tif).parse()
    for ch in qptiff_channels + ome_channels:
        assert ch.get("index") is not None


def test_file_level_parser_malformed_xml_raises():
    config = _get_config("ome-tiff")
    mock_tif = MagicMock()
    mock_page = MagicMock()
    mock_page.description = "this is not valid XML <<<"
    mock_tif.series = [MagicMock()]
    mock_tif.series[0].pages = [mock_page]
    parser = FileLevelParser(config, mock_tif)
    with pytest.raises(ET.ParseError):
        parser.parse()
