# create by lesomras on 2026-4-12
import re
from typing import Optional, Union, NamedTuple

from utils.reporter import Reporter
from .source_code import Line, SourceCode
from .mcd import (
    BlockType,
    MCDMeta,
    MCDBlock,
    ChainItem,
    ChainItemComment,
    ChainItemRawCommand,
    ChainItemBlock,
    MCDChain,
    MCD,
)
from .exceptions import MCDParsingException, MCDFormatException, MCDVersionException

class Comment(NamedTuple):
    ln: Line
    text: str


class RawCommand(NamedTuple):
    ln: Line
    command: str


class ChainLabel(NamedTuple):
    ln: Line
    name: str


class CommandState(NamedTuple):
    ln: Line
    type: BlockType = BlockType.Chain
    conditional: bool = False
    always_active: bool = True
    needs_redstone: bool = False
    tick_delay: int = 0


MCDToken = Union[Comment, RawCommand, ChainLabel, CommandState]

class Label(NamedTuple):
    ln: Line
    name: str


class TokenizeMCD(NamedTuple):
    labels: list[Label]
    tokens: list[MCDToken]


class MCDParser:
    def __init__(
        self,
        document: str,
        enable_warning: bool = True,
        strict_mode: bool = True,
        relaxed: bool = True,
    ) -> None:
        """
        MCD 文本分析器

        @param document: 原始 MCD 文档内容（字符串）
        @param enable_warning: 是否启用警告输出，默认为 True
        @param strict_mode: 是否启用严格模式（格式错误会报错），默认为 True
        @param relaxed: 是否宽松模式（容忍某些非标准行为），默认为 True
        """
        self.reporter = Reporter()

        self.source_code = SourceCode(document)
        self.mcd_version = -1

        self.enable_warning = enable_warning
        self.strict_mode = strict_mode
        self.relaxed = relaxed

        self.meta_info: list[MCDMeta] = []
        self._meta_info_idx: list[int] = [] # 1-based

    def _init(self) -> TokenizeMCD:
        """内部初始化：执行元数据解析并返回词法分析结果。"""
        self._metadata()
        return self._tokenize()

    def parse(self) -> MCD:
        """
        解析函数，根据 mcd_version 自动选择按照哪个版本解析。

        @return: 解析得到的 MCD 对象
        @raises MCDParsingException: 当解析过程中存在错误且 strict_mode 为 True 时抛出
        """
        return self._semantic_analysis(self._init(), version = self.mcd_version)

    def parse_v1(self) -> MCD:
        """强制按照 MCD v1 格式解析文档。"""
        return self._semantic_analysis(self._init(), version = 1)

    def parse_v2(self) -> MCD:
        """强制按照 MCD v2 格式解析文档。"""
        return self._semantic_analysis(self._init(), version = 2)

    def _metadata(self) -> None:
        """
        解析 metadata 字段，形如 "@key = value"。
        同时根据 @mcd_version 判断版本（1 或 2）。
        """
        for l in self.source_code.lines:
            if (not l.content.startswith("@")) or (split_idx := l.content.find("=")) == -1:
                continue

            key = l.content[1:split_idx].strip()
            value = l.content[split_idx+1:].strip()

            e = False
            if key == "" and self._report(l, "Metadata key is empty", *l.left_relative_range(1, split_idx - 1)):
                e = True
            if value == "" and self._report(l, "Metadata value is empty", *l.left_relative_range(split_idx + 1, len(l.original_content) - 1)):
                e = True
            if e:
                continue

            if key == "mcd_version":
                if value == "2":
                    self.mcd_version = 2
                elif value == "1":
                    self.mcd_version = 1

            self.meta_info.append(
                MCDMeta(
                    key = key,
                    value = value
                )
            )
            self._meta_info_idx.append(l.ln)

        if self.mcd_version == -1:
            self.mcd_version = 1

    def _tokenize(self) -> TokenizeMCD:
        """
        词法分析：将源码行转换为 Token 流。

        @return: TokenizeMCD 对象，包含 labels 列表和 tokens 列表
        """
        labels: list[Label] = []
        tokens: list[MCDToken] = []

        chain_count = 1
        label_function = False
        label_end = False

        for l in self.source_code.lines:
            if l.ln in self._meta_info_idx:
                continue

            # ###Function### / ###End###
            if l.content.startswith("###") and l.content.endswith("###"):
                label_name = l.content[3:-3].strip().lower()
                if label_name == "":
                    label_name = "未命名标签"
                    self._report(l, "Label name is empty", *l.relative_range(3, 3))

                labels.append(Label(l, label_name))
                continue

            # comment
            if l.content.startswith("#"):
                comment_text = l.content[1:].lstrip()
                tokens.append(Comment(l, comment_text))
                continue

            # v1 command
            if self.mcd_version == 1:
                # 将前部有斜杠或者英文字母的文本视为命令，否则视为隐式注释
                first_char = l.content[0]
                if first_char == '/' or (first_char.isalpha() and ord(first_char) < 128):
                        tokens.append(RawCommand(l, l.content))
                else:
                    tokens.append(Comment(l, l.content))
                    self._report_line(l.ln, "Comments need to be displayed")
                continue

            # v2 only
            if self.mcd_version != 2:
                continue

            # ---Chain Name---
            if l.content.startswith("---") and l.content.endswith("---"):
                chain_name = l.content[3:-3].strip()
                if chain_name == "":
                    chain_name = f"Chain {chain_count}"
                    chain_count += 1
                    self._report(l, "Chain name is empty", *l.relative_range(3, 3))

                tokens.append(ChainLabel(l, chain_name))
                continue

            # > state
            if l.content.startswith(">"):
                state_str = l.content[1:].lstrip()

                if self.strict_mode:
                    spaces_offset = len(l.content) - len(state_str)
                    result = self._parse_state_strictly(state_str, l, spaces_offset)
                else:
                    result = self._parse_state(state_str, l)

                if result is not None:
                    tokens.append(result)
                continue

            # 理论上可以将任何东西作为命令, 这个检查之后再做
            tokens.append(RawCommand(l, l.content))

        self.reporter.done(MCDParsingException)
        return TokenizeMCD(labels, tokens)

    def _parse_state(self, state_str: str, l: Line) -> CommandState:
        """
        接受状态字符串并进行简单解析（宽松模式），解析总是成功。

        @param state_str: 状态字符串（如 "I?t5"）
        @param l: 所在行的 Line 对象
        @return: CommandState 对象，包含解析后的方块状态
        """
        state_upper = state_str.upper()
        if "I" in state_upper:
            pending_block_type = BlockType.Impulse
        elif "R" in state_upper:
            pending_block_type = BlockType.Repeat
        else:
            pending_block_type = BlockType.Chain

        pending_conditional = "?" in state_str
        pending_always_active = "!" not in state_str
        pending_needs_redstone = not pending_always_active

        tick_match = re.search(r"[tT](\d+)", state_str)
        if tick_match:
            pending_tick_delay = int(tick_match.group(1))
        else:
            pending_tick_delay = 0

        return CommandState(
            l,
            pending_block_type,
            pending_conditional,
            pending_always_active,
            pending_needs_redstone,
            pending_tick_delay,
        )

    def _parse_state_strictly(self, state_str: str, l: Line, spaces_offset: int) -> Optional[CommandState]:
        """
        接受状态字符串并进行严格解析，解析失败返回 None。

        @param state_str: 状态字符串
        @param l: 所在行的 Line 对象
        @param spaces_offset: state_str 在原始行中的起始偏移（字符数）
        @return: 解析成功返回 CommandState，失败返回 None
        """
        def error_at(offset: int, msg: str) -> None:
            col = spaces_offset + offset
            self._report(l, msg, *l.left_relative_len_range(col, 1))

        def error_remaining(offset: int, msg: str) -> None:
            col = spaces_offset + offset
            self._report(l, msg, *l.relative_range(col, 0))

        def check_remaining(offset: int, location: str) -> bool:
            if offset < state_str_len:
                error_remaining(offset, f"Unexpected characters after {location}")
                return True
            return False

        state_str_len = len(state_str)

        pending_block_type = BlockType.Chain
        pending_conditional = False
        pending_always_active = True
        pending_needs_redstone = False
        pending_tick_delay = 0

        pointer = 0
        # parse block type
        if state_str_len == 0: # <=> state_str_len <= pointer
            return CommandState(l, pending_block_type, pending_conditional, pending_always_active, pending_needs_redstone, pending_tick_delay)

        match state_str[pointer].upper():
            case "C" | "_":
                pending_block_type = BlockType.Chain #(default)
                pointer += 1
            case "R":
                pending_block_type = BlockType.Repeat
                pointer += 1
            case "I":
                pending_block_type = BlockType.Impulse
                pointer += 1
            case "H":
                pending_block_type = BlockType.CommandLine
                pointer += 1
                if check_remaining(pointer, "'H' (CommandLine Mode)"):
                    return None
                return CommandState(l, pending_block_type)
            case "?" | "!" | "T":
                pending_block_type = BlockType.Chain
            case _:
                error_at(pointer, "Expected block type ('I', 'R' or 'C'), or to ignore it ('_')")
                return None

        # parse conditional
        if state_str_len <= pointer:
            return CommandState(l, pending_block_type)

        c = state_str[pointer]
        match c:
            case "?":
                pending_conditional = True
                pointer += 1
            case "_":
                pending_conditional = False #(default)
                pointer += 1
            case _:
                if c == "!" or c.lower() == "t":
                    pending_conditional = False #(default)
                else:
                    error_at(pointer, "Expected conditional comment ('?'), or to ignore it ('_')")
                    return None

        # parse always_active / needs redstone
        if state_str_len <= pointer:
            return CommandState(l, pending_block_type, pending_conditional)

        c = state_str[pointer]
        match c:
            case "!":
                pending_always_active = False
                pending_needs_redstone = True
                pointer += 1
            case "_":
                pending_always_active = True # (default)
                pending_needs_redstone = False #(default)
                pointer += 1
            case _:
                if c.lower() == "t":
                    pending_always_active = True #(default)
                    pending_needs_redstone = False #(default)
                else:
                    error_at(pointer, "Expected needs redstone comment ('!'), or to ignore it ('_')")
                    return None

        # parse tick delay
        if state_str_len <= pointer:
            return CommandState(l, pending_block_type, pending_conditional, pending_always_active, pending_needs_redstone)

        c = state_str[pointer]
        if c.lower() != "t":
            error_at(pointer, "Expected delay tick comment ('t')")
            return None
        pointer += 1

        if state_str_len <= pointer:
            error_at(pointer - 1, f"Expected delay tick after '{c}'")
            return None

        if state_str[pointer] == "_":
            if check_remaining(pointer, "delay tick"):
                return None
            return CommandState(l, pending_block_type, pending_conditional, pending_always_active, pending_needs_redstone, pending_tick_delay)

        start_pointer = pointer
        while state_str_len > pointer:
            c = state_str[pointer]
            if not ('0' <= c <= '9'):
                error_at(pointer, f"Expected a integer, found a non-digit character: {c}")
                return None
            pointer += 1

        pending_tick_delay = int(state_str[start_pointer:pointer])
        if check_remaining(pointer, "delay tick"):
            return None

        return CommandState(l, pending_block_type, pending_conditional, pending_always_active, pending_needs_redstone, pending_tick_delay)

    def _semantic_analysis(self, tokenize_mcd: TokenizeMCD, version: int) -> MCD:
        """
        语义分析：将 Token 流转换为 MCD 对象。

        @param tokenize_mcd: 词法分析结果，包含 labels 和 tokens
        @param version: 要使用的 MCD 版本（1 或 2）
        @return: 构建完成的 MCD 对象
        @raises MCDParsingException: 当存在错误且 strict_mode 为 True 时抛出
        """
        self.reporter.reset()
        # state
        pointer = 0
        tokens = tokenize_mcd.tokens

        label_function, label_end = self._analysis_labels(tokenize_mcd.labels)
        if label_function is None:
            start_ln = tokens[0].ln.ln if tokens else 0
            end_ln = label_end.ln.ln if label_end is not None else len(self.source_code.original_lines)
            self._report_lines(start_ln, end_ln, "Expected the label 'End' before commands")

        if label_end is None:
            ln = tokens[-1].ln.ln if tokens else len(self.source_code.original_lines)
            self._report_line(ln, "Expected label 'End' after commands")

        elif tokens and tokens[-1].ln.ln > label_end.ln.ln:
            self._report_lines(label_end.ln.ln, tokens[-1].ln.ln, "Unexpected commands after label 'End'")

        root_comments = []
        for token in tokens:
            if not isinstance(token, Comment):
                break
            root_comments.append(token.text)

        match version:
            case 1:
                chains = self._analysis_v1(tokens)
            case 2:
                chains = self._analysis_v2(tokens)
            case _:
                raise MCDVersionException(f"Invalid MCD version: {version}")

        self.reporter.done(MCDParsingException)
        return MCD(
            meta_info = self.meta_info,
            root_comments = root_comments,
            chains = chains,
            is_v2 = self.mcd_version == 2,
        )

    def _analysis_labels(self, labels: list[Label]) -> tuple[Optional[Label], Optional[Label]]:
        """
        分析标签列表，检查合法性、重复性，并返回第一个 function 标签和最后一个 end 标签。

        @param labels: Label 对象列表
        @return: (func_label, end_label)，若不存在则为 None
        """
        func_label = None
        end_label = None

        for lbl in labels:
            name = lbl.name
            if name == "function":
                if func_label is not None:
                    self._report_line(lbl.ln.ln, "Duplicate label 'Function'")
                else:
                    func_label = lbl
            elif name == "end":
                if end_label is not None:
                    self._report_line(end_label.ln.ln, "Duplicate label 'End'")
                end_label = lbl
            else:
                self._report_line(lbl.ln.ln, f"Invalid label name '{name}', expected 'Function' or 'End'")
        return func_label, end_label

    def _analysis_v1(self, tokens: list[MCDToken]) -> list[MCDChain]:
        """
        v1 语义分析：将所有 RawCommand 和 Comment 放入一个默认链。

        @param tokens: MCDToken 列表
        @return: 包含单个 MCDChain 的列表
        """
        current_chain = MCDChain(name = "分离的命令")

        for token in tokens:
            match token:
                case RawCommand(l, command):
                    current_chain.items.append(ChainItemRawCommand(command = command))
                case Comment(_, text):
                    current_chain.items.append(ChainItemComment(text = text))
                case _:
                    raise MCDFormatException(f"Unexpected token type: {type(token).__name__}")
        return [current_chain]

    def _analysis_v2(self, tokens: list[MCDToken]) -> list[MCDChain]:
        """
        v2 语义分析：处理链标签、状态挂起、命令与状态配对，生成链列表。

        @param tokens: MCDToken 列表
        @return: 解析得到的 MCDChain 列表
        """
        chains: list[MCDChain] = []
        current_chain: Optional[MCDChain] = None
        pending_state: Optional[CommandState] = None

        for token in tokens:
            match token:
                case ChainLabel(ln, name):
                    if pending_state:
                        self._report_line(pending_state.ln.ln, "Unused state comment before chain label")
                        pending_state = None
                    current_chain = MCDChain(name=name)
                    chains.append(current_chain)

                case CommandState(ln = ln):
                    if current_chain is None:
                        current_chain = MCDChain(name="Chain 0")
                        chains.append(current_chain)
                        self._report_line(ln.ln, "State outside any chain, created default chain", enable_relaxed = True)
                    if pending_state:
                        self._report_line(pending_state.ln.ln, "Unused state comment")
                    pending_state = token

                case RawCommand(ln, command):
                    if current_chain is None:
                        current_chain = MCDChain(name="Chain 0")
                        chains.append(current_chain)
                        self._report_line(ln.ln, "Command outside any chain, created default chain", enable_relaxed = True)

                    if pending_state:
                        block = MCDBlock(
                            type=pending_state.type,
                            conditional=pending_state.conditional,
                            always_active=pending_state.always_active,
                            needs_redstone=pending_state.needs_redstone,
                            tick_delay=pending_state.tick_delay,
                            command=command,
                        )
                        pending_state = None
                    else:
                        block = MCDBlock(command=command)

                    current_chain.items.append(ChainItemBlock(block=block))

                case Comment(ln, text):
                    if current_chain is not None:
                        current_chain.items.append(ChainItemComment(text=text))
                case _:
                    raise MCDFormatException(f"Unexpected token type in v2: {type(token).__name__}")

        if pending_state:
            self._report_line(pending_state.ln.ln, "Unused state comment at end of file")

        return chains

    def _report(self, l: Line, message: str, start_ptr: int, end_ptr: int) -> bool:
        """
        根据 strict_mode 和 relaxed 设置，报告错误或警告。

        @param l: 所在行的 Line 对象
        @param message: 错误/警告消息
        @param start_ptr: 高亮起始绝对位置（字符索引）
        @param end_ptr: 高亮结束绝对位置（半开区间）
        @return: 若报告了错误（strict_mode 或非 relaxed）返回 True，否则 False
        """
        if self.strict_mode or (not self.relaxed):
            self.reporter.print_error_with_context(
                lines = self.source_code.original_lines,
                line_no = l.ln,
                start_char = start_ptr,
                end_char = end_ptr,
                message = message,
            )
            return True
        if self.enable_warning:
            self.reporter.print_warning_with_context(
                lines = self.source_code.original_lines,
                line_no = l.ln,
                start_char = start_ptr,
                end_char = end_ptr,
                message = message,
            )
        return False

    def _report_line(self, line_no: int, message: str, enable_relaxed = False) -> bool:
        """
        报告只关联行号的错误或警告（无高亮标记）。

        @param line_no: 行号（1-indexed）
        @param message: 消息内容
        @return: 若报告了错误（strict_mode 或非 relaxed）返回 True，否则 False
        """
        if ((not enable_relaxed) and self.strict_mode) or (not self.relaxed):
            self.reporter.print_error_line(
                lines=self.source_code.original_lines,
                line_no=line_no,
                message=message,
            )
            self.had_error = True
            return True
        if self.enable_warning:
            self.reporter.print_warning_line(
                lines=self.source_code.original_lines,
                line_no=line_no,
                message=message,
            )
        return False

    def _report_lines(self, start_line: int, end_line: int, message: str) -> bool:
        """
        报告一个行范围的错误或警告（无高亮标记）。

        @param start_line: 起始行号（1-indexed）
        @param end_line: 结束行号（1-indexed，包含）
        @param message: 消息内容
        @return: 若报告了错误（strict_mode 或非 relaxed）返回 True，否则 False
        """
        if self.strict_mode or (not self.relaxed):
            # 错误
            self.reporter.print_error_lines(
                lines=self.source_code.original_lines,
                start_line=start_line,
                end_line=end_line,
                message=message,
            )
            self.had_error = True
            return True
        elif self.enable_warning:
            # 警告
            self.reporter.print_warning_lines(
                lines=self.source_code.original_lines,
                start_line=start_line,
                end_line=end_line,
                message=message,
            )
        return False
