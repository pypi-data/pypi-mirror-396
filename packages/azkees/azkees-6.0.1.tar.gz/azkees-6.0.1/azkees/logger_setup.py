"""
Logger setup module for azkees project.

This module:
- Reads logging config from environment variables.
- Retrieves SMTP credentials from Azure Key Vault.
- Supports ANSI color-coded log levels.
- Configures console, file, and optional email handlers.
"""

import inspect
import logging
import os
import pathlib
import platform
from logging.handlers import SMTPHandler, TimedRotatingFileHandler
from smtplib import SMTPException

from azure.core.exceptions import AzureError
from dotenv import find_dotenv, load_dotenv

from azkees.az_base import AzBase

# === Load environment variables ===
load_dotenv(find_dotenv())

# === Determine platform-specific paths ===
# Support LOG_FOLDER env var for testing, otherwise use platform-specific defaults
if os.getenv("LOG_FOLDER"):
    LOG_FOLDER = os.getenv("LOG_FOLDER")
elif platform.system() == "Windows":
    LOG_FOLDER = os.getenv("log_folder_windows", "C:/energy/logs")
else:
    LOG_FOLDER = os.getenv("log_folder_linux", "./logs")  # Use local logs by default

# Create log directory with proper error handling
try:
    pathlib.Path(LOG_FOLDER).mkdir(parents=True, exist_ok=True)
except PermissionError:
    # Fall back to local logs directory if we can't write to system folder
    LOG_FOLDER = "./logs"
    pathlib.Path(LOG_FOLDER).mkdir(parents=True, exist_ok=True)

# === Initialize Azure Key Vault client (lazy initialization) ===
key_smpt_vault_section = os.getenv("key_smpt_vault_section")
_az_client = None

def get_vault_secret(key: str) -> str | None:
    """
    Retrieve a secret value from Azure Key Vault.

    Args:
        key (str): Secret key to look up.

    Returns:
        str or None: Secret value or None if not found.
    """
    global _az_client
    if _az_client is None and key_smpt_vault_section:
        try:
            _az_client = AzBase(config_section=key_smpt_vault_section)
        except (ValueError, FileNotFoundError):
            # Vault client not available - SMTP logging will be disabled
            return None
    
    if _az_client is None:
        return None
    
    try:
        return _az_client.get_secret(name=key)
    except AzureError:
        return None

# === Retrieve SMTP secrets (will be None if vault unavailable) ===
SMTP_HOST = get_vault_secret(os.getenv("key_smtp_host")) if os.getenv("key_smtp_host") else None
SMTP_PORT = get_vault_secret(os.getenv("key_smtp_port")) if os.getenv("key_smtp_port") else None
SMTP_PWD = get_vault_secret(os.getenv("key_smtp_pwd")) if os.getenv("key_smtp_pwd") else None
SMTP_USERNAME = get_vault_secret(os.getenv("key_smtp_username")) if os.getenv("key_smtp_username") else None

# === Add custom SUCCESS log level ===
SUCCESS_LEVEL = 25
logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")

def success(self, msg, *args, **kwargs):
    """
    Custom log method for SUCCESS level.
    """
    if self.isEnabledFor(SUCCESS_LEVEL):
        self.log(SUCCESS_LEVEL, msg, *args, **kwargs)

logging.Logger.success = success  # Inject into Logger class

# === ANSI color formatter utilities ===

def get_color(level_name: str, default: str) -> str:
    """
    Get ANSI color code for a log level from .env.

    Args:
        level_name (str): Level name like DEBUG, INFO, etc.
        default (str): Fallback ANSI code.

    Returns:
        str: ANSI escape sequence
    """
    raw = os.getenv(f"COLOR_{level_name}", default)
    return bytes(raw, "utf-8").decode("unicode_escape")

class CustomFormatter(logging.Formatter):
    """
    Formatter that applies ANSI color codes to console output.
    """
    def __init__(self, fmt: str):
        super().__init__()
        self.fmt = fmt
        reset = get_color("RESET", "\x1b[0m")
        self.formats = {
            logging.DEBUG: get_color("DEBUG", "\x1b[38;21m") + fmt + reset,
            logging.INFO: get_color("INFO", "\x1b[38;5;39m") + fmt + reset,
            SUCCESS_LEVEL: get_color("SUCCESS", "\x1b[38;5;40m") + fmt + reset,
            logging.WARNING: get_color("WARNING", "\x1b[38;5;226m") + fmt + reset,
            logging.ERROR: get_color("ERROR", "\x1b[38;5;196m") + fmt + reset,
            logging.CRITICAL: get_color("CRITICAL", "\x1b[31;1m") + fmt + reset,
        }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.formats.get(record.levelno, self.fmt)
        return logging.Formatter(log_fmt).format(record)

# === Log level & format helpers ===

def get_log_level_from_env(default: str = "INFO") -> int:
    """
    Fetch log level from environment.

    Args:
        default (str): Fallback level.

    Returns:
        int: Logging level constant.
    """
    level_str = os.getenv("LOG_LEVEL", default).upper()
    return getattr(logging, level_str, logging.INFO)

def get_log_format_from_env(
    default: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
) -> str:
    """
    Fetch log format from environment.

    Args:
        default (str): Fallback format.

    Returns:
        str: Log format string.
    """
    return os.getenv("LOG_FORMAT", default)

# === Main logger builder ===

def get_logger(logger_name: str) -> logging.Logger:
    """
    Builds a fully configured logger with color, file, and optional email handlers.

    Args:
        logger_name (str): Logger name (usually module or project name).

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(logger_name)

    if logger.handlers:
        return logger  # Already configured

    log_level = get_log_level_from_env()
    formatter_str = get_log_format_from_env()
    logger.setLevel(log_level)

    # === Console handler ===
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(CustomFormatter(formatter_str))
    logger.addHandler(console_handler)

    # === File handler ===
    caller_module = inspect.getmodule(inspect.stack()[1][0])
    caller_module_name = caller_module.__name__.split(".")[-1] if caller_module else "main"
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

    # === Email handler (optional) ===
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
            logger.error("Failed to configure email handler: %s", e)
    else:
        logger.warning("SMTP credentials missing. Email handler not attached.")

    logger.propagate = False
    return logger

# === Global logger for azkees ===
log = get_logger("azkees")
