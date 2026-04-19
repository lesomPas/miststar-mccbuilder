import sys
from wcwidth import wcwidth
from typing import Type

# 孩子们这一部分AI代劳了
# ---------- ANSI 颜色与样式 ----------
RESET = "\033[0m"
RED = "\033[31m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
CYAN = "\033[36m"
GRAY = "\033[90m"

BOLD = "\033[1m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"

# 组合样式
ERROR_STYLE = BOLD + RED          # 错误标签：红+粗
WARNING_STYLE = BOLD + YELLOW     # 警告标签：黄+粗
NOTE_STYLE = ITALIC + GRAY        # note: 斜体灰
LINE_NUM_STYLE = CYAN             # 行号：青色
CARET_STYLE = BOLD + RED + UNDERLINE  # ^ 标记：红+粗+下划线

def _supports_color() -> bool:
    """ 检测终端是否支持颜色（非 TTY 或 Windows 旧版可禁用） """
    if not hasattr(sys.stdout, "isatty"):
        return False
    if not sys.stdout.isatty():
        return False
    return True

COLOR_ENABLED = _supports_color()

def _style(text: str, code: str) -> str:
    """ 应用 ANSI 样式，若颜色禁用则返回原文本 """
    if COLOR_ENABLED:
        return f"{code}{text}{RESET}"
    return text

