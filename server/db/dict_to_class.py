import dataclasses
from typing import (
    Any,
    Type,
    Union,
    get_args,
    get_origin,
    get_type_hints
)
import inspect
# https://docs.python.org/3/library/types.html#:~:text=class%20types.-,GenericAlias,-(t_origin%2C%20t_args)%C2%B6
# GenericAlias is the type used for parameterized lists and dicts
# ie: list[int], dict[str,object], etc
from types import GenericAlias
from enum import Enum

primitiveTypes = set([bool, int, float, str])
def is_primitive(type: type):
    return type in primitiveTypes or is_extended_primitive(type)

def is_extended_primitive(type: type):
    if not inspect.isclass(type):
        return False
    for primitive in primitiveTypes:
        if issubclass(type, primitive):
            return True
    return False

def is_enum(type: type):
    return inspect.isclass(type) and issubclass(type, Enum)

def is_optional(typeT: type):
    origin = get_origin(typeT)
    args = get_args(typeT)
    return origin is Union and type(None) in args 

def deserialize_enum(v: Any, enumType: Type[Enum]) -> Enum:
    return enumType(v)

def get_type_hierarchy(classType: type):
    '''
    Returns the type hierarchy in method/variable resolution order

        A
        /\----\
       B  C    H
       |  |    |
       D  |    G
         /\
        E  F

    becomes
    [A, B, D, C, E, F, H, G]   
    '''
    def get_bases(classType: type):
        bases = [base for base in classType.__bases__ if base != object]
        bases.reverse()
        return bases

    typeHierarchy = [classType]
    bases = get_bases(classType)

    while len(bases) > 0:
        base = bases.pop()
        typeHierarchy.append(base)
        
        for base in get_bases(base):
            bases.append(base)

    return typeHierarchy

def get_attributes(classType: type) -> dict[str, type]:
    attributes = {}
    # Use the python defined method/variable resolution order to get the correct type for each attribute
    for type in get_type_hierarchy(classType):
        for attrName, attrType in getattr(type, '__annotations__', {}).items():
            if attrName not in attributes.keys():
                attributes[attrName] = attrType
    
    return attributes

def get_empty_constructor():
    def __init__(self):
        pass

    return __init__

def deserialize_object(d: dict, classType: type):
    '''
    Constructs an instance of the given type from the supplied dictionary.

    Any field in the dict that has no corresponding type will be set on
    the object as its raw value.

    Currently does not support Union types
    '''
    # Avoid running the constructor by forcing an
    # empty init function to run instead of the real init.
    # This avoids any potential stateful code from running
    # Think some field on the object that sets a value based
    # on the day of the week
    class_init = classType.__init__
    classType.__init__ = get_empty_constructor()
    cls = classType()
    classType.__init__ = class_init

    attributes = get_attributes(classType)

    type_hints = get_type_hints(class_init)
    if dataclasses.is_dataclass(classType):
        type_hints.pop("return", None)

    # Sereialize any field that we can find a type hint for,
    # otherwise set it to the raw primitve value
    for name, value in d.items():
        # Check if an attribute with the given name exists, but overrite 
        # the type if it exists in the constructor type_hints
        type = attributes.pop(name) if name in attributes.keys() else None
        type = type_hints.pop(name) if name in type_hints.keys() else type
        cls.__dict__[name] = deserialize(value, type) if type else value

    return cls

def deserialize_list(l: list, classType: type):
    deserializedList = []
    for value in l:
        deserializedList.append(deserialize(value, classType))

    return deserializedList

def deserialize_dict(d: dict, keyType: type, valueType: type):
    deserializedDict = {}
    for key, value in d.items():
        deserializedKey = deserialize(key, keyType)
        deserializedValue = deserialize(value, valueType)
        deserializedDict[deserializedKey] = deserializedValue

    return deserializedDict
    
def deserialize(value: Any, classType: type):
    if value == None:
        # Allow None values for any type
        return None
    if is_primitive(classType):
        return classType(value)
    if is_enum(classType):
        return classType(value)
    if is_optional(classType):
        # If the parameter is optional, unpack the optional type and deserialize that type
        realType = classType.__args__[0]
        return deserialize(value, realType)
    if isinstance(classType, GenericAlias):
        typeArgs = classType.__args__
        originType = classType.__origin__
        if originType == type([]): # list of some type
            typeArg = typeArgs[0] # List paramaterization only takes 1 argument
            return deserialize_list(value, typeArg)
        else:
            keyType = typeArgs[0]
            valueType = typeArgs[1]
            return deserialize_dict(value, keyType, valueType)
    else:
        return deserialize_object(value, classType)

if __name__ == "__main__":

    aisle = [
        {
            "shoes" : [
                {
                    "size": 10,
                    "name": "Airmax",
                    "condition" : "Excellent"
                }, {
                    "size": 11,
                    "name": "Jordan",
                    "condition" : "Excellent"
                },
            ],
            "rows": [{"1":1}, {"2":2}]
        }, {
            "shoes" : [
                {
                    "size": 5,
                    "name": "Sketchers",
                    "condition" : "Excellent"
                },{
                    "size": 6,
                    "name": "Heelies",
                    "condition" : "Excellent"
                },
            ],
            "rows": [{"3":3}, {"4":4}]
        },
    ]

    from enum import Enum

    class Condition(Enum):
        EXCELENT = "Excellent"
        GOOD = "Good"
        BAD = "Bad"
        AWFUL = "Awful"

    class ShoeBox():
        def __init__(self, size: int, name: str, condition: Condition):
            self.size = size
            self.name = name
            self.condition = condition
        
        def __str__(self):
            return "{} {} in {} condition".format(self.size, self.name, self.condition)

    class Shelf():
        def __init__(self, shoes: list[ShoeBox], rows: list[dict[str,int]]):
            self.shoes = shoes
            self.rows = rows
        def __str__(self):
            s = ""
            for shoe in self.shoes:
                s += str(shoe) + "\n"
            s += str(self.rows)
            return s
        
    from models.token import Token
    data = {
        "success": True,
        "_id": "1",
        "num": 1,
        "url": "https://ipfs.io/ipfs/QmXQyUWciz8zLhtkfsFDHUyhzEezqaeA3Hw8wYVBPNviNa/1",
        "traits": [{"trait_type": "BACKGROUND", "value": "Aquamarine", "rarity": 0.10275}, {"trait_type": "BODY", "value": "Blue Grey", "rarity": 0.050125}, {"trait_type": "Horn", "value": "Pearl Stud", "rarity": 0.024625}, {"trait_type": "Mouth", "value": "Grin 1", "rarity": 0.068}, {"trait_type": "EYE", "value": "Hypnotized", "rarity": 0.07625}],
        "rarity": 0.28890000000000005
    }

    token = deserialize(data, Token)
    print(token.__dict__)
    #print(des)
    #print(json.dumps(des))
    #for shelf in des:
    #    print(shelf)
    
    