from .om.ombase import OMBase


class _OMFound(BaseException):
    def __init__(self, object_):
        self.object = object_


def assertType(x, types):
    if not isinstance(x, types):
        istype = type(types) is type
        types_str = types.__name__ if istype else " or ".join(t.__name__ for t in types)
        raise TypeError("Expected %s, but got %s" % (types_str, type(x).__name__))


def setattrType(obj, attr, value, types):
    assertType(value, types)
    setattr(obj, attr, value)


def setattrOM(obj, attr, value, kinds=None):
    assertOM(value, kinds)
    setattr(obj, attr, value)
    value.parent = obj


def valueAssert(condition, msg):
    if not condition:
        raise ValueError(msg)


def isOM(x, kinds=None):
    if not isinstance(x, OMBase):
        return False
    if kinds is not None and type(kinds) is not list:
        kinds = [kinds]

    return kinds is None or x.kind in kinds


def assertOM(x, kinds=None):
    if not isOM(x):
        raise TypeError("Expected an OM object, but got " + type(x).__name__)

    if kinds is not None and type(kinds) is not list:
        kinds = [kinds]

    if kinds is not None and x.kind not in kinds:
        raise TypeError("Expected %s object, but got %s" % (" or ".join(kinds), x.kind))
