# created by lesomras on 2026-7-22

from __future__ import annotations

from typing import Optional
from enum import Enum

from .base import TextComponent
from .rawtext import Rawtext
from .translate import Translate, TranslateKind

from ..exceptions import InvalidValueException


class TranslateBuilder:
    __slots__ = ("raw", "translate")

    def __init__(self, translate: str, raw: Optional[Rawtext] = None) -> None:
        assert (raw is None) or isinstance(raw, Rawtext)
        assert isinstance(translate, str)
        self.raw = raw
        self.translate = Translate(translate=translate)

    def _conflict_check(self, check_kind: TranslateKind, default_factory) -> None:
        kind = self.translate.kind
        if kind == TranslateKind.PureTranslate:
            self.translate.with_content = default_factory()
            return

        if kind != check_kind:
            if kind == TranslateKind.RawtextTranslate:
                raise InvalidValueException("TranslateKind was locked into rawtext translate, string is disabled.")
            if kind == TranslateKind.StringTranslate:
                raise InvalidValueException("TranslateKind was locked into string translate, TextComponent is disabled.")


    def include(self, *args) -> TranslateBuilder:
        self._conflict_check(TranslateKind.RawtextTranslate, Rawtext)
        self.translate.with_content.add(*args) # type: ignore
        return self

    def include_asc(self, *args) -> TranslateBuilder:
        self._conflict_check(TranslateKind.RawtextTranslate, Rawtext)
        self.translate.with_content.add_semantic_component(*args) # type: ignore
        return self

    def include_string(self, *args) -> TranslateBuilder:
        self._conflict_check(TranslateKind.StringTranslate, list)
        if not all(isinstance(i, str) for i in args):
            raise InvalidValueException.type_exception_value("The args", "str", args)
        self.translate.with_content.extend(args) # type: ignore
        return self

    def rawtext(self) -> Rawtext:
        if self.raw is None:
            return Rawtext(data=[self.translate, ])
        self.raw.data.append(self.translate)
        return self.raw

    def build(self, *args) -> Rawtext:
        if args:
            self._conflict_check(TranslateKind.RawtextTranslate, Rawtext)

            self.translate.with_content.add(*args) # type: ignore
        return self.rawtext()

    def build_asc(self, *args) -> Rawtext:
        if args:
            self._conflict_check(TranslateKind.RawtextTranslate, Rawtext)

            self.translate.with_content.add_semantic_component(*args) # type: ignore
        return self.rawtext()

    def build_string(self, *args) -> Rawtext:
        if args:
            self._conflict_check(TranslateKind.StringTranslate, list)
            if not all(isinstance(i, str) for i in args):
                raise InvalidValueException.type_exception_value("The args", "str", args)

            self.translate.with_content.extend(args) # type: ignore
        return self.rawtext()
