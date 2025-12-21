# create by lesomras on 2025-12-21

def tokenize_template(content: str) -> list[tuple[str, bool]]:
    """
    对模板字符串进行词法分析, 将其拆分为文本片段和插值域.

    此函数是模板系统的词法分析器, 识别模板中的普通文本和由花括号 {} 界定的插值域.
    它将处理转义序列 {{ 和 }}(分别转换为字面量 { 和 }), 并正确匹配嵌套的插值域边界.

    args: content 待解析的模板字符串.例如: "Hello {@p}, you have {kills[].Steve}!"

    return: 一个列表, 其中每个元素是一个二元组 (segment, is_formatted).
        - segment (str): 提取出的文本片段.
        - is_formatted (bool): 标识该片段是否为需要后续处理的插值域.
          - True: 该片段是一个插值域内容(不包含外层的定界符 {}), 应传递给 infer_type.
          - False: 该片段是普通文本(或转义后的花括号).

    mapping:
        >>> tokenize_template("Hello {{@p}}, you have {kills[].Steve}!")
        [
            ('Hello ', False),          # 普通文本
            ('{', False),               # 转义后的字面量左大括号
            ('@p', False),              # 普通文本(因转义, 不被识别为插值域)
            (', you have ', False),     # 普通文本
            ('kills[].Steve', True),    # 插值域内容, 需进一步推断类型
            ('!', False)                # 普通文本
        ]
    """
    n = len(content)
    package: list[str] = []
    result = []
    p = 0

    def push_sentence(is_formated: bool):
        if package:
            result.append(("".join(package), is_formated))
            package.clear()

    while p < n:
        item = content[p]
        if item == "{" and p + 1 < n and content[p + 1] == "{":
            package.append("{")
            p += 2
        elif item == "}" and p + 1 < n and content[p + 1] == "}":
            package.append("}")
            p += 2
        elif item == "{":
            push_sentence(False)

            p2 = p + 1
            depth = 1
            while (p2 < n and depth != 0):
                i = content[p2]
                if i == "{":
                    depth += 1
                    package.append("{")
                    p2 += 1
                elif i == "}":
                    depth -= 1
                    if depth != 0:
                        package.append("}")
                    p2 += 1
                elif i == "{" and p2 + 1 < n and content[p2 + 1] == "{":
                    package.append("{")
                    p2 += 2
                elif i == "}" and p2 + 1 < n and content[p2 + 1] == "}":
                    package.append("}")
                    p2 += 2
                else:
                    package.append(i)
                    p2 += 1

            if depth != 0:
                p += 1
                package.clear()
                # print(f"Warning: {content} the '{{' is suspended\n")
                continue
            push_sentence(True)
            p = p2

        elif item == "}":
            p += 1
        else:
            package.append(item)
            p += 1

    push_sentence(False)
    return result