from datetime import datetime
from pydantic_core import ValidationError
from app.models.thumbnail_request import WMSThumbRequest, Projections
from app.util.path_utils import generate_thumbnail_paths
import pytest


def make_request(**kwargs):
    defaults = dict(
        id="abc123",
        wms_url="http://foo.bar.com:8080/wms?service=WMS",
        wms_layer=None,
        wms_style=None,
        wms_zoom_level=0,
        wms_timeout=120,
        add_coastlines=True,
        projection=Projections.PlateCarree,
        thumbnail_extent=None,
        wms_layers_mmd=list(),
        start_date=None,
    )
    defaults.update(kwargs)
    return WMSThumbRequest(**defaults)


def test_generate_thumbnail_paths_with_date():
    req = make_request(start_date=datetime(2024, 7, 2))
    path, full_path = generate_thumbnail_paths(req, "https://thumb-host/", "img/")
    assert path == "com.bar.foo/2024/07/02/abc123.png"
    assert full_path.endswith(path)
    assert full_path.startswith("https://thumb-host/img/")


def test_generate_thumbnail_paths_without_date():
    req = make_request(start_date=None)
    path, full_path = generate_thumbnail_paths(req, "https://host/", "img/")
    expected_shard = f"com.bar.foo/{req.id[:4]}/abc123.png"
    assert path.startswith(expected_shard)
    assert full_path.endswith(path)


def test_generate_thumbnail_paths_host_no_port():
    req = make_request(wms_url="https://baz.qux.org/wms")
    path, _ = generate_thumbnail_paths(req, "h/", "/i/")
    assert path.startswith("org.qux.baz/")


def test_generate_thumbnail_paths_host_empty():
    match_error_message = "Input should be a valid URL*"
    with pytest.raises(ValidationError, match=match_error_message):
        make_request(wms_url="not-a-url")


def test_generate_thumbnail_paths_naming_authority_with_date():
    req = make_request(id="foo.bar.baz:barbaz", start_date=datetime(2025, 1, 2))
    path, full_path = generate_thumbnail_paths(req, "https://host.xxx.yy", "/img/")
    assert path.startswith("foo.bar.baz/2025/01/02/barbaz.png")
    assert full_path.endswith(path)
    assert path == "foo.bar.baz/2025/01/02/barbaz.png"
    assert full_path == "https://host.xxx.yy/img/foo.bar.baz/2025/01/02/barbaz.png"


def test_generate_thumbnail_paths_naming_authority_without_date():
    req = make_request(id="foo:barbaz", start_date=None)
    path, full_path = generate_thumbnail_paths(req, "https://thumb-host/", "img/")
    assert path.startswith("foo/barb/barbaz.png")  # 'barb' is first 4 chars of local_id
    assert full_path.endswith(path)
    assert full_path.startswith("https://thumb-host/img/")


def test_generate_thumbnail_paths_naming_authority_short_localid():
    req = make_request(id="foo:ab", start_date=None)
    path, _ = generate_thumbnail_paths(req, "h/", "/i/")
    assert path.startswith("foo/no_date/ab.png")


def test_generate_thumbnail_paths_short_localid():
    req = make_request(id="ab", start_date=None)
    path, _ = generate_thumbnail_paths(req, "h/", "/i/")
    assert path == "com.bar.foo/no_date/ab.png"