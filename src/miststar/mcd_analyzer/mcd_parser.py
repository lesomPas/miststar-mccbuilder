# created by lesomras on 2026-8-1

import re
from enum import Enum
from typing import Optional, Literal, NamedTuple

from miststar.exceptions import InvalidValueException
from .exceptions import MCDParsingException

from .mcd import BlockKind, MCDMeta, MCDChain, CommandState, ChainItem, MCDChain, MCD
from .mcd_lexer import DocumentTokenKind, DocumentToken, DocumentLexer


VERSION_RE = re.compile(r'^\s*@mcd_version\s*=\s*(\S+)', re.MULTILINE)

def detect_version(doc: str) -> int:
    if (m := VERSION_RE.search(doc)):
        return int(m.group(1)) if m.group(1) in ("1", "2") else -1
    return 1


STATE_SECTIONS = [
    {
        "_": BlockKind.Chain,
        "I": BlockKind.Impulse,
        "C": BlockKind.Chain,
        "R": BlockKind.Repeat,
        "H": BlockKind.Chat,
        "error": ("Invalid char: '{}'"
                  ", excepted 'I' (Impulse), 'C' (Chain), 'R' (Repeat), 'H' (Chat) or '_' (Chain).")
    },
    {
        "_": False,
        "?": True,
        "error": ("Invalid char: '{}'"
                  ", excepted '?' (Conditional) or '_' (Unconditional).")
    },
    {
        "_": True,
        "!": False,
        "error": ("Invalid char: '{}'"
                  ", excepted '!' (Need Redstones) or '_' (Always Active).")
    }
]

STATE_CHARS = {k for sec in STATE_SECTIONS for k in sec.keys() if k != "error"}.union({"t", "T"})


class DocumentCursor:
    def __init__(self, doc: str, lexer: DocumentLexer):
        self._iter = iter(lexer.tokenize(doc))

        try:
            current = next(self._iter)
        except StopIteration:
            raise MCDParsingException("Empty document: no tokens produced by lexer")

        self.current: Optional[DocumentToken] = current

        try:
            peek = next(self._iter)
        except StopIteration:
            peek = None

        self.peek: Optional[DocumentToken] = peek

    def bump(self) -> Optional[DocumentToken]:
        old_current = self.current
        self.current = self.peek
        try:
            self.peek = next(self._iter)
        except StopIteration:
            self.peek = None
        return old_current

    def is_eof(self) -> bool:
        return self.current is None


class MCDParserConfig(NamedTuple):
    # mcd_version = 1, 2
    unmatch_mode: Literal["forbid", "ignore", "comment", "text_command"] = "comment"
    extra_mode: Literal["forbid", "ignore"] = "ignore"
    label_mode: Literal["strict", "ignore"] = "ignore"

    # mcd_version = 2
    chain_label_mode: Literal["strict", "auto"] = "auto"
    state_generator: Literal["strict", "simple"] = "simple"
    unused_state: Literal["forbid", "ignore"] = "ignore"


