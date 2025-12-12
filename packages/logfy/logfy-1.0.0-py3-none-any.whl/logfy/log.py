from __future__ import annotations

import logging
import colorlog
from typing import Any

# Register custom levels
logging.addLevelName(25, "SUCCESS")
logging.addLevelName(45, "FAIL")


def _create_colored_handler():
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s %(name)s %(levelname)8s │ %(message)s",
        datefmt="%H:%M:%S",
        log_colors={
            "DEBUG":    "cyan",
            "INFO":     "green",
            "WARNING":  "yellow",
            "ERROR":    "red",
            "CRITICAL": "bold_red",
            "SUCCESS":  "bold_green",
            "FAIL":     "bold_red",
        }
    ))
    return handler


class ClogAdapter(logging.LoggerAdapter):
    def __init__(self, name: str = "logfy"):
        logger = logging.getLogger(name)
        if not logger.handlers:
            logger.addHandler(_create_colored_handler())
            logger.setLevel(logging.DEBUG)
        super().__init__(logger, {})

    def process(self, msg: Any, kwargs: dict) -> tuple[Any, dict]:
        return msg, kwargs

    def success(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        self.log(25, msg, *args, **kwargs)

    def fail(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        self.log(45, msg, *args, **kwargs)


def get_logger(name: str = "logfy") -> ClogAdapter:
    """Get a beautifully colored logger with .success() and .fail() methods"""
    return ClogAdapter(name)