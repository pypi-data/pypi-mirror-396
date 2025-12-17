# src/anypoint_sdk/_logging.py
from __future__ import annotations

import logging
from typing import Any, Protocol


class LoggerLike(Protocol):
    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
    def info(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
    def error(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
    def child(self, suffix: str) -> "LoggerLike": ...


class StdlibLogger(LoggerLike):
    def __init__(self, logger: logging.Logger) -> None:
        self._log = logger

    def debug(self, msg: str, *a: Any, **kw: Any) -> None:
        self._log.debug(msg, *a, **kw)

    def info(self, msg: str, *a: Any, **kw: Any) -> None:
        self._log.info(msg, *a, **kw)

    def warning(self, msg: str, *a: Any, **kw: Any) -> None:
        self._log.warning(msg, *a, **kw)

    def error(self, msg: str, *a: Any, **kw: Any) -> None:
        self._log.error(msg, *a, **kw)

    def child(self, suffix: str) -> "LoggerLike":
        return StdlibLogger(self._log.getChild(suffix))


class NullLogger(LoggerLike):
    def debug(self, msg: str, *a: Any, **kw: Any) -> None:
        pass

    def info(self, msg: str, *a: Any, **kw: Any) -> None:
        pass

    def warning(self, msg: str, *a: Any, **kw: Any) -> None:
        pass

    def error(self, msg: str, *a: Any, **kw: Any) -> None:
        pass

    def child(self, suffix: str) -> "LoggerLike":
        return self


def default_logger() -> StdlibLogger:
    base = logging.getLogger("anypoint_sdk")
    if not any(isinstance(h, logging.NullHandler) for h in base.handlers):
        base.addHandler(logging.NullHandler())
    return StdlibLogger(base)
