"""
Logging package to support structured, color-coded, and secure logging.

Features:
- ANSI color-coded console logs (configurable via .env).
- Log level and format controlled via .env.
- Custom SUCCESS log level in green.
- Rotating file logs.
- Optional email alerts on critical errors from Azure Key Vault.
"""

import inspect
import logging
import os
import pathlib
import platform
from logging.handlers import TimedRotatingFileHandler, SMTPHandler
from smtplib import SMTPException

from dotenv import find_dotenv, load_dotenv

# === Load environment variables ===
load_dotenv(find_dotenv())

# === Azure Key Vault initialization (optional) ===
key_smpt_vault_section = os.getenv("key_smpt_vault_section")
az_client = None

try:
    from azkees.az import Az, KeyNotFoundError
    az_client = Az(config_section=key_smpt_vault_section)
except ImportError:
    KeyNotFoundError = Exception  # type: ignore


def get_vault_secret(key: str) -> str | None:
    """
    Retrieve a secret value from Azure Key Vault.

    Args:
        key (str): Secret key to look up.

    Returns:
        str or None: Secret value or None if not found.

    Note:
        Returns None if azkees is not installed or if the secret is not found.
    """
    if az_client is None:
        return None

    try:
        return az_client.get_secrets(name=key).get("value")
    except KeyNotFoundError:
        return None
    except Exception:
        return None


# === Retrieve SMTP secrets ===
SMTP_HOST = get_vault_secret(os.getenv("key_smtp_host"))
SMTP_PORT = get_vault_secret(os.getenv("key_smtp_port"))
SMTP_PWD = get_vault_secret(os.getenv("key_smtp_pwd"))
SMTP_USERNAME = get_vault_secret(os.getenv("key_smtp_username"))

# === Platform-specific log folder ===
if platform.system() == "Windows":
    LOG_FOLDER = os.getenv("LOG_FOLDER_windows", "C:/energy/logs")
else:
    LOG_FOLDER = os.getenv("LOG_FOLDER_linux", "/var/log")

pathlib.Path(LOG_FOLDER).mkdir(parents=True, exist_ok=True)

# === Custom SUCCESS log level ===
SUCCESS_LEVEL = 25
logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")


def success(self: logging.Logger, msg: str, *args, **kwargs) -> None:
    """
    Custom log method for SUCCESS level.

    Args:
        self: Logger instance.
        msg: Log message.
        *args: Message formatting arguments.
        **kwargs: Additional keyword arguments.
    """
    if self.isEnabledFor(SUCCESS_LEVEL):
        self.log(SUCCESS_LEVEL, msg, *args, **kwargs)


logging.Logger.success = success  # type: ignore


# === Utilities ===


def get_log_level_from_env(default: str = "INFO") -> int:
    """
    Fetch the log level from the environment.

    Args:
        default (str): Fallback level if not set or invalid.

    Returns:
        int: Logging level constant.
    """
    level_str = os.getenv("LOG_LEVEL", default).upper()
    return getattr(logging, level_str, logging.INFO)


def get_log_format_from_env(
    default: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
) -> str:
    """
    Fetch the log format string from the environment.

    Args:
        default (str): Fallback format string.

    Returns:
        str: The format string for log messages.
    """
    return os.getenv("LOG_FORMAT", default)


def get_color(level_name: str, default: str) -> str:
    """
    Get ANSI color code for the given log level from .env.

    Decodes escape sequences so \\x1b becomes the real ANSI code.

    Args:
        level_name (str): e.g. DEBUG, INFO, SUCCESS
        default (str): fallback color if not found

    Returns:
        str: Interpreted ANSI string
    """
    raw = os.getenv(f"COLOR_{level_name}", default)
    return bytes(raw, "utf-8").decode("unicode_escape")


# === Custom Color Formatter ===


class CustomFormatter(logging.Formatter):
    """Formatter that applies ANSI color codes based on log level.

    Colors are fetched dynamically from environment variables.
    """

    def __init__(self, fmt: str) -> None:
        """Initialize the CustomFormatter.

        Args:
            fmt (str): The base format string.
        """
        super().__init__()
        self.fmt = fmt
        reset = get_color("RESET", "\x1b[0m")
        self.formats = {
            logging.DEBUG: (
                get_color("DEBUG", "\x1b[38;21m") + fmt + reset
            ),
            logging.INFO: (
                get_color("INFO", "\x1b[38;5;39m") + fmt + reset
            ),
            SUCCESS_LEVEL: (
                get_color("SUCCESS", "\x1b[38;5;40m") + fmt + reset
            ),
            logging.WARNING: (
                get_color("WARNING", "\x1b[38;5;226m") + fmt + reset
            ),
            logging.ERROR: (
                get_color("ERROR", "\x1b[38;5;196m") + fmt + reset
            ),
            logging.CRITICAL: (
                get_color("CRITICAL", "\x1b[31;1m") + fmt + reset
            ),
        }

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with appropriate color.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: The formatted log message with color codes.
        """
        log_fmt = self.formats.get(record.levelno, self.fmt)
        return logging.Formatter(log_fmt).format(record)


# === Main logger factory ===


def get_logger(logger_name: str) -> logging.Logger:
    """Create a logger with colored console and rotating file logs.

    Uses LOG_FORMAT from .env for both handlers.
    Prevents duplicates and supports optional email alerts.

    Args:
        logger_name (str): Name for the logger, typically __name__.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(logger_name)

    if logger.handlers:
        return logger

    log_level = get_log_level_from_env()
    formatter_str = get_log_format_from_env()
    logger.setLevel(log_level)

    # === Console Handler (colored) ===
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(CustomFormatter(formatter_str))
    logger.addHandler(console_handler)

    # === File Handler (plain format) ===
    caller_module = inspect.getmodule(inspect.stack()[1][0])
    caller_module_name = (
        caller_module.__name__.split(".")[-1]
        if caller_module
        else "main"
    )
    log_file_path = pathlib.Path(LOG_FOLDER) / f"{caller_module_name}.log"

    file_handler = TimedRotatingFileHandler(
        filename=str(log_file_path),
        when="midnight",
        backupCount=7,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(formatter_str))
    logger.addHandler(file_handler)

    # === Email Handler (optional) ===
    if SMTP_HOST and SMTP_PORT and SMTP_PWD and SMTP_USERNAME:
        try:
            email_handler = SMTPHandler(
                mailhost=(SMTP_HOST, int(SMTP_PORT)),
                fromaddr=SMTP_USERNAME,
                toaddrs=[SMTP_USERNAME],
                subject="Critical Error Logged",
                credentials=(SMTP_USERNAME, SMTP_PWD),
                secure=[]
            )
            email_handler.setLevel(logging.CRITICAL)
            email_handler.setFormatter(logging.Formatter(formatter_str))
            logger.addHandler(email_handler)
        except (OSError, ValueError, SMTPException) as e:
            logger.error(
                "Failed to configure email handler: %s",
                e
            )
    else:
        if os.getenv("key_smtp_host"):
            logger.warning(
                "SMTP credentials missing. Email handler not attached."
            )

    logger.propagate = False

    return logger
