from .ombase import OMBase
from ..util import setattrType
import xml.etree.ElementTree as ET

class OMString(OMBase):
    """Implementation of the OMString object

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_basic
    """

    kind = "OMSTR"
    __match_args__ = ("string",)

    def __init__(self, string, id=None):
        setattrType(self, "id", id, (str, type(None)))
        setattrType(self, "string", string, str)

    def toElement(self):
        el = ET.Element(self.kind)
        el.set("id", self.__dict__.get("id"))
        el.text = self.string
        return el

