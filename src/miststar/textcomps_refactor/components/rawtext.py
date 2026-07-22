# created by lesomras on 2026-7-22

from __future__ import annotations
from typing import TYPE_CHECKING

from collections.abc import Iterable
from dataclasses import dataclass, field

from .base import TextComponent
from ..exceptions import InvalidValueException

from .text import Text
from .score import Score
from .selector import Selector
from .translate import Translate
from .template import template_analysis

from ..analyzer import SemanticComponentAnalyzer

if TYPE_CHECKING:
    from .translate_builder import TranslateBuilder


@dataclass(slots=True)
class Rawtext(TextComponent):
    data: list[TextComponent] = field(default_factory=list)

    def __post_init__(self):
        if not all(isinstance(i, TextComponent) for i in self.data):
            raise InvalidValueException.type_exception_value("data", "list[TextComponent]", self.data)

    @classmethod
    def from_dictionary(cls, d: dict) -> Rawtext:
        data = d["rawtext"]
        data = rawtext_lexer(data)
        return cls(data)

    @classmethod
    def from_iterable(cls, iterable: Iterable[TextComponent]) -> Rawtext:
        data = list(iterable)
        return cls(data)

    @classmethod
    def from_component(cls, *args: TextComponent) -> Rawtext:
        for i in args:
            if not isinstance(i, TextComponent):
                raise InvalidValueException.type_exception("The args", "TextComponent", i)
        return cls(data=list(args))

    @classmethod
    def from_template(cls, template: str) -> Rawtext:
        return cls(data=template_analysis(template))

    def to_dictionary(self) -> dict:
        return {"rawtext": [i.to_dictionary() for i in self.data]}

    def add(self, *args: TextComponent) -> Rawtext:
        """将文本组件加入到Rawtext中"""
        for i in args:
            if not isinstance(i, TextComponent):
                raise InvalidValueException.type_exception("The args", "TextComponent", i)
        self.data.extend(args)
        return self

    def add_semantic_component(self, *args: str | TextComponent) -> Rawtext:
        """将一个特定形式的字符串解析为文本组件加入到Rawtext中, 若本来就是文本组件则直接加入"""
        for sentence in args:
            # TextComponent
            if isinstance(sentence, TextComponent):
                self.data.append(sentence)
                continue

            if not isinstance(sentence, str):
                raise InvalidValueException.type_exception("sentence", "str", sentence)
            sentence_type, sentence_data = SemanticComponentAnalyzer.analyze(sentence)
            match sentence_type:
                case "text":
                    self.data.append(Text(sentence_data[0]))
                case "selector":
                    self.data.append(Selector(sentence_data[0]))
                case "score":
                    self.data.append(Score(sentence_data[0], sentence_data[1]))
        return self

    def asc(self, *args: str | TextComponent) -> Rawtext:
        self.add_semantic_component(*args)
        return self

    def add_iterable(self, iterable: Iterable[TextComponent]) -> Rawtext:
        temp = list(iterable)
        for i in temp:
            if not isinstance(i, TextComponent):
                raise InvalidValueException.type_exception("The elements of iterable", "TextComponent", i)
        self.data.extend(temp)
        return self

    def text(self, content: str) -> Rawtext:
        self.data.append(Text(content))
        return self

    def score(self, name: str, objective: str) -> Rawtext:
        self.data.append(Score(name, objective))
        return self

    def selector(self, selector: str) -> Rawtext:
        self.data.append(Selector(selector))
        return self

    def translate(self, translate: str) -> TranslateBuilder:
        """快速构建Translate文本组件. translate参数为Translate的第一个形参"""
        from .translate_builder import TranslateBuilder
        return TranslateBuilder(translate, self)

    def template(self, template: str) -> Rawtext:
        return self.add(*template_analysis(template))

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, index: int) -> TextComponent:
        return self.data[index]


def _array_processing(dictionary: dict) -> dict:
    """按照预先设定的顺序解析dictionary中多余的格式"""
    priority = {
        "translate": 4,
        "text": 3,
        "score": 2,
        "selector": 1,
        None: 0
    }

    result = None
    for k in dictionary.keys():
        if (p := priority.get(k)) is None:
            continue
        if result is None or p >= priority[result]:
            result = k
    return {result: dictionary[result]} if result is not None else {}


def rawtext_lexer(sequence: list[dict]) -> list[TextComponent]:
    """字典组成的列表转化为由文本组件组成的列表"""
    if not all(isinstance(i, dict) for i in sequence):
        raise InvalidValueException.type_exception_value("sequence", "list[dict]", sequence)

    result: list[TextComponent] = []
    for sentence in sequence:
        if len(sentence) > 1 and not ("translate" in sentence and "with" in sentence):
            sentence = _array_processing(sentence)

        if sentence == {}:
            continue
        elif "translate" in sentence:
            result.append(Translate.from_dictionary(sentence))
        elif "text" in sentence:
            result.append(Text.from_dictionary(sentence))
        elif "score" in sentence:
            result.append(Score.from_dictionary(sentence))
        elif "selector" in sentence:
            result.append(Selector.from_dictionary(sentence))
        elif "rawtext" in sentence:
            result.append(Rawtext.from_dictionary(sentence))
        else:
            raise InvalidValueException(f"The element of sequence must contain translate(with), text, score or selector , got {sentence!r}")
    return result

