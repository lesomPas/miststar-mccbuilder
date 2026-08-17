# created by lesomras on 2026-8-6
from __future__ import annotations

from typing import Literal, Optional

from .exceptions import MCDBuilderException
from .mcd import MCD, MCDChain, MCDMeta, ChainItem, CommandState, BlockKind


class MCDBuilder:
    __slots__ = ("mcd", "mcd_version")

    def __init__(self, mcd_version: Literal[1, 2], mcd: Optional[MCD] = None):
        if mcd is not None and mcd.version != mcd_version:
            raise MCDBuilderException(
                f"Version mismatch: expected v{mcd_version}, "
                f"but provided MCD is v{mcd.version}"
            )

        self.mcd = MCD.create(mcd_version) if mcd is None else mcd
        self.mcd_version: Literal[1, 2] = mcd_version

    @property
    def last_chain(self) -> MCDChain:
        try:
            return self.mcd.chains[-1]
        except IndexError as e:
            raise MCDBuilderException(
                "No chain available: call add_chain() or build_chain() first"
            ) from e

    def add_chain(self, chain_name: str) -> MCDBuilder:
        if self.mcd_version != 2:
            raise MCDBuilderException(
                "add_chain() is only available in MCD v2"
            )

        self.mcd.chains.append(MCDChain(name=chain_name))
        return self

    def add_meta(self, key: str, value: str) -> MCDBuilder:
        self.mcd.meta_info.append(MCDMeta(key=key, value=value))
        return self

    def add_comment(self, comment: str) -> MCDBuilder:
        self.last_chain.items.append(ChainItem.Comment(text=comment))
        return self

    def add_text_command(self, text_command: str) -> MCDBuilder:
        if self.mcd_version != 1:
            raise MCDBuilderException(
                "add_text_command() is only available in MCD v1; "
                "use add_marked_command() for v2"
            )

        self.last_chain.items.append(ChainItem.TextCommand(command=text_command))
        return self

    def add_marked_command(
        self,
        marked_command: str,
        kind: BlockKind = BlockKind.Chain,
        conditional: bool = False,
        always_active: bool = True,
        tick_delay: int = 0,
    ) -> MCDBuilder:
        if self.mcd_version != 2:
            raise MCDBuilderException(
                "add_marked_command() is only available in MCD v2; "
                "use add_text_command() for v1"
            )

        self.last_chain.items.append(ChainItem.MarkedCommand(
            command = marked_command,
            state = CommandState(
                kind = kind,
                conditional = conditional,
                always_active = always_active,
                tick_delay = tick_delay,
            )
        ))
        return self

    def build_chain(self, chain_name: str, index: int = -1) -> ChainBuilder:
        if self.mcd_version != 2:
            raise MCDBuilderException(
                "build_chain() is only available in MCD v2"
            )
        if index == -1:
            sequence = []
        else:
            sequence = self.mcd.chains[index].items

        self.mcd.chains.append(MCDChain(name=chain_name, items=sequence))
        return ChainBuilder(self.mcd_version, sequence)

    def end(self) -> MCD:
        return self.mcd


class ChainBuilder:
    def __init__(self, mcd_version: Literal[1, 2], items: list[ChainItem]):
        self.items = items
        self.mcd_version = mcd_version

    def add_comment(self, comment: str) -> ChainBuilder:
        self.items.append(ChainItem.Comment(text=comment))
        return self

    def add_text_command(self, text_command: str) -> ChainBuilder:
        if self.mcd_version != 1:
            raise MCDBuilderException(
                "add_text_command() is only available in MCD v1"
            )

        self.items.append(ChainItem.TextCommand(command=text_command))
        return self

    def add_marked_command(
        self,
        marked_command: str,
        kind: BlockKind = BlockKind.Chain,
        conditional: bool = False,
        always_active: bool = True,
        tick_delay: int = 0,
    ) -> ChainBuilder:
        if self.mcd_version != 2:
            raise MCDBuilderException(
                "add_marked_command() is only available in MCD v2"
            )

        self.items.append(ChainItem.MarkedCommand(
            command = marked_command,
            state = CommandState(
                kind = kind,
                conditional = conditional,
                always_active = always_active,
                tick_delay = tick_delay,
            )
        ))
        return self
