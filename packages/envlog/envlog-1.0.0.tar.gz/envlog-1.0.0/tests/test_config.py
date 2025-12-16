"""Tests for envlog.config module."""

import logging
import os

from envlog.config import build_dict_config, init, reset
from envlog.parser import LogSpec


class TestBuildDictConfig:
    """Tests for build_dict_config function."""

    def test_default_spec(self):
        spec = LogSpec(default_level="INFO")
        config = build_dict_config(spec)

        assert config["version"] == 1
        assert config["disable_existing_loggers"] is False
        assert "console" in config["handlers"]
        assert config["root"]["level"] == "INFO"

    def test_module_levels(self):
        spec = LogSpec(
            default_level="WARNING",
            module_levels={"myapp": "DEBUG", "otherlib": "ERROR"},
        )
        config = build_dict_config(spec)

        assert config["root"]["level"] == "WARNING"
        assert "myapp" in config["loggers"]
        assert config["loggers"]["myapp"]["level"] == "DEBUG"
        assert config["loggers"]["otherlib"]["level"] == "ERROR"

    def test_custom_format(self):
        spec = LogSpec()
        config = build_dict_config(
            spec,
            log_format="%(name)s - %(message)s",
            date_format="%Y-%m-%d",
        )

        fmt = config["formatters"]["standard"]["format"]
        assert fmt == "%(name)s - %(message)s"
        assert config["formatters"]["standard"]["datefmt"] == "%Y-%m-%d"


class TestInit:
    """Tests for init function."""

    def setup_method(self):
        """Reset configuration before each test."""
        reset()
        # Clear any PTHN_LOG from environment
        os.environ.pop("PTHN_LOG", None)

    def test_init_with_explicit_spec(self):
        init(log_spec="debug")

        logger = logging.getLogger("test")
        assert logger.getEffectiveLevel() == logging.DEBUG

    def test_init_from_env_var(self):
        os.environ["PTHN_LOG"] = "info"
        init()

        logger = logging.getLogger("test")
        assert logger.getEffectiveLevel() == logging.INFO

    def test_init_with_custom_env_var(self):
        os.environ["MY_LOG"] = "error"
        init(env_var="MY_LOG")

        logger = logging.getLogger("test")
        assert logger.getEffectiveLevel() == logging.ERROR

    def test_explicit_spec_overrides_env(self):
        os.environ["PTHN_LOG"] = "info"
        init(log_spec="error")

        logger = logging.getLogger("test")
        assert logger.getEffectiveLevel() == logging.ERROR

    def test_module_specific_levels(self):
        init(log_spec="warn,myapp=debug")

        root_logger = logging.getLogger()
        myapp_logger = logging.getLogger("myapp")

        assert root_logger.level == logging.WARNING
        assert myapp_logger.level == logging.DEBUG

    def test_hierarchical_loggers(self):
        init(log_spec="warn,myapp.core=debug")

        logger = logging.getLogger("myapp.core")
        assert logger.level == logging.DEBUG

    def test_init_without_spec_uses_defaults(self):
        init()

        logger = logging.getLogger("test")
        assert logger.getEffectiveLevel() == logging.WARNING

    def test_init_twice_does_not_reconfigure(self, caplog):
        init(log_spec="info")
        init(log_spec="debug")  # Should not apply

        logger = logging.getLogger("test")
        # Should still be INFO from first init
        assert logger.getEffectiveLevel() == logging.INFO

    def test_force_reconfigure(self):
        init(log_spec="info")
        init(log_spec="debug", force=True)

        logger = logging.getLogger("test")
        assert logger.getEffectiveLevel() == logging.DEBUG


class TestReset:
    """Tests for reset function."""

    def test_reset_allows_reinit(self):
        init(log_spec="info")
        reset()
        init(log_spec="debug")

        logger = logging.getLogger("test")
        assert logger.getEffectiveLevel() == logging.DEBUG