# ---------- 显示宽度计算 ----------
def display_width_with_tabs(s: str, tab_width: int = 4) -> int:
    """ 计算字符串在终端中的显示宽度，正确处理制表符和宽字符 """
    width = 0
    for ch in s:
        if ch == '\t':
            width = ((width // tab_width) + 1) * tab_width
        else:
            w = wcwidth(ch)
            if w > 0:
                width += w
    return width

class Reporter:
    """
    错误/警告收集器，支持延迟抛出异常

    收集解析过程中的多个错误和警告，最后统一输出并决定是否抛出异常
    """

    def __init__(self) -> None:
        self.warnings = []   # 存储格式化的警告信息（字符串）
        self.errors = []     # 存储格式化的错误信息（字符串）

    def print_error_with_context(
        self,
        lines: list[str],
        line_no: int,
        start_char: int,
        end_char: int,
        message: str,
        context_lines: int = 2,
        tab_width: int = 4,
        file_name: str = "<input>"
    ) -> None:
        """ 生成带上下文代码片段的错误信息，并添加到 errors 列表 """
        error_lines = []
        # 边界检查
        if line_no < 1 or line_no > len(lines):
            error_lines.append(f"{file_name}: error: line {line_no} out of range")
            self.errors.append('\n'.join(error_lines))
            return

        error_line = lines[line_no - 1]
        if start_char < 0 or end_char > len(error_line) or start_char > end_char:
            error_lines.append(f"{file_name}: error: invalid character range")
            self.errors.append('\n'.join(error_lines))
            return

        # 计算显示列（1-indexed）
        prefix = error_line[:start_char]
        target = error_line[start_char:end_char]
        start_col = display_width_with_tabs(prefix, tab_width) + 1
        end_col = start_col + display_width_with_tabs(target, tab_width) - 1
        if end_col < start_col:
            end_col = start_col

        # 上下文行范围
        start_idx = max(0, line_no - 1 - context_lines)
        end_idx = min(len(lines), line_no + context_lines)
        max_line_num_width = len(str(end_idx))

        # 错误头：文件:行:列 错误标签 消息
        loc = f"{file_name}:{line_no}:{start_col}"
        error_lines.append(f"{_style(loc, BLUE)} {_style('error:', ERROR_STYLE)} {message}")

        # 输出上下文代码行
        for i in range(start_idx, end_idx):
            current_line_num = i + 1
            raw_line = lines[i]
            displayed_line = raw_line.expandtabs(tab_width)
            line_num_str = f"{current_line_num:>{max_line_num_width}}"
            error_lines.append(f"{_style(line_num_str, LINE_NUM_STYLE)} | {displayed_line}")

            if current_line_num == line_no:
                indent = start_col - 1
                caret_len = max(1, end_col - start_col + 1)
                caret_line = f"{' ' * (max_line_num_width + 3)}{' ' * indent}{'^' * caret_len}"
                error_lines.append(_style(caret_line, CARET_STYLE))

        # 附加 note 信息
        error_lines.append(_style(f"note: {message}", NOTE_STYLE) + "\n")
        self.errors.append('\n'.join(error_lines))

    def print_warning_with_context(
        self,
        lines: list[str],
        line_no: int,
        start_char: int,
        end_char: int,
        message: str,
        context_lines: int = 2,
        tab_width: int = 4,
        file_name: str = "<input>"
    ) -> None:
        """ 生成带上下文代码片段的警告信息，并添加到 warnings 列表 """
        warning_lines = []
        if line_no < 1 or line_no > len(lines):
            warning_lines.append(f"{file_name}: warning: line {line_no} out of range")
            self.warnings.append('\n'.join(warning_lines))
            return

        warning_line = lines[line_no - 1]
        if start_char < 0 or end_char > len(warning_line) or start_char > end_char:
            warning_lines.append(f"{file_name}: warning: invalid character range")
            self.warnings.append('\n'.join(warning_lines))
            return

        prefix = warning_line[:start_char]
        target = warning_line[start_char:end_char]
        start_col = display_width_with_tabs(prefix, tab_width) + 1
        end_col = start_col + display_width_with_tabs(target, tab_width) - 1
        if end_col < start_col:
            end_col = start_col

        start_idx = max(0, line_no - 1 - context_lines)
        end_idx = min(len(lines), line_no + context_lines)
        max_line_num_width = len(str(end_idx))

        loc = f"{file_name}:{line_no}:{start_col}"
        warning_lines.append(f"{_style(loc, BLUE)} {_style('warning:', WARNING_STYLE)} {message}")

        for i in range(start_idx, end_idx):
            current_line_num = i + 1
            raw_line = lines[i]
            displayed_line = raw_line.expandtabs(tab_width)
            line_num_str = f"{current_line_num:>{max_line_num_width}}"
            warning_lines.append(f"{_style(line_num_str, LINE_NUM_STYLE)} | {displayed_line}")

            if current_line_num == line_no:
                indent = start_col - 1
                caret_len = max(1, end_col - start_col + 1)
                caret_line = f"{' ' * (max_line_num_width + 3)}{' ' * indent}{'^' * caret_len}"
                warning_lines.append(_style(caret_line, CARET_STYLE))

        warning_lines.append(_style(f"note: {message}", NOTE_STYLE) + "\n")
        self.warnings.append('\n'.join(warning_lines))

    def print_error_line(
        self,
        lines: list[str],
        line_no: int,
        message: str,
        context_lines: int = 2,
        tab_width: int = 4,
        file_name: str = "<input>"
    ) -> None:
        """生成只关联行号的错误信息（无下划线标记），并添加到 errors 列表。"""
        error_lines = []
        if line_no < 1 or line_no > len(lines):
            error_lines.append(f"{file_name}: error: line {line_no} out of range")
            self.errors.append('\n'.join(error_lines))
            return

        start_idx = max(0, line_no - 1 - context_lines)
        end_idx = min(len(lines), line_no + context_lines)
        max_line_num_width = len(str(end_idx))

        loc = f"{file_name}:{line_no}"
        error_lines.append(f"{_style(loc, BLUE)} {_style('error:', ERROR_STYLE)} {message}")

        for i in range(start_idx, end_idx):
            current_line_num = i + 1
            raw_line = lines[i]
            displayed_line = raw_line.expandtabs(tab_width)
            line_num_str = f"{current_line_num:>{max_line_num_width}}"
            error_lines.append(f"{_style(line_num_str, LINE_NUM_STYLE)} | {displayed_line}")

        error_lines.append(_style(f"note: {message}", NOTE_STYLE) + "\n")
        self.errors.append('\n'.join(error_lines))

    def print_warning_line(
        self,
        lines: list[str],
        line_no: int,
        message: str,
        context_lines: int = 2,
        tab_width: int = 4,
        file_name: str = "<input>"
    ) -> None:
        """生成只关联行号的警告信息（无下划线标记），并添加到 warnings 列表。"""
        warning_lines = []
        if line_no < 1 or line_no > len(lines):
            warning_lines.append(f"{file_name}: warning: line {line_no} out of range")
            self.warnings.append('\n'.join(warning_lines))
            return

        start_idx = max(0, line_no - 1 - context_lines)
        end_idx = min(len(lines), line_no + context_lines)
        max_line_num_width = len(str(end_idx))

        loc = f"{file_name}:{line_no}"
        warning_lines.append(f"{_style(loc, BLUE)} {_style('warning:', WARNING_STYLE)} {message}")

        for i in range(start_idx, end_idx):
            current_line_num = i + 1
            raw_line = lines[i]
            displayed_line = raw_line.expandtabs(tab_width)
            line_num_str = f"{current_line_num:>{max_line_num_width}}"
            warning_lines.append(f"{_style(line_num_str, LINE_NUM_STYLE)} | {displayed_line}")

        warning_lines.append(_style(f"note: {message}", NOTE_STYLE) + "\n")
        self.warnings.append('\n'.join(warning_lines))

    def print_error_lines(
        self,
        lines: list[str],
        start_line: int,
        end_line: int,
        message: str,
        tab_width: int = 4,
        file_name: str = "<input>"
    ) -> None:
        """报告一个连续行范围的错误（无高亮标记）。"""
        error_lines = []
        if start_line < 1 or end_line > len(lines) or start_line > end_line:
            error_lines.append(f"{file_name}: error: invalid line range {start_line}-{end_line}")
            self.errors.append('\n'.join(error_lines))
            return

        start_idx = max(0, start_line - 1)
        end_idx = min(len(lines), end_line)   # 不包含
        max_line_num_width = len(str(end_idx))

        loc = f"{file_name}:{start_line}-{end_line}"
        error_lines.append(f"{_style(loc, BLUE)} {_style('error:', ERROR_STYLE)} {message}")

        for i in range(start_idx, end_idx):
            current_line_num = i + 1
            raw_line = lines[i]
            displayed_line = raw_line.expandtabs(tab_width)
            line_num_str = f"{current_line_num:>{max_line_num_width}}"
            error_lines.append(f"{_style(line_num_str, LINE_NUM_STYLE)} | {displayed_line}")

        error_lines.append(_style(f"note: {message}", NOTE_STYLE) + "\n")
        self.errors.append('\n'.join(error_lines))

    def print_warning_lines(
        self,
        lines: list[str],
        start_line: int,
        end_line: int,
        message: str,
        tab_width: int = 4,
        file_name: str = "<input>"
    ) -> None:
        """报告一个连续行范围的警告（无高亮标记）。"""
        warning_lines = []
        if start_line < 1 or end_line > len(lines) or start_line > end_line:
            warning_lines.append(f"{file_name}: warning: invalid line range {start_line}-{end_line}")
            self.warnings.append('\n'.join(warning_lines))
            return

        start_idx = max(0, start_line - 1)
        end_idx = min(len(lines), end_line)
        max_line_num_width = len(str(end_idx))

        loc = f"{file_name}:{start_line}-{end_line}"
        warning_lines.append(f"{_style(loc, BLUE)} {_style('warning:', WARNING_STYLE)} {message}")

        for i in range(start_idx, end_idx):
            current_line_num = i + 1
            raw_line = lines[i]
            displayed_line = raw_line.expandtabs(tab_width)
            line_num_str = f"{current_line_num:>{max_line_num_width}}"
            warning_lines.append(f"{_style(line_num_str, LINE_NUM_STYLE)} | {displayed_line}")

        warning_lines.append(_style(f"note: {message}", NOTE_STYLE) + "\n")
        self.warnings.append('\n'.join(warning_lines))

    def done(self, exception: Type[Exception]) -> None:
        """
        结束收集：打印所有警告到 stderr，如果有错误则抛出异常
        @parameter:
          exception: 当存在错误时抛出的异常类（如 MCDParsingException）
        """
        # 所有警告输出到标准错误流
        for warn in self.warnings:
            print(warn, file=sys.stderr)

        # 如果有错误，拼接所有错误信息后抛出异常（也输出到 stderr）
        if self.errors:
            raise exception('\n' + '\n'.join(self.errors))

    def reset(self) -> None:
        self.warnings.clear()
        self.errors.clear()