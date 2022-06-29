

class Metadata():
    def __init__(self, 
        collectionName: str,
        collectionSize: int,
        contractAddress: str,
        contractABI: str
    ):
        self._id = collectionName
        self.collectionName = collectionName
        self.collectionSize = collectionSize
        self.contractAddress = contractAddress
        self.contractABI = contractABI
