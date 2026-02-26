import pathlib
import pytest

TEST_DATA_DIR = pathlib.Path(__file__).parent.parent / "test_data"


@pytest.fixture
def qptiff_path():
    path = TEST_DATA_DIR / "Roche_Fusion_TonsilandIntestine_1.qptiff"
    if not path.exists():
        pytest.skip(f"Test data not found: {path}")
    return path


@pytest.fixture
def ome_tiff_path():
    path = TEST_DATA_DIR / "A-1.ome.tif"
    if not path.exists():
        pytest.skip(f"Test data not found: {path}")
    return path


@pytest.fixture
def ome_tiff_path_2():
    path = TEST_DATA_DIR / "Untitled.ome.tif"
    if not path.exists():
        pytest.skip(f"Test data not found: {path}")
    return path
