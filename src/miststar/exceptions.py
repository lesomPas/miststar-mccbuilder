# create by lesomras on 2026-4-12

class MiststarException(Exception):
    """ MiststarMccbuilder 根异常 """
    pass


class InvalidValueException(MiststarException):
    """无效值异常"""
    @classmethod
    def type_exception(cls, attr: str, type_str: str, obj):
        return cls(f"{attr} must be {type_str}, got {type(obj).__name__}")

    @classmethod
    def type_exception_value(cls, attr: str, type_str: str, obj):
        return cls(f"{attr} must be {type_str}, got {obj!r}")


# 历史遗留
class CommandException(MiststarException):
    """所有有关异常基类"""
    pass

class MissingArgument(CommandException):
    """参数丢失异常"""
    pass

# ~ TypeError
class UnsupportedArgument(CommandException):
    """参数类型异常"""
    pass

# ~ ValueError
class MalformedArgument(CommandException):
    """参数值异常"""
    pass

class MissingException(CommandException):
    """参数丢失异常"""
    pass

# ~ TypeError
class UnsupportedException(CommandException):
    """参数类型异常"""
    pass

# ~ ValueError
class MalformedException(CommandException):
    """参数值异常"""
    pass

class SemanticException(CommandException):
    """语义异常"""
    pass

class ReferenceNotFoundException(CommandException):
    """未发现引用异常 (uuid未找到)"""
    pass
