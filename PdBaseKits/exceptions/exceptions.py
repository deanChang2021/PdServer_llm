from enum import Enum
from typing import Union


class ErrorCode(Enum):
    MISS_REQUIRED_VARIABLE_ERROR = 11
    MAX_RETRY_ERROR = 12
    REQUEST_PARAMS_ERROR = 13
    BANNED_PROMPT_ERROR = 14
    QUEUE_FULL_ERROR = 15
    SOURCE_QUEUE_EMPTY_ERROR = 16
    SOURCE_QUEUE_NOT_ENOUGH_ERROR=17
    CONSUR_ID_NOT_EXIST_ERROR=18
    SQL_CONNECT_ERROR = 19


class SuccessCode(Enum):
    SUCCESS = 0


ReturnCode = Union[ErrorCode, SuccessCode]


class APPBaseException(Exception):
    code: ErrorCode
    message: str

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class MissRequiredVariableError(APPBaseException):
    """缺少必需变量"""
    code = ErrorCode.MISS_REQUIRED_VARIABLE_ERROR


class MaxRetryError(APPBaseException):
    """请求最大重试错误"""
    code = ErrorCode.MAX_RETRY_ERROR


class RequestParamsError(APPBaseException):
    """请求参数异常"""
    code = ErrorCode.REQUEST_PARAMS_ERROR


class BannedPromptError(APPBaseException):
    """提示词被禁用"""
    code = ErrorCode.BANNED_PROMPT_ERROR


class QueueFullError(APPBaseException):
    """队列已满"""
    code = ErrorCode.QUEUE_FULL_ERROR



class NoExeSourceError(APPBaseException):
    """执行资源为空"""
    code = ErrorCode.SOURCE_QUEUE_EMPTY_ERROR

class ExeSourceNotEnoughError(APPBaseException):
    """执行资源为空"""
    code = ErrorCode.SOURCE_QUEUE_NOT_ENOUGH_ERROR


class ConsurIdNotExistError(APPBaseException):
    """执行资源为空"""
    code = ErrorCode.CONSUR_ID_NOT_EXIST_ERROR


class SqlConnectError(APPBaseException):
    """执行资源为空"""
    code = ErrorCode.SQL_CONNECT_ERROR
