# create by lesomras on 2026-1-3
from __future__ import annotations
from enum import Enum

from .tokens_view import TokensView

class ErrorReasonLevel(Enum):
    Excess = 0               # 命令后面有多余部分
    RequireSpace = 1         # 缺少空格
    Incomplete = 2           # 命令不完整
    TypeException = 3        # 类型不匹配
    ContentException = 4     # 内容不匹配
    LogicException = 5       # 逻辑错误
    IdException = 6          # ID错误

MaxLevel = ErrorReasonLevel.IdException

class ErrorReason(object):
    __slots__ = ("level", "start", "end", "error_reason")

    def __init__(self, level: ErrorReasonLevel, start: int, end: int, error_reason: str) -> None:
        self.level = level
        self.start = start
        self.end = end
        self.error_reason = error_reason

    @classmethod
    def build_from_view(cls, level: ErrorReasonLevel, tokens_view: TokensView, error_reason: str) -> ErrorReason:
        return cls(level, tokens_view.start_index, tokens_view.end_index, error_reason)

    @staticmethod
    def excess(start: int, end: int, error_reason: str) -> ErrorReason:
        return ErrorReason(ErrorReasonLevel.Excess, start, end, error_reason)

    @staticmethod
    def excess_v(tokens_view: TokensView, error_reason: str) -> ErrorReason:
        return ErrorReason.build_from_view(ErrorReasonLevel.Excess, tokens_view, error_reason)

    @staticmethod
    def require_space(start: int, end: int) -> ErrorReason:
        return ErrorReason(ErrorReasonLevel.RequireSpace, start, end, "命令不完整，缺少空格")

    @staticmethod
    def require_space_v(tokens_view: TokensView) -> ErrorReason:
        return ErrorReason.build_from_view(ErrorReasonLevel.RequireSpace, tokens_view, "命令不完整，缺少空格")

    @staticmethod
    def incomplete(start: int, end: int, error_reason: str) -> ErrorReason:
        return ErrorReason(ErrorReasonLevel.Incomplete, start, end, error_reason)

    @staticmethod
    def incomplete_v(tokens_view: TokensView, error_reason: str) -> ErrorReason:
        return ErrorReason.build_from_view(ErrorReasonLevel.Incomplete, tokens_view, error_reason)

    @staticmethod
    def type_exception(start: int, end: int, error_reason: str) -> ErrorReason:
        return ErrorReason(ErrorReasonLevel.TypeException, start, end, error_reason)

    @staticmethod
    def type_exception_v(tokens_view: TokensView, error_reason: str) -> ErrorReason:
        return ErrorReason.build_from_view(ErrorReasonLevel.TypeException, tokens_view, error_reason)

    @staticmethod
    def content_exception(start: int, end: int, error_reason: str) -> ErrorReason:
        return ErrorReason(ErrorReasonLevel.ContentException, start, end, error_reason)

    @staticmethod
    def content_exception_v(tokens_view: TokensView, error_reason: str) -> ErrorReason:
        return ErrorReason.build_from_view(ErrorReasonLevel.ContentException, tokens_view, error_reason)

    @staticmethod
    def logic_exception(start: int, end: int, error_reason: str) -> ErrorReason:
        return ErrorReason(ErrorReasonLevel.LogicException, start, end, error_reason)

    @staticmethod
    def logic_exception_v(tokens_view: TokensView, error_reason: str) -> ErrorReason:
        return ErrorReason.build_from_view(ErrorReasonLevel.LogicException, tokens_view, error_reason)

    @staticmethod
    def id_exception(start: int, end: int, error_reason: str) -> ErrorReason:
        return ErrorReason(ErrorReasonLevel.IdException, start, end, error_reason)

    @staticmethod
    def id_exception_v(tokens_view: TokensView, error_reason: str) -> ErrorReason:
        return ErrorReason.build_from_view(ErrorReasonLevel.IdException, tokens_view, error_reason)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ErrorReason):
            return False
        return (self.start == other.start and 
                self.end == other.end and 
                self.error_reason == other.error_reason)