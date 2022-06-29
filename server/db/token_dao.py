from pymongo.collection import Collection
from fastapi import Depends, Path

from models.token import Token

from db.mongodb import get_tokens_collection
from db.base_dao import BaseDAO

class TokenDAO(BaseDAO):
    '''
    Responsible for manipulating the collections/jobs Collection
    '''
    def __init__(self, tokensCollection: Collection = Depends(get_tokens_collection)):
        self.collection = tokensCollection
        self.classType = Token