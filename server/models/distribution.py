

class Distribution():
    def __init__(self, collectionName: str, distribution: dict[str, dict[str, int]]):
        self._id = collectionName
        self.collectionName = collectionName
        self.distribution = distribution