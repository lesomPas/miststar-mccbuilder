# create by lesomras on 2025-12-13

from .exceptions import MissingArgument, UnsupportedArgument, MalformedArgument
from collections.abc import Callable

def is_value(d: dict, key: str, data_type: type) -> bool:
    """检查一个字典中是否有指定的键, 且该键指向的类型为data_type"""
    if not isinstance(d, dict) or not isinstance(key, str) or not isinstance(data_type, type):
        raise UnsupportedArgument("Exception parameter type")
    return key in d and isinstance(d[key], data_type)

def list_of(sequence: list, data_type: type) -> bool:
    """检查一个列表是否为一个data_type泛型列表"""
    if not isinstance(sequence, list) or not isinstance(data_type, type):
        raise UnsupportedArgument("Exception parameter type")
    return all(isinstance(i, data_type) for i in sequence)

def matching(dictionary: dict, pattern: dict) -> None:
    """
    将字典dictionary与字典模板pattern做匹配, 遇到不匹配项则立即报出错误.
    关于如何写pattern请查看文档

    argument:
        dictionary: 待匹配的字典
        pattern: 匹配的模板
    return:
        None: 匹配通过的情况下
    """
    if not isinstance(dictionary, dict) or not isinstance(pattern, dict):
        raise TypeError("Both arguments must be dictionaries")
    stack = [(dictionary, pattern)]

    while stack:
        data, pat = stack.pop(-1)
        for key, pat_value in pat.items():
            if key not in data:
                raise MissingArgument(f"Missing required parameter: '{key}'")

            data_value = data[key]
            if isinstance(pat_value, dict) and isinstance(data_value, dict):
                stack.append((data_value, pat_value))
                continue

            # print(pat_value, "\n", data_value, "\n", key, "\n", stack)
            _type_checking(pat_value, data_value, key, stack=stack)

        if len(data) != len(pat):
            extra_keys = set(data.keys()) - set(pat.keys())
            raise MalformedArgument(f"Unexpected parameter(s): {', '.join(extra_keys)}")


def _type_checking(pat_value, data_value, key, stack) -> None:
    #breakpoint()
    # 字符串匹配模式
    if pat_value is str:
        if not isinstance(data_value, str):
            raise UnsupportedArgument(f"Parameter '{key}' must be a string")
        return

    # 数字匹配模式
    elif pat_value == "number":
        if not isinstance(data_value, (int, float)):
            raise UnsupportedArgument(f"Parameter '{key}' must be a number (int or float)")
        return

    # 整数匹配模式
    elif pat_value is int:
        if not isinstance(data_value, int):
            raise UnsupportedArgument(f"Parameter '{key}' must be an integer")
        return

    # 浮点数匹配模式
    elif pat_value is float:
        if not isinstance(data_value, float):
            raise UnsupportedArgument(f"Parameter '{key}' must be a float")
        return

    # 自定义匹配模式
    elif callable(pat_value):
        if not pat_value(data_value, key):
            raise MalformedArgument(f"Callable Return Invalid Value Signal local(data_value::{data_value}, key::{key})")
        return

    # 定长数组匹配模式
    elif isinstance(pat_value, list):
        if not isinstance(data_value, list):
            raise UnsupportedArgument(f"Parameter '{key}' must be a list")
        if len(data_value) != len(pat_value):
            raise MalformedArgument(f"List '{key}' must have exactly {len(pat_value)} items")

        for p, d in zip(pat_value, data_value):
            if isinstance(p, dict) and isinstance(d, dict):
                stack.append((d, p))
                continue
            _type_checking(p, d, key, stack)

    # 泛型非定长数组匹配模式
    elif isinstance(pat_value, tuple):
        if not isinstance(data_value, list):
            raise UnsupportedArgument(f"Parameter '{key}' must be a list")
        if len(pat_value) == 0:
            raise ValueError("Tuple pattern must contain at least one type")

        p = pat_value[0]
        if callable(p):
            if not p(data_value, key):
                raise MalformedArgument(f"Callable Return Invalid Value Signal local(data_value::{data_value}, key::{key})")
            return

        if isinstance(p, type):
            expected_type = p.__name__
        elif p == "number":
            expected_type = "number (int or float)"
            p = (int, float)
        else:
            raise ValueError("Tuple pattern must contain at least one type")

        if any(not isinstance(i, p) for i in data_value):
            raise UnsupportedArgument(f"All items in list '{key}' must be of type {expected_type}")

    # 保底类型匹配模式
    elif isinstance(pat_value, type):
        if not isinstance(data_value, pat_value):
            raise UnsupportedArgument(f"Parameter '{key}' must be of type {pat_value.__name__}")
        return
    # 错误情况
    else:
        raise MissingArgument(f"Invalid pattern for parameter '{key}'")