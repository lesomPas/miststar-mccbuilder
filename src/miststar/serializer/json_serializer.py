# create by lesomras on 2025-12-18
import json
from pathlib import Path

from ..internal.exceptions import MalformedArgument

class JsonSerializer(object):
    """JSON序列化器"""

    @staticmethod
    def loads(json_str: str):
        """从JSON字符串加载Python对象"""
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise MalformedArgument(f"无效的JSON: {e}") from e

    @staticmethod
    def load(file_path: str | Path):
        """从文件加载Python对象"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {path}")

        with open(path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError as e:
                raise MalformedArgument(f"文件中的JSON无效: {e}") from e

    @staticmethod
    def dumps(data, indent: int = 2, ensure_ascii: bool = False) -> str:
        """将Python对象序列化为JSON字符串"""
        return json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)

    @staticmethod
    def dump(data, file_path: str | Path, indent: int = 2, ensure_ascii: bool = False) -> None:
        """将Python对象保存到文件"""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)

    @staticmethod
    def is_valid_json(json_str: str) -> bool:
        """检查字符串是否为有效的JSON"""
        try:
            json.loads(json_str)
            return True
        except json.JSONDecodeError:
            return False


class CompactSerializer(object):
    """紧凑序列化器 (无缩进)"""

    @staticmethod
    def loads(json_str: str):
        """从JSON字符串加载Python对象 (与父类相同)"""
        return JsonSerializer.loads(json_str)

    @staticmethod
    def load(file_path: str | Path):
        """从文件加载Python对象 (与父类相同)"""
        return JsonSerializer.load(file_path)

    @staticmethod
    def dumps(data, indent: int = 0, ensure_ascii: bool = False) -> str:
        """将Python对象序列化为紧凑JSON字符串 (indent := 0)"""
        return JsonSerializer.dumps(data, 0, ensure_ascii = ensure_ascii)

    @staticmethod
    def dump(data, file_path: str | Path, indent: int = 0, ensure_ascii: bool = False) -> None:
        """将Python对象保存为紧凑JSON文件 (indent := 0)"""
        JsonSerializer.dump(data, file_path, 0, ensure_ascii = ensure_ascii)


# 快捷函数
def load_json(file_path: str | Path):
    """从文件加载JSON"""
    return JsonSerializer.load(file_path)


def loads_json(json_str: str):
    """从字符串加载JSON"""
    return JsonSerializer.loads(json_str)


def dump_json(data, file_path: str | Path, indent: int = 2, ensure_ascii: bool = False) -> None:
    """保存JSON到文件"""
    JsonSerializer.dump(data, file_path, indent, ensure_ascii)


def dumps_json(data, indent: int = 2, ensure_ascii: bool = False) -> str:
    """序列化JSON到字符串"""
    return JsonSerializer.dumps(data, indent, ensure_ascii)


def dump_json_compact(data, file_path: str | Path, ensure_ascii: bool = False) -> None:
    """保存紧凑JSON到文件"""
    CompactSerializer.dump(data, file_path, ensure_ascii=ensure_ascii)


def dumps_json_compact(data, ensure_ascii: bool = False) -> str:
    """序列化紧凑JSON到字符串"""
    return CompactSerializer.dumps(data, ensure_ascii=ensure_ascii)
