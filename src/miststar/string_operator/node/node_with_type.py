# create by lesomras on 2026-1-1
from enum import Enum
from typing import Optional

class NodeTypeId(Enum):
    Wrapped = 0            # 封装节点
    Block = 1              # 方块
    Boolean = 2            # 布尓值
    Command = 3            # 命令
    CommandName = 4        # 命令名
    Float = 5              # 小数
    Integer = 6            # 整数
    IntegerWithUnit = 7    # 带单位的整数
    Item = 8               # 物品
    LF = 9                 # 结束节点
    NamespaceId = 10       # 带命名空间的id
    NormalId = 11          # 普通id
    PreCommand = 12        # 每条命令
    Position = 13          # 位置
    RelativeFloat = 14     # 相对坐标
    Repeat = 15            # 重复的参数
    String = 16            # 字符串
    TargetSelector = 17    # 目标选择器
    Text = 18              # 文字
    Range = 19             # 范围
    Json = 20              # Json文本
    JsonBoolean = 21       # Json布尔值
    JsonElement = 22       # Json元素
    JsonEntry = 23         # Json键值对
    JsonFloat = 24         # Json小数
    JsonInteger = 25       # Json整数
    JsonList = 26          # Json列表
    JsonNull = 27          # Json空值
    JsonObject = 28        # Json对象
    JsonString = 29        # Json字符串
    And = 30               # 和节点
    Any = 31               # 任何节点
    Entry = 32             # 键值对
    EqualEntry = 33        # 可以是不等号的键值对
    List = 34              # 数组
    Or = 35                # 或节点
    SingleSymbol = 36      # 单个字符
    Optional = 37          # 可选节点

class NodeBase(object):
    pass

class NodeWithType(object):
    def __init__(self) -> None:
        self.node_type_id: Optional[NodeTypeId] = None
        self.data: Optional[NodeBase] = None

class FreeableNodeWithTypes(object):
    def __init__(self) -> None:
        self.nodes: list[NodeWithType] = []