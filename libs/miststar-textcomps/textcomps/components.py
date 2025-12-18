# create by lesomras on 2025-12-13

from abc import ABC, abstractmethod
from pprint import pformat
from typing import Union, Optional

from internal.dict_checking import is_value, list_of, matching
from internal.exceptions import UnsupportedArgument, MissingArgument, MalformedArgument

priority = {
    "translate": 4,
    "text": 3,
    "score": 2,
    "selector": 1,
    None: 0
}
segmentation = ">[]"

class TextComponent(ABC):
    """所有文本组件的基类"""

    def with_id(self) -> str:
        """返回组件的唯一标识符与信息"""
        return f"{id(self)}::{str(self)}"

    @classmethod
    @abstractmethod
    def from_dictionary(cls, dictionary: dict) -> "TextComponent":
        """实现由字典到文本组件的转换"""
        pass

    @staticmethod
    @abstractmethod
    def build_dictionary(*args, **kwargs) -> dict:
        """实现由参数到字典的转换"""
        pass

    @abstractmethod
    def to_dictionary(self) -> dict:
        """实现由该文本组件到字典的转换"""
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass


class Rawtext(TextComponent):
    """实现Minecraft BE中rawtext文本组件的模式, 本质上是个容器"""

    def __init__(self, sequence: Optional[list[TextComponent]] = None) -> None:
        """实现由TextComponent列表到Rawtext的转换"""
        sequence = sequence if sequence is not None else []
        if not list_of(sequence, TextComponent):
            raise UnsupportedArgument("Sequence must be None or a list of TextComponents")
        self._data = sequence


    @classmethod
    def from_dictionary(cls, dictionary: dict) -> "Rawtext":
        matching(dictionary, pattern = {
            "rawtext": lambda data_value, key: isinstance(data_value, list)
        })
        sequence = rawtext_lexer(dictionary["rawtext"])
        return cls(sequence)

    @staticmethod
    def build_dictionary() -> dict:
        return {}

    def to_dictionary(self) -> dict:
        return {
            "rawtext": [i.to_dictionary() for i in self._data]
        }

    def add(self, *args) -> "Rawtext":
        """将一个文本组件加入到Rawtext中"""
        for obj in args:
            if not isinstance(obj, TextComponent):
                raise TypeError("arguments must be subclass of TextComponent")
            self._data.append(obj)
        return self

    def adx(self, *args) -> "Rawtext":
        """将一个特定形式的字符串解析为文本组件加入到Rawtext中, 若本来就是文本组件则直接加入"""
        for sentence in args:
            # TextComponent
            if isinstance(sentence, TextComponent):
                self.add(sentence)
                continue
            if not isinstance(sentence, str):
                raise UnsupportedArgument("The parameters must be a subclass of TextComponent or string")

            # Score
            elif (p := sentence.find(segmentation)) != -1:
                self.add(Score(sentence[:p], sentence[p+len(segmentation):]))
                continue

            # Selector
            elif len(sentence) >= 2 and sentence[0] == "@" and sentence[1] in ["p", "r", "a", "e", "s", "n"]:
                if len(sentence) == 2:
                    self.add(Selector(sentence))
                    continue
                no_whitespace = sentence.replace(" ", "")
                if no_whitespace[-1] == "]" and no_whitespace[2] == "[":
                    self.add(Selector(sentence))
                    continue
            elif len(sentence) >= 10 and sentence[:10] == "@initiator":
                if len(sentence) == 10:
                    self.add(Selector(sentence))
                    continue
                no_whitespace = sentence.replace(" ", "")
                if no_whitespace[-1] == "]" and no_whitespace[10] == "[":
                    self.add(Selector(sentence))
                    continue

            # default Text
            self.add(Text(sentence))
        return self


    def add_sequence(self, sequence: list[TextComponent]) -> "Rawtext":
        """将一个泛型列表中的文本组件按顺序加入"""
        return self.add(*sequence)

    def get_data(self) -> list[TextComponent]:
        return self._data.copy()

    def translate(self, translate: str) -> "TranslateBuilder":
        """快速构建Translate文本组件. translate参数为Translate的第一个形参"""
        if not isinstance(translate, str):
            raise UnsupportedArgument("build failed")

        return TranslateBuilder(self, translate)

    def __str__(self) -> str:
        return pformat(self._data)

    def __repr__(self) -> str:
        return f"-rawtext::{str(self)}"


