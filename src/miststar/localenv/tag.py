# create by lesomras on 2025-12-22

from .entity import Entity

class LocalTags(object):
    def __init__(self) -> None:
        self.tags: set[str] = set()
        self.entities: dict[str, set[Entity]] = {}

    def has_tag(self, entity: Entity, tag: str) -> bool:
        """检测entity上是否存在tag标签"""
        return tag in self.entities and entity in self.entities[tag]

    def tag_add(self, entity: Entity, tag: str) -> None:
        """给entity增加一个tag标签"""
        self.tags.add(tag)
        entity.tags.add(tag)
        if tag not in self.entities:
            self.entities[tag] = {entity}
        else:
            self.entities[tag].add(entity)

    def tag_remove(self, entity: Entity, tag: str) -> None:
        "去除entity上的tag标签"""
        if not self.has_tag(entity, tag):
            return

        entity.tags.remove(tag)
        self.entities[tag].remove(entity)
        if len(self.entities[tag]) == 0:
            del self.entities[tag]

    def serialize(self) -> dict:
        _serializer = lambda x: [repr(i) for i in x]
        return {i: _serializer(j) for i, j in self.entities.items()}