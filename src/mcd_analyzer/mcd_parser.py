# create by lesomras on 2026-4-12
import re
from typing import Optional

from ..utils.reporter import Reporter
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
from .exceptions import MCDParsingException

class MCDParser:
    def __init__(
        self,
        document: str,
        enable_warning: bool = True,
        strict_mode: bool = True,
    ) -> None:
        """
        MCD 文本分析器
        @parameters:
          document: 原始文档内容
          enable_warning: 启用警告 (strict_mode 默认启用)
          strict_mode: 严格模式, 启用错误. 解析失败不返回解析结果.
        """
        self.reporter = Reporter()

        self.lines = document.splitlines()
        self.mcd_version = 1

        self.enable_warning = enable_warning
        self.strict_mode = strict_mode

        self._metadata()

    def parse(self) -> MCD:
        """ 解析函数，根据mcd版本自动选择按照哪个版本解析 """
        if self.mcd_version == 2:
            return self.parse_v2()
        else:
            return self.parse_v1()

    def _metadata(self) -> None:
        """ 解析metadata字段，形如"@key = value"。同时判断版本 """
        self.meta_info = []
        self._meta_info_idx = [] # 1-indexed

        for ln, content in enumerate(self.lines, start=1):
            if (not content) or content.isspace():
                continue

            l_content = content.lstrip()
            if (not l_content.startswith("@")) or (split_idx := l_content.find("=")) == -1:
                continue

            start_idx = len(content) - len(l_content)
            key = l_content[1:split_idx].strip()
            value = l_content[split_idx+1:].strip()

            if key == "" and self._report(ln, start_idx+1, split_idx, "Metadata key is empty"):
                continue
            if value == "" and self._report(ln, start_idx+split_idx+1, len(content), "Metadata value is empty"):
                continue
            if key == "mcd_version" and value == "2":
                self.mcd_version = 2

            self.meta_info.append(
                MCDMeta(
                    key = key,
                    value = value
                )
            )
            self._meta_info_idx.append(ln)

    def parse_v1(self) -> MCD:
        """ 按照MCDv1解析文档内容 """
        root_comments = []
        current_chain = MCDChain(name = "分离的命令")

        label_function = False
        label_end = False

        ln = 1
        for ln, content in enumerate(self.lines, start=1):
            if ln in self._meta_info_idx:
                continue

            l_content = content.lstrip()
            start_idx = len(content) - len(l_content)
            lr_content = l_content.rstrip()
            end_idx = start_idx + len(lr_content) - 1 # 包括最后一个字符

            if not lr_content:
                continue

            # ###Function### / ###End###
            if lr_content.startswith("###") and lr_content.endswith("###"):
                label_name = lr_content[3:-3].strip().lower()

                if label_name == "function":
                    label_function = True
                elif label_name == "end":
                    label_end = True
                else:
                    self._report(ln, start_idx + 3, end_idx - 2, "Label name must be 'Function' or 'End'.")
                continue

            # #comment
            if lr_content.startswith("#"):
                comment_text = lr_content[1:].lstrip()
                if current_chain is not None:
                    current_chain.items.append(ChainItemComment(text = comment_text))
                else:
                    root_comments.append(comment_text)
                continue

            # 将前部有斜杠或者英文字母的文本视为命令，否则视为隐式注释
            first_char = lr_content[0]
            if first_char == '/' or (first_char.isalpha() and ord(first_char) < 128):
                    current_chain.items.append(ChainItemRawCommand(command=lr_content))
            else:
                current_chain.items.append(ChainItemComment(text=lr_content))
                self._report(ln, 0, len(content), "Comments need to be displayed")

        if not label_function:
            self._report(1, 0, 0, "Expected the label ###Function###")
        if not label_end:
            self._report(ln, 0, 0, "Expected the label ###End###")

        self.reporter.done(MCDParsingException)
        return MCD(
            meta_info = self.meta_info,
            root_comments = root_comments,
            chains = [current_chain, ],
            is_v2 = False,
        )

    def parse_v2(self) -> MCD:
        """ 按照MCDv2解析文档内容，方块状态处理函数由strict_mode决定 """
        root_comments = []
        chains = []

        current_chain: Optional[MCDChain] = None

        pending_block_type = BlockType.Chain
        pending_conditional = False
        pending_always_active = True
        pending_needs_redstone = False
        pending_tick_delay = 0
        has_pending_state = False
        #                        ln,  length
        pending_state_str: tuple[int, int] = (0, 0)

        label_function = False
        label_end = False

        ln = 1
        for ln, content in enumerate(self.lines, start=1):
            if ln in self._meta_info_idx:
                continue

            l_content = content.lstrip()
            start_idx = len(content) - len(l_content)
            lr_content = l_content.rstrip()
            end_idx = start_idx + len(lr_content) - 1 # 包括最后一个字符

            if not lr_content:
                continue

            # ###Function### / ###End###
            if lr_content.startswith("###") and lr_content.endswith("###"):
                label_name = lr_content[3:-3].strip().lower()

                if label_name == "function":
                    label_function = True
                elif label_name == "end":
                    label_end = True
                else:
                    self._report(ln, start_idx + 3, end_idx - 2, "Label name must be 'Function' or 'End'.")
                continue

            # ---Chain Name---
            if lr_content.startswith("---") and lr_content.endswith("---"):
                chain_name = lr_content[3:-3].strip()

                if chain_name == "":
                    chain_name = "未命名命令链"
                    self._report(ln, start_idx + 3, end_idx - 2, "Chain name is empty")

                current_chain = MCDChain(name = chain_name)
                chains.append(current_chain)
                has_pending_state = False
                continue

            # #comment
            if lr_content.startswith("#"):
                comment_text = lr_content[1:].lstrip()
                if current_chain is not None:
                    current_chain.items.append(ChainItemComment(text = comment_text))
                else:
                    root_comments.append(comment_text)
                continue

            # > state
            if lr_content.startswith(">"):
                if has_pending_state:
                    self._report(pending_state_str[0], 0, pending_state_str[1], "Unused state comment")
                state_str = lr_content[1:].lstrip()

                if self.strict_mode:
                    state_start_idx = len(lr_content) - len(state_str)
                    result = self._parse_state_strictly(state_str, ln, start_idx + state_start_idx)
                else:
                    result = self._parse_state(state_str)

                if result is not None:
                    pending_block_type, \
                    pending_conditional, \
                    pending_always_active, \
                    pending_needs_redstone, \
                    pending_tick_delay = result

                    has_pending_state = True
                    pending_state_str = (ln, len(content))
                continue

            if current_chain is None:
                current_chain = MCDChain(name = "分离的命令")
                chains.append(current_chain)
                self._report_warning(ln, 0, len(content), "Chain name is required")

            if has_pending_state:
                block = MCDBlock(
                    type = pending_block_type,
                    conditional = pending_conditional,
                    always_active = pending_always_active,
                    needs_redstone = pending_needs_redstone,
                    tick_delay = pending_tick_delay,
                    command = lr_content,
                )
            else:
                block = MCDBlock(command = lr_content)

            current_chain.items.append(ChainItemBlock(block = block))
            has_pending_state = False

        if has_pending_state:
            self._report(pending_state_str[0], 0, pending_state_str[1], "No command matched the state comment")

        if not label_function:
            self._report(1, 0, 0, "Expected the label ###Function###")
        if not label_end:
            self._report(ln, 0, 0, "Expected the label ###End###")

        self.reporter.done(MCDParsingException)
        return MCD(
            meta_info = self.meta_info,
            root_comments = root_comments,
            chains = chains,
            is_v2 = True,
        )

    def _parse_state(self, state_str: str) -> tuple[BlockType, bool, bool, bool, int]:
        """
        接受状态str并进行简单解析, 解析总是成功.
        @return:
          tuple.0: block type
          tuple.1: conditional
          tuple.2: always active
          tuple.3: needs redstone
          tuple.4: tick delay
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

        return (
            pending_block_type,
            pending_conditional,
            pending_always_active,
            pending_needs_redstone,
            pending_tick_delay,
        )

    def _parse_state_strictly(self, state_str: str, line_no: int, state_start_col: int) -> Optional[tuple[BlockType, bool, bool, bool, int]]:
        """
        接受状态str并进行严格解析, 解析失败返回None.
        @return:
          tuple.0: block type
          tuple.1: conditional
          tuple.2: always active
          tuple.3: needs redstone
          tuple.4: tick delay
        """
        def error_at(offset: int, msg: str) -> None:
            col = state_start_col + offset
            end_col = col + 1
            self._report_error(line_no, col, col + 1, msg)

        state_str_len = len(state_str)

        pending_block_type = BlockType.Chain
        pending_conditional = False
        pending_always_active = True
        pending_needs_redstone = False
        pending_tick_delay = 0

        pointer = 0
        # parse block type
        if state_str_len == 0: # <=> state_str_len <= pointer
            return (pending_block_type, pending_conditional, pending_always_active, pending_needs_redstone, pending_tick_delay)

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
            case "?" | "!" | "T":
                pending_block_type = BlockType.Chain
            case _:
                error_at(pointer, "Expected block type ('I', 'R' or 'C'), or to ignore it ('_')")
                return None

        # parse conditional
        if state_str_len <= pointer:
            return (pending_block_type, pending_conditional, pending_always_active, pending_needs_redstone, pending_tick_delay)

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
                    error_at(pointer, "Expected the conditional comment ('?'), or to ignore it ('_')")
                    return None

        # parse always_active / needs redstone
        if state_str_len <= pointer:
            return (pending_block_type, pending_conditional, pending_always_active, pending_needs_redstone, pending_tick_delay)

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
                    error_at(pointer, "Expected the needs redstone comment ('!'), or to ignore it ('_')")
                    return None

        # parse tick delay
        if state_str_len <= pointer:
            return (pending_block_type, pending_conditional, pending_always_active, pending_needs_redstone, pending_tick_delay)

        c = state_str[pointer]
        if c.lower() != "t":
            error_at(pointer, "Expected the delay tick comment ('t')")
            return None
        pointer += 1

        if state_str_len <= pointer:
            error_at(pointer - 1, f"Expected the delay tick after '{c}'")
            return None

        if state_str[pointer] == "_":
            return (pending_block_type, pending_conditional, pending_always_active, pending_needs_redstone, pending_tick_delay)

        start_pointer = pointer
        while state_str_len > pointer:
            c = state_str[pointer]
            if not ('0' <= c <= '9'):
                error_at(pointer, f"Expected a integer, found a non-digit character: {c}")
                return None
            pointer += 1

        pending_tick_delay = int(state_str[start_pointer:pointer])
        return (pending_block_type, pending_conditional, pending_always_active, pending_needs_redstone, pending_tick_delay)

    def _report(self, line_no: int, start_char: int, end_char: int, message: str) -> bool:
        if self.strict_mode:
            self._report_error(line_no, start_char, end_char, message)
            return True
        if self.enable_warning:
            self._report_warning(line_no, start_char, end_char, message)
        return False

    def _report_warning(self, line_no: int, start_char: int, end_char: int, message: str) -> None:
        if not self.enable_warning:
            return
        self.reporter.print_warning_with_context(
            lines = self.lines,
            line_no = line_no,
            start_char = start_char,
            end_char = end_char,
            message = message,
            # file_name = self.file_name
        )

    def _report_error(self, line_no: int, start_char: int, end_char: int, message: str) -> None:
        self.reporter.print_error_with_context(
            lines = self.lines,
            line_no = line_no,
            start_char = start_char,
            end_char = end_char,
            message = message,
            # file_name = self.file_name
        )
