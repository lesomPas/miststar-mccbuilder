# created by lesomras on 2026-7-22

from __future__ import annotations

import json
from pathlib import Path
from typing import Union, Iterable, Optional

from .components.rawtext import Rawtext
from .components.base import TextComponent
from miststar.exceptions import InvalidValueException


class Parser:
    """Rawtext 解析器，提供文件/字符串加载、验证和转换功能"""

    @staticmethod
    def parse_file(file_path: Union[str, Path]) -> Rawtext:
        """
        从 JSON 文件加载 Rawtext 对象

        Args:
            file_path: 文件路径（字符串或 Path 对象）

        Returns:
            Rawtext 对象

        Raises:
            FileNotFoundError: 文件不存在
            InvalidValueException: JSON 格式错误或结构不符合 Rawtext 规范
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise InvalidValueException(f"Invalid JSON in file {path}: {e}") from e
        except Exception as e:
            raise InvalidValueException(f"Failed to read file {path}: {e}") from e

        return Parser._parse_data(data)

    @staticmethod
    def parse_string(json_str: str) -> Rawtext:
        """
        从 JSON 字符串加载 Rawtext 对象

        Args:
            json_str: JSON 格式的字符串

        Returns:
            Rawtext 对象

        Raises:
            InvalidValueException: JSON 解析失败或结构错误
        """
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise InvalidValueException(f"Invalid JSON string: {e}") from e

        return Parser._parse_data(data)

    @staticmethod
    def parse_data(data: dict) -> Rawtext:
        """
        从字典数据加载 Rawtext 对象（直接使用已有字典）

        Args:
            data: 字典数据（应包含 "rawtext" 键或为单个组件字典）

        Returns:
            Rawtext 对象

        Raises:
            InvalidValueException: 数据结构无效
        """
        return Parser._parse_data(data)

    @staticmethod
    def _parse_data(data: dict) -> Rawtext:
        """内部解析：确保数据为合法 rawtext 格式并调用 from_dictionary"""
        if not isinstance(data, dict):
            raise InvalidValueException("Data must be a dictionary")

        # 若数据没有 "rawtext" 键，尝试包装为单个组件（兼容旧版）
        if "rawtext" not in data:
            # 检查是否为单个已知组件
            if any(key in data for key in ("text", "selector", "score", "translate")):
                data = {"rawtext": [data]}
            else:
                raise InvalidValueException("Missing 'rawtext' key and not a known component")

        return Rawtext.from_dictionary(data)

    @staticmethod
    def validate_file(file_path: Union[str, Path]) -> tuple[bool, str]:
        """
        验证文件是否为有效的 Rawtext JSON

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
        验证字符串是否为有效的 Rawtext JSON

        Returns:
            (是否有效, 错误信息或成功消息)
        """
        try:
            Parser.parse_string(json_str)
            return True, "Valid Rawtext JSON string"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def to_json_compatible(obj: TextComponent) -> dict:
        """
        将任意 TextComponent 转换为 JSON 兼容字典
        若 obj 不是 Rawtext，会自动包装为 {"rawtext": [...]}
        """
        if isinstance(obj, Rawtext):
            return obj.to_dictionary()
        elif isinstance(obj, TextComponent):
            # 单个组件包装为 Rawtext
            return Rawtext([obj]).to_dictionary()
        else:
            raise InvalidValueException("Expected a TextComponent object")

    @staticmethod
    def extract_components(rawtext: Rawtext) -> list[TextComponent]:
        """从 Rawtext 中提取组件列表（浅拷贝）"""
        if not isinstance(rawtext, Rawtext):
            raise InvalidValueException("Expected a Rawtext object")
        return rawtext.data.copy()


# ---------- 快捷函数（便于直接使用） ----------

def parse_file(file_path: Union[str, Path]) -> Rawtext:
    """解析 JSON 文件为 Rawtext 对象"""
    return Parser.parse_file(file_path)


def parse_string(json_str: str) -> Rawtext:
    """解析 JSON 字符串为 Rawtext 对象"""
    return Parser.parse_string(json_str)


def parse_data(data: dict) -> Rawtext:
    """解析字典为 Rawtext 对象"""
    return Parser.parse_data(data)


def to_json_dict(obj: TextComponent) -> dict:
    """将 TextComponent 转换为 JSON 兼容字典"""
    return Parser.to_json_compatible(obj)


def validate_rawtext_file(file_path: Union[str, Path]) -> tuple[bool, str]:
    """验证文件是否为有效的 Rawtext JSON"""
    return Parser.validate_file(file_path)


def validate_rawtext_string(json_str: str) -> tuple[bool, str]:
    """验证字符串是否为有效的 Rawtext JSON"""
    return Parser.validate_string(json_str)


def extract_components(rawtext: Rawtext) -> list[TextComponent]:
    """从 Rawtext 提取所有组件"""
    return Parser.extract_components(rawtext)
