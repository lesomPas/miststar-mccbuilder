# created by lesomras on 2026-7-28
from .base import TextComponent
from .rawtext import Rawtext
from .translate import Translate

def RawtextWith(*args: TextComponent) -> Rawtext:
    return Rawtext.from_component(*args)

def TranslateWithComp(translate: str, *args: TextComponent) -> Translate:
    return Translate(translate, Rawtext.from_component(*args))

def TranslateWithString(translate: str, *args: str) -> Translate:
    return Translate(translate, list(args))
