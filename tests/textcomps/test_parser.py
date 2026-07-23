"""
测试 Parser 模块：文件/字符串/字典解析、验证、批量处理、序列化辅助
"""
import json
import pytest
from miststar.textcomps_refactor import (
    Rawtext, Text, Score, Selector, Translate,
    Parser,
    parse_file, parse_string, parse_data,
    to_json_dict,
    validate_rawtext_file, validate_rawtext_string,
    extract_components
)
from miststar.textcomps_refactor.exceptions import InvalidValueException


# ============================================================================
# 测试 Parser 静态方法
# ============================================================================

class TestParser:
    """测试 Parser 类的静态方法"""

    # ---------- parse_data ----------
    def test_parse_data_full(self):
        d = {"rawtext": [{"text": "Hello"}, {"selector": "@p"}]}
        raw = Parser.parse_data(d)
        assert len(raw) == 2
        assert raw[0].content == "Hello"
        assert raw[1].selector == "@p"

    def test_parse_data_single_component_autowrap(self):
        """单组件字典应自动包装为 {"rawtext": [...]}"""
        d = {"text": "Hello"}
        raw = Parser.parse_data(d)
        assert len(raw) == 1
        assert raw[0].content == "Hello"

    def test_parse_data_single_score_autowrap(self):
        d = {"score": {"name": "Steve", "objective": "kills"}}
        raw = Parser.parse_data(d)
        assert len(raw) == 1
        assert raw[0].name == "Steve"

    def test_parse_data_single_translate_autowrap(self):
        d = {"translate": "gui.done"}
        raw = Parser.parse_data(d)
        assert len(raw) == 1
        assert raw[0].translate == "gui.done"

    def test_parse_data_invalid(self):
        """既无 rawtext 也不是已知组件的字典"""
        with pytest.raises(InvalidValueException) as exc:
            Parser.parse_data({"unknown": "foo"})
        assert "Missing 'rawtext' key" in str(exc.value)

    def test_parse_data_not_dict(self):
        with pytest.raises(InvalidValueException) as exc:
            Parser.parse_data("not a dict")  # type: ignore
        assert "dictionary" in str(exc.value).lower()

    # ---------- parse_string ----------
    def test_parse_string_full(self):
        s = '{"rawtext": [{"text": "Hi"}]}'
        raw = Parser.parse_string(s)
        assert len(raw) == 1
        assert raw[0].content == "Hi"

    def test_parse_string_single_autowrap(self):
        s = '{"text": "Hi"}'
        raw = Parser.parse_string(s)
        assert len(raw) == 1
        assert raw[0].content == "Hi"

    def test_parse_string_invalid_json(self):
        with pytest.raises(InvalidValueException) as exc:
            Parser.parse_string("{invalid json}")
        assert "Invalid JSON" in str(exc.value)

    # ---------- parse_file ----------
    def test_parse_file(self, tmp_path):
        file = tmp_path / "test.json"
        file.write_text('{"rawtext": [{"text": "file content"}]}', encoding="utf-8")
        raw = Parser.parse_file(file)
        assert len(raw) == 1
        assert raw[0].content == "file content"

    def test_parse_file_autowrap(self, tmp_path):
        file = tmp_path / "single.json"
        file.write_text('{"text": "single"}', encoding="utf-8")
        raw = Parser.parse_file(file)
        assert len(raw) == 1
        assert raw[0].content == "single"

    def test_parse_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            Parser.parse_file("nonexistent.json")

    def test_parse_file_invalid_json(self, tmp_path):
        file = tmp_path / "invalid.json"
        file.write_text('{"text": "missing quote}', encoding="utf-8")
        with pytest.raises(InvalidValueException) as exc:
            Parser.parse_file(file)
        assert "Invalid JSON" in str(exc.value)

    # ---------- validate_file ----------
    def test_validate_file_valid(self, tmp_path):
        file = tmp_path / "valid.json"
        file.write_text('{"rawtext": []}', encoding="utf-8")
        ok, msg = Parser.validate_file(file)
        assert ok is True
        assert "Valid" in msg

    def test_validate_file_invalid(self, tmp_path):
        file = tmp_path / "invalid.json"
        file.write_text('{"foo": "bar"}', encoding="utf-8")
        ok, msg = Parser.validate_file(file)
        assert ok is False
        assert "Missing" in msg

    # ---------- validate_string ----------
    def test_validate_string_valid(self):
        ok, msg = Parser.validate_string('{"rawtext": []}')
        assert ok is True
        assert "Valid" in msg

    def test_validate_string_invalid(self):
        ok, msg = Parser.validate_string('{"foo": "bar"}')
        assert ok is False

    def test_validate_string_invalid_json(self):
        ok, msg = Parser.validate_string("{invalid}")
        assert ok is False
        assert "Invalid JSON" in msg

    # ---------- to_json_compatible ----------
    def test_to_json_compatible_rawtext(self):
        raw = Rawtext([Text("Hi")])
        d = Parser.to_json_compatible(raw)
        assert d == {"rawtext": [{"text": "Hi"}]}

    def test_to_json_compatible_single_component(self):
        d = Parser.to_json_compatible(Text("Hi"))
        assert d == {"rawtext": [{"text": "Hi"}]}

    def test_to_json_compatible_score(self):
        s = Score("Steve", "kills")
        d = Parser.to_json_compatible(s)
        assert d == {"rawtext": [{"score": {"name": "Steve", "objective": "kills"}}]}

    def test_to_json_compatible_invalid(self):
        with pytest.raises(InvalidValueException):
            Parser.to_json_compatible("not a component")  # type: ignore

    # ---------- extract_components ----------
    def test_extract_components(self):
        raw = Rawtext([Text("a"), Selector("@p")])
        components = Parser.extract_components(raw)
        assert len(components) == 2
        assert components[0].content == "a"
        assert components[1].selector == "@p"
        # 应是浅拷贝
        assert components is not raw.data
        assert components == raw.data

    def test_extract_components_invalid(self):
        with pytest.raises(InvalidValueException):
            Parser.extract_components(Text("x"))  # type: ignore


# ============================================================================
# 测试快捷函数（与 Parser 方法等价，仅验证转发）
# ============================================================================

class TestConvenienceFunctions:
    """测试快捷函数是否正常工作"""

    def test_parse_file(self, tmp_path):
        file = tmp_path / "test.json"
        file.write_text('{"text": "hello"}', encoding="utf-8")
        raw = parse_file(file)
        assert raw[0].content == "hello"

    def test_parse_string(self):
        raw = parse_string('{"text": "hello"}')
        assert raw[0].content == "hello"

    def test_parse_data(self):
        raw = parse_data({"text": "hello"})
        assert raw[0].content == "hello"

    def test_to_json_dict(self):
        d = to_json_dict(Text("hello"))
        assert d == {"rawtext": [{"text": "hello"}]}

    def test_validate_rawtext_file(self, tmp_path):
        file = tmp_path / "valid.json"
        file.write_text('{"rawtext": []}', encoding="utf-8")
        ok, msg = validate_rawtext_file(file)
        assert ok is True

    def test_validate_rawtext_string(self):
        ok, msg = validate_rawtext_string('{"rawtext": []}')
        assert ok is True

    def test_extract_components(self):
        raw = Rawtext([Text("a")])
        comps = extract_components(raw)
        assert len(comps) == 1
