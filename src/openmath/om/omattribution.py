from .ombase import OMBase
from ..util import setattrType, setattrOM, assertType, valueAssert, assertOM
import xml.etree.ElementTree as ET


class OMAttribution(OMBase):
    """Implementation of the OMAttribution object

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_compound
    """

    kind = "OMATTR"
    __match_args__ = ("attributes", "object")

    def __init__(self, attributes, object_, cdbase=None, id=None):
        setattrType(self, "id", id, (str, type(None)))
        setattrType(self, "cdbase", cdbase, (str, type(None)))
        self.setObject(object_)
        self.setAttributes(attributes)

    def setObject(self, object_):
        setattrOM(self, "object", object_)

    def setAttributes(self, attrs):
        for attr in attrs:
            assertType(attr, (tuple,list))
            valueAssert(len(attr) == 2, "Attributes must be two values")
            assertOM(attr[0], "OMS")
            assertOM(attr[1])
            attr[0].parent = self
            attr[1].parent = self
        self.attributes = tuple(attrs)

    def toElement(self):
        el = ET.Element(self.kind)
        el.set("id", self.__dict__.get("id"))
        el.set("cdbase", self.__dict__.get("cdbase"))
        attrs = ET.Element("OMATP")
        for a, b in self.attributes:
            attrs.append(a.toElement())
            attrs.append(b.toElement())
        el.append(attrs)
        el.append(self.object.toElement())
        return el
