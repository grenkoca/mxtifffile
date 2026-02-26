import pytest

from mxtifffile import MxTiffFile


def test_qptifffile_importable():
    from mxtifffile import QPTiffFile
    assert QPTiffFile is not None


def test_qptifffile_emits_deprecation_warning(qptiff_path):
    from mxtifffile import QPTiffFile
    with pytest.warns(DeprecationWarning):
        tif = QPTiffFile(str(qptiff_path))
    tif.close()


def test_deprecation_warning_message(qptiff_path):
    from mxtifffile import QPTiffFile
    with pytest.warns(DeprecationWarning, match=r"deprecated|QPTiffFile"):
        tif = QPTiffFile(str(qptiff_path))
    tif.close()


def test_qptifffile_is_mxtifffile_instance(qptiff_path):
    from mxtifffile import QPTiffFile
    with pytest.warns(DeprecationWarning):
        tif = QPTiffFile(str(qptiff_path))
    assert isinstance(tif, MxTiffFile)
    tif.close()
