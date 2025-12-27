# create by lesomras on 2025-12-22
from __future__ import annotations
from typing import Union, Optional
import math

class Int32:
    """32位有符号整数类"""
    __slots__ = ("value", )

    # 32位整数范围
    MIN = -0x80000000  # -2^31
    MAX = 0x7FFFFFFF   # 2^31 - 1
    MASK = 0xFFFFFFFF  # 2^32 - 1

    def __init__(self, value: Union[Int32, int] = 0):
        """初始化，将值限制在32位范围内"""
        self.value: int = 0

        if isinstance(value, Int32):
            self.value = value.value & self.MASK
        else:
            self.value = int(value) & self.MASK

        if self.value & 0x80000000:
            self.value = self.value - 0x100000000

    def copy(self) -> Int32:
        """拷贝一个新的Int32"""
        return Int32(self.value)

    # ========== 算术运算 ==========

    def __add__(self, other: Union[Int32, int]) -> Int32:
        """加法运算"""
        if not isinstance(other, Int32):
            other = Int32(other)
        result = (self.value + other.value) & self.MASK

        if result & 0x80000000:
            result -= 0x100000000
        return Int32(result)

    def __sub__(self, other: Union[Int32, int]) -> Int32:
        """减法运算"""
        if not isinstance(other, Int32):
            other = Int32(other)
        result = (self.value - other.value) & self.MASK

        if result & 0x80000000:
            result -= 0x100000000
        return Int32(result)

    def __mul__(self, other: Union[Int32, int]) -> Int32:
        """乘法运算"""
        if not isinstance(other, Int32):
            other = Int32(other)
        result = (self.value * other.value) & self.MASK

        if result & 0x80000000:
            result -= 0x100000000
        return Int32(result)

    def __truediv__(self, other: Union[Int32, int]) -> float:
        """真除法，返回浮点数"""
        if not isinstance(other, Int32):
            other = Int32(other)
        return self.value / other.value

    def __floordiv__(self, other: Union[Int32, int]) -> Int32:
        """整除运算"""
        if not isinstance(other, Int32):
            other = Int32(other)
        if other.value == 0:
            raise ZeroDivisionError("division by zero")
        result = self.value // other.value
        return Int32(result)

    def __mod__(self, other: Union[Int32, int]) -> Int32:
        """取模运算"""
        if not isinstance(other, Int32):
            other = Int32(other)
        if other.value == 0:
            raise ZeroDivisionError("modulo by zero")
        result = self.value % other.value
        return Int32(result)

    def __divmod__(self, other: Union[Int32, int]) -> tuple[Int32, Int32]:
        """返回 (商, 余数)"""
        return (self // other, self % other)

    def __pow__(self, other: Union[Int32, int], mod: Optional[int] = None) -> Int32:
        """幂运算"""
        if not isinstance(other, Int32):
            other = Int32(other)

        if mod is not None:
            result = pow(self.value, other.value, mod)
        else:
            result = pow(self.value, other.value)

        return Int32(result)

    # ========== 反向算术运算 ==========

    def __radd__(self, other: Union[Int32, int]) -> Int32:
        """反向加法"""
        return self + other

    def __rsub__(self, other: Union[Int32, int]) -> Int32:
        """反向减法"""
        if not isinstance(other, Int32):
            other = Int32(other)
        return other - self

    def __rmul__(self, other: Union[Int32, int]) -> Int32:
        """反向乘法"""
        return self * other

    def __rfloordiv__(self, other: Union[Int32, int]) -> Int32:
        """反向整除"""
        if not isinstance(other, Int32):
            other = Int32(other)
        return other // self

    def __rmod__(self, other: Union[Int32, int]) -> Int32:
        """反向取模"""
        if not isinstance(other, Int32):
            other = Int32(other)
        return other % self

    def __rdivmod__(self, other: Union[Int32, int]) -> tuple[Int32, Int32]:
        """反向divmod"""
        return divmod(other, self)

    def __rpow__(self, other: Union[Int32, int], mod: Optional[int] = None) -> Int32:
        """反向幂运算"""
        if not isinstance(other, Int32):
            other = Int32(other)

        if mod is not None:
            result = pow(other.value, self.value, mod)
        else:
            result = pow(other.value, self.value)

        return Int32(result)

    # ========== 位运算 ==========

    def __and__(self, other: Union[Int32, int]) -> Int32:
        """位与运算"""
        if not isinstance(other, Int32):
            other = Int32(other)
        return Int32(self.value & other.value)

    def __or__(self, other: Union[Int32, int]) -> Int32:
        """位或运算"""
        if not isinstance(other, Int32):
            other = Int32(other)
        return Int32(self.value | other.value)

    def __xor__(self, other: Union[Int32, int]) -> Int32:
        """位异或运算"""
        if not isinstance(other, Int32):
            other = Int32(other)
        return Int32(self.value ^ other.value)

    def __lshift__(self, n: int) -> Int32:
        """左移运算"""
        n = n & 0x1F  # 限制在0-31位
        result = (self.value << n) & self.MASK

        if result & 0x80000000:
            result -= 0x100000000
        return Int32(result)

    def __rshift__(self, n: int) -> Int32:
        """算术右移（保持符号位）"""
        n = n & 0x1F  # 限制在0-31位
        return Int32(self.value >> n)

    # ========== 反向位运算 ==========

    def __rand__(self, other: Union[Int32, int]) -> Int32:
        """反向位与"""
        if not isinstance(other, Int32):
            other = Int32(other)
        return other & self

    def __ror__(self, other: Union[Int32, int]) -> Int32:
        """反向位或"""
        if not isinstance(other, Int32):
            other = Int32(other)
        return other | self

    def __rxor__(self, other: Union[Int32, int]) -> Int32:
        """反向位异或"""
        if not isinstance(other, Int32):
            other = Int32(other)
        return other ^ self

    def __rlshift__(self, other: Union[Int32, int]) -> Int32:
        """反向左移"""
        if not isinstance(other, Int32):
            other = Int32(other)
        return other << self.value

    def __rrshift__(self, other: Union[Int32, int]) -> Int32:
        """反向右移"""
        if not isinstance(other, Int32):
            other = Int32(other)
        return other >> self.value

    # ========== 一元操作 ==========

    def __neg__(self) -> Int32:
        """取负"""
        return Int32(-self.value)

    def __pos__(self) -> Int32:
        """取正"""
        return self

    def __abs__(self) -> Int32:
        """绝对值"""
        return Int32(abs(self.value))

    def __invert__(self) -> Int32:
        """按位取反"""
        return Int32(~self.value)

    # ========== 比较运算 ==========

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, (Int32, int)):
            return False
        return self.value == Int32(other).value

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __lt__(self, other: Union[Int32, int]) -> bool:
        if not isinstance(other, Int32):
            other = Int32(other)
        return self.value < other.value

    def __le__(self, other: Union[Int32, int]) -> bool:
        if not isinstance(other, Int32):
            other = Int32(other)
        return self.value <= other.value

    def __gt__(self, other: Union[Int32, int]) -> bool:
        if not isinstance(other, Int32):
            other = Int32(other)
        return self.value > other.value

    def __ge__(self, other: Union[Int32, int]) -> bool:
        if not isinstance(other, Int32):
            other = Int32(other)
        return self.value >= other.value

    # ========== 类型转换 ==========

    def __index__(self) -> int:
        """当需要整数索引时调用（如切片、bin(), oct(), hex()）"""
        return self.value

    def __int__(self) -> int:
        return self.value

    def __float__(self) -> float:
        return float(self.value)

    def __bool__(self) -> bool:
        return self.value != 0

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"Int32({self.value})"

    def __hash__(self) -> int:
        return hash(self.value)

    def __format__(self, format_spec: str) -> str:
        return format(self.value, format_spec)

    # ========== 原地运算 ==========

    def __iadd__(self, other: Union[Int32, int]) -> Int32:
        """原地加法"""
        result = self + other
        self.value = result.value
        return self

    def __isub__(self, other: Union[Int32, int]) -> Int32:
        """原地减法"""
        result = self - other
        self.value = result.value
        return self

    def __imul__(self, other: Union[Int32, int]) -> Int32:
        """原地乘法"""
        result = self * other
        self.value = result.value
        return self

    def __ifloordiv__(self, other: Union[Int32, int]) -> Int32:
        """原地整除"""
        result = self // other
        self.value = result.value
        return self

    def __imod__(self, other: Union[Int32, int]) -> Int32:
        """原地取模"""
        result = self % other
        self.value = result.value
        return self

    def __ipow__(self, other: Union[Int32, int], mod: Optional[int] = None) -> Int32:
        """原地幂运算"""
        result = self ** other
        self.value = result.value
        return self

    def __iand__(self, other: Union[Int32, int]) -> Int32:
        """原位与"""
        result = self & other
        self.value = result.value
        return self

    def __ior__(self, other: Union[Int32, int]) -> Int32:
        """原位或"""
        result = self | other
        self.value = result.value
        return self

    def __ixor__(self, other: Union[Int32, int]) -> Int32:
        """原位异或"""
        result = self ^ other
        self.value = result.value
        return self

    def __ilshift__(self, n: int) -> Int32:
        """原地左移"""
        result = self << n
        self.value = result.value
        return self

    def __irshift__(self, n: int) -> Int32:
        """原地右移"""
        result = self >> n
        self.value = result.value
        return self

    # ========== 特殊方法 ==========

    def __round__(self, n: Optional[int] = None) -> Int32:
        """四舍五入，对于整数总是返回自身"""
        return self

    def __trunc__(self) -> Int32:
        """截断，返回整数部分"""
        return self

    def __floor__(self) -> Int32:
        """向下取整，返回自身"""
        return self

    def __ceil__(self) -> Int32:
        """向上取整，返回自身"""
        return self

    # ========== 实用方法 ==========

    def to_unsigned(self) -> int:
        """转换为无符号32位整数"""
        return self.value & self.MASK

    @classmethod
    def from_unsigned(cls, value: int) -> Int32:
        """从无符号整数创建"""
        value = value & cls.MASK

        if value & 0x80000000:
            value -= 0x100000000
        return cls(value)

    def truncdiv(self, other: Union[Int32, int]) -> Int32:
        """整除运算 (向零取整)"""
        if not isinstance(other, Int32):
            other = Int32(other)
        if other.value == 0:
            raise ZeroDivisionError("division by zero")
        return Int32(math.trunc(self.value / other.value))

    # ========== 兼容性方法 ==========

    def __getstate__(self) -> int:
        """用于pickle序列化"""
        return self.value

    def __setstate__(self, state: int) -> None:
        """用于pickle反序列化"""
        self.value = state & self.MASK
        if self.value & 0x80000000:
            self.value -= 0x100000000


const_min = Int32(Int32.MIN)
const_max = Int32(Int32.MAX)