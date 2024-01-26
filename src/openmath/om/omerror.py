from .ombase import OMBase
from ..util import setattrType, setattrOM
import xml.etree.ElementTree as ET


class OMError(OMBase):
    """Implementation of the OMError object

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_compound
    """

    kind = "OME"
    __match_args__ = ("error", "arguments")

    def __init__(self, error, arguments, id=None):
        setattrType(self, "id", id, (str, type(None)))
        self.setError(error)
        self.setArguments(arguments)

    def setError(self, error):
        setattrOM(self, "error", error, "OMS")

    def setArguments(self, arguments):
        for arg in arguments:
            assertOM(arg)
            arg.parent = self
        self.arguments = tuple(arguments)

    def toElement(self):
        el = ET.Element(self.kind)
        el.set("id", self.__dict__.get("id"))
        el.append(self.error.toElement())
        for a in self.arguments:
            el.append(a.toElement())
        return el
