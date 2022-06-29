from enum import Enum

class DummyClass():
    def __init__(self, dummyValue: str):
        self.dummyValue = dummyValue

    def __eq__(self, other):
        return self.dummyValue == other.dummyValue

class TestEnum(Enum):
    TEST_1 = 1
    TEST_2 = "Two"
