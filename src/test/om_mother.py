from openmath import *
from random import randint, randbytes, random, choice

map = {}

def of(kind: str, **kargs):
    return map[kind](**kargs)

def genOMobject():
    return of(choice(map.keys()))

def _genOMinteger(value=randint(-1000, 1000)):
    return OMInteger(value)

def _genOMstring(value=choice(["foo","bar","baz"])):
    return OMString(value)

def _genOMbytearray(value=randbytes(8)):
    return OMBytearray(value)

def _genOMfloat(value=random()):
    return OMFloat(value)

def _genOMsymbol(name=choice([
        "sym_foo",
        "sym_bar",
        "sym_baz",
    ]), cd="test_cd"):
    return OMSymbol(name, cd)

def _genOMvariable(name=choice([
        "var_foo",
        "var_bar",
        "var_baz",
    ])):
    return OMVariable(name)

def _genOMapplication(symbol=_genOMsymbol(), args=()):
    return OMApplication(symbol, args)

def _genOMbinding(
        symbol=_genOMsymbol(), 
        variables=(_genOMvariable(), _genOMvariable()),
        object_=_genOMsymbol()
    ):
    return OMBinding(symbol, variables, object_)

def _genOMattribution(
        object_=_genOMsymbol(),
        attributes=((_genOMsymbol(), _genOMstring()),)
    ):
    return OMAttribution(attributes, object_)

map = {
    OMInteger.kind: _genOMinteger,
    OMString.kind: _genOMstring,
    OMFloat.kind: _genOMfloat,
    OMBytearray.kind: _genOMbytearray,
    OMSymbol.kind: _genOMsymbol,
    OMApplication.kind: _genOMapplication,
    OMVariable.kind: _genOMvariable,
    OMBinding.kind: _genOMbinding,
    OMAttribution.kind: _genOMattribution,
    # OMReference.kind: genOMreference,
    # OMError.kind: genOMerror,
    # OMForeign.kind: genOMforeign,
}