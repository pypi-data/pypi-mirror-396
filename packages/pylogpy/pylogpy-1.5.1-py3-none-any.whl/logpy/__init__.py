"""
logpy - Structured, color-coded, and secure logging package.

Features:
- ANSI color-coded console logs (configurable via .env).
- Custom SUCCESS log level in green.
- Rotating file logs.
- Optional email alerts on critical errors from Azure Key Vault.
"""

from logpy.log import get_logger, get_log_level_from_env, get_log_format_from_env

__version__ = "1.4.3"
__author__ = "bek42"
__email__ = "bharani.nitturi@gmail.com"
__license__ = "MIT"

__all__ = [
    "get_logger",
    "get_log_level_from_env",
    "get_log_format_from_env",
]
