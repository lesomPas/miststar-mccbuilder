# create by lesomras on 2025-12-21

from .components import TextComponent, Rawtext, Text, Score, Selector, infer_type
from ..internal.exceptions import UnsupportedArgument
from ..internal.string import tokenize_template

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
        raise UnsupportedArgument("'template' must be a string")

    result: list[TextComponent] = []
    for sentence, is_formated in tokenize_template(template):
        if not is_formated:
            result.append(Text(sentence))
            continue

        sentence_type, sentence_data = infer_type(sentence)
        match sentence_type:
            case "text":
                result.append(Text(sentence_data[0]))
            case "selector":
                result.append(Selector(sentence_data[0]))
            case "score":
                result.append(Score(sentence_data[0], sentence_data[1]))

    return result


def template_builder(template: str) -> Rawtext:
    """根据模板生成Rawtext"""
    return Rawtext(template_analysis(template))