class MCDParserV1:
    def __init__(self, lexer: DocumentLexer, config: MCDParserConfig):
        self.config = config
        self.lexer = lexer

    def generate_mcd(self, doc: str) -> MCD:
        cursor = DocumentCursor(doc, self.lexer)

        meta_info = []
        chain_item = []

        self.matched_start = False
        self.matched_end = False

        while cursor.current is not None:
            cur = cursor.current

            match cur.kind:
                case DocumentTokenKind.Meta:
                    meta_info.append(MCDMeta(key=cur.data, value=cur.extra_data))
                    cursor.bump()

                case DocumentTokenKind.Label:
                    self._analyze_label(cursor, cur)

                case DocumentTokenKind.Comment:
                    chain_item.append(ChainItem.Comment(cur.data))
                    cursor.bump()

                case DocumentTokenKind.TextCommand:
                    chain_item.append(ChainItem.TextCommand(cur.data))
                    cursor.bump()

                case DocumentTokenKind.UnmatchLine:
                    self._analyze_unmatch_line(cursor, cur, chain_item)

                case _:
                    self._analyze_extra(cursor, cur)

        if self.config.label_mode == "strict" and not self.matched_end:
            raise MCDParsingException("Missing 'End' label: expected ###End### to close the document")

        return MCD(
            meta_info = meta_info,
            chains = [MCDChain(name="分离的命令", items=chain_item)],
            version = 1,
        )

    def _analyze_label(self, cursor: DocumentCursor, cur: DocumentToken) -> None:
        if self.config.label_mode != "strict":
            cursor.bump()
            return

        if cur.data.lower() == "function":
            if not self.matched_start:
                self.matched_start = True
                cursor.bump()
                return
            raise MCDParsingException(f"Duplicate label 'Function' at document token {cur!r}")

        if cur.data.lower() == "end":
            if cursor.peek is None:
                self.matched_end = True
                cursor.bump()
                return
            raise MCDParsingException(f"Label 'End' must be the last token, but found more content afterwards")

        raise MCDParsingException(f"Invalid label '{cur.data}': expected 'Function' or 'End'")

    def _analyze_unmatch_line(self, cursor: DocumentCursor, cur: DocumentToken, chain_item: list[ChainItem]) -> None:
        match self.config.unmatch_mode:
            case "forbid": raise InvalidValueException(f"Unexpected unmatched line: {cur.data!r}")
            case "ignore": pass
            case "comment": chain_item.append(ChainItem.Comment(cur.data))
            case "text_command": chain_item.append(ChainItem.TextCommand(cur.data))
        cursor.bump()

    def _analyze_extra(self, cursor: DocumentCursor, cur: DocumentToken) -> None:
        match self.config.extra_mode:
            case "forbid": raise InvalidValueException(f"Unexpected token kind {cur.kind.name} in v1 parser: {cur.data!r}")
            case "ignore": pass
        cursor.bump()


class ChainState(Enum):
    Interrupt = "ChainState.Interrupt"
    End = "ChainState.End"


