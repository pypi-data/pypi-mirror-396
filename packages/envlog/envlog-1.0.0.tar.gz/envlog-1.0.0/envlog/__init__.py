"""
envlog - Rust RUST_LOG-style environment variable configuration for Python logging.

Provides a simple way to configure Python's standard library logging using
environment variables with Rust's RUST_LOG syntax (via PTHN_LOG by default).
"""

from envlog.config import init, reset
from envlog.parser import parse_log_spec

__version__ = "1.0.0"
__all__ = ["init", "reset", "parse_log_spec"]
