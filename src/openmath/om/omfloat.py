from .ombase import OMBase
from ..util import setattrType
import xml.etree.ElementTree as ET


class OMFloat(OMBase):
    """Implementation of the OMFloat object

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_basic
    """

    kind = "OMF"
    __match_args__ = ("float",)

    def __init__(self, float_: float, id=None):
        setattrType(self, "id", id, (str, type(None)))
        setattrType(self, "float", float_, float)

    def toElement(self):
        el = ET.Element(self.kind)
        el.set("id", self.__dict__.get("id"))
        el.text = str(self.float)
        return el
