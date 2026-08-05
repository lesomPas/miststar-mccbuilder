# created by lesomras on 2026-7-22

from __future__ import annotations
from dataclasses import dataclass

from .base import TextComponent
from miststar.exceptions import InvalidValueException


@dataclass(slots=True)
class Selector(TextComponent):
    selector: str

    def __post_init__(self):
        if not isinstance(self.selector, str):
            raise InvalidValueException.type_exception("selector", "str", self.selector)

    @classmethod
    def from_dictionary(cls, d: dict) -> Selector:
        selector = d["selector"]
        return cls(selector=selector)

    @staticmethod
    def build_dictionary(selector: str) -> dict:
        return {"selector": selector}

    def to_dictionary(self) -> dict:
        return {"selector": self.selector}
