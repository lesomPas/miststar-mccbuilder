# created by lesomras on 2026-7-22

from __future__ import annotations
from dataclasses import dataclass

from .base import TextComponent
from ..exceptions import InvalidValueException


@dataclass(slots=True)
class Text(TextComponent):
    content: str

    def __post_init__(self):
        if not isinstance(self.content, str):
            raise InvalidValueException.type_exception("content", "str", self.content)

    @classmethod
    def from_dictionary(cls, d: dict) -> Text:
        content = d["text"]
        return cls(content=content)

    @staticmethod
    def build_dictionary(content: str) -> dict:
        return {"text": content}

    def to_dictionary(self) -> dict:
        return {"text": self.content}

    def _str_sequence(self) -> list[str]:
        result = []
        content = self.content.splitlines()
        for i, ln in enumerate(content):
            if i == 0:
                result.append(f"text  | {ln}")
            else:
                result.append(f"      | {ln}")
        return result

    def __str__(self) -> str:
        result = []
        content = self.content.splitlines()
        for i, ln in enumerate(content):
            if i == 0:
                result.append(f"text  | {ln}")
            else:
                result.append(f"      | {ln}")
        return "\n".join(result)
