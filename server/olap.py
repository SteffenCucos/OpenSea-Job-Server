

from dataclasses import dataclass


@dataclass
class Member:
    name: str
    parent: 'Member'
    dimension: 'Dimension'
    children: list['Member'] = None

    def is_leaf(self):
        return len(self.children) == 0

    def is_root(self):
        return self.parent is None

@dataclass
class Dimension:
    name: str
    roots: list[Member] = []

    def insert_root(self, member: Member):
        self.roots.append(member)

        
@dataclass
class Intersection:
    value: int
    members: list[Member]


@dataclass
class Slice:
    members: list[Member]