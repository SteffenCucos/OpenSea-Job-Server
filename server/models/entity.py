
from datetime import datetime as Datetime

from .id import Id, create_id

def Entity(_id_source: str = None):
    class IdEntity:
        _id: Id
        _created_time: Datetime

        def __post_init__(self):
            if _id_source:
                self._id = Id(str(getattr(self, _id_source)))
            else:
                self._id = create_id()

            self._created_time = Datetime.now()

    return IdEntity