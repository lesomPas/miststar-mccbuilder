# create by lesomras on 2026-4-12
from miststar.exceptions import MiststarException

class MCDAnalyzerException(MiststarException):
    """ MCD 相关根异常 """
    pass

class MCDParsingException(MCDAnalyzerException):
    """ string 转化为 MCD 时失败 """
    pass

class MCDVersionException(MCDAnalyzerException):
    """ MCD 版本异常 """
    pass

class MCDFormatException(MCDAnalyzerException):
    """ MCD 格式异常 """
    pass

class MCDLoadingException(MCDAnalyzerException):
    """ MCD 加载异常 """
    pass