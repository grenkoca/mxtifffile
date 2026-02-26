import pytest

from mxtifffile import MxTiffFile


def test_open_qptiff(qptiff_path):
    tif = MxTiffFile(str(qptiff_path))
    tif.close()


def test_open_ome_tiff(ome_tiff_path):
    tif = MxTiffFile(str(ome_tiff_path))
    tif.close()


def test_open_ome_tiff_2(ome_tiff_path_2):
    tif = MxTiffFile(str(ome_tiff_path_2))
    tif.close()


def test_channels_not_empty(qptiff_path, ome_tiff_path, ome_tiff_path_2):
    for path in (qptiff_path, ome_tiff_path, ome_tiff_path_2):
        with MxTiffFile(str(path)) as tif:
            assert len(tif.channel_info) > 0


def test_channel_biomarker_nonempty(qptiff_path, ome_tiff_path):
    for path in (qptiff_path, ome_tiff_path):
        with MxTiffFile(str(path)) as tif:
            for ch in tif.channel_info:
                name = ch.get("biomarker") or ch.get("name")
                assert isinstance(name, str) and len(name) > 0


def test_custom_formats_config_missing_raises(qptiff_path, tmp_path):
    missing_json = str(tmp_path / "custom.json")
    with pytest.raises(FileNotFoundError):
        MxTiffFile(str(qptiff_path), formats_config=missing_json)
