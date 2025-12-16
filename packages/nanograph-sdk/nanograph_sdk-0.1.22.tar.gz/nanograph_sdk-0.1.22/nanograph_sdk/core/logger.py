from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Optional

_LEVEL_MAP = {
    "error": logging.ERROR,
    "warn": logging.WARNING,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "success": logging.INFO,
    "debug": logging.DEBUG,
}

_DEFAULT_SCOPE = "NanoSDK"


def _parse_level(raw: Optional[str]) -> int:
    if not raw:
        return logging.INFO
    normalised = raw.strip().lower()
    return _LEVEL_MAP.get(normalised, logging.INFO)


def _effective_level() -> int:
    env_value = (
        os.environ.get("NANOSDK_LOG_LEVEL")
        or os.environ.get("NANOCORE_LOG_LEVEL")
        or os.environ.get("LOG_LEVEL")
    )
    return _parse_level(env_value)


class _NanoFormatter(logging.Formatter):
    def __init__(self, scope: str) -> None:
        super().__init__("%(message)s")
        self.scope = scope

    def format(self, record: logging.LogRecord) -> str:
        display_level = getattr(record, "display_level", record.levelname.upper())
        message = super().format(record)
        return f"[{self.scope}] | [{display_level}] {message}"


@lru_cache(maxsize=None)
def _build_logger(scope: str) -> logging.Logger:
    logger = logging.getLogger(scope)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(_NanoFormatter(scope))
        logger.addHandler(handler)
        logger.propagate = False
    logger.setLevel(_effective_level())
    return logger


class StructuredLogger:
    """Small wrapper that mirrors the JS logger API for consistent output."""

    def __init__(self, scope: str) -> None:
        self.scope = scope
        self._logger = _build_logger(scope)

    def info(self, message: str, *args, **kwargs) -> None:
        self._logger.info(message, *args, **kwargs)

    def warn(self, message: str, *args, **kwargs) -> None:
        self._logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        self._logger.error(message, *args, **kwargs)

    def debug(self, message: str, *args, **kwargs) -> None:
        self._logger.debug(message, *args, **kwargs)

    def success(self, message: str, *args, **kwargs) -> None:
        self._logger.info(message, *args, extra={"display_level": "SUCCESS"}, **kwargs)

    def child(self, segment: str) -> "StructuredLogger":
        return StructuredLogger(f"{self.scope}/{segment}")


def create_logger(segment: Optional[str] = None) -> StructuredLogger:
    scope = f"{_DEFAULT_SCOPE}/{segment}" if segment else _DEFAULT_SCOPE
    return StructuredLogger(scope)


def resolve_logger(logger: Optional[StructuredLogger], segment: Optional[str] = None) -> StructuredLogger:
    if logger is None:
        return create_logger(segment)
    return logger.child(segment) if segment else logger


logger = create_logger()
