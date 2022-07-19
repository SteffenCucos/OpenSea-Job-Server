

from dataclasses import dataclass

from .entity import Entity

@dataclass
class Distribution(Entity("collectionName")):
    collectionName: str
    collectionSize: int
    distribution: dict[str, dict[str, int]]
        