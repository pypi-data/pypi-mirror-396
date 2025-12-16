"""Integration tests for envlog package."""

import logging
import os

from envlog import init, reset


class TestIntegration:
    """End-to-end integration tests."""

    def setup_method(self):
        """Reset configuration and logging before each test."""
        reset()
        os.environ.pop("PTHN_LOG", None)
        # Reset logging configuration
        logging.root.handlers = []
        logging.root.setLevel(logging.WARNING)

    def test_basic_usage(self):
        """Test basic usage pattern."""
        os.environ["PTHN_LOG"] = "info"
        init()

        logger = logging.getLogger("myapp")
        logger.info("This should appear")
        logger.debug("This should not appear")

    def test_module_specific_configuration(self):
        """Test module-specific log levels."""
        init(log_spec="warn,myapp.core=debug,myapp.db=info")

        core_logger = logging.getLogger("myapp.core")
        db_logger = logging.getLogger("myapp.db")
        other_logger = logging.getLogger("otherlib")

        assert core_logger.level == logging.DEBUG
        assert db_logger.level == logging.INFO
        assert other_logger.getEffectiveLevel() == logging.WARNING

    def test_hierarchy_inheritance(self):
        """Test that child loggers inherit from parents."""
        init(log_spec="warn,myapp=debug")

        parent = logging.getLogger("myapp")
        child = logging.getLogger("myapp.submodule")

        # Parent should be DEBUG
        assert parent.level == logging.DEBUG
        # Child should inherit (level 0 = NOTSET, uses parent)
        assert child.getEffectiveLevel() == logging.DEBUG

    def test_rust_style_syntax(self):
        """Test Rust-style module separator (::)."""
        init(log_spec="myapp::core=debug")

        logger = logging.getLogger("myapp.core")
        assert logger.level == logging.DEBUG

    def test_trace_level_maps_to_debug(self):
        """Test that Rust's trace level maps to Python's DEBUG."""
        init(log_spec="trace")

        logger = logging.getLogger("test")
        assert logger.getEffectiveLevel() == logging.DEBUG

    def test_complex_configuration(self):
        """Test complex multi-module configuration."""
        spec = "warn,app=info,app.core=debug,app.db=trace," "lib1=error,lib2.special=debug"
        init(log_spec=spec)

        assert logging.getLogger("app").level == logging.INFO
        assert logging.getLogger("app.core").level == logging.DEBUG
        # trace->DEBUG
        assert logging.getLogger("app.db").level == logging.DEBUG
        assert logging.getLogger("lib1").level == logging.ERROR
        assert logging.getLogger("lib2.special").level == logging.DEBUG
        other_level = logging.getLogger("other").getEffectiveLevel()
        assert other_level == logging.WARNING
