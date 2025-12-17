# coding: UTF-8
"""
@software: PyCharm
@author: Lionel Johnson
@contact: https://fairy.host
@organization: https://github.com/FairylandFuture
@datetime: 2025-11-29 16:28:11 UTC+08:00
"""

from enum import Enum


class EncodingEnum(str, Enum):
    UTF8 = "UTF-8"
    GBK = "GBK"
    GB2312 = "GB2312"
    GB18030 = "GB18030"


class LogLevelEnum(str, Enum):
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
