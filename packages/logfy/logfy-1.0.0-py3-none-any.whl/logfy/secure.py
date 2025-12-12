from __future__ import annotations

import builtins
from pathlib import Path
from typing import Optional

from logcrypt import Logger as cryptlogger
from logcrypt import generate_key

# Global secure logger (will replace the default one)
secure_logger = None


def enable_secure_logging(
    filename: str = "logfy_secure.log",
    key_file: str = ".logfy_key",
    correlation_id: Optional[str] = None,
    log_level: str = "DEBUG",
) -> cryptlogger:
    """
    Enable secure encrypted logging.

    Returns a logger that writes to:
      • Beautiful colored console
      • Encrypted + checksummed file (tamper-evident)

    Automatically upgrades the global `logfy.log` if used.
    """
    global secure_logger

    key_path = Path(key_file)
    if not key_path.exists():
        generate_key(encryption_key=None, key_file=str(key_path))

    secure_logger = cryptlogger(
        file_name=filename,
        encrypt_file=True,
        key_file=str(key_path),
        log_level=log_level.upper(),
        correlation_id=correlation_id or "logfy",
        async_logging=True,
        file_format="text",
    )

    print(f"Secure logging enabled → {filename}")
    print(f"Encryption key → {key_path.resolve()}")

    # Auto-upgrade global `logfy.log`
    try:
        if hasattr(builtins, "__logfy_make_secure__"):
            builtins.__logfy_make_secure__()  # type: ignore
    except Exception:
        pass

    return secure_logger