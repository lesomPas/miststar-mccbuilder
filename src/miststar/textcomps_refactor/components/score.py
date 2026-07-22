# created by lesomras on 2026-7-22

from __future__ import annotations
from dataclasses import dataclass

from .base import TextComponent
from ..exceptions import InvalidValueException


@dataclass(slots=True)
class Score(TextComponent):
    name: str
    objective: str

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise InvalidValueException.type_exception("name", "str", self.name)
        if not isinstance(self.objective, str):
            raise InvalidValueException.type_exception("objective", "str", self.objective)

    @classmethod
    def from_dictionary(cls, d: dict) -> Score:
        inner = d["score"]
        name = inner["name"]
        objective = inner["objective"]
        return cls(name=name, objective=objective)

    @staticmethod
    def build_dictionary(name: str, objective: str) -> dict:
        return {"score": {"name": name, "objective": objective}}

    def to_dictionary(self) -> dict:
        return {"score": {"name": self.name, "objective": self.objective}}

    @classmethod
    def p(cls, objective: str) -> Score:
        return cls(name="@p", objective=objective)

    @classmethod
    def r(cls, objective: str) -> Score:
        return cls(name="@r", objective=objective)

    @classmethod
    def a(cls, objective: str) -> Score:
        return cls(name="@a", objective=objective)

    @classmethod
    def e(cls, objective: str) -> Score:
        return cls(name="@e", objective=objective)

    @classmethod
    def s(cls, objective: str) -> Score:
        return cls(name="@s", objective=objective)

    @classmethod
    def n(cls, objective: str) -> Score:
        return cls(name="@n", objective=objective)

    @classmethod
    def initiator(cls, objective: str) -> Score:
        return cls(name="@initiator", objective=objective)

    def __str__(self) -> str:
        return f"score | {self.name} scoreboard :{self.objective}"
