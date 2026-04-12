import sys
from wcwidth import wcwidth

def display_width_with_tabs(s: str, tab_width: int = 4) -> int:
    width = 0
    for ch in s:
        if ch == '\t':
            width = ((width // tab_width) + 1) * tab_width
        else:
            w = wcwidth(ch)
            if w > 0:
                width += w
    return width

def print_error_with_context(
    lines: list[str],
    line_no: int,
    start_char: int,
    end_char: int,
    message: str,
    context_lines: int = 2,
    tab_width: int = 4,
    file_name: str = "<input>"
) -> None:
    # lines = source.splitlines()
    if line_no < 1 or line_no > len(lines):
        print(f"{file_name}: error: line {line_no} out of range", file=sys.stderr)
        return

    error_line = lines[line_no - 1]
    if start_char < 0 or end_char > len(error_line) or start_char > end_char:
        print(f"{file_name}: error: invalid character range", file=sys.stderr)
        return

    prefix = error_line[:start_char]
    target = error_line[start_char:end_char]
    start_col = display_width_with_tabs(prefix, tab_width) + 1
    end_col = start_col + display_width_with_tabs(target, tab_width) - 1
    if end_col < start_col:
        end_col = start_col

    start_idx = max(0, line_no - 1 - context_lines)
    end_idx = min(len(lines), line_no + context_lines)
    max_line_num_width = len(str(end_idx))

    print(f"{file_name}:{line_no}:{start_col}: error: {message}")

    for i in range(start_idx, end_idx):
        current_line_num = i + 1
        raw_line = lines[i]
        displayed_line = raw_line.expandtabs(tab_width)
        print(f"{current_line_num:>{max_line_num_width}} | {displayed_line}")

        if current_line_num == line_no:
            indent = start_col - 1
            caret_len = max(1, end_col - start_col + 1)
            print(f"{' ' * (max_line_num_width + 3)}{' ' * indent}{'^' * caret_len}")

    print(f"note: {message}\n")


def print_warning_with_context(
    lines: list[str],
    line_no: int,
    start_char: int,
    end_char: int,
    message: str,
    context_lines: int = 2,
    tab_width: int = 4,
    file_name: str = "<input>"
) -> None:
    if line_no < 1 or line_no > len(lines):
        print(f"{file_name}: warning: line {line_no} out of range", file=sys.stderr)
        return

    warning_line = lines[line_no - 1]
    if start_char < 0 or end_char > len(warning_line) or start_char > end_char:
        print(f"{file_name}: warning: invalid character range", file=sys.stderr)
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

    print(f"{file_name}:{line_no}:{start_col}: warning: {message}")

    for i in range(start_idx, end_idx):
        current_line_num = i + 1
        raw_line = lines[i]
        displayed_line = raw_line.expandtabs(tab_width)
        print(f"{current_line_num:>{max_line_num_width}} | {displayed_line}")

        if current_line_num == line_no:
            indent = start_col - 1
            caret_len = max(1, end_col - start_col + 1)
            print(f"{' ' * (max_line_num_width + 3)}{' ' * indent}{'^' * caret_len}")

    print(f"note: {message}\n")

