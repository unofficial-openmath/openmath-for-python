from .ombase import OMBase
from ..util import setattrType, setattrOM
import xml.etree.ElementTree as ET


class OMObject(OMBase):
    """Implementation of the OpenMath object constructor OMOBJ

    Arguments:
        object -- The OpenMath object

    Keyword arguments:
        xmlns -- XML namespace, usually "http://www.openmath.org/OpenMath"
        version -- OpenMath version (default="2.0")
        cdbase -- Base CD URI (default=None)
    """

    kind = "OMOBJ"
    __match_args__ = ("object",)

    def __init__(self, object_, **kwargs):
        self.xmlns = None
        self.version = "2.0"
        self.cdbase = None
        self.__dict__.update(kwargs)
        self.setObject(object_)

    def setObject(self, object_):
        setattrOM(self, "object", object_)

    def toElement(self):
        el = ET.Element(self.kind)
        el.set("xmlns", self.__dict__.get("xmlns"))
        el.set("version", self.__dict__.get("version"))
        el.set("cdbase", self.__dict__.get("cdbase"))
        el.set("id", self.__dict__.get("id"))
        el.append(self.object.toElement())
        return el
