# created by lesomras on 2026-7-22

from __future__ import annotations
from typing import TYPE_CHECKING

from typing import Optional
from dataclasses import dataclass

from .base import TextComponent, TranslateKind
from ..exceptions import InvalidValueException

if TYPE_CHECKING:
    from .rawtext import Rawtext


@dataclass(slots=True)
class Translate(TextComponent):
    translate: str
    with_content: Optional[Rawtext | list[str]] = None

    def __post_init__(self):
        if not isinstance(self.translate, str):
            raise InvalidValueException.type_exception("translate", "str", self.translate)

        # Rawtext 暂时不检查了
        if isinstance(self.with_content, list):
            if not all(isinstance(i, str) for i in self.with_content):
                raise InvalidValueException.type_exception_value("with_content", "list[str] or Rawtext", self.with_content)

    @property
    def kind(self) -> TranslateKind:
        if self.with_content:
            if isinstance(self.with_content, list):
                return TranslateKind.StringTranslate
            else:
                return TranslateKind.RawtextTranslate
        else:
            return TranslateKind.PureTranslate

    @classmethod
    def from_dictionary(cls, d: dict) -> Translate:
        from .rawtext import Rawtext

        translate = d["translate"]
        with_content = d.get("with")
        if isinstance(with_content, dict):
            with_content = Rawtext.from_dictionary(with_content)
        return cls(translate, with_content)

    @staticmethod
    def build_dictionary(translate: str, with_content: Optional[Rawtext | list[str]] = None) -> dict:
        if with_content:
            if isinstance(with_content, list):
                return {"translate": translate, "with": with_content}
            else:
                return {"translate": translate, "with": with_content.to_dictionary()}
        else:
            return {"translate": translate}

    def to_dictionary(self) -> dict:
        return Translate.build_dictionary(self.translate, self.with_content)
