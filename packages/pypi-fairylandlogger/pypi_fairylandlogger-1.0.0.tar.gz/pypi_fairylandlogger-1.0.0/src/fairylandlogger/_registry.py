# coding: UTF-8
"""
@software: PyCharm
@author: Lionel Johnson
@contact: https://fairy.host
@organization: https://github.com/FairylandFuture
@datetime: 2025-11-29 16:56:33 UTC+08:00
"""

import os
import threading
import typing as t
from enum import Enum
from pathlib import Path

from loguru import logger as _loguru_logger

from ._appenders import AbstractLoggerAppender, ConsoleLoggerAppender, FileLoggerAppender, JSONLoggerAppender
from ._enums import LogLevelEnum
from ._structure import LoggerConfigStructure, LoggerRecordStructure


class LoggerRegistry:
    _instance: t.Optional["LoggerRegistry"] = None
    _lock: threading.RLock = threading.RLock()
    _LOG_LEVEL_ORDER: t.List[str] = ["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    def __init__(self):
        self._configured: bool = False
        self._config: t.Optional[LoggerConfigStructure] = None
        self._appenders: t.List[AbstractLoggerAppender] = []
        self._level: t.Union[str, LogLevelEnum] = LogLevelEnum.INFO
        self._levels: t.Dict[str, t.Union[str, LogLevelEnum]] = {}
        self._logger_file_handlers: t.Dict[str, t.List[int]] = {}  # Track logger-specific file handlers

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value: t.Union[str, LogLevelEnum]):
        self._level = value

    @property
    def config(self) -> t.Optional[LoggerConfigStructure]:
        return self._config

    @property
    def appenders(self) -> t.List[AbstractLoggerAppender]:
        return self._appenders.copy()

    @property
    def is_configured(self) -> bool:
        return self._configured

    @classmethod
    def get_instance(cls) -> "LoggerRegistry":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        with cls._lock:
            cls._instance = None
            try:
                _loguru_logger.remove()
            except Exception as error:
                raise error

    def configure(self, config: LoggerConfigStructure):
        with self._lock:
            self._reset_loguru_handlers()
            self._appenders.clear()
            self._logger_file_handlers.clear()

            self._config = config
            self._level = config.level

            if config.console:
                self._add_console_appender()

            if config.file:
                self._add_file_appenders(config)

            self._configured = True

    def _reset_loguru_handlers(self):
        try:
            _loguru_logger.remove()
        except Exception as error:
            raise error

    def _add_console_appender(self):
        console = ConsoleLoggerAppender(level=self._level)
        console.add_sink()
        self._appenders.append(console)

    def _add_file_appenders(self, config: LoggerConfigStructure):
        path = self._get_log_file_path(config.dirname, config.filename)

        # Add standard file appender
        file_appender = FileLoggerAppender(
            path=path,
            level=self._level,
            rotation=config.rotation,
            retention=config.retention,
            encoding=config.encoding,
            pattern=config.pattern,
        )
        file_appender.add_sink()
        self._appenders.append(file_appender)

        # Add JSON appender if enabled
        if config.json:
            json_path = self._get_json_log_path(path)
            json_appender = JSONLoggerAppender(
                path=json_path,
                level=self._level,
                rotation=config.rotation,
                retention=config.retention,
                encoding=config.encoding,
            )
            json_appender.add_sink()
            self._appenders.append(json_appender)

    def _get_log_file_path(self, dirname: t.Union[str, Path], filename: str) -> t.Union[str, Path]:
        os.makedirs(dirname, exist_ok=True)

        if isinstance(dirname, Path):
            return dirname.joinpath(filename)
        elif isinstance(dirname, str):
            return os.path.join(dirname, filename)
        else:
            raise TypeError("dirname must be str or Path")

    def _get_json_log_path(self, path: t.Union[str, Path]) -> str:
        json_path = str(path)
        if json_path.endswith('.log'):
            json_path = json_path[:-4] + "-json" + '.log'
        else:
            json_path = json_path + '.json'
        return json_path

    def ensure_default(self):
        if not self._configured:
            self.configure(LoggerConfigStructure())

    @classmethod
    def _should_log(cls, msg_level: t.Union[str, LogLevelEnum], eff_level: t.Union[str, LogLevelEnum]) -> bool:
        msg_level = msg_level.value if isinstance(msg_level, LogLevelEnum) else msg_level
        eff_level = eff_level.value if isinstance(eff_level, LogLevelEnum) else eff_level

        try:
            return cls._LOG_LEVEL_ORDER.index(msg_level) >= cls._LOG_LEVEL_ORDER.index(eff_level)
        except ValueError:
            return True

    def set_level(self, prefix: str, level: t.Union[str, LogLevelEnum]) -> None:
        with self._lock:
            self._levels[prefix] = level

    def _effective_level(self, logger_name: str) -> str:
        best = ("", self._level)
        for p, lvl in self._levels.items():
            if logger_name.startswith(p) and len(p) > len(best[0]):
                best = (p, lvl)

        return best[1]

    def register_logger_file(self, logger_name: str, dirname: str = "") -> None:
        if not self._config or not self._config.file or not logger_name:
            return

        with self._lock:
            # Skip if already registered
            if logger_name in self._logger_file_handlers:
                return

            # Build logger-specific file path
            if logger_name.endswith(".log"):
                log_filename = logger_name
            else:
                log_filename = f"{logger_name}.log"

            if not dirname:
                dirname = self._config.dirname
            else:
                dirname = os.path.join(self._config.dirname, dirname)
                os.makedirs(dirname, exist_ok=True)

            log_path = self._get_log_file_path(dirname, log_filename)

            # Add logger-specific file handler
            handler_id = _loguru_logger.add(
                sink=log_path,
                rotation=self._config.rotation,
                retention=self._config.retention,
                encoding=self._config.encoding.value if isinstance(self._config.encoding, Enum) else self._config.encoding,
                level=self._level.value if isinstance(self._level, LogLevelEnum) else self._level,
                format=self._config.pattern,
                filter=lambda record: record["extra"].get("logger_name") == logger_name,
                enqueue=True,
                backtrace=True,
                diagnose=True,
            )

            # Track the handler
            self._logger_file_handlers[logger_name] = [handler_id]

    def route(self, record: LoggerRecordStructure) -> None:
        if not self._should_log(record.level, self._effective_level(record.name)):
            return

        depth = record.depth
        msg = f"[{record.name}] {record.message}"

        extra_context = {"logger_name": record.name}
        self._log_message(record.level, msg, depth, extra_context)

    def _log_message(self, level: LogLevelEnum, msg: str, depth: int, extra: t.Dict[str, t.Any]) -> None:
        log_method = self._get_log_method(level)
        log_method(depth, msg, extra)

    def _get_log_method(self, level: LogLevelEnum) -> t.Callable:
        level_methods = {
            LogLevelEnum.TRACE: lambda d, m, e: _loguru_logger.opt(depth=d).bind(**e).trace(m),
            LogLevelEnum.DEBUG: lambda d, m, e: _loguru_logger.opt(depth=d).bind(**e).debug(m),
            LogLevelEnum.INFO: lambda d, m, e: _loguru_logger.opt(depth=d).bind(**e).info(m),
            LogLevelEnum.WARNING: lambda d, m, e: _loguru_logger.opt(depth=d).bind(**e).warning(m),
            LogLevelEnum.ERROR: lambda d, m, e: _loguru_logger.opt(depth=d).bind(**e).error(m),
            LogLevelEnum.SUCCESS: lambda d, m, e: _loguru_logger.opt(depth=d).bind(**e).success(m),
            LogLevelEnum.CRITICAL: lambda d, m, e: _loguru_logger.opt(depth=d).bind(**e).critical(m),
        }

        return level_methods.get(level, level_methods[LogLevelEnum.CRITICAL])
