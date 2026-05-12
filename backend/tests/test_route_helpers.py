"""Tests for underlying functions used by API routes (no server/TestClient)."""
import pytest

from backend.api.routes.generate import _group_parts_for_3mf, _stl_zip_name
from backend.api.routes.parts import _rotation_suffix, _parse_preview_filename


class TestPartsRotationSuffix:
    """Tests for _rotation_suffix used by part preview cache key."""

    def test_all_zero_returns_empty(self):
        assert _rotation_suffix(0, 0, 0) == ""

    def test_single_axis(self):
        assert "_r90" in _rotation_suffix(90, 0, 0)
        assert "_r-90" in _rotation_suffix(-90, 0, 0)
        assert _rotation_suffix(90, 0, 0) == "_r90_0_0"

    def test_all_axes(self):
        s = _rotation_suffix(90, 45, 30)
        assert s == "_r90_45_30"

    def test_float_rounded(self):
        assert _rotation_suffix(90.7, 0, 0) == "_r91_0_0"


class TestParsePreviewFilename:
    """Tests for _parse_preview_filename used by preview-cache list."""

    def test_simple_stem(self):
        assert _parse_preview_filename("3005_256") == {
            "ldraw_id": "3005",
            "size": 256,
            "rotation_x": 0,
            "rotation_y": 0,
            "rotation_z": 0,
            "quality_key": "",
        }

    def test_with_rotation(self):
        assert _parse_preview_filename("3005_512_r-90_0_0") == {
            "ldraw_id": "3005",
            "size": 512,
            "rotation_x": -90,
            "rotation_y": 0,
            "rotation_z": 0,
            "quality_key": "",
        }

    def test_with_quality_key(self):
        assert _parse_preview_filename("3005_256_qabc123") == {
            "ldraw_id": "3005",
            "size": 256,
            "rotation_x": 0,
            "rotation_y": 0,
            "rotation_z": 0,
            "quality_key": "abc123",
        }

    def test_with_color_suffix(self):
        # Parser allows optional _c[hex] at end; groups 4,5,6 are rotation
        out = _parse_preview_filename("3005_256_cff5500")
        assert out["ldraw_id"] == "3005"
        assert out["size"] == 256
        assert out["rotation_x"] == 0 and out["rotation_y"] == 0 and out["rotation_z"] == 0

    def test_invalid_returns_empty(self):
        assert _parse_preview_filename("") == {}
        assert _parse_preview_filename("nospace") == {}
        assert _parse_preview_filename("3005") == {}


class TestGenerateOutputHelpers:
    def test_group_parts_for_3mf_keeps_same_stl_in_different_colors(self, tmp_path):
        stl = tmp_path / "3005.stl"
        rows = [
            (stl, "3005", "CC0000"),
            (stl, "3005", "0055BF"),
            (stl, "3005", "cc0000"),
        ]

        grouped = _group_parts_for_3mf(rows)

        assert grouped == [
            (stl, "3005", 2, "CC0000"),
            (stl, "3005", 1, "0055BF"),
        ]

    def test_stl_zip_name_includes_color_when_available(self):
        assert _stl_zip_name("3005", 1, "cc0000") == "stls/3005_CC0000_1.stl"
        assert _stl_zip_name("3005", 1, None) == "stls/3005_1.stl"
