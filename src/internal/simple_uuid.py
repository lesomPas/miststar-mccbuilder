# create by lesomras on 2025-12-23
import uuid
from typing import TypeVar, Generic, Optional

from .exceptions import UnsupportedException, MalformedException, SemanticException

T = TypeVar('T')

def new_uuid() -> str:
    return str(uuid.uuid4())

class UUIDSpace(Generic[T]):
    """
    管理uuid的空间

    * 内部遵循一致化假设:
    (1) free_uuids ∪ mapping.keys() = uuids
    (2) free_uuids ∩ mapping.keys() = {}

    请确保你对内部状态的一切修改均符合该假设, 否则代码可能出现无法预期的行为
    """

    def __init__(self) -> None:
        self.uuids: set[str] = set()
        self.free_uuids: set[str] = set()
        self.mapping: dict[str, T] = {}

    def has_uuid(self, _uuid: str) -> bool:
        return _uuid in self.uuids

    def is_free(self, _uuid: str) -> bool:
        return _uuid in self.free_uuids

    def is_mapped(self, _uuid: str) -> bool:
        return _uuid in self.mapping

    def generate(self) -> str:
        _uuid = new_uuid()
        self.uuids.add(_uuid)
        self.free_uuids.add(_uuid)
        return _uuid

    def generate_uuids(self, nums: int = 1) -> list[str]:
        if not isinstance(nums, int) or nums < 0:
            raise UnsupportedException(f"'nums' must be a positive integer, but received {type(nums)}({nums}).")

        result = [new_uuid() for _ in range(nums)]
        self.uuids.update(result)
        self.free_uuids.update(result)
        return result

    def generate_and_custom(self, _value: T) -> str:
        _uuid = new_uuid()
        self.uuids.add(_uuid)
        self.mapping[_uuid] = _value
        return _uuid

    def custom(self, _value: T) -> str:
        if not self.free_uuids:
            return self.generate_and_custom(_value)

        _uuid = self.free_uuids.pop()
        self.mapping[_uuid] = _value
        return _uuid

    def custom_uuid(self, _uuid: str, _value: T) -> None:
        if self.is_mapped(_uuid):
            raise MalformedException(f"uuid {_uuid} already exists in this uuid space.")

        if self.has_uuid(_uuid):
            self.free_uuids.remove(_uuid)
        else:
            self.uuids.add(_uuid)
        self.mapping[_uuid] = _value

    def add_uuid(self, _uuid: str) -> None:
        if not self.has_uuid(_uuid):
            self.uuids.add(_uuid)
            self.free_uuids.add(_uuid)

    def delete_uuid(self, _uuid: str) -> None:
        self.forced_free(_uuid)

        if self.has_uuid(_uuid):
            self.uuids.remove(_uuid)
            self.free_uuids.remove(_uuid)

    def forced_free(self, _uuid: str, default: Optional[T] = None) -> Optional[T]:
        if self.is_mapped(_uuid):
            r = self.mapping[_uuid]
            del self.mapping[_uuid]
            self.free_uuids.add(_uuid)
            return r
        return None

    def get_value(self, _uuid: str, default: Optional[T] = None) -> Optional[T]:
        return self.mapping.get(_uuid, default)

    def clear(self) -> None:
        self.uuids.clear()
        self.free_uuids.clear()
        self.mapping.clear()

    @property
    def uuids_set(self) -> set[str]:
        return self.uuids.copy()

    def __contains__(self, _uuid: str) -> bool:
        return self.has_uuid(_uuid)

    def __len__(self) -> int:
        return len(self.uuids)

    def __iter__(self):
        return iter(self.uuids)

    def __repr__(self) -> str:
        return f"UUIDSpace(length={len(self.uuids)})"

    def invariant_check(self) -> bool:
        """一致化假设检测函数, 在测试中被使用"""
        # 检查条件1: free_uuids ∪ mapping.keys() = uuids
        union_set = self.free_uuids.union(set(self.mapping.keys()))
        if union_set != self.uuids:
            return False

        # 检查条件2: free_uuids ∩ mapping.keys() = {}
        intersection_set = self.free_uuids.intersection(set(self.mapping.keys()))
        if intersection_set:
            return False

        return True