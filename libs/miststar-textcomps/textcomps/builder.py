# create by lesomras on 2025-12-21

from .components import TextComponent, Rawtext, Text, Score, Selector, infer_type
from internal.exceptions import UnsupportedArgument
from internal.string import tokenize_template

def template_analysis(template: str) -> list[TextComponent]:
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
    return Rawtext(template_analysis(template))