class TranslateBuilder(object):
    def __init__(self, raw: Rawtext, translate: str) -> None:
        if not isinstance(raw, Rawtext) or not isinstance(translate, str):
            raise UnsupportedArgument("build failed")

        self.raw = raw
        self.translate = translate

    def build(self, *args) -> Rawtext:
        if args == ():
            return self.raw.add(Translate(self.translate))

        if any(not isinstance(i, TextComponent) for i in args):
            raise UnsupportedArgument("build failed")

        withraw = Rawtext().add_sequence(list(args))
        return self.raw.add(Translate(self.translate, with_content = withraw))

    def build_adx(self, *args) -> Rawtext:
        if args == ():
            return self.raw.add(Translate(self.translate))

        withraw = Rawtext().adx(*args)
        return self.raw.add(Translate(self.translate, with_content = withraw))

    def string_build(self, *args) -> Rawtext:
        if args == ():
            return self.raw.add(Translate(self.translate))

        if any(not isinstance(i, str) for i in args):
            raise UnsupportedArgument("build failed")

        return self.raw.add(Translate(self.translate, string_sequence = list(args)))

    def sequence_build(self, sequence: list[TextComponent]) -> Rawtext:
        return self.build(*sequence)

    def sequence_str_build(self, sequence: list[str]) -> Rawtext:
        return self.string_build(*sequence)


class Text(TextComponent):
    """实现Minecraft BE中text组件的模式"""

    def __init__(self, content: str) -> None:
        """实现由参数到Text的转换"""
        if not isinstance(content, str):
            raise UnsupportedArgument("Content must be a string")

        self.content = content

    @classmethod
    def from_dictionary(cls, dictionary: dict) -> "Text":
        matching(dictionary, pattern = {
            "text": str
        })
        return cls(dictionary["text"])

    @staticmethod
    def build_dictionary(content: str) -> dict:
        if not isinstance(content, str):
            raise UnsupportedArgument("Content must be a string")

        return Text._to_dictionary(content)

    def to_dictionary(self) -> dict:
        return self._to_dictionary(self.content)

    @staticmethod
    def _to_dictionary(content: str) -> dict:
        return {
            "text": content
        }

    def __str__(self) -> str:
        return self.content

    def __repr__(self) -> str:
        return f"-text::{str(self)}"


