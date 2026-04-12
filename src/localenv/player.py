# create by lesomras on 2025-12-22

from .entity import Entity

class Player(Entity):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._type = "entity::player"

    def __str__(self) -> str:
        return f"player {self.name}({self.uuid})"

    def __repr__(self) -> str:
        return f"entity::player {self.name}({self.uuid})"