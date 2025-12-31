# create by lesomras on 2025-12-31
from enum import Enum

class TokenType(Enum):
    string = "字符串类型"
    number = "数字类型"
    symbol = "符号类型"
    space = "空格"
    lf = "换行符类型"
    undefined = "未定义类型"


class Token(object):
    __slots__ = ("token_type", "pos", "content")

    def __init__(self, token_type: TokenType, pos: int, content: str) -> None:
        self.token_type = token_type
        self.pos = pos
        self.content = content

    def get_head(self) -> int:
        return self.pos

    def get_tail(self) -> int:
        return self.pos + len(self.content)

    def __str__(self) -> str:
        return f"({self.token_type}){self.content}"

    def __repr__(self) -> str:
        return f"({self.token_type}::{self.pos}){self.content}"


class TokenizedContent(object):
    __slots__ = ("content", "tokens")

    def __init__(self, content: str, tokens: list[Token]) -> None:
        self.content = content
        self.tokens = tokens

    def get_token_head(self, index: int) -> int:
        return self.tokens[index].get_head() if index != 0 else 0

    def __str__(self) -> str:
        return f"(TokenizedContent){self.content}"

    def __repr__(self) -> str:
        return self.content + repr(self.tokens)