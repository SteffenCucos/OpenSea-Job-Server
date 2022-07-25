from pymongo.collection import Collection
from fastapi import Depends

from models.distribution import Distribution

from db.mongodb import get_distributions_collection
from db.base_dao import BaseDAO

class DistributionDAO(BaseDAO):
    '''
    Responsible for manipulating the collections/distributions Collection
    '''
    def __init__(self, distributionsCollection: Collection = Depends(get_distributions_collection)):
        super().__init__(distributionsCollection, Distribution)