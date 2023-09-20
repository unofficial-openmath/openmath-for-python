from .ombase import OMBase
from ..util import setattrType
import xml.etree.ElementTree as ET

class OMVariable(OMBase):
    """Implementation of the OMVariable object

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_basic
    """

    kind = "OMV"
    __match_args__ = ("name",)

    def __init__(self, name: str, id=None):
        setattrType(self, "id", id, (str, type(None)))
        setattrType(self, "name", name, str)

    def toElement(self):
        el = ET.Element(self.kind)
        el.set("id", self.__dict__.get("id"))
        el.set("name", self.name)
        return el

