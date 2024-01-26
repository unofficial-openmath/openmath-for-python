from dataclasses import dataclass, field

from .. import OMSymbol


@dataclass
class ContentDictionary:
    name: str = None
    description: str = None
    revision: str = None
    review: str = None
    version: str = None
    status: str = None
    base: str = None
    url: str = None
    comment: str = field(default=None, repr=False)
    definitions: list = field(default_factory=list)

    def __getitem__(self, key):
        if type(key) == int:
            return self.definitions[key]

        if type(key) == str:
            for d in self.definitions:
                if d.name == key:
                    return d
            raise KeyError(key)

        if isinstance(key, OMSymbol):
            if key.getCDBase != self.cdbase or key.cd != self.name:
                raise KeyError(key)
            return __getitem__[key.name]

        raise TypeError(
            "ContentDictionary indices must be integers, strings or openmath.OMSymbol"
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
