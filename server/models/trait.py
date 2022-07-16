
class Trait():
    def __init__(self, trait_type: str, value: str, rarity: float = 0.0):
        self.trait_type = trait_type
        self.value = value
        self.rarity = rarity
    
    def __eq__(self, other):
        return self.trait_type == other.trait_type \
                and self.value == other.value
                #and self.rarity == other.rarity

    def __str__(self):
        return "{}:{}".format(self.trait_type, self.value)