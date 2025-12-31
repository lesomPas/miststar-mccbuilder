# create by lesomras on 2025-12-30

from miststar.internal.int32 import Int32
from miststar.internal.simple_uuid import new_uuid

class Entity(object):
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.uuid: str = new_uuid()
        self.scoreboards: dict[str, Int32] = {}
        self.tags: set[str] = set()
        self._type: str = "entity"

    def serialize(self) -> dict:
        return {
            "type": self._type,
            "name": self.name,
            "uuid": self.uuid,
            "scoreboards": {i: int(j) for i, j in self.scoreboards.items()},
            "tags": list(self.tags),
        }

    def group_serialize(self) -> tuple[str, dict]:
        return self.uuid, {
            "type": self._type,
            "name": self.name,
            "scoreboards": {i: int(j) for i, j in self.scoreboards.items()},
            "tags": list(self.tags),
        }

    def __eq__(self, other) -> bool:
        if not isinstance(other, Entity):
            return False
        return (
            self.name == other.name and 
            self.uuid == other.uuid and 
            self.scoreboards == other.scoreboards and 
            self.tags == other.tags
        )

    def __hash__(self) -> int:
        return hash(self.uuid)

    def __str__(self) -> str:
        return f"entity {self.name}({self.uuid})"

    def __repr__(self) -> str:
        return f"entity {self.name}({self.uuid})"