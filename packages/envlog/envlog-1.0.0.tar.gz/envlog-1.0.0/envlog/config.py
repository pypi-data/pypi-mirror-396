"""
Configuration builder for Python's logging.config.dictConfig.
"""

import logging
import logging.config
import os
from typing import Any, Dict, Optional

from envlog.parser import LogSpec, parse_log_spec

# Track if we've already configured logging
_configured = False


def build_dict_config(
    spec: LogSpec, log_format: Optional[str] = None, date_format: Optional[str] = None
) -> Dict[str, Any]:
    """
    Build a logging.config.dictConfig dictionary from a LogSpec.

    Args:
        spec: Parsed log specification
        log_format: Log message format string (default: standard format)
        date_format: Date format string (default: ISO-8601 style)

    Returns:
        Dictionary suitable for logging.config.dictConfig
    """
    if log_format is None:
        log_format = "%(asctime)s [%(levelname)8s] %(name)s: %(message)s"

    if date_format is None:
        date_format = "%Y-%m-%d %H:%M:%S"

    # Build the configuration
    config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": log_format,
                "datefmt": date_format,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "stream": "ext://sys.stderr",
            },
        },
        "root": {
            "level": spec.default_level,
            "handlers": ["console"],
        },
        "loggers": {},
    }

    # Add module-specific loggers
    for module, level in spec.module_levels.items():
        config["loggers"][module] = {
            "level": level,
            "handlers": ["console"],
            "propagate": False,
        }

    return config


def init(
    log_spec: Optional[str] = None,
    env_var: str = "PTHN_LOG",
    log_format: Optional[str] = None,
    date_format: Optional[str] = None,
    force: bool = False,
) -> None:
    """
    Initialize logging from a RUST_LOG-style specification.

    Reads from environment variable or explicit log_spec parameter.
    Configures Python's standard library logging using dictConfig.

    Args:
        log_spec: Explicit log specification (overrides env_var if provided)
        env_var: Environment variable name to read (default: 'PTHN_LOG')
        log_format: Custom log message format
        date_format: Custom date format
        force: Force reconfiguration even if already configured

    Examples:
        >>> import os
        >>> os.environ['PTHN_LOG'] = 'info'
        >>> init()

        >>> init(log_spec='warn,myapp=debug')

        >>> init(env_var='MY_LOG')
    """
    global _configured

    if _configured and not force:
        logging.getLogger(__name__).debug(
            "Logging already configured. Use force=True to reconfigure."
        )
        return

    # Determine the specification to use
    spec_str = log_spec
    if spec_str is None:
        spec_str = os.environ.get(env_var, "")

    # Parse the specification
    if spec_str:
        spec = parse_log_spec(spec_str)
    else:
        # No specification provided, use defaults
        spec = parse_log_spec("warning")

    # Build and apply configuration
    config = build_dict_config(spec, log_format=log_format, date_format=date_format)
    logging.config.dictConfig(config)

    _configured = True

    # Log that we've configured (use root logger)
    logger = logging.getLogger("envlog")
    logger.debug(f"Logging configured: {spec}")


def reset() -> None:
    """
    Reset the configuration state.

    This allows init() to be called again without force=True.
    Does not modify the actual logging configuration.
    """
    global _configured
    _configured = False
