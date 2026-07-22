# created by lesomras on 2026-7-22

from .base import TextComponent
from .text import Text
from .score import Score
from .selector import Selector
from ..analyzer import SemanticComponentAnalyzer, TemplateLexer

from ..exceptions import InvalidValueException


def template_analysis(template: str) -> list[TextComponent]:
    """
    根据模板生成包含文本组件的列表

    args: template 待处理的模板
    return: 解析过后的文本组件列表
    mapping:
        "我是{@s}" -> [Text("我是"), Selector("@s")]
        "我一共有{coins[].@s}个金币{.}" -> [Text("我一共有"), Score("@s", "coins"), Text("个金币"), Text(".")]
    """
    if not isinstance(template, str):
        raise InvalidValueException.type_exception("template", "str", template)

    result: list[TextComponent] = []
    for sentence, is_formated in TemplateLexer.tokenize(template):
        if not is_formated:
            result.append(Text(sentence))
            continue

        sentence_type, sentence_data = SemanticComponentAnalyzer.analyze(sentence)
        match sentence_type:
            case "text":
                result.append(Text(sentence_data[0]))
            case "selector":
                result.append(Selector(sentence_data[0]))
            case "score":
                result.append(Score(sentence_data[0], sentence_data[1]))

    return result
