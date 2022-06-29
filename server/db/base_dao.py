from typing import TypeVar, Generic

T = TypeVar('T')

from pymongo.collection import Collection

from .dict_to_class import deserialize
from .class_to_dict import serialize

from models.id import Id

def validate_has_id(object: object):
    objectFields = object.__dict__
    if "_id" not in objectFields:
        raise "object must have _id field"

def get_id_criteria(object):
    return {
        "_id": object._id
    }

# Save all the fields from the object into mongo
def get_update_query(object):
    return {
        "$set" : serialize(object)
    }

class BaseDAO(Generic[T]):
    def __init__(self):
        self.collection: Collection = None
        self.classType: type = None

    def save(self, object: T) -> Id:
        validate_has_id(object)
        return self.collection.insert_one(serialize(object)).inserted_id

    def save_many(self, lst: list[T]) -> list[Id]:
        for object in lst:
            validate_has_id(object)
        print("validated")
        serialized = serialize(lst)
        print("serialized")
        inserted = self.collection.insert_many(serialized)
        print("inserted")
        return inserted

    def update(self, object: T):
        validate_has_id(object)
        self.collection.update_one(get_id_criteria(object), get_update_query(object))

    def find_one_by_name(self, name: str) -> T:
        return self.find_one_by_condition({"name": name})

    def find_one_by_id(self, id: str) -> T:
        return self.find_one_by_condition({"_id": id})

    def find_one_by_condition(self, condition: dict) -> T:
        ret = self.collection.find_one(condition)
        if ret:
            return deserialize(value=ret, classType=self.classType)
        return None