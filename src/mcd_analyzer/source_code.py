from typing import NamedTuple

class Line(NamedTuple):
    ln: int
    original_content: str
    content: str
    start_ptr: int
    end_ptr: int

    def relative_range(self, left_offset: int, right_offset: int) -> tuple[int, int]:
        return (self.start_ptr + left_offset, self.end_ptr - right_offset + 1)

    def left_relative_range(self, left_offset: int, right_ptr: int) -> tuple[int, int]:
        return (self.start_ptr + left_offset, right_ptr + 1)

    def left_relative_len_range(self, left_offset: int, length) -> tuple[int, int]:
        left = self.start_ptr + left_offset
        return (left, left + length)

    def absolute_range(self, left_ptr: int, right_ptr: int) -> tuple[int, int]:
        return (left_ptr, right_ptr + 1)

class SourceCode(object):
    def __init__(self, code: str) -> None:
        self.code = code
        self.original_lines = code.splitlines()
        self.lines: list[Line] = []
        self.parse_lines()

    def parse_lines(self) -> None:
        for ln, content in enumerate(self.original_lines, start = 1):
            if not content:
                continue

            l_content = content.lstrip()
            start_ptr = len(content) - len(l_content)
            lr_content = l_content.rstrip()
            end_ptr = start_ptr + len(lr_content) - 1 # 包括最后一个字符

            if not lr_content:
                continue

            self.lines.append(Line(ln, content, lr_content, start_ptr, end_ptr))
