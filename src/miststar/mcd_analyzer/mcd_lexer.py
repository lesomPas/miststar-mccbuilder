# created by lesomras on 2026-7-28

from enum import Enum
from typing import NamedTuple, Protocol
from collections.abc import Iterable


class DocumentTokenKind(Enum):
    # mcd_version = 1
    # mcd_version = 2
    Label = "DocumentTokenKind.Label"

    # mcd_version = 1
    # mcd_version = 2
    Comment = "DocumentTokenKind.Comment"

    # mcd_version = 1
    # mcd_version = 2
    UnmatchLine = "DocumentTokenKind.UnmatchLine"

    # mcd_version = 1
    # mcd_version = 2
    Meta = "DocumentTokenKind.Meta"

    # mcd_version = 1
    TextCommand = "DocumentTokenKind.TextCommand"

    # mcd_version = 2
    ChainLabel = "DocumentTokenKind.ChainLabel"

    # mcd_version = 2
    State = "DocumentTokenKind.State"

    # mcd_version = 2
    MarkedCommand = "DocumentTokenKind.MarkedCommand"


class DocumentToken(NamedTuple):
    kind: DocumentTokenKind
    data: str
    extra_data: str = ""


class DocumentLexer(Protocol):
    def tokenize(self, document: str) -> Iterable[DocumentToken]:
        ...


class MCDLexerV1(DocumentLexer):
    def tokenize(self, document: str) -> Iterable[DocumentToken]:
        for line in document.splitlines():
            line = line.strip()
            if not line:
                continue

            # Label ###Function### || ###End###
            if line.startswith("###") and line.endswith("###") and len(line) >= 6:
                yield DocumentToken(
                    kind=DocumentTokenKind.Label,
                    data=line[3:-3].strip()
                )

            # Comment
            elif line.startswith("#"):
                yield DocumentToken(
                    kind=DocumentTokenKind.Comment,
                    data=line[1:].lstrip()
                )

            # Meta
            elif line.startswith("@") and (eq_index := line.find("=")) != -1:
                key = line[1:eq_index].strip()
                value = line[eq_index+1:].strip()
                yield DocumentToken(
                    kind=DocumentTokenKind.Meta,
                    data=key,
                    extra_data=value,
                )

            # TextCommand (v1)
            elif line.startswith("/") or is_ascii_alphabetic(line[0]):
                yield DocumentToken(
                    kind=DocumentTokenKind.TextCommand,
                    data=line
                )
            # UnmatchLine
            else:
                yield DocumentToken(
                    kind=DocumentTokenKind.UnmatchLine,
                    data=line
                )


class MCDLexerV2(DocumentLexer):
    def tokenize(self, document: str) -> Iterable[DocumentToken]:
        for line in document.splitlines():
            line = line.strip()
            if not line:
                continue

            # Label ###Function### || ###End###
            if line.startswith("###") and line.endswith("###") and len(line) >= 6:
                yield DocumentToken(
                    kind=DocumentTokenKind.Label,
                    data=line[3:-3].strip()
                )

            # ChainLabel ---Chain N---
            elif line.startswith("---") and line.endswith("---") and len(line) >= 6:
                yield DocumentToken(
                    kind=DocumentTokenKind.ChainLabel,
                    data=line[3:-3].strip()
                )

            # Comment
            elif line.startswith("#"):
                yield DocumentToken(
                    kind=DocumentTokenKind.Comment,
                    data=line[1:].lstrip()
                )

            # State > state
            elif line.startswith(">"):
                yield DocumentToken(
                    kind=DocumentTokenKind.State,
                    data=line[1:].lstrip()
                )

            # Meta
            elif line.startswith("@") and (eq_index := line.find("=")) != -1:
                key = line[1:eq_index].strip()
                value = line[eq_index+1:].strip()
                yield DocumentToken(
                    kind=DocumentTokenKind.Meta,
                    data=key,
                    extra_data=value,
                )

            # MarkedCommand (v2)
            elif line.startswith("/") or is_ascii_alphabetic(line[0]):
                yield DocumentToken(
                    kind=DocumentTokenKind.MarkedCommand,
                    data=line
                )
            # UnmatchLine
            else:
                yield DocumentToken(
                    kind=DocumentTokenKind.UnmatchLine,
                    data=line
                )


def is_ascii_alphabetic(c) -> bool:
    """c: char (str)"""
    return ('a' <= c <= 'z') or ('A' <= c <= 'Z')
