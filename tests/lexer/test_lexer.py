from string_operator.lexer.lexer import tokenize
from string_operator.lexer.token import TokenType, TokenizedContent

HEADER = '\033[95m'
BLUE = '\033[94m'
CYAN = '\033[96m'
GREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
PURPLE = '\033[35m'


def printout(r: TokenizedContent) -> None:
    for token in r.tokens:
        match token.token_type:
            case TokenType.string:
                print(f"{GREEN}{token.content}{ENDC}", end="")
            case TokenType.number:
                print(f"{BLUE}{token.content}{ENDC}", end="")
            case TokenType.symbol:
                print(f"{FAIL}{token.content}{ENDC}", end="")
            case TokenType.lf:
                print(f"{WARNING}\\n{ENDC}", end="")
            case TokenType.space:
                print(f" ", end="")


command = "/execute if score \"§d§l对局时间(分)\" 信息栏 matches 58 run execute if score \"§d§l对局时间(秒)\" 信息栏 matches ..0 run structure load z3 55 93 181"
printout(tokenize(command))