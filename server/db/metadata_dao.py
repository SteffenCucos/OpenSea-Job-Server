from pymongo.collection import Collection
from fastapi import Depends

from models.metadata import Metadata

from db.mongodb import get_metadata_collection
from db.base_dao import BaseDAO



class MetadataDAO(BaseDAO):
    '''
    Responsible for manipulating the collections/metadata Collection
    '''
    def __init__(self, metadataCollection: Collection = Depends(get_metadata_collection)):
        super().__init__(metadataCollection, Metadata)