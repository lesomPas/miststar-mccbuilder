# create by lesomras on 2025-12-13

class CommandException(Exception):
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