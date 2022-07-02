from enum import Enum
import traceback
from models.id import Id, create_id

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

class CollectionLoadJob():
    def __init__(self, 
                collectionName: str, 
                progress: float = 0.0,
                loaded: int = 0,
                total: int = 0,
                status: Status = Status.CREATED, 
                error: str = "",
                _id: Id = None
                ):
        self.collectionName = collectionName
        self.progress = progress
        self.loaded = loaded
        self.total = total
        self.status = status.value
        self.error = error
        if _id == None:
            _id = create_id()
        self._id = _id
        
    def get_status(self) -> Status:
        return self.status

    def update_status(self, status: Status):
        self.status = status

    def set_error(self, error: Exception):
        self.error = ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__))

    def increment_loaded(self, newLoads):
        self.loaded += newLoads
        self.progress = self.loaded / self.total

        