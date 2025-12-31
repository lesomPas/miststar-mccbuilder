# create by lesomras on 2025-12-22
from __future__ import annotations
from typing import Union
from random import randint
from functools import partial

from .entity import Entity
from miststar.internal.exceptions import ReferenceNotFoundException, MalformedException
from miststar.internal.int32 import Int32, checking32, build32, Integer

class Scoreboard(object):
    def __init__(self, objective: str, display_name: str = "") -> None:
        # uuid -> Int32
        self.mapping: dict[str, Int32] = {}
        self.objective = objective
        self.display_name = display_name

    def has_entity(self, entity: Entity) -> bool:
        """检测entity是否在scoreboard中"""
        return entity.uuid in self.mapping

    def get_scoreboard_value(self, entity: Entity) -> Int32:
        if (u := entity.uuid) not in self.mapping:
            raise ReferenceNotFoundException(f"no entity found with uuid as {entity.uuid}")
        return self.mapping[u]

    def set_scoreboard_value(self, entity: Entity, value: Integer = 0) -> None:
        if (u := entity.uuid) not in self.mapping:
            raise ReferenceNotFoundException(f"no entity found with uuid as {entity.uuid}")
        v = build32(value)
        self.mapping[u] = v
        entity.scoreboards[self.objective] = v

    def players_set(self, entity: Entity, count: Integer = 0) -> None:
        """直接设定entity在scoreboard中的值"""
        if not checking32(count):
            raise MalformedException("'count' must be a valid 32-bit integer")
        v = build32(count)
        self.mapping[entity.uuid] = v
        entity.scoreboards[self.objective] = v

    def players_add(self, entity: Entity, count: Integer) -> None:
        """将entity在scoreboard中存储的值与传入值相加"""
        if not checking32(count):
            raise MalformedException("'count' must be a valid 32-bit integer")
        v = build32(count)
        if (u := entity.uuid) not in self.mapping:
            self.mapping[u] = v
            entity.scoreboards[self.objective] = v
            return
        self.mapping[u] += v
        entity.scoreboards[self.objective] += v

    def players_remove(self, entity: Entity, count: Integer) -> None:
        """将entity在scoreboard中存储的值与传入值相减"""
        self.players_add(entity, -count)

    def players_random(self, entity: Entity, _min: Integer, _max: Integer) -> Int32:
        """在_min与_max随机选一个值作为entity的新值"""
        if not checking32(_min):
            raise MalformedException("min must be a valid 32-bit integer")
        if not checking32(_max):
            raise MalformedException("max must be a valid 32-bit integer")
        if _min >= _max:
            raise MalformedException("min must be less than max")
        result = Int32(randint(int(_min), int(_max)))
        self.mapping[entity.uuid] = result
        entity.scoreboards[self.objective] = result
        return result

    def players_reset(self, entity: Entity) -> None:
        """删除entity在scoreboard中的数据条目"""
        if (u := entity.uuid) in self.mapping:
            del self.mapping[u]
            del entity.scoreboards[self.objective] 

    def players_test(self, entity: Entity, _min: Integer, _max: Integer = 2147483647) -> bool:
        """检测entity在scoreboard中的值是否在_min与_max中"""
        if not checking32(_min):
            raise MalformedException("min must be a valid 32-bit integer")
        if not checking32(_max):
            raise MalformedException("max must be a valid 32-bit integer")
        return _min <= self.get_scoreboard_value(entity) <= _max

    @staticmethod
    def players_operation(player: Entity, target_objective: Scoreboard, operation: str, selector: Entity, objective: Scoreboard) -> None:
        """给定两个实体和两个scoreboard, 一个操作, 对两个实体在scoreboard中的值进行一定的操作"""
        if target_objective.has_entity(player):
            player_value = target_objective.mapping[player.uuid].copy()
        else:
            player_value = Int32(0)
            target_objective.players_set(player, Int32(0))

        if objective.has_entity(selector):
            selector_value = objective.mapping[selector.uuid].copy()
        else:
            selector_value = Int32(0)
            objective.players_set(selector, Int32(0))

        setter = partial(target_objective.players_set, entity = player)

        match operation:
            case "=":
                setter(count = selector_value)
            case "+=":
                setter(count = player_value + selector_value)
            case "-=":
                setter(count = player_value - selector_value)
            case "*=":
                setter(count = player_value * selector_value)
            case "/=":
                if selector_value != 0:
                    setter(count = player_value.truncdiv(selector_value))
            case "%=":
                if selector_value != 0:
                    setter(count = player_value % selector_value)
            case "><":
                setter(count = selector_value)
                objective.players_set(selector, player_value)
            case "<":
                if selector_value < player_value:
                    setter(count = selector_value)
            case ">":
                if selector_value > player_value:
                    setter(count = selector_value)
            case _:
                raise MalformedException(f"{operation} does not have a corresponding operation")

    def serialize(self) -> dict:
        return {
            "objective": self.objective,
            "display_name": self.display_name,
            "mapping": {i: int(j) for i, j in self.mapping.items()}
        }

    def group_serialize(self) -> tuple[str, dict]:
        return self.objective, {
            "display_name": self.display_name,
            "mapping": {i: int(j) for i, j in self.mapping.items()}
        }

class LocalScoreboards(object):
    def __init__(self) -> None:
        # Scoreboard.objective -> Scoreboard
        self.mapping: dict[str, Scoreboard] = {}

    def has_scoreboard(self, objective: str) -> bool:
        """检测是否存在scoreboard"""
        return objective in self.mapping

    def get_scoreboard(self, objective: str) -> Scoreboard:
        """动态获取scoreboard"""
        return self.mapping[objective]

    def add_scoreboard(self, objective: str, display_name: str = "") -> Scoreboard:
        """动态添加scoreboard"""
        if objective in self.mapping:
            raise MalformedException(f"objective {objective} already exists in this local scoreboards.")
        sc = Scoreboard(objective, display_name)
        self.mapping[objective] = sc
        return sc

    def objectives_add(self, objective: str, display_name: str = "") -> Scoreboard:
        """动态添加scoreboard (minecraft api)"""
        return self.add_scoreboard(objective, display_name)

    def objectives_remove(self, objective: str) -> None:
        """动态移除scoreboard"""
        if objective in self.mapping:
            del self.mapping[objective]

    def serialize(self) -> dict:
        return {i: j.group_serialize()[1] for i, j in self.mapping.items()}