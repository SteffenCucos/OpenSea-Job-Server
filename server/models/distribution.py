

class Distribution():
    def __init__(self, collectionName: str, collectionSize: int, distribution: dict[str, dict[str, int]]):
        self._id = collectionName
        self.collectionName = collectionName
        self.collectionSize = collectionSize
        self.distribution = distribution
        