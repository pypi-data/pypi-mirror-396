"""Tests for envlog.parser module."""

import pytest

from envlog.parser import normalize_level, parse_log_spec


class TestNormalizeLevel:
    """Tests for normalize_level function."""

    def test_lowercase_levels(self):
        assert normalize_level("trace") == "DEBUG"
        assert normalize_level("debug") == "DEBUG"
        assert normalize_level("info") == "INFO"
        assert normalize_level("warn") == "WARNING"
        assert normalize_level("warning") == "WARNING"
        assert normalize_level("error") == "ERROR"
        assert normalize_level("critical") == "CRITICAL"

    def test_uppercase_levels(self):
        assert normalize_level("INFO") == "INFO"
        assert normalize_level("DEBUG") == "DEBUG"
        assert normalize_level("ERROR") == "ERROR"

    def test_mixed_case(self):
        assert normalize_level("Info") == "INFO"
        assert normalize_level("WaRn") == "WARNING"

    def test_invalid_level(self):
        with pytest.raises(ValueError, match="Unknown log level"):
            normalize_level("invalid")


class TestParseLogSpec:
    """Tests for parse_log_spec function."""

    def test_empty_spec(self):
        spec = parse_log_spec("")
        assert spec.default_level == "WARNING"
        assert spec.module_levels == {}

    def test_default_level_only(self):
        spec = parse_log_spec("info")
        assert spec.default_level == "INFO"
        assert spec.module_levels == {}

    def test_module_level_only(self):
        spec = parse_log_spec("myapp=debug")
        assert spec.default_level == "WARNING"
        assert spec.module_levels == {"myapp": "DEBUG"}

    def test_default_and_module(self):
        spec = parse_log_spec("warn,myapp=debug")
        assert spec.default_level == "WARNING"
        assert spec.module_levels == {"myapp": "DEBUG"}

    def test_multiple_modules(self):
        spec = parse_log_spec("info,myapp=debug,otherlib=error")
        assert spec.default_level == "INFO"
        assert spec.module_levels == {
            "myapp": "DEBUG",
            "otherlib": "ERROR",
        }

    def test_hierarchical_modules(self):
        spec = parse_log_spec("myapp.core=debug,myapp.db=trace")
        assert spec.module_levels == {
            "myapp.core": "DEBUG",
            "myapp.db": "DEBUG",  # trace maps to DEBUG
        }

    def test_rust_style_separators(self):
        spec = parse_log_spec("myapp::core=debug")
        assert spec.module_levels == {"myapp.core": "DEBUG"}

    def test_whitespace_handling(self):
        spec = parse_log_spec("  warn , myapp = debug , other = error  ")
        assert spec.default_level == "WARNING"
        assert spec.module_levels == {
            "myapp": "DEBUG",
            "other": "ERROR",
        }

    def test_multiple_defaults_error(self):
        with pytest.raises(ValueError, match="Multiple default levels"):
            parse_log_spec("info,warn")

    def test_empty_module_name_error(self):
        with pytest.raises(ValueError, match="Empty module name"):
            parse_log_spec("=debug")

    def test_empty_level_error(self):
        with pytest.raises(ValueError, match="Empty level"):
            parse_log_spec("myapp=")

    def test_invalid_module_name(self):
        with pytest.raises(ValueError, match="Invalid module name"):
            parse_log_spec("my-app=debug")

    def test_equality(self):
        spec1 = parse_log_spec("warn,myapp=debug")
        spec2 = parse_log_spec("warn,myapp=debug")
        assert spec1 == spec2

    def test_repr(self):
        spec = parse_log_spec("warn,myapp=debug")
        assert "WARNING" in repr(spec)
        assert "myapp" in repr(spec)
