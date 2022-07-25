import pytest

from .serialization_helpers import (
    DummyClass,
    TestEnum
)

from server.db.class_to_dict import default_serializer as serializer
from server.models.token import Token
from server.models.trait import Trait

PRIMITIVE_DATA = [
    # Primitives can ber serialized to themselves
    (True, True),
    (1, 1),
    (1.5, 1.5),
    ("String", "String"),
]
@pytest.mark.parametrize("value, expected", PRIMITIVE_DATA)
def test_serialize_primitive(value, expected):
    serialized = serializer.serialize(value)
    assert serialized == expected

ENUM_DATA = [
    (TestEnum.TEST_1, 1),
    (TestEnum.TEST_2, "Two")
]
@pytest.mark.parametrize("value, expected", ENUM_DATA)
def test_serialize_enum(value, expected):
    # Enums should be serialized to the serialization of their value
    # even if that value is itself a class
    assert serializer.serialize(value) == expected

def test_serialize_list():
    lst = [1, 2, 3]
    expected = [1, 2, 3]
    assert serializer.serialize(lst) == expected

def test_serialize_dict():
    dct = {"Key": "Value"}
    expected = {"Key": "Value"}
    assert serializer.serialize(dct) == expected

def test_serialize_object():
    obj = DummyClass("Some Value")
    expected = {"dummyValue":"Some Value"}
    assert serializer.serialize(obj) == expected

def test_serialize_token():
    token = Token(success=True, num=1, url="urlString", traits=[Trait(trait_type="size", value="10")])
    expected = {
        "success": True,
        "_id": "1",
        "num": 1,
        "url": "urlString",
        "error": None,
        "rarity": None,
        "traits": [
            {
                "trait_type": "size",
                "value": "10",
                "rarity": None
            }
        ]
    }
    assert serializer.serialize(token) == expected
    