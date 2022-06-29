import pytest

from server.models.token import Token
from server.models.trait import Trait

from .serialization_helpers import (
    DummyClass,
    TestEnum
)

from server.db.dict_to_class import deserialize

PRIMITIVE_DATA = [
    (True, bool),
    (1, int),
    (1.5, float),
    ("String", str),
]
@pytest.mark.parametrize("value, type", PRIMITIVE_DATA)
def test_deserialize_primitive(value, type):
    deserialized = deserialize(value, type)
    assert deserialized == value

ENUM_DATA = [
    (1, TestEnum.TEST_1),
    ("Two", TestEnum.TEST_2)
]
@pytest.mark.parametrize("value, expected", ENUM_DATA)
def test_deserialize_enum(value, expected):
    print(value, expected)
    assert deserialize(value, TestEnum) == expected

def test_deserialize_list():
    lst = [1, 2, 3]
    expected = [1, 2, 3]
    assert deserialize(lst, list[int]) == expected

def test_deserialize_dict():
    dct = {"Key": "Value"}
    expected = {"Key": "Value"}
    assert deserialize(dct, dict[str,str]) == expected

def test_deserialize_object():
    dct = {"dummyValue": "Value"}
    expected = DummyClass("Value")
    deserialized = deserialize(dct, DummyClass)
    assert isinstance(deserialized, DummyClass)
    assert deserialize(dct, DummyClass) == expected

def test_deserialize_token():
    tokenData = {
        "success": True,
        "_id": "1",
        "num": 1,
        "url": "urlString",
        "traits": [
            {
                "trait_type": "size",
                "value": "10"
            }
        ]
    }

    expected = Token(success=True, num=1, url="urlString", traits=[Trait(trait_type="size", value="10")])
    deserialized = deserialize(tokenData, Token)
    assert isinstance(deserialized, Token)
    assert deserialized == expected

def test_deserialize_class_with_optional_field():
    pass
    