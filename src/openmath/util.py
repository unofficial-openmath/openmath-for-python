from .om.ombase import OMBase

class _OMFound(BaseException):
    def __init__(self, object_):
        self.object = object_


def removeNoneAttrib(elem):
    """Remove None attributes from XML tree"""
    elem.attrib = {k: elem.attrib[k] for k in elem.attrib if elem.attrib[k] is not None}
    for subelem in elem:
        removeNoneAttrib(subelem)


def assertType(x, types):
    if not isinstance(x, types):
        raise ValueError("Expected %s, but got %s" % (" or ".join(t.__name__ for t in types), type(x).__name__))


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
        raise ValueError("Expected an OM object, but got "+type(x).__name__)

    if kinds is not None and type(kinds) is not list:
        kinds = [kinds]

    if kinds is not None and x.kind not in kinds:
        raise ValueError(
            "Expected %s object, but got %s" % (" or ".join(kinds), x.kind)
        )