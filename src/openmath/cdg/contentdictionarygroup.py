from dataclasses import dataclass, field

from .. import OMSymbol

@dataclass
class ContentDictionaryGroup:
    name: str = None
    description: str = None
    version: str = None
    revision: str = None
    url: str = None
    memebers: list = field(default_factory=list)
    includes: list = field(default_factory=list)
    comment: str = field(default=None, repr=False)

    def __getitem__(self, key):
        if type(key) == int:
            return self.definitions[key]

        if type(key) == str:
            for d in self.definitions:
                if d.name == key:
                    return d
            raise KeyError(key)

        raise TypeError(
            "ContentDictionaryGroup indices must be integers or strings"
        )

    def __contains__(self, key):
        if type(key) == str:
            for d in self.definitions:
                if key == d.name:
                    return True
            return False

        if isinstance(key, OMSymbol):
            return (
                key.getCDBase() == self.base
                and key.cd == self.name
                and key.name in self
            )

        return key in definitions

    def symbol(self, key, alsobase=False):
        if key not in self:
            raise KeyError(key)
        return OMSymbol(key, self.name, self.base if alsobase else None)
