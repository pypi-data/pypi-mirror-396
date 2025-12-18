# logpy

A production-ready Python logging package providing structured, color-coded, and secure logging with optional email alerts.

![Python](https://img.shields.io/badge/python-v3.12+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-1.4.3-blue)

## Features

- **🎨 Color-Coded Logs:** ANSI color-coded console output (configurable via environment variables)
- **📊 Custom SUCCESS Level:** Additional log level between WARNING and ERROR for success notifications
- **📁 Rotating File Handler:** Daily rotating file logs with 7-day retention
- **📧 Optional Email Alerts:** Send critical errors via SMTP from Azure Key Vault
- **🔧 Environment-Driven:** All configuration via environment variables with sensible defaults
- **🪟 Cross-Platform:** Works seamlessly on Windows and Linux with platform-specific log directories
- **🛡️ Graceful Degradation:** Missing optional features (SMTP) don't crash the logger

## Installation

### From PyPI

```bash
pip install logpy
```

### From Source

```bash
git clone https://github.com/bek42/logpy.git
cd logpy
poetry install
```

## Quick Start

```python
from logpy import get_logger

logger = get_logger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.success("Operation completed successfully!")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical issue")
```

## Configuration

All configuration is controlled via environment variables. Create a `.env` file in your project root:

```bash
# Log Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Log Format
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# ANSI Color Codes (optional)
COLOR_DEBUG=\x1b[38;21m
COLOR_INFO=\x1b[38;5;39m
COLOR_SUCCESS=\x1b[38;5;40m
COLOR_WARNING=\x1b[38;5;226m
COLOR_ERROR=\x1b[38;5;196m
COLOR_CRITICAL=\x1b[31;1m
COLOR_RESET=\x1b[0m

# File Handler - Platform-specific log directories
LOG_FOLDER_linux=/var/log
LOG_FOLDER_windows=C:/energy/logs

# SMTP Configuration (optional - for email alerts on CRITICAL)
key_smtp_host=SMTP_HOST_KEY_NAME
key_smtp_port=SMTP_PORT_KEY_NAME
key_smtp_username=SMTP_USERNAME_KEY_NAME
key_smtp_pwd=SMTP_PASSWORD_KEY_NAME
key_smpt_vault_section=default
```

See [.env.example](.env.example) for a complete example.

## Environment Variables Reference

### Logging Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | INFO | Logging level: DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL |
| `LOG_FORMAT` | `%(asctime)s - %(name)s - %(levelname)s - %(message)s` | Log message format string |

### Color Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `COLOR_DEBUG` | `\x1b[38;21m` | ANSI code for DEBUG level |
| `COLOR_INFO` | `\x1b[38;5;39m` | ANSI code for INFO level |
| `COLOR_SUCCESS` | `\x1b[38;5;40m` | ANSI code for SUCCESS level |
| `COLOR_WARNING` | `\x1b[38;5;226m` | ANSI code for WARNING level |
| `COLOR_ERROR` | `\x1b[38;5;196m` | ANSI code for ERROR level |
| `COLOR_CRITICAL` | `\x1b[31;1m` | ANSI code for CRITICAL level |
| `COLOR_RESET` | `\x1b[0m` | ANSI reset code |

### Log Directory Configuration

| Variable | Default (Linux) | Default (Windows) | Description |
|----------|-----------------|-------------------|-------------|
| `LOG_FOLDER_linux` | `/var/log` | N/A | Log directory on Linux |
| `LOG_FOLDER_windows` | N/A | `C:/energy/logs` | Log directory on Windows |

### SMTP Configuration (Optional)

For email alerts on CRITICAL errors, configure these Azure Key Vault secret key names:

| Variable | Description |
|----------|-------------|
| `key_smtp_host` | Key name for SMTP host in Azure Key Vault |
| `key_smtp_port` | Key name for SMTP port in Azure Key Vault |
| `key_smtp_username` | Key name for SMTP username in Azure Key Vault |
| `key_smtp_pwd` | Key name for SMTP password in Azure Key Vault |
| `key_smpt_vault_section` | Azure Key Vault section/config name (default: `default`) |

## Usage Examples

### Basic Logging

```python
from logpy import get_logger

logger = get_logger("myapp")

logger.info("Application started")
logger.success("Data processed successfully")
logger.warning("API response time exceeded 5s")
logger.error("Failed to connect to database")
```

### With Custom Log Format

```python
import os
os.environ["LOG_FORMAT"] = "[%(levelname)s] %(asctime)s | %(name)s >> %(message)s"

from logpy import get_logger

logger = get_logger("custom")
logger.info("Custom format applied")
```

### With Custom Colors

```python
import os

# Use purple for INFO level
os.environ["COLOR_INFO"] = "\x1b[38;5;135m"

from logpy import get_logger

logger = get_logger("colorful")
logger.info("This INFO message is now purple!")
```

### Disable Color Output

```python
import os

# Set all colors to reset code (removes color)
os.environ["COLOR_DEBUG"] = "\x1b[0m"
os.environ["COLOR_INFO"] = "\x1b[0m"
os.environ["COLOR_SUCCESS"] = "\x1b[0m"
os.environ["COLOR_WARNING"] = "\x1b[0m"
os.environ["COLOR_ERROR"] = "\x1b[0m"
os.environ["COLOR_CRITICAL"] = "\x1b[0m"

from logpy import get_logger

logger = get_logger("plain")
logger.info("No colors in output")
```

### With Email Alerts

Configure Azure Key Vault secrets and environment variables:

```bash
# .env
key_smtp_host=smtp_host_secret
key_smtp_port=smtp_port_secret
key_smtp_username=smtp_user_secret
key_smtp_pwd=smtp_pwd_secret
key_smpt_vault_section=production
```

```python
from logpy import get_logger

logger = get_logger("critical_app")

try:
    # Critical operation
    result = risky_operation()
except Exception as e:
    # This will send an email alert
    logger.critical("Operation failed: %s", e)
```

## Logging Levels

logpy supports all standard Python logging levels plus a custom `SUCCESS` level:

| Level | Value | Description |
|-------|-------|-------------|
| DEBUG | 10 | Detailed information for debugging |
| INFO | 20 | General informational messages |
| **SUCCESS** | **25** | Operation completed successfully (custom) |
| WARNING | 30 | Warning messages |
| ERROR | 40 | Error messages |
| CRITICAL | 50 | Critical system failures (triggers email if configured) |

## API Reference

### `get_logger(logger_name: str) -> logging.Logger`

Creates and configures a logger instance with colored console and rotating file handlers.

**Parameters:**
- `logger_name` (str): Name for the logger, typically `__name__`

**Returns:**
- `logging.Logger`: Configured logger instance

**Example:**
```python
from logpy import get_logger

logger = get_logger("myapp.module")
logger.info("Logger initialized")
```

### `get_log_level_from_env(default: str = "INFO") -> int`

Fetch the log level from the `LOG_LEVEL` environment variable.

**Parameters:**
- `default` (str): Fallback level if not set or invalid (default: "INFO")

**Returns:**
- `int`: Logging level constant (e.g., `logging.DEBUG`)

### `get_log_format_from_env(default: str = "...") -> str`

Fetch the log format string from the `LOG_FORMAT` environment variable.

**Parameters:**
- `default` (str): Fallback format if not set

**Returns:**
- `str`: Format string for log messages

## Testing

Run the test suite:

```bash
poetry install
poetry run pytest
```

Run linting:

```bash
poetry run flake8 .
```

## How It Works

1. **Initialization:** When `get_logger()` is called, logpy loads environment variables from `.env`
2. **Console Handler:** Adds a colored StreamHandler using `CustomFormatter`
3. **File Handler:** Adds a `TimedRotatingFileHandler` that rotates daily with 7-day retention
4. **Email Handler (Optional):** If SMTP credentials are available in Azure Key Vault, adds an SMTPHandler for CRITICAL errors
5. **Graceful Degradation:** Missing Azure Key Vault or SMTP config logs a warning but doesn't crash

### File Logging

Log files are automatically created in:
- **Linux:** `/var/log/` (configurable via `LOG_FOLDER_linux`)
- **Windows:** `C:/energy/logs/` (configurable via `LOG_FOLDER_windows`)

File names are based on the caller module (e.g., `myapp.log`)

### Email Alerts

When a CRITICAL error is logged and SMTP is configured:
1. The error message is formatted using `LOG_FORMAT`
2. An email is sent from SMTP_USERNAME to SMTP_USERNAME
3. Subject: "Critical Error Logged"
4. If SMTP fails, an error is logged but execution continues

## Troubleshooting

### Logs not appearing in file

- **Check permissions:** Ensure the log directory is writable
- **Check path:** Verify `LOG_FOLDER_linux` or `LOG_FOLDER_windows` is correct
- **Check logger name:** File names are based on the module name (last part of logger name)

### Colors not showing

- **Terminal support:** Not all terminals support 256-color ANSI codes
- **Check COLOR_* env vars:** Verify color codes are set correctly
- **Override colors:** Set `COLOR_*` environment variables explicitly

### Email alerts not working

- **Check Azure Key Vault:** Verify azkees can access the vault
- **Check secrets:** Ensure SMTP secret keys exist and are accessible
- **Check SMTP config:** Verify SMTP host, port, and credentials are correct
- **Check logs:** Look for "Failed to configure email handler" messages

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository** on GitHub
2. **Create a feature branch:** `git checkout -b feature/your-feature`
3. **Follow commit conventions:** Use [Conventional Commits](https://www.conventionalcommits.org/)
   - `feat(scope): description` - New features
   - `fix(scope): description` - Bug fixes
   - `docs(scope): description` - Documentation
   - `chore(scope): description` - Build/dependency changes
4. **Add tests** for new features
5. **Run linting:** `poetry run flake8 .`
6. **Submit a pull request** with clear description

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation:** See this README for usage guides
- **Issues:** Report bugs on [GitHub Issues](https://github.com/bek42/logpy/issues)
- **Security:** For security issues, please email bharani.nitturi@gmail.com instead of using GitHub issues

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and release notes.

## Author

**bek42** - [bharani.nitturi@gmail.com](mailto:bharani.nitturi@gmail.com)

---

**Made with ❤️ for better logging in Python**