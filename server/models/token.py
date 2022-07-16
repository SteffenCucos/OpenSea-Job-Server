
import traceback
from .trait import Trait
from .id import Id

class Token():
    def __init__(self, success: bool, num: int, url: str, traits: list[Trait], error: str = None, rarity: float = None, _id: Id = None):
        if _id == None:
            self._id = Id(str(num))
        else:
            self._id = _id
        self.success = success
        self.num = num
        self.url = url
        self.traits = traits
        self.error = error
        self.rarity = rarity
        # Rarity is wrong right now?

    def set_error(self, error: Exception):
        self.error = ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__))

    def __eq__(self, other):
         return self._id == other._id \
                and self.num == other.num \
                and self.url == other.url \
                and self.success == other.success \

    def __str__(self):
        if self.success:
            return "num:{} rarity: {} traits: {}".format(self.num, self.rarity, len(self.traits))
        else:
            return "num:{} Failed to load"
        pass