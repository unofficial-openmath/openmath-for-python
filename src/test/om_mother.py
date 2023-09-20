from openmath import *
from random import randint, randbytes, random, choice

map = {}

def of(kind: str, **kargs):
    return map[kind](**kargs)

def genOMobject():
    return of(choice(map.keys()))

def genOMinteger(value=randint(-1000, 1000)):
    return OMInteger(value)

def genOMstring(value=choice(["foo","bar","baz"])):
    return OMString(value)

def genOMbytearray(value=randbytes(8)):
    return OMBytearray(value)

def genOMfloat(value=random()):
    return OMFloat(value)

def genOMsymbol(name=choice([
        "sym_foo",
        "sym_bar",
        "sym_baz",
    ]), cd="test_cd"):
    return OMSymbol(name, cd)

def genOMvariable(name=choice([
        "var_foo",
        "var_bar",
        "var_baz",
    ])):
    return OMVariable(name)

def genOMapplication(symbol=genOMsymbol(), args=()):
    return OMApplication(symbol, args)

def genOMbinding(
        symbol=genOMsymbol(), 
        variables=(genOMvariable(), genOMvariable()),
        object_=genOMsymbol()
    ):
    return OMBinding(symbol, variables, object_)

def genOMattribution(
        object_=genOMsymbol(),
        attributes=((genOMsymbol(), genOMstring()),)
    ):
    return OMAttribution(attributes, object_)

map = {
    OMInteger.kind: genOMinteger,
    OMString.kind: genOMstring,
    OMFloat.kind: genOMfloat,
    OMBytearray.kind: genOMbytearray,
    OMSymbol.kind: genOMsymbol,
    OMVariable.kind: genOMvariable,
    OMApplication.kind: genOMapplication,
    OMVariable.kind: genOMvariable,
    OMBinding.kind: genOMbinding,
    OMAttribution.kind: genOMattribution,
    # OMReference.kind: genOMreference,
    # OMError.kind: genOMerror,
    # OMForeign.kind: genOMforeign,
}