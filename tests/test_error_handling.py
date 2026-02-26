import pytest
import tifffile

from mxtifffile import MxTiffFile, MxTiffFormatError


def test_open_nonexistent_file_raises():
    with pytest.raises((FileNotFoundError, tifffile.TiffFileError)):
        MxTiffFile("nonexistent_file.tif")


def test_open_fake_tif_raises(tmp_path):
    fake_tif = tmp_path / "fake.tif"
    fake_tif.write_text("this is not a TIFF file")
    with pytest.raises(Exception):
        MxTiffFile(str(fake_tif))


def test_mx_tiff_format_error_importable():
    from mxtifffile import MxTiffFormatError
    assert MxTiffFormatError is not None


def test_mx_tiff_format_error_is_exception():
    assert issubclass(MxTiffFormatError, Exception)
