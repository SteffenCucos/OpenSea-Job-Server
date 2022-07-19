from dataclasses import dataclass
from enum import Enum
import traceback

from models.id import Id, create_id
from .entity import Entity

class Status(Enum):
    ERROR = "ERROR"
    CREATED = "CREATED"
    PREPARING = "PREPARING"
    LOADING = "LOADING"
    FINISHED = "FINISHED"

    def __repr__(self):
        return self.value

    def __str__(self):
        return self.value

@dataclass
class CollectionLoadJob(Entity()):
    collectionName: str
    progress: float = 0.0
    loaded: int = 0
    total: int = 0
    status: Status = Status.CREATED
    error: str = ""
        
    def get_status(self) -> Status:
        return self.status

    def update_status(self, status: Status):
        self.status = status

    def set_error(self, error: Exception):
        self.error = ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__))

    def increment_loaded(self, newLoads):
        self.loaded += newLoads
        self.progress = self.loaded / self.total