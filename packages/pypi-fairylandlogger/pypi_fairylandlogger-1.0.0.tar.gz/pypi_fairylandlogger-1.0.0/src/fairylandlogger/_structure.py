# coding: UTF-8
"""
@software: PyCharm
@author: Lionel Johnson
@contact: https://fairy.host
@organization: https://github.com/FairylandFuture
@datetime: 2025-11-29 16:27:03 UTC+08:00
"""

import os
import typing as t
from dataclasses import dataclass
from pathlib import Path

import yaml

from ._enums import LogLevelEnum, EncodingEnum

_DEFAULT_LOG_PATTERN = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{line} | P:{process} T:{thread} - {message}"


@dataclass(frozen=True)
class LoggerConfigStructure:
    level: LogLevelEnum = LogLevelEnum.INFO
    console: bool = True
    file: bool = False
    dirname: t.Optional[t.Union[str, Path]] = "logs"
    filename: str = "fairyland-logger.log"
    rotation: str = "5 MB"
    retention: str = "180 days"
    pattern: str = _DEFAULT_LOG_PATTERN
    json: bool = False
    encoding: EncodingEnum = EncodingEnum.UTF8

    @staticmethod
    def from_env(frefix: str = "FAIRY_LOG_") -> "LoggerConfigStructure":
        def get_bool(name: str, default: bool) -> bool:
            v = os.getenv(f"{frefix}{name}")
            if v is None:
                return default
            return v.strip().lower() in {"1", "true", "yes", "on"}

        return LoggerConfigStructure(
            level=LogLevelEnum(os.getenv(f"{frefix}LEVEL", "INFO")),
            console=get_bool("ENABLE_CONSOLE", True),
            file=get_bool("ENABLE_FILE", False),
            dirname=os.getenv(f"{frefix}DIR", "logs"),
            filename=os.getenv(f"{frefix}FILE", "fairyland-logger.log"),
            rotation=os.getenv(f"{frefix}ROTATION", "5 MB"),
            retention=os.getenv(f"{frefix}RETENTION", "180 days"),
            pattern=os.getenv(f"{frefix}PATTERN", _DEFAULT_LOG_PATTERN),
            json=get_bool("JSON", False),
            encoding=EncodingEnum(os.getenv(f"{frefix}ENCODING", "UTF-8")),
        )

    @staticmethod
    def from_yaml(path: t.Union[str, Path]) -> "LoggerConfigStructure":
        with open(path, "r", encoding=EncodingEnum.UTF8) as stream:
            content = yaml.safe_load(stream) or {}

        data = content.get("fairyland", {}).get("logger", {})

        return LoggerConfigStructure(
            level=LogLevelEnum(data.get("level", "INFO")),
            console=bool(data.get("console", True)),
            file=bool(data.get("file", False)),
            dirname=data.get("dirname", "logs"),
            filename=data.get("filename", "fairyland-logger.log"),
            rotation=data.get("rotation", "5 MB"),
            retention=data.get("retention", "180 days"),
            pattern=data.get("pattern", _DEFAULT_LOG_PATTERN),
            json=bool(data.get("json", False)),
            encoding=EncodingEnum(data.get("encoding", "UTF-8")),
        )


@dataclass(frozen=False)
class LoggerRecordStructure:
    name: str
    level: LogLevelEnum
    message: str
    depth: int = 5
    extra: t.Optional[t.Dict[str, t.Any]] = None
