from __future__ import annotations

from pathlib import Path
from typing import Generator, Optional

from logcrypt import decrypt_log


def decrypt_secure_log(
    logfile: str | Path,
    key_file: Optional[str | Path] = None,
    key: Optional[str] = None,
) -> Generator[str, None, None]:
    """
    Decrypt a logfy-encrypted log file.

    Auto-finds key using smart defaults:
      • <logfile>.key
      • .logfy_key in same dir or home
    """
    logfile = Path(logfile)

    if key is None and key_file is None:
        candidates = [
            logfile.with_suffix(".key"),
            logfile.parent / ".logfy_key",
            Path.home() / ".logfy_key",
        ]
        for candidate in candidates:
            if candidate.exists():
                key_file = candidate
                break

    if key is None and key_file is not None:
        key = Path(key_file).read_text().strip()

    if key is None:
        raise FileNotFoundError(
            "Encryption key not found. Provide key, key_file, or use default locations."
        )

    entries = decrypt_log(str(logfile), encryption_key=key)

    for entry in entries:
        yield entry["decrypted_line"]