class Score(TextComponent):
    """实现Minecraft BE中score文本组件的模式"""

    def __init__(self, name: str, objective: str) -> None:
        """实现由参数到Score的转换"""
        if not (isinstance(name, str) and isinstance(objective, str)):
            raise UnsupportedArgument("Name and Objective must be a string")

        self.name = name
        self.objective = objective

    @classmethod
    def from_dictionary(cls, dictionary: dict) -> "Score":
        matching(dictionary, pattern = {
            "score": {
                "name": str,
                "objective": str
            }
        })
        return cls(dictionary["score"]["name"], dictionary["score"]["objective"])

    @staticmethod
    def build_dictionary(name: str, objective: str) -> dict:
        if not (isinstance(name, str) and isinstance(objective, str)):
            raise UnsupportedArgument("Name and Objective must be a string")

        return Score._to_dictionary(name, objective)

    def to_dictionary(self) -> dict:
        return self._to_dictionary(self.name, self.objective)

    @staticmethod
    def _to_dictionary(name, objective) -> dict:
        return {
            "score": {
                "name": name,
                "objective": objective
            }
        }

    @classmethod
    def p(cls, objective: str) -> "Score":
        if not isinstance(objective, str):
            raise UnsupportedArgument("Objective must be a string")
        return cls("@p", objective)

    @classmethod
    def r(cls, objective: str) -> "Score":
        if not isinstance(objective, str):
            raise UnsupportedArgument("Objective must be a string")
        return cls("@r", objective)

    @classmethod
    def a(cls, objective: str) -> "Score":
        if not isinstance(objective, str):
            raise UnsupportedArgument("Objective must be a string")
        return cls("@a", objective)

    @classmethod
    def e(cls, objective: str) -> "Score":
        if not isinstance(objective, str):
            raise UnsupportedArgument("Objective must be a string")
        return cls("@e", objective)

    @classmethod
    def s(cls, objective: str) -> "Score":
        if not isinstance(objective, str):
            raise UnsupportedArgument("Objective must be a string")
        return cls("@s", objective)

    @classmethod
    def n(cls, objective: str) -> "Score":
        if not isinstance(objective, str):
            raise UnsupportedArgument("Objective must be a string")
        return cls("@n", objective)

    @classmethod
    def initiator(cls, objective: str) -> "Score":
        if not isinstance(objective, str):
            raise UnsupportedArgument("Objective must be a string")
        return cls("@initiator", objective)

    def __str__(self) -> str:
        return f"{self.name} >> {self.objective}"

    def __repr__(self) -> str:
        return f"-score::{str(self)}"


class Selector(TextComponent):
    """实现Minecraft BE中selector文本组件的模式"""

    def __init__(self, content: str) -> None:
        """实现由参数到Selector的转换"""
        if not isinstance(content, str):
            raise UnsupportedArgument("Content must be a string")

        self.content = content

    @classmethod
    def from_dictionary(cls, dictionary: dict) -> "Selector":
        matching(dictionary, pattern = {
            "selector": str
        })
        return cls(dictionary["selector"])

    @staticmethod
    def build_dictionary(content: str) -> dict:
        if not isinstance(content, str):
            raise UnsupportedArgument("Content must be a string")

        return Selector._to_dictionary(content)

    def to_dictionary(self) -> dict:
        return self._to_dictionary(self.content)

    @staticmethod
    def _to_dictionary(content: str) -> dict:
        return {
            "selector": content
        }

    def __str__(self) -> str:
        return self.content

    def __repr__(self) -> str:
        return f"-selector::{str(self)}"


class Translate(TextComponent):
    """实现Minecraft BE中Translate文本组件的模式"""
    def __init__(self, translate: str, with_content: Optional[Rawtext] = None, string_sequence: Optional[list[str]] = None) -> None:
        """
        构建Translate文本组件, 实际开发中建议使用Rawtext.translate(...).build(...)
        args:
            translate: 翻译模板/待填充模板
            with_content: 填充内容 (优先级最高)
            string_sequence: 字符串填充内容
        """
        if not isinstance(translate, str):
            raise UnsupportedArgument("'translate' must be a string")
        self.translate = translate
        self.with_content = None
        self.string_sequence = None

        if with_content is not None:
            if not (isinstance(with_content, Rawtext)):
                raise UnsupportedArgument("'with_content' must be a Rawtext")
            self.with_content = with_content
            return

        if string_sequence is not None:
            if not list_of(string_sequence, str):
                raise UnsupportedArgument("'string_sequence' must be list of strings")
            self.string_sequence = string_sequence

    def is_pure_translate(self) -> bool:
        return self.with_content is None and self.string_sequence is None

    def is_rawtext_translate(self) -> bool:
        return self.with_content is not None

    def is_string_translate(self) -> bool:
        return self.string_sequence is not None

    @staticmethod
    def from_dictionary(dictionary: dict) -> "Translate":
        if len(dictionary) > 2:
            raise ValueError("Dictionary contains extra keys")
        if not is_value(dictionary, "translate", str):
            raise UnsupportedArgument("'translate' must be a string")
        translate = dictionary["translate"]

        with_content: Union[list[str], dict, None] = None
        if "with" not in dictionary:
            if len(dictionary) > 1:
                raise MalformedArgument("Dictionary contains extra keys")
            return Translate(translate)

        # breakpoint()
        with_value = dictionary["with"]
        if isinstance(with_value, dict):
            return Translate(translate, with_content = Rawtext.from_dictionary(with_value))
        elif list_of(with_value, str):
            return Translate(translate, string_sequence = with_value)
        else:
            raise UnsupportedArgument("'with' must be a list of strings or a dictionary")

    @staticmethod
    def build_dictionary(translate: str, with_content: Optional[Rawtext] = None, string_sequence: Optional[list[str]] = None) -> dict:
        if not isinstance(translate, str):
            raise UnsupportedArgument("'translate' must be a string")
        if with_content is not None:
            if not (isinstance(with_content, Rawtext)):
                raise UnsupportedArgument("'with_content' must be a Rawtext")
            return Translate._to_dictionary(translate, with_content = with_content)

        elif string_sequence is not None:
            if not list_of(string_sequence, str):
                raise UnsupportedArgument("'string_sequence' must be list of strings")
            return Translate._to_dictionary(translate, string_sequence = string_sequence)

        else:
            return Translate._to_dictionary(translate)

    def to_dictionary(self) -> dict:
        return self._to_dictionary(self.translate, self.with_content, self.string_sequence)

    @staticmethod
    def _to_dictionary(translate: str, with_content: Optional[Rawtext] = None, string_sequence: Optional[list[str]] = None) -> dict:
        if with_content is not None:
            return {
                "translate": translate,
                "with": with_content.to_dictionary()
            }

        if string_sequence is not None:
            return {
                "translate": translate,
                "with": string_sequence
            }

        return {"translate": translate}

    def __str__(self) -> str:
        if self.is_rawtext_translate():
            return f"{self.translate}\n  {pformat(self.with_content)}"
        elif self.is_string_translate():
            return f"{self.translate}\n  {pformat(self.string_sequence)}"
        return self.translate

    def __repr__(self) -> str:
        if self.is_rawtext_translate():
            return f"-translate::{self.translate}\n  -with::{pformat(self.with_content)}"
        elif self.is_string_translate():
            return f"-translate::{self.translate}\n  -with::{pformat(self.string_sequence)}"
        return f"-translate::{self.translate}"


def _array_processing(dictionary: dict) -> dict:
    """按照预先设定的顺序解析dictionary中多余的格式"""
    results = None
    for sentence in dictionary.keys():
        if (p := priority.get(sentence, -1)) == -1:
            raise MalformedArgument("priority dictionary error")
        if p >= priority[results]:
            results = sentence
    return {results: dictionary[results]} if results is not None else {}


def rawtext_lexer(sequence: list[dict]) -> list[TextComponent]:
    """这样由字典组成的列表转化为由文本组件组成的列表"""
    if not list_of(sequence, dict):
        raise UnsupportedArgument("dictionary error")

    results: list[TextComponent] = []
    for sentence in sequence:
        if len(sentence) > 1 and not ("translate" in sentence and "with" in sentence):
            sentence = _array_processing(sentence)

        if sentence == {}:
            continue
        elif "text" in sentence:
            results.append(Text.from_dictionary(sentence))
        elif "score" in sentence:
            results.append(Score.from_dictionary(sentence))
        elif "selector" in sentence:
            results.append(Selector.from_dictionary(sentence))
        elif "translate" in sentence:
            results.append(Translate.from_dictionary(sentence))
        elif "rawtext" in sentence:
            results.append(Rawtext.from_dictionary(sentence))
        else:
            raise MalformedArgument("dictionary error")
    return results
