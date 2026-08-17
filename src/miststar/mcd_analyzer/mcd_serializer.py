# created by lesomras on 2026-8-10
from typing import Optional, Literal

from .mcd import MCD, ChainItem, CommandState, BlockKind
from .mcd_lexer import DocumentLexer, MCDLexerV1, MCDLexerV2
from .mcd_parser import MCDParserConfig, MCDParserV1, MCDParserV2, detect_version


class MCDFormatter:
    default_newline_dict = {
        "meta": False,
        "label": True,
        "chain_label": False,
        "comment": False,
        "text_command": False,
        "marked_command": True,
    }

    def __init__(
        self,
        full_state_string: bool = False,
        newline_dict: Optional[dict[str, bool]] = None,
        newline_folding: bool = True,
    ):
        self.full_state_string = full_state_string
        self.newline_dict = newline_dict if newline_dict is not None else self.default_newline_dict
        self.newline_folding = newline_folding

    def _newline(self, kind: str) -> bool:
        res = self.newline_dict.get(kind, None)
        return res if res is not None else self.default_newline_dict[kind]

    def _string_state(self, state: CommandState) -> str:
        state_str = ""
        match state.kind:
            case BlockKind.Chain:
                state_str += 'C' # 一般来说方块类型不会使用省略符'_', 太不直观了
            case BlockKind.Repeat:
                state_str += 'R'
            case BlockKind.Impulse:
                state_str += 'I'
            case BlockKind.Chat:
                return 'H'

        if self.full_state_string or state.conditional:
            state_str += '?' if state.conditional else '_'

        if self.full_state_string or not state.always_active:
            state_str += '!' if not state.always_active else '_'

        if self.full_state_string or state.tick_delay != 0:
            state_str += f"t{state.tick_delay if state.tick_delay != 0 else '_'}"

        return state_str

    def string_mcd(self, mcd: MCD) -> str:
        string_builder = []
        include_name = mcd.version != 1

        def newline(kind: str) -> None:
            if self._newline(kind):
                string_builder.append("\n")

        def string_chain(items: list[ChainItem], name: str) -> None:
            if string_builder[-1] != "\n" or not self.newline_folding:
                string_builder.append("\n")

            if include_name:
                string_builder.append(f"---{name}---\n")
                newline("chain_label")

            for it in items:
                match it:
                    case ChainItem.Comment(text=text): # type: ignore
                        string_builder.append(f"#{text}\n")
                        newline("comment")

                    case ChainItem.TextCommand(command=command): # type: ignore
                        string_builder.append(f"{command}\n")
                        newline("text_command")

                    case ChainItem.MarkedCommand(command=command, state=state): # type: ignore
                        string_builder.append(f"> {self._string_state(state)}\n")
                        string_builder.append(f"{command}\n")
                        newline("marked_command")

        for meta in mcd.meta_info:
            string_builder.append(f"@{meta.key}={meta.value}\n")
            newline("meta")

        if (len(string_builder) > 0 and string_builder[-1] != "\n") or not self.newline_folding:
            string_builder.append("\n")

        string_builder.append("###Function###\n")
        newline("label")

        for chain in mcd.chains:
            string_chain(chain.items, chain.name)

        string_builder.append("###End###")
        return "".join(string_builder)


class MCDSerializer:
    def __init__(
        self,
        formatter: Optional[MCDFormatter],
        parser_config: Optional[MCDParserConfig] = None,
    ):
        self.formatter = formatter if formatter is not None else MCDFormatter()
        self.parser_config = parser_config if parser_config is not None else MCDParserConfig()

    def string_mcd(self, mcd: MCD) -> str:
        return self.formatter.string_mcd(mcd)

    def get_mcd_parser(self, version: Literal[1, 2], lexer: Optional[DocumentLexer] = None) -> MCDParserV1 | MCDParserV2:
        if version == 1:
            lexer = lexer if lexer is not None else MCDLexerV1()
            return MCDParserV1(lexer, self.parser_config)
        if version == 2:
            lexer = lexer if lexer is not None else MCDLexerV2()
            return MCDParserV2(lexer, self.parser_config)

    def load_mcd(self, doc: str, lexer: Optional[DocumentLexer] = None, version_exception: bool = False) -> MCD:
        version = detect_version(doc)
        if version not in (1, 2):
            version = 1

        return self.get_mcd_parser(version, lexer).generate_mcd(doc)
