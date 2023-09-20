from .ombase import OMBase
from ..util import setattrType
import xml.etree.ElementTree as ET

class OMSymbol(OMBase):
    """Implementation of the OMSymbol object

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_basic
    """

    kind = "OMS"
    __match_args__ = ("name", "cd")

    def __init__(self, name: str, cd: str, cdbase=None, id=None):
        setattrType(self, "id", id, (str, type(None)))
        setattrType(self, "cdbase", cdbase, (str, type(None)))
        setattrType(self, "cd", cd, str)
        setattrType(self, "name", name, str)

    def toElement(self):
        el = ET.Element(self.kind)
        el.set("id", self.__dict__.get("id"))
        el.set("name", self.name)
        el.set("cd", self.cd)
        if self.cdbase is not None:
            el.set("cdbase", self.cdbase)
        return el
