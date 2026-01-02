# create by lesomras on 2026-1-3
from typing import Callable

from string_operator.lexer.token import TokenType, Token, TokenizedContent

class TokensView(object):
    def __init__(self, tokenized_content: TokenizedContent, start: int, end: int) -> None:
        self.tokenized_content = tokenized_content
        self.start = start
        self.end = end
        self.cache_string = tokenized_content.content[
            tokenized_content.get_token_head(start) : tokenized_content.get_token_head(end)
        ]

    def is_empty(self) -> bool:
        return self.start >= self.end

    def has_value(self) -> bool:
        return self.start < self.end

    def __getitem__(self, index: int) -> Token:
        return self.tokenized_content.tokens[self.start + index]

    def size(self) -> int:
        return self.end - self.start

    def is_all_space(self) -> int:
        return all(self.tokenized_content.tokens[i].token_type == TokenType.space for i in range(self.start, self.end))

    def for_each(self, function: Callable[[Token], None]) -> None:
        for i in range(self.start, self.end):
            function(self.tokenized_content.tokens[i])

    def string(self) -> str:
        return self.cache_string