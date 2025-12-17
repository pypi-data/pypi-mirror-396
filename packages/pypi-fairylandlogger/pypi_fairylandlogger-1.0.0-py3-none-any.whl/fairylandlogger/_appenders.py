# coding: UTF-8
"""
@software: PyCharm
@author: Lionel Johnson
@contact: https://fairy.host
@organization: https://github.com/FairylandFuture
@datetime: 2025-11-29 16:50:50 UTC+08:00
"""

import abc
import typing as t
from pathlib import Path

from loguru import logger as _loguru_logger

from fairylandlogger import __banner__
from ._enums import LogLevelEnum, EncodingEnum


class AbstractLoggerAppender(abc.ABC):

    @abc.abstractmethod
    def add_sink(self): ...


class ConsoleLoggerAppender(AbstractLoggerAppender):
    _DEFAULT_PATTERN = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    def __init__(self, level: t.Union[str, LogLevelEnum] = LogLevelEnum.INFO, pattern: t.Optional[str] = None):
        self._level = level
        self.pattern = pattern or self._DEFAULT_PATTERN

    @property
    def level(self):
        return self._level.value if isinstance(self._level, LogLevelEnum) else self._level

    @level.setter
    def level(self, value: t.Union[str, LogLevelEnum]):
        self._level = value

    def add_sink(self):
        print(__banner__)
        _loguru_logger.add(
            sink=lambda x: print(x, end=""),
            level=self.level,
            format=self.pattern,
            colorize=True,
        )


class FileLoggerAppender(AbstractLoggerAppender):

    def __init__(
            self,
            path: t.Union[str, Path],
            level: t.Union[str, LogLevelEnum] = LogLevelEnum.INFO,
            retention: str = "180 days",
            rotation: str = "5 MB",
            encoding: t.Union[str, EncodingEnum] = EncodingEnum.UTF8,
            pattern: t.Optional[str] = None,
    ):
        self.path = path
        self._level = level
        self.rotation = rotation
        self.retention = retention
        self._encoding = encoding
        self.pattern = pattern

    @property
    def level(self):
        return self._level.value if isinstance(self._level, LogLevelEnum) else self._level

    @level.setter
    def level(self, value: t.Union[str, LogLevelEnum]):
        self._level = value

    @property
    def encoding(self):
        return self._encoding.value if isinstance(self._encoding, EncodingEnum) else self._encoding

    @encoding.setter
    def encoding(self, value: t.Union[str, EncodingEnum]):
        self._encoding = value

    def add_sink(self):
        _loguru_logger.add(
            sink=self.path,
            rotation=self.rotation,
            retention=self.retention,
            encoding=self.encoding,
            level=self.level,
            format=self.pattern,
            enqueue=True,
            backtrace=True,
            diagnose=True,
        )


class JSONLoggerAppender(AbstractLoggerAppender):

    def __init__(
            self,
            path: t.Union[str, Path],
            level: t.Union[str, LogLevelEnum] = LogLevelEnum.INFO,
            retention: str = "180 days",
            rotation: str = "5 MB",
            encoding: t.Union[str, EncodingEnum] = EncodingEnum.UTF8,
            pattern: t.Optional[str] = None,
    ):
        self.path = path
        self._level = level
        self.rotation = rotation
        self.retention = retention
        self._encoding = encoding
        self.__pattern = pattern  # Ignore this parameter in JSON mode

    @property
    def level(self):
        return self._level.value if isinstance(self._level, LogLevelEnum) else self._level

    @level.setter
    def level(self, value: t.Union[str, LogLevelEnum]):
        self._level = value

    @property
    def encoding(self):
        return self._encoding.value if isinstance(self._encoding, EncodingEnum) else self._encoding

    @encoding.setter
    def encoding(self, value: t.Union[str, EncodingEnum]):
        self._encoding = value

    def add_sink(self):
        _loguru_logger.add(
            sink=self.path,
            rotation=self.rotation,
            retention=self.retention,
            encoding=self.encoding,
            level=self.level,
            enqueue=True,
            backtrace=True,
            diagnose=True,
            serialize=True,
        )
