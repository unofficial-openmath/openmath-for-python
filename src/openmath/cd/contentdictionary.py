from dataclasses import dataclass, field
from typing import List
from .. import OMSymbol
from .symboldefinition import SymbolDefinition


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
    definitions: List[SymbolDefinition] = field(default_factory=list)

    def __getitem__(self, key: int | str | OMSymbol) -> SymbolDefinition:
        if type(key) == int:
            return self.definitions[key]

        if type(key) == str:
            for d in self.definitions:
                if d.name == key:
                    return d
            raise KeyError(key)

        if isinstance(key, OMSymbol):
            if key.getCDBase() not in (self.base, None) or key.cd != self.name:
                raise KeyError(key)
            return self.__getitem__(key.name)

        raise TypeError(
            "ContentDictionary indices must be integers, strings or OMSymbols"
        )

    def __contains__(self, key: str | OMSymbol):
        if type(key) == str:
            for d in self.definitions:
                if key == d.name:
                    return True
            return False

        if isinstance(key, OMSymbol):
            return (
                (key.getCDBase() in (self.base, None))
                and key.cd == self.name
                and key.name in self
            )

        return key in definitions

    def symbol(self, key, alsobase=False):
        if key not in self:
            raise KeyError(key)
        return OMSymbol(key, self.name, self.base if alsobase else None)
