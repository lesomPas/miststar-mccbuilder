# created by lesomras on 2026-7-22

"""
Minecraft Rawtext JSON Processor
用于处理Minecraft基岩版原始JSON文本格式

主要功能：
- 创建和操作Minecraft原始JSON文本组件
- 序列化和反序列化JSON格式
- 验证和解析Rawtext数据
"""

__version__ = "3.0.0"
__author__ = "lesomras"

# 核心组件
from .components import (
    TextComponent,
    TranslateKind,
    Rawtext,
    Text,
    Score,
    Selector,
    Translate,
    TranslateBuilder,
    template_analysis,
    RawtextWith,
    TranslateWithComp,
    TranslateWithString,
)

# 解析器
from .parser import (
    Parser,
    parse_file,
    parse_string,
    parse_data,
    to_json_dict,
    validate_rawtext_file,
    validate_rawtext_string,
    extract_components,
)

# 打印机
from .printer import StructuredPrinter, default_printer, printraw

# 异常
from .exceptions import InvalidValueException

# 分析器（高级用户可能用到）
from .analyzer import SemanticComponentAnalyzer, TemplateLexer

__all__ = [
    # 版本
    "__version__",
    "__author__",

    # 组件
    "TextComponent",
    "TranslateKind",
    "Rawtext",
    "Text",
    "Score",
    "Selector",
    "Translate",
    "TranslateBuilder",
    "template_analysis",
    "RawtextWith",
    "TranslateWithComp",
    "TranslateWithString",

    # 解析器
    "Parser",
    "parse_file",
    "parse_string",
    "parse_data",
    "to_json_dict",
    "validate_rawtext_file",
    "validate_rawtext_string",
    "extract_components",

    # 打印机
    "StructuredPrinter",
    "default_printer",
    "printraw",

    # 异常
    "InvalidValueException",

    # 分析器
    "SemanticComponentAnalyzer",
    "TemplateLexer",
]
