from __future__ import annotations

from .log import get_logger, ClogAdapter
from .secure import enable_secure_logging
from .decrypt import decrypt_secure_log

# Convenience global logger (starts as colored console only)
log = get_logger("loggercolor")

# Will be called by enable_secure_logging() to upgrade the global `log`
def _make_global_log_secure() -> None:
    global log
    if secure_logger is not None:
        log = secure_logger  # type: ignore
        log.debug("Global `loggercolor.log` upgraded to secure (encrypted) logging")

__all__ = [
    "get_logger",
    "ClogAdapter",
    "enable_secure_logging",
    "decrypt_secure_log",
    "log",
]