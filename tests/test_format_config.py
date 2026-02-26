import json
import pytest

from mxtifffile.format_config import load_formats, FormatConfig, FormatDetection


def teardown_function():
    load_formats.cache_clear()


def test_load_formats_returns_nonempty_list():
    configs = load_formats()
    assert len(configs) > 0


def test_each_item_is_format_config():
    configs = load_formats()
    for cfg in configs:
        assert isinstance(cfg, FormatConfig)
        assert isinstance(cfg.id, str) and len(cfg.id) > 0


def test_each_item_has_detection():
    configs = load_formats()
    for cfg in configs:
        assert isinstance(cfg.detection, FormatDetection)


def test_load_formats_custom_path(tmp_path):
    custom_json = tmp_path / "custom.json"
    custom_json.write_text(json.dumps({
        "formats": [
            {
                "id": "test-format",
                "name": "Test Format",
                "detection": {
                    "xml_root_tag": "Test",
                    "xml_namespace": None,
                    "tifffile_flag": None,
                },
                "metadata_scope": "per_page",
                "channel_fields": {},
            }
        ]
    }))
    configs = load_formats(path=str(custom_json))
    assert len(configs) == 1
    assert configs[0].id == "test-format"


def test_load_formats_nonexistent_path_raises():
    with pytest.raises(FileNotFoundError):
        load_formats(path="/nonexistent/path.json")


def test_load_formats_cache_identity():
    load_formats.cache_clear()
    first = load_formats()
    second = load_formats()
    assert first is second
