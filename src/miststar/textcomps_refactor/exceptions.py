# created by lesomras on 2026-7-22

from miststar.exceptions import MiststarException

class InvalidValueException(MiststarException):
    """无效值异常"""
    @classmethod
    def type_exception(cls, attr: str, type_str: str, obj):
        return cls(f"{attr} must be {type_str}, got {type(obj).__name__}")

    @classmethod
    def type_exception_value(cls, attr: str, type_str: str, obj):
        return cls(f"{attr} must be {type_str}, got {obj!r}")
