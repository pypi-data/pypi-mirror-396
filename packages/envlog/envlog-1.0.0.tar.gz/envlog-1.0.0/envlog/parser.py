"""
Parser for RUST_LOG-style logging specifications.

Syntax:
    - PTHN_LOG=info                           # Default level
    - PTHN_LOG=myapp=debug                    # Module-specific level
    - PTHN_LOG=warn,myapp=debug               # Default + module override
    - PTHN_LOG=myapp.submodule=trace          # Hierarchical modules
    - PTHN_LOG=warn,myapp=debug,other=error   # Multiple overrides
"""

import re
from typing import Dict, Optional

# Standard logging levels (lowercase to Python logging level names)
LEVEL_MAP = {
    "trace": "DEBUG",  # Rust's trace maps to Python's DEBUG
    "debug": "DEBUG",
    "info": "INFO",
    "warn": "WARNING",
    "warning": "WARNING",
    "error": "ERROR",
    "critical": "CRITICAL",
    "off": "CRITICAL",  # Rust's off - set to highest level
}


class LogSpec:
    """Parsed logging specification."""

    def __init__(
        self, default_level: Optional[str] = None, module_levels: Optional[Dict[str, str]] = None
    ):
        """
        Initialize a log specification.

        Args:
            default_level: Default logging level (Python level name)
            module_levels: Dict mapping module names to level names
        """
        self.default_level = default_level or "WARNING"
        self.module_levels = module_levels or {}

    def __repr__(self):
        return f"LogSpec(default={self.default_level}, modules={self.module_levels})"

    def __eq__(self, other):
        if not isinstance(other, LogSpec):
            return False
        return (
            self.default_level == other.default_level and self.module_levels == other.module_levels
        )


def normalize_level(level: str) -> str:
    """
    Normalize a level string to Python logging level name.

    Args:
        level: Level string (e.g., 'debug', 'INFO', 'warn')

    Returns:
        Normalized Python logging level name (e.g., 'DEBUG', 'WARNING')

    Raises:
        ValueError: If level is not recognized
    """
    level_lower = level.lower()
    if level_lower not in LEVEL_MAP:
        raise ValueError(
            f"Unknown log level: {level}. " f"Valid levels: {', '.join(LEVEL_MAP.keys())}"
        )
    return LEVEL_MAP[level_lower]


def parse_log_spec(spec: str) -> LogSpec:
    """
    Parse a RUST_LOG-style logging specification.

    Args:
        spec: Log specification string (e.g., 'warn,myapp=debug,other=error')

    Returns:
        LogSpec object with parsed configuration

    Raises:
        ValueError: If specification syntax is invalid

    Examples:
        >>> parse_log_spec('info')
        LogSpec(default=INFO, modules={})

        >>> parse_log_spec('warn,myapp=debug')
        LogSpec(default=WARNING, modules={'myapp': 'DEBUG'})

        >>> parse_log_spec('myapp.core=trace,otherlib=error')
        LogSpec(default=WARNING, modules={'myapp.core': 'DEBUG', 'otherlib': 'ERROR'})
    """
    if not spec or not spec.strip():
        return LogSpec()

    spec = spec.strip()
    parts = [p.strip() for p in spec.split(",")]

    default_level = None
    module_levels = {}

    for part in parts:
        if not part:
            continue

        # Check if it's a module=level or just a level
        if "=" in part:
            module, level = part.split("=", 1)
            module = module.strip()
            level = level.strip()

            if not module:
                raise ValueError(f"Empty module name in: {part}")
            if not level:
                raise ValueError(f"Empty level in: {part}")

            # Replace Rust's :: with Python's .
            module = module.replace("::", ".")

            # Validate module name (basic check)
            if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*$", module):
                raise ValueError(f"Invalid module name: {module}")

            normalized_level = normalize_level(level)
            module_levels[module] = normalized_level
        else:
            # It's a default level
            if default_level is not None:
                raise ValueError(f"Multiple default levels specified: {default_level} and {part}")
            default_level = normalize_level(part)

    return LogSpec(default_level=default_level, module_levels=module_levels)
