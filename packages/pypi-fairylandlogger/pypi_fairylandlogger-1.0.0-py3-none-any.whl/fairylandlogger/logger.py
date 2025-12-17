# coding: UTF-8
"""
@software: PyCharm
@author: Lionel Johnson
@contact: https://fairy.host
@organization: https://github.com/FairylandFuture
@datetime: 2025-11-29 16:58:56 UTC+08:00
"""

from ._structure import LoggerConfigStructure, LoggerRecordStructure
from ._registry import LoggerRegistry
from ._enums import LogLevelEnum


class Logger:

    def __init__(self, name: str, dirname: str = ""):
        self._name = name
        self._dirname = dirname
        self._registry = LoggerRegistry.get_instance()

        if name:
            self._registry.register_logger_file(name, dirname)

    @property
    def name(self) -> str:
        return self._name

    @property
    def dirname(self):
        return self._dirname

    def _emit(self, level: LogLevelEnum, msg: str, **kwargs) -> None:
        record = LoggerRecordStructure(
            name=self._name,
            level=level.upper(),
            message=msg,
            extra=kwargs or {}
        )
        self._registry.route(record)

    def trace(self, msg: str, **kwargs) -> None:
        self._emit(LogLevelEnum.TRACE, msg, **kwargs)

    def debug(self, msg: str, **kwargs) -> None:
        self._emit(LogLevelEnum.DEBUG, msg, **kwargs)

    def info(self, msg: str, **kwargs) -> None:
        self._emit(LogLevelEnum.INFO, msg, **kwargs)

    def success(self, msg: str, **kwargs) -> None:
        self._emit(LogLevelEnum.SUCCESS, msg, **kwargs)

    def warning(self, msg: str, **kwargs) -> None:
        self._emit(LogLevelEnum.WARNING, msg, **kwargs)

    def error(self, msg: str, **kwargs) -> None:
        self._emit(LogLevelEnum.ERROR, msg, **kwargs)

    def critical(self, msg: str, **kwargs) -> None:
        self._emit(LogLevelEnum.CRITICAL, msg, **kwargs)


class LogManager:
    _configured: bool = False

    @classmethod
    def configure(cls, config: LoggerConfigStructure) -> None:
        LoggerRegistry.get_instance().configure(config)
        cls._configured = True

    @classmethod
    def get_logger(cls, name: str = "", dirname: str = "") -> Logger:
        if not cls._configured:
            LoggerRegistry.get_instance().ensure_default()
            cls._configured = True
        return Logger(name, dirname)

    @classmethod
    def reset(cls) -> None:
        LoggerRegistry.reset()
        cls._configured = False

    @classmethod
    def set_level(cls, prefix: str, level: str) -> None:
        LoggerRegistry.get_instance().set_level(prefix, level)

    @classmethod
    def get_registry(cls) -> LoggerRegistry:
        return LoggerRegistry.get_instance()
