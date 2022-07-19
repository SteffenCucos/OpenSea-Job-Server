from .id import Id, create_id

from typing import Any
from dataclasses import dataclass, field


def Entity(_id_source: str = None):
    class IdEntity:
        _id: Id

        def __post_init__(self):
            if _id_source:
                self._id = Id(str(getattr(self, _id_source)))
            else:
                self._id = create_id()

    return IdEntity