
from dataclasses import dataclass

from .entity import Entity

@dataclass
class Metadata(Entity("collectionName")):
    collectionName: str
    collectionSize: int
    contractAddress: str
    contractABI: str
