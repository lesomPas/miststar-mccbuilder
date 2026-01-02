"""
Minecraft Rawtext JSON Processor
用于处理Minecraft基岩版原始JSON文本格式

主要功能：
- 创建和操作Minecraft原始JSON文本组件
- 序列化和反序列化JSON格式
- 验证和解析Rawtext数据
"""

__version__ = "2.0.0"
__author__ = "lesomras"
__description__ = "Minecraft Rawtext JSON Processor"

# 组件系统
from .components import (
    TextComponent,    # 所有文本组件的基类
    Rawtext,          # Rawtext容器
    Text,             # 纯文本组件
    Score,            # 计分板组件
    Selector,         # 选择器组件
    Translate,        # 翻译组件
    TranslateBuilder, # 翻译构建组件
    infer_type,       # 类型推断组件
)

# 解析器
from .parser import (
    Parser,         # 主要解析器
    parse_file,     # 快捷函数：从文件解析
    parse_string,   # 快捷函数：从字符串解析
    to_json_dict,   # 快捷函数：转换为JSON字典
    validate_rawtext_file,    # 快捷函数：验证文件
    validate_rawtext_string,  # 快捷函数：验证字符串
    extract_components,      # 快捷函数：提取组件
)

# 模板系统
from .builder import (
    template_analysis,    # 模板解析构造函数
    template_builder,     # 模板生成构造函数
)
# 导出列表
__all__ = [
    # 版本信息
    "__version__", "__author__", "__description__",

    # 组件类
    "TextComponent",
    "Rawtext",
    "Text",
    "Score",
    "Selector",
    "Translate",

    # 构建器类
    "TranslateBuilder",
    "template_analysis",
    "template_builder",

    # 解析器
    "Parser",
    "parse_file",
    "parse_string",
    "to_json_dict",
    "validate_rawtext_file",
    "validate_rawtext_string",
    "extract_components",
]

# 包级配置
CONFIG = {
    "default_indent": 4,          # 默认缩进
    "ensure_ascii": False,        # 默认不强制ASCII编码
    "default_encoding": "utf-8",  # 默认编码
}
