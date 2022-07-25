import dataclasses
from typing import (
    Any,
    Type,
    Union,
    Callable,
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

class Deserializer:
    def __init__(self, middleware: dict[type, Callable[[object], type]] = []):
        self.middleware = middleware

    def deserialize_enum(self, v: Any, enumType: Type[Enum]) -> Enum:
        return enumType(v)

    def deserialize_simple_object(self, d: dict, classType: type):
        '''
        Constructs an instance of the given type from the supplied dictionary.

        Any field in the dict that has no corresponding type will be set on
        the object as its raw value.

        Currently does not support Union types
        '''
        attributes = get_attributes(classType)

        type_hints = get_type_hints(classType.__init__)
        if dataclasses.is_dataclass(classType):
            type_hints.pop("return", None)

        # Create an empty instance of classType
        # Some types (ex: datetime.datetime) prohibit this call
        # and will need a custom deserializer
        cls = object.__new__(classType)

        # Sereialize any field that we can find a type hint for,
        # otherwise set it to the raw primitve value
        for name, value in d.items():
            # Check if an attribute with the given name exists, but overrite
            # the type if it exists in the constructor type_hints
            type = attributes.pop(name) if name in attributes.keys() else None
            type = type_hints.pop(name) if name in type_hints.keys() else type
            cls.__dict__[name] = self.deserialize(value, type) if type else value

        if len(attributes.keys()) + len(type_hints.keys()) > 0:
            # There are attributes or init_parameters that weren't found in the dictionary
            pass

        return cls

    def deserialize_list(self, lst: list, classType: type):
        deserializedList = []
        for value in lst:
            deserializedList.append(self.deserialize(value, classType))

        return deserializedList

    def deserialize_dict(self, d: dict, keyType: type, valueType: type):
        deserializedDict = {}
        for key, value in d.items():
            deserializedKey = self.deserialize(key, keyType)
            deserializedValue = self.deserialize(value, valueType)
            deserializedDict[deserializedKey] = deserializedValue

        return deserializedDict

    def deserialize(self, value: Any, classType: type):
        if value is None:
            # Allow None values
            return None
        if is_primitive(classType):
            return classType(value)
        if is_enum(classType):
            return classType(value)
        if is_optional(classType):
            # If the parameter is optional, unpack the optional type and deserialize that type
            realType = classType.__args__[0]
            return self.deserialize(value, realType)
        if isinstance(classType, GenericAlias):
            typeArgs = classType.__args__
            originType = classType.__origin__
            if originType is list:  # list of some type
                typeArg = typeArgs[0]  # List paramaterization only takes 1 argument
                return self.deserialize_list(value, typeArg)
            else:
                keyType = typeArgs[0]
                valueType = typeArgs[1]
                return self.deserialize_dict(value, keyType, valueType)
        if (deserializer := self.middleware.get(classType, None)) is not None:
            return deserializer(value)

        return self.deserialize_simple_object(value, classType)


default_deserializer = Deserializer(middleware={})
