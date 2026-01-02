# create by lesomras on 2025-12-31
from string_operator.lexer.token import TokenType, Token, TokenizedContent

whole_number_symbols = {
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ".", "+", "-"
}
number_symbols = {
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."
}
interrupt_symbols = {
    ',', '@', '~', '^', '/', '$', '&', '\'', '!', '#', '%', '+', '*', 
    '=', '[', '{', ']', '}', '\\', '|', '<', '>', '`', '\"', ' ', '\n'
}
symbols = {
    ',', '@', '~', '^', '/', '$', '&', '\'', '!', '#', '%', '*', '=', 
    '[', '{', ']', '}', '\\', '|', '<', '>', '`', ':'
}

class Lexer(object):
    def __init__(self, content: str) -> None:
        self.content = content
        self.pos = 0
        self.tokens: list[Token] = []

    def get_number_token(self, index: int) -> None:
        while (self.pos < len(self.content)):
            if self.content[self.pos] not in whole_number_symbols:
                self.tokens.append(Token(TokenType.number, index, self.content[index:self.pos]))
                return
            self.pos += 1
        self.tokens.append(Token(TokenType.number, index, self.content[index:]))

    def get_string_token(self, is_double_quote: bool) -> None:
        index = self.pos
        while (self.pos < len(self.content)):
            char = self.content[self.pos]
            if char == '\\':
                self.pos += 1
            elif is_double_quote and char == '"':
                self.pos += 1
                self.tokens.append(Token(TokenType.string, index, self.content[index:self.pos]))
                return
            elif char in interrupt_symbols:
                self.tokens.append(Token(TokenType.string, index, self.content[index:self.pos]))
                return
            self.pos += 1
        self.tokens.append(Token(TokenType.string, index, self.content[index:]))

    def lexer(self) -> None:
        while (self.pos < len(self.content)):
            char = self.content[self.pos]
            if char == "\n":
                self.tokens.append(Token(TokenType.lf, self.pos, "\n"))
                self.pos += 1

            elif char == " ":
                self.tokens.append(Token(TokenType.space, self.pos, " "))
                self.pos += 1

            elif char in number_symbols:
                self.get_number_token(self.pos)

            elif char == "+" or char == "-":
                origin_pos = self.pos
                self.pos += 1
                if self.pos < len(self.content) and self.content[self.pos] in number_symbols:
                    self.get_number_token(origin_pos)
                else:
                    self.tokens.append(Token(TokenType.symbol, origin_pos, char))

            elif char in symbols:
                self.tokens.append(Token(TokenType.symbol, self.pos, char))
                self.pos += 1

            elif char == '"':
                self.get_string_token(True)

            else:
                self.get_string_token(False)

    def get_tokens(self) -> list[Token]:
        return self.tokens

def tokenize(content: str) -> TokenizedContent:
    lexer = Lexer(content)
    lexer.lexer()
    tokens = lexer.get_tokens()
    return TokenizedContent(content, tokens)