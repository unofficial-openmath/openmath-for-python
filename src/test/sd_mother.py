from openmath.om.ombase import OMBase
from openmath.cd import *
from random import randint, choice
from typing import List

_symbol_roles = [
    "application",
    "binder",
    "attribution",
    "semantic_attribution",
    "error",
    "constant",
]


def of(
    name: str = "test_sd_%04d" % randint(0, 999),
    description: str = "symbol description",
    role: str = choice(_symbol_roles),
    cmp: List[str] = [],
    fmp: List[OMBase] = [],
    examples: list = [],
):
    return SymbolDefinition(
        name=name,
        description=description,
        role=role,
        cmp=cmp,
        fmp=fmp,
        examples=examples,
    )
