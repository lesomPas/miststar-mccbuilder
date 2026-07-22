# created by lesomras on 2026-7-22

from __future__ import annotations

from enum import Enum

from typing import Self
from typing import Protocol, runtime_checkable

@runtime_checkable
class TextComponent(Protocol):
    """所有文本组件的基类"""

    @classmethod
    def from_dictionary(cls, d: dict) -> Self:
        """实现由字典到文本组件的转换"""
        ...

    def to_dictionary(self) -> dict:
        """实现由该文本组件到字典的转换"""
        ...

    def __str__(self) -> str:
        ...


class TranslateKind(Enum):
    PureTranslate = "TranslateKind.PureTranslate"
    RawtextTranslate = "TranslateKind.RawtextTranslate"
    StringTranslate = "TranslateKind.StringTranslate"
