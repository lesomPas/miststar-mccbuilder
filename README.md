# miststar-mccbuilder

[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Minecraft 基岩版命令与文本组件构建工具集。

`miststar-mccbuilder` 提供了一套用于处理 Minecraft Bedrock Edition 的 Python 工具，包括：

- **`textcomps`**：Rawtext / TextComponent 快速构建与解析库
- **`mcd_analyzer`**：MCD（命令链文档）解析器与构建器
- **`localenv`**：本地计分板、实体、标签等状态模拟
- **`serializer`**：通用 JSON 序列化工具

---

## 安装

使用 [uv](https://docs.astral.sh/uv/)：

```bash
uv pip install -e .
```

或使用 pip：

```bash
pip install -e .
```

---

## 快速开始

### 1. 构建 Rawtext 文本组件

```python
from miststar.textcomps import Rawtext, Text, Score, Selector

raw = Rawtext()
raw.text("Hello ").selector("@p").text(", your score: ").score("@p", "kills")
print(raw.to_dictionary())
```

输出：

```json
{
  "rawtext": [
    {"text": "Hello "},
    {"selector": "@p"},
    {"text": ", your score: "},
    {"score": {"name": "@p", "objective": "kills"}}
  ]
}
```

### 2. 使用模板快速构建

```python
from miststar.textcomps import Rawtext

raw = Rawtext.from_template("Hello {@p}, you have {kills[].@p} kills!")
print(raw.to_dictionary())
```

### 3. 解析 JSON 文件

```python
from miststar.textcomps import parse_file

rawtext = parse_file("path/to/your/rawtext.json")
```

### 4. 解析 MCD 命令链文档

```python
from miststar.mcd_analyzer.mcd_serializer import MCDSerializer

doc = """
@mcd_version = 2
###Function###
---Main---
> I?
/say hello
###End###
"""

serializer = MCDSerializer()
mcd = serializer.load_mcd(doc)
print(mcd)
```

### 5. 构建 MCD 文档

```python
from miststar.mcd_analyzer.mcd_builder import MCDBuilder
from miststar.mcd_analyzer.mcd import BlockKind

builder = MCDBuilder(2)
builder.add_chain("Main")
builder.add_marked_command("/say hello", kind=BlockKind.Impulse, conditional=True)
mcd = builder.end()
```

---

## 开发

### 运行测试

```bash
uv run pytest
```

### 类型检查

```bash
uv run mypy src
uv run pyright
```

---

## 项目结构

```text
src/miststar/
├── mcd_analyzer/        # MCD 命令链文档解析与构建
├── textcomps/           # Minecraft Rawtext 组件库
├── localenv/            # 本地环境模拟（计分板、实体、标签）
├── serializer/          # JSON 序列化工具
└── exceptions.py        # 全局异常体系
```

---

## 许可证

[MIT](LICENSE)
