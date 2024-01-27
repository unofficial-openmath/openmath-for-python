from dataclasses import dataclass, field
from typing import List

from ..om.ombase import OMBase


@dataclass(frozen=True)
class SymbolDefinition:
    name: str = None
    description: str = None
    role: str = None
    cmp: List[str] = field(default_factory=list)
    fmp: List[OMBase] = field(default_factory=list)
    examples: list = field(default_factory=list)
