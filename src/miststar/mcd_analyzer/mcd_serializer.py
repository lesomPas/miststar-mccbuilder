# create by lesomras on 2026-4-12
import json
from typing import Optional, Union, Any

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
from .mcd_parser import MCDParser
from .exceptions import MCDFormatException, MCDVersionException, MCDLoadingException

class MCDEncoder(json.JSONEncoder):
    """ MCD数据类及枚举序列化为JSON格式 """
    def default(self, o: Any) -> Any:
        if isinstance(o, BlockType):
            return o.name.lower()
        if isinstance(o, MCDMeta):
            return { "key": o.key, "value": o.value, }
        if isinstance(o, MCDBlock):
            if o.type == BlockType.CommandLine:
                return {
                    "type": o.type.name.lower(),
                    "command": o.command,
                }
            return {
                "type": o.type.name.lower(),
                "conditional": o.conditional,
                "alwaysActive": o.always_active,
                "needsRedstone": o.needs_redstone,
                "tickDelay": o.tick_delay,
                "command": o.command,
            }
        if isinstance(o, ChainItemComment):
            return { "comment": o.text, }
        if isinstance(o, ChainItemRawCommand):
            return { "rawCommand": o.command, }
        if isinstance(o, ChainItemBlock):
            return o.block
        if isinstance(o, MCDChain):
            return { "name": o.name, "blocks": o.items, }
        if isinstance(o, MCD):
            return {
                "meta": o.meta_info,
                "rootComments": o.root_comments,
                "chains": o.chains,
                "isV2": o.is_v2,
            }
        return super().default(o)


def mcd_decoder_hook(dct: dict) -> Any:
    """ 用于json.loads的object_hook """
    # 1. 判断是否为 ChainItemComment
    if "comment" in dct and len(dct) == 1:
        return ChainItemComment(text = dct["comment"])
    # 2. 判断是否为 ChainItemRawCommand
    if "rawCommand" in dct and len(dct) == 1:
        return ChainItemRawCommand(command = dct["rawCommand"])
    # 3. 判断是否为 MCDBlock（同时也是 ChainItemBlock）
    if "type" in dct and "command" in dct and set(dct.keys()) <= {"type", "conditional", "alwaysActive", "needsRedstone", "tickDelay", "command"}:
        type_str = dct["type"].upper()
        try:
            block_type = BlockType[type_str]
        except KeyError:
            block_type = BlockType.Chain
        block = MCDBlock(
            type=block_type,
            conditional = dct.get("conditional", False),
            always_active = dct.get("alwaysActive", True),
            needs_redstone = dct.get("needsRedstone", False),
            tick_delay = dct.get("tickDelay", 0),
            command = dct.get("command", ""),
        )
        return ChainItemBlock(block=block)
    # 4. 判断是否为 MCDChain
    if "name" in dct and "blocks" in dct and set(dct.keys()) <= {"name", "blocks"}:
        return MCDChain(name = dct["name"], items = dct["blocks"])
    # 5. 判断是否为 MCD 顶层对象
    if "meta" in dct and "chains" in dct and "isV2" in dct:
        return MCD(
            meta_info = [MCDMeta(key=m["key"], value=m["value"]) for m in dct["meta"]],
            root_comments = dct.get("rootComments", []),
            chains = dct['chains'],
            is_v2 = dct["isV2"],
        )
    return dct


class MCDSerializer:
    def __init__(self, full_state_string: bool = True) -> None:
        self.full_state_string = full_state_string

    def load_string_document(
        self,
        document: str,
        version: Optional[int] = None,
        enable_warning: bool = True,
        strict_mode: bool = True,
        relaxed: bool = True,
    ) -> MCD:
        """ 将字符串转换为MCD """
        parser = MCDParser(
            document = document,
            enable_warning = enable_warning,
            strict_mode = strict_mode,
            relaxed = relaxed,
        )
        match version:
            case None: return parser.parse()
            case 1: return parser.parse_v1()
            case 2: return parser.parse_v2()
            case _:
                raise MCDVersionException(f"Invalid MCD version: {version}, excepted 1 or 2")

    def dump_string(self, mcd: MCD) -> str:
        """ 转化为字符串形式 """
        output_lines = []

        for info in mcd.meta_info:
            output_lines.append(f"@{info.key}={info.value}")
        output_lines.append("\n###Function###")

        for root_comment in mcd.root_comments:
            output_lines.append(f"# {root_comment}")

        if not mcd.is_v2:
            if len(mcd.chains) != 1:
                raise MCDFormatException("In MCD v1, the length of mcd.chains must be 1")

            chain = mcd.chains[0]
            output_lines.append("")
            for item in chain.items:
                match item:
                    case ChainItemComment(text = text):
                        output_lines.append(f"# {text}")
                    case ChainItemRawCommand(command = command):
                        output_lines.append(f"{command}")
                    case _:
                        raise MCDFormatException(f"Excepted ChainItemComment or ChainItemRawCommand, got {type(item).__name__}")
            output_lines.append("###End###")
            return '\n'.join(output_lines)

        for chain in mcd.chains:
            output_lines.append(f"\n---{chain.name}---")
            for item in chain.items:
                match item:
                    case ChainItemComment(text = text):
                        output_lines.append(f"# {text}")
                    case ChainItemBlock(block = block):
                        state_str = ""
                        if self.full_state_string or block.type != BlockType.Chain:
                            match block.type:
                                case BlockType.Chain: state_str += 'C' # 一般来说方块类型不会使用省略符'_', 太不直观了
                                case BlockType.Repeat: state_str += 'R'
                                case BlockType.Impulse: state_str += 'I'
                                case BlockType.CommandLine:
                                    output_lines.append(f"> H")
                                    output_lines.append(f"{block.command}")
                                    continue

                        if self.full_state_string or block.conditional:
                            state_str += '?' if block.conditional else '_'

                        if self.full_state_string or block.needs_redstone:
                            state_str += '!' if block.needs_redstone else '_'

                        if self.full_state_string or block.tick_delay != 0:
                            state_str += f"t{block.tick_delay if block.tick_delay != 0 else '_'}"

                        if state_str:
                            output_lines.append(f"> {state_str}")
                        output_lines.append(f"{block.command}")
                    case _:
                        raise MCDFormatException(f"Excepted ChainItemComment or ChainItemBlock, got {type(item).__name__}")

        output_lines.append("###End###")
        return '\n'.join(output_lines)

    def load_json_document(self, data: Union[str, dict]) -> MCD:
        """ 反序列化MCD """
        if isinstance(data, str):
            try:
                obj = json.loads(data, object_hook=mcd_decoder_hook)
            except json.JSONDecodeError as e:
                raise MCDLoadingException(f"Invalid JSON format: {e}")
        else:
            obj = json.loads(json.dumps(data), object_hook=mcd_decoder_hook)
        if not isinstance(obj, MCD):
            raise MCDLoadingException(f"Invalid data type: {type(obj).__name__}")
        return obj

    def dump_json(self, mcd: MCD, indent: int = 2, ensure_ascii: bool = False) -> str:
        """ 序列化为JSON字符串 """
        return json.dumps(mcd, cls=MCDEncoder, indent=indent, ensure_ascii=ensure_ascii)

if __name__ == "__main__":
    serializer = MCDSerializer(full_state_string = True)
    mcd = serializer.load_string_document(document = """
@mcd_version = 2

###Function###
---a---
> t114514

###End###
""", strict_mode = False)

    string = serializer.dump_json(mcd)
    print(mcd)
    print(string)

    mcd2 = serializer.load_json_document(string)
    print(mcd2)