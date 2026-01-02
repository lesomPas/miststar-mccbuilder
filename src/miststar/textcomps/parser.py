# create by lesomras on 2025-12-14

from pathlib import Path
from typing import Union

from .components import rawtext_lexer, Rawtext, TextComponent
from miststar.internal.exceptions import MalformedArgument, UnsupportedArgument
from miststar.serializer import JsonSerializer, CompactSerializer


class Parser:
    """Rawtext专用解析器"""

    @staticmethod
    def parse_file(file_path: Union[str, Path]) -> Rawtext:
        """
        解析JSON文件为Rawtext对象

        Args:
            file_path: 文件路径

        Returns:
            Rawtext对象

        Raises:
            FileNotFoundError: 文件不存在
            MalformedArgument: JSON解析失败或格式错误
        """
        try:
            data = JsonSerializer.load(file_path)
        except FileNotFoundError:
            raise
        except Exception as e:
            raise MalformedArgument(f"Failed to parse file: {e}") from e

        return Parser._parse_data(data)

    @staticmethod
    def parse_string(json_str: str) -> Rawtext:
        """
        解析JSON字符串为Rawtext对象

        Args:
            json_str: JSON格式的字符串

        Returns:
            Rawtext对象

        Raises:
            MalformedArgument: JSON解析失败或格式错误
        """
        try:
            data = JsonSerializer.loads(json_str)
        except Exception as e:
            raise MalformedArgument(f"Failed to parse string: {e}") from e

        return Parser._parse_data(data)

    @staticmethod
    def parse_data(data: dict) -> Rawtext:
        """
        解析字典数据为Rawtext对象

        Args:
            data: 原始字典数据

        Returns:
            Rawtext对象

        Raises:
            MalformedArgument: 数据格式错误
        """
        return Parser._parse_data(data)

    @staticmethod
    def _parse_data(data) -> Rawtext:
        """
        内部解析方法

        Args:
            data: 原始数据

        Returns:
            Rawtext对象

        Raises:
            MalformedArgument: 数据格式错误
        """
        if not isinstance(data, dict):
            raise MalformedArgument("Data must be a dictionary")

        # 检查是否是有效的rawtext格式
        if "rawtext" not in data:
            # 如果不是rawtext格式，尝试包装成rawtext
            # 这允许直接加载单个文本组件
            data = {"rawtext": [data]}

        return Rawtext.from_dictionary(data)

    @staticmethod
    def validate_file(file_path: Union[str, Path]) -> tuple[bool, str]:
        """
        验证文件是否为有效的Rawtext JSON

        Args:
            file_path: 文件路径

        Returns:
            (是否有效, 错误信息或成功消息)
        """
        try:
            Parser.parse_file(file_path)
            return True, "Valid Rawtext JSON file"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def validate_string(json_str: str) -> tuple[bool, str]:
        """
        验证字符串是否为有效的Rawtext JSON

        Args:
            json_str: JSON字符串

        Returns:
            (是否有效, 错误信息或成功消息)
        """
        try:
            Parser.parse_string(json_str)
            return True, "Valid Rawtext JSON string"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def extract_text_components(rawtext: Rawtext) -> list[TextComponent]:
        """
        从Rawtext中提取所有文本组件

        Args:
            rawtext: Rawtext对象

        Returns:
            文本组件列表
        """
        if not isinstance(rawtext, Rawtext):
            raise UnsupportedArgument("Argument must be a Rawtext object")

        return rawtext.get_data()


    @staticmethod
    def to_json_compatible(obj: TextComponent) -> dict:
        """
        将TextComponent转换为JSON兼容的字典

        Args:
            obj: TextComponent对象

        Returns:
            JSON兼容的字典

        Raises:
            UnsupportedArgument: 参数类型错误
        """
        if isinstance(obj, Rawtext):
            return obj.to_dictionary()
        elif isinstance(obj, TextComponent):
            # 单个组件包装成rawtext
            rawtext = Rawtext([obj])
            return rawtext.to_dictionary()
        else:
            raise UnsupportedArgument("Argument must be a TextComponent")


class BatchParser:
    """批量解析器"""

    @staticmethod
    def parse_directory(directory: Union[str, Path],
                        pattern: str = "*.json") -> dict:
        """
        解析目录下的所有JSON文件

        Args:
            directory: 目录路径
            pattern: 文件匹配模式

        Returns:
            文件名到Rawtext对象的映射
        """
        path = Path(directory)
        if not path.exists() or not path.is_dir():
            raise FileNotFoundError(f"Directory not found: {directory}")

        results: dict = {}
        for file_path in path.glob(pattern):
            try:
                rawtext = Parser.parse_file(file_path)
                results[str(file_path)] = rawtext
            except Exception as e:
                results[str(file_path)] = f"Error: {e}"

        return results

    @staticmethod
    def parse_files(file_paths: list[Union[str, Path]]) -> dict:
        """
        解析多个文件

        Args:
            file_paths: 文件路径列表

        Returns:
            文件名到Rawtext对象的映射
        """
        results: dict = {}
        for file_path in file_paths:
            try:
                rawtext = Parser.parse_file(file_path)
                results[str(file_path)] = rawtext
            except Exception as e:
                results[str(file_path)] = f"Error: {e}"

        return results


# 快捷函数
def parse_file(file_path: Union[str, Path]) -> Rawtext:
    """解析JSON文件为Rawtext对象（快捷函数）"""
    return Parser.parse_file(file_path)


def parse_string(json_str: str) -> Rawtext:
    """解析JSON字符串为Rawtext对象（快捷函数）"""
    return Parser.parse_string(json_str)


def to_json_dict(obj: TextComponent) -> dict:
    """将TextComponent转换为JSON兼容的字典（快捷函数）"""
    return Parser.to_json_compatible(obj)


def validate_rawtext_file(file_path: Union[str, Path]) -> tuple[bool, str]:
    """验证文件是否为有效的Rawtext JSON（快捷函数）"""
    return Parser.validate_file(file_path)


def validate_rawtext_string(json_str: str) -> tuple[bool, str]:
    """验证字符串是否为有效的Rawtext JSON（快捷函数）"""
    return Parser.validate_string(json_str)


def extract_components(rawtext: Rawtext) -> list[TextComponent]:
    """从Rawtext中提取所有文本组件（快捷函数）"""
    return Parser.extract_text_components(rawtext)

