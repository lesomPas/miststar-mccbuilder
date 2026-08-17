# create by lesomras on 2026-4-12
from __future__ import annotations

from typing import Literal

from dataclasses import dataclass, field
from enum import Enum

# 感谢lans开源!

class BlockKind(Enum):
    Impulse = "BlockKind.Impulse"  # 脉冲
    Chain = "BlockKind.Chain"      # 连锁
    Repeat = "BlockKind.Repeat"    # 循环
    Chat = "BlockKind.Chat"        # 手动输入


@dataclass(slots=True)
class MCDMeta:
    """ 元数据行，例如 @author = xxx """
    key: str
    value: str


@dataclass(slots=True)
class CommandState:
    """ v2 格式的命令方块，携带方块类型和状态信息 """
    kind: BlockKind = BlockKind.Chain
    conditional: bool = False
    always_active: bool = True
    tick_delay: int = 0

    def derive(self) -> tuple[BlockKind, bool, bool, int]:
        return (self.kind, self.conditional, self.always_active, self.tick_delay)


class ChainItem:
    """ 链中的一个元素：可能是注释、v1 原始指令、或 v2 命令方块 """
    Comment: type["Comment"]
    TextCommand: type["TextCommand"]
    MarkedCommand: type["MarkedCommand"]


@dataclass(slots=True)
class Comment(ChainItem):
    text: str


@dataclass(slots=True)
class TextCommand(ChainItem):
    command: str


@dataclass(slots=True)
class MarkedCommand(ChainItem):
    command: str
    state: CommandState


ChainItem.Comment = Comment
ChainItem.TextCommand = TextCommand
ChainItem.MarkedCommand = MarkedCommand


@dataclass(slots=True)
class MCDChain:
    """ 一条命令链 """
    name: str
    items: list[ChainItem] = field(default_factory=list)


@dataclass(slots=True)
class MCD:
    """ 解析后的完整 MCD 结构 """
    meta_info: list[MCDMeta] = field(default_factory=list)
    chains: list[MCDChain] = field(default_factory=list)
    version: Literal[1, 2] = 1

    @classmethod
    def create(cls, mcd_version: Literal[1, 2]) -> MCD:
        if mcd_version == 1:
            return cls(
                chains = [MCDChain(name="分离的命令")],
                version = mcd_version,
            )
        if mcd_version == 2:
            return cls(version=2)
