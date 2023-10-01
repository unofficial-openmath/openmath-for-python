from dataclasses import dataclass, field

from ..om.ombase import OMBase

@dataclass
class SymbolDefinition:
    name: str = None
    description: str = None
    role: str = None
    cmp: list[str] = field(default_factory=list)
    fmp: list[OMBase] = field(default_factory=list)
    examples: list = field(default_factory=list)