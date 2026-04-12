from dataclasses import dataclass, field
from enum import StrEnum

# 感谢lans开源!

class BlockType(StrEnum):
    Impulse = "脉冲"
    Chain = "连锁"
    Repeat = "循环"

@dataclass
class MCDMeta:
    """ 元数据行，例如 @author = xxx """
    key: str
    value: str

@dataclass
class MCDBlock:
    """ v2 格式的命令方块，携带方块类型和状态信息 """
    type: BlockType = BlockType.Chain
    conditional: bool = False
    always_active: bool = True
    needs_redstone: bool = False
    tick_delay: int = 0
    command: str = ""


# 这个方案好神秘，但我觉得这个可能是最符合原来意思的
class ChainItem:
    """ 链中的一个元素：可能是注释、v1 原始指令、或 v2 命令方块 """
    pass

@dataclass
class ChainItemComment(ChainItem):
    text: str

@dataclass
class ChainItemRawCommand(ChainItem):
    command: str

@dataclass
class ChainItemBlock(ChainItem):
    block: MCDBlock

@dataclass
class MCDChain:
    """ 一条命令链 """
    name: str
    items: list[ChainItem] = field(default_factory=list)

@dataclass
class MCD:
    """ 解析后的完整 MCD 结构 """
    meta_info: list[MCDMeta] = field(default_factory=list)
    root_comments: list[str] = field(default_factory=list)
    chains: list[MCDChain] = field(default_factory=list)
    is_v2: bool = False

