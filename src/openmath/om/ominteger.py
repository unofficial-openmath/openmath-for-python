from .ombase import OMBase
from ..util import setattrType
import xml.etree.ElementTree as ET


class OMInteger(OMBase):
    """Implementation of the OMInteger object

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_basic
    """

    kind = "OMI"
    __match_args__ = ("integer",)

    def __init__(self, integer: int, id=None):
        setattrType(self, "id", id, (str, type(None)))
        setattrType(self, "integer", integer, int)

    def toElement(self):
        el = ET.Element(self.kind)
        el.set("id", self.__dict__.get("id"))
        el.text = str(self.integer)
        return el
