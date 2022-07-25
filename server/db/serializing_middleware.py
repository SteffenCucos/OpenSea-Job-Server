
from datetime import datetime

from .dict_to_class import Deserializer
from .class_to_dict import Serializer


def get_application_serializer():
    def serialize_date(value: object):
        return repr(value)

    return Serializer(
        middleware={
            datetime: serialize_date
        }
    )


def get_application_deserializer():
    def deserialize_date(value: object):
        arg_str = value.split("(")[1]
        arg_str = arg_str.replace(")", "")
        args = arg_str.strip(" ").split(",")
        args = [int(arg) for arg in args]

        return datetime(*args)
        
    return Deserializer(
        middleware={
            datetime: deserialize_date
        }
    )