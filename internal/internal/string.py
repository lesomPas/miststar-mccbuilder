# create by lesomras on 2025-12-21

def tokenize_template(content: str) -> list[tuple[str, bool]]:
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