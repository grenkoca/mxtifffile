from unittest.mock import MagicMock
import pytest
import tifffile

from mxtifffile import ANCHOR_MARKER
from mxtifffile.heuristic import heuristic_detect
from mxtifffile.exceptions import MxTiffFormatError


def test_anchor_marker_is_dapi():
    assert ANCHOR_MARKER == "DAPI"


def test_heuristic_detect_real_data(qptiff_path, ome_tiff_path):
    """heuristic_detect should find channels in at least one real file containing DAPI."""
    found_any = False
    for path in (qptiff_path, ome_tiff_path):
        with tifffile.TiffFile(str(path)) as tif:
            result = heuristic_detect(tif)
        if result is not None and len(result) > 0:
            found_any = True
            break
    assert found_any, "heuristic_detect found no channels in any real test data file"


def test_heuristic_detect_no_anchor_returns_none():
    """Mock tifffile with XML that has no anchor marker should return None."""
    mock_tif = MagicMock()
    mock_page = MagicMock()
    mock_page.description = "<Root><Channel>SomeOtherMarker</Channel></Root>"
    mock_tif.series = [MagicMock()]
    mock_tif.series[0].pages = [mock_page]
    result = heuristic_detect(mock_tif)
    assert result is None
