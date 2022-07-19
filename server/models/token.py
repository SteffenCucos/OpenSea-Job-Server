
from dataclasses import dataclass

import traceback

from .trait import Trait
from .entity import Entity


@dataclass
class Token(Entity("num")):
    success: bool
    num: int
    url: str
    traits: list[Trait]
    error: str = None
    rarity: float = None

    def set_error(self, error: Exception):
        self.error = ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__))