class MCDParserV2(MCDParserV1):
    def generate_mcd(self, doc: str) -> MCD:
        cursor = DocumentCursor(doc, self.lexer)

        self.meta_info = []
        self.chains = []

        self.matched_start = False
        self.matched_end = False
        has_chain = False

        chain_count = 0
        root_comments, cur_chain = self._generate_prefix_chain(cursor)

        if cur_chain == ChainState.Interrupt:
            if self.config.chain_label_mode == "strict":
                raise MCDParsingException("Command outside any chain, but chain_label_mode is strict")
            chain_count += 1
            cur_chain = f"Chain {chain_count}"

        while cur_chain != ChainState.End:
            chain_count += 1

            cur_chain = self._generate_chain(cursor, cur_chain) # type: ignore
            if cur_chain == "":
                cur_chain = f"Chain {chain_count}"

            if not has_chain:
                self.chains[0].items = root_comments + self.chains[0].items
                has_chain = True

        if self.config.label_mode == "strict" and not self.matched_end:
            raise MCDParsingException("Missing 'End' label: expected ###End### to close the document")

        if not has_chain:
            self.chains.append(MCDChain(name="分离的命令", items=root_comments))

        return MCD(
            meta_info = self.meta_info,
            chains = self.chains,
            version = 2,
        )

    def _generate_prefix_chain(self, cursor: DocumentCursor) -> tuple[list[ChainItem], str | ChainState]:
        chain_item = []

        while cursor.current is not None:
            cur = cursor.current
            match cur.kind:
                case DocumentTokenKind.ChainLabel:
                    cursor.bump()
                    return (chain_item, cur.data)

                # 下面这三个与_generate_chain中的是基本完全相同
                case DocumentTokenKind.Meta:
                    self.meta_info.append(MCDMeta(key=cur.data, value=cur.extra_data))
                    cursor.bump()

                case DocumentTokenKind.Label:
                    self._analyze_label(cursor, cur)

                case DocumentTokenKind.Comment:
                    chain_item.append(ChainItem.Comment(cur.data))
                    cursor.bump()

                case _:
                    return (chain_item, ChainState.Interrupt)

        return (chain_item, ChainState.End)

    def _generate_chain(self, cursor: DocumentCursor, name: str) -> str | ChainState:
        chain_item = []
        pending_state: Optional[CommandState] = None

        while cursor.current is not None:
            cur = cursor.current
            match cur.kind:
                case DocumentTokenKind.ChainLabel:
                    self.chains.append(MCDChain(name=name, items=chain_item))
                    cursor.bump()
                    return cur.data

                case DocumentTokenKind.Meta:
                    self.meta_info.append(MCDMeta(key=cur.data, value=cur.extra_data))
                    cursor.bump()

                case DocumentTokenKind.Label:
                    self._analyze_label(cursor, cur)
                    pending_state = None

                case DocumentTokenKind.Comment:
                    chain_item.append(ChainItem.Comment(cur.data))
                    cursor.bump()

                case DocumentTokenKind.State:
                    pending_state = self._analyze_command_state(cursor, cur, chain_item)

                case DocumentTokenKind.MarkedCommand:
                    state = pending_state if pending_state else CommandState()
                    chain_item.append(ChainItem.MarkedCommand(state=state, command=cur.data))
                    pending_state = None
                    cursor.bump()

                case DocumentTokenKind.UnmatchLine:
                    self._analyze_unmatch_line(cursor, cur, chain_item)

                case _:
                    self._analyze_extra(cursor, cur)

        self.chains.append(MCDChain(name=name, items=chain_item))
        return ChainState.End

    def _analyze_command_state(self, cursor: DocumentCursor, cur: DocumentToken, chain_item: list[ChainItem]) -> Optional[CommandState]:
        cursor.bump()
        next_cur = cursor.current
        pending_state = self._generate_command_state(cur.data)

        if next_cur is not None and next_cur.kind == DocumentTokenKind.MarkedCommand:
            chain_item.append(ChainItem.MarkedCommand(state=pending_state, command=next_cur.data))
            cursor.bump()
            return None

        if self.config.unused_state == "forbid":
            raise MCDParsingException(f"Unused state comment '{cur.data}': expected a command immediately after state")

        return pending_state

    def _generate_command_state(self, state_str: str) -> CommandState:
        if self.config.state_generator == "simple":
            return self.generate_state_simply(state_str)
        else:
            return self.generate_state_strictly(state_str)

    @staticmethod
    def generate_state_simply(state_str: str) -> CommandState:
        if not state_str:
            return CommandState()

        state_upper = state_str.upper()

        if "I" in state_upper:
            kind = BlockKind.Impulse
        elif "R" in state_upper:
            kind = BlockKind.Repeat
        elif "H" in state_upper:
            kind = BlockKind.Chat
        else:
            kind = BlockKind.Chain

        conditional = "?" in state_str
        always_active = "!" not in state_str

        tick_match = re.search(r"[tT](\d+|_)", state_str)
        if tick_match:
            tick_str = tick_match.group(1)
            tick_delay = 0 if tick_str == "_" else int(tick_str)
        else:
            tick_delay = 0

        return CommandState(
            kind=kind,
            conditional=conditional,
            always_active=always_active,
            tick_delay=tick_delay,
        )

    @staticmethod
    def generate_state_strictly(state_str: str) -> CommandState:
        if not state_str:
            return CommandState()

        values = []

        ptr = 0
        char = state_str[0]
        for sec in STATE_SECTIONS:
            if ptr < len(state_str):
                char = state_str[ptr].upper()

            if char in sec:
                values.append(sec[char])
                ptr += 1
            elif char in STATE_CHARS:
                values.append(sec["_"])
            else:
                raise MCDParsingException(sec["error"].format(char))

        if values[0] == BlockKind.Chat and state_str.upper() != "H":
            raise MCDParsingException(f"Extra chars: '{state_str[1:]}', Chat Mode expected no extra character.")

        if ptr >= len(state_str):
            return CommandState(
                kind=values[0],
                conditional=values[1],
                always_active=values[2],
                tick_delay=0,
            )

        if state_str[ptr].lower() != "t" or (ptr + 1) >= len(state_str):
            raise MCDParsingException(f"Invalid tick value: '{state_str[ptr:]}', expected 't_' or 't(\\d+)'.")

        tick_str = state_str[ptr+1:]
        if tick_str != "_" and not all('0' <= c <= '9' for c in tick_str):
            raise MCDParsingException(f"Invalid tick value: '{state_str[ptr:]}', expected 't_' or 't(\\d+)'.")

        tick = 0 if tick_str == "_" else int(tick_str)
        return CommandState(
            kind=values[0],
            conditional=values[1],
            always_active=values[2],
            tick_delay=tick,
        )
