# create by lesomras on 2025-12-22
from __future__ import annotations
from typing import Union
from random import randint
from functools import partial

from miststar.internal.exceptions import ReferenceNotFoundException, MalformedException
from miststar.internal.int32 import Int32
from miststar.internal.interval import checking32

class Scoreboard(object):
    def __init__(self, objective: str, display_name: str = "") -> None:
        # uuid -> Int32
        self.mapping: dict[str, Int32] = {}
        self.objective = objective
        self.display_name = display_name

    def has_player(self, _uuid: str) -> bool:
        return _uuid in self.mapping

    def get_scoreboard_value(self, _uuid: str) -> Int32:
        if _uuid not in self.mapping:
            raise ReferenceNotFoundException(f"no entity found with uuid as {_uuid}")
        return self.mapping[_uuid]

    def set_scoreboard_value(self, _uuid: str, _value: Union[Int32, int] = 0) -> None:
        if _uuid not in self.mapping:
            raise ReferenceNotFoundException(f"no entity found with uuid as {_uuid}")

        if isinstance(_value, int):
            _value = Int32(_value)
        self.mapping[_uuid] = _value

    def players_set(self, _uuid, count: Union[Int32, int]) -> None:
        if not checking32(count):
            raise MalformedException("'count' must be a valid 32-bit integer")
        self.set_scoreboard_value(_uuid, count)

    def players_add(self, _uuid: str, count: Union[Int32, int]) -> None:
        if not checking32(count):
            raise MalformedException("'count' must be a valid 32-bit integer")
        self.mapping[_uuid] = self.get_scoreboard_value(_uuid) + count

    def players_remove(self, _uuid: str, count: Union[Int32, int]) -> None:
        if not checking32(count):
            raise MalformedException("'count' must be a valid 32-bit integer")
        self.mapping[_uuid] = self.get_scoreboard_value(_uuid) - count

    def players_random(self, _uuid: str, _min: Union[Int32, int], _max: Union[Int32, int]) -> Int32:
        if not checking32(_min):
            raise MalformedException("min must be a valid 32-bit integer")
        if not checking32(_max):
            raise MalformedException("max must be a valid 32-bit integer")
        if _min >= _max:
            raise MalformedException("min must be less than max")
        self.set_scoreboard_value(_uuid, randint(int(_min), int(_max)))
        return self.mapping[_uuid]

    def players_reset(self, _uuid: str) -> None:
        if _uuid not in self.mapping:
            raise ReferenceNotFoundException(f"no entity found with uuid as {_uuid}")
        del self.mapping[_uuid]

    def players_test(self, _uuid: str, _min: Union[Int32, int], _max: Union[Int32, int] = 2147483647) -> bool:
        if not checking32(_min):
            raise MalformedException("min must be a valid 32-bit integer")
        if not checking32(_max):
            raise MalformedException("max must be a valid 32-bit integer")
        return _min <= self.get_scoreboard_value(_uuid) <= _max

    @staticmethod
    def players_operation(player: str, target_objective: Scoreboard, operation: str, selector: str, objective: Scoreboard) -> None:
        if target_objective.has_player(player):
            player_value = target_objective.get_scoreboard_value(player).copy()
        else:
            player_value = Int32(0)
            target_objective.set_scoreboard_value(player, Int32(0))

        if objective.has_player(selector):
            selector_value = objective.get_scoreboard_value(selector).copy()
        else:
            selector_value = Int32(0)
            objective.set_scoreboard_value(selector, Int32(0))

        setter = partial(target_objective.set_scoreboard_value, _uuid = player)

        match operation:
            case "=":
                setter(_value = selector_value)
            case "+=":
                setter(_value = player_value + selector_value)
            case "-=":
                setter(_value = player_value - selector_value)
            case "*=":
                setter(_value = player_value * selector_value)
            case "/=":
                if selector_value != 0:
                    setter(_value = player_value.truncdiv(selector_value))
            case "%=":
                if selector_value != 0:
                    setter(_value = player_value % selector_value)
            case "><":
                setter(_value = selector_value)
                objective.set_scoreboard_value(selector, player_value)
            case "<":
                if selector_value < player_value:
                    setter(_value = selector_value)
            case ">":
                if selector_value > player_value:
                    setter(_value = selector_value)
            case _:
                raise MalformedException(f"{operation} does not have a corresponding operation")

class LocalScoreboards(object):
    def __init__(self) -> None:
        # Scoreboard.objective -> Scoreboard
        self.mapping: dict[str, Scoreboard] = {}
