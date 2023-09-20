from .ombase import OMBase
from ..util import setattrType
import xml.etree.ElementTree as ET
import json

class OMForeign(OMBase):
    """Implementation of OMFOREIGN objects

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_json-omforeign---foreign-objects
    """

    kind = "OMFOREIGN"
    __match_args__ = ("foreign", "encoding")

    def __init__(self, foreign, encoding=None, id=None):
        setattrType(self, "id", id, (str, type(None)))
        setattrType(self, "encoding", encoding, (str, type(None)))
        _valueAssert(foreign is not None, "Foreign object can't be None")

    def toElement(self):
        el = ET.Element(self.kind)
        el.set("id", self.__dict__.get("id"))
        el.set("encoding", self.__dict__.get("encoding"))
        if isinstance(self.foreign, ET.Element):
            el.append(self.foreign)
        elif type(self.foreign) is dict:
            el.text = json.dumps(self.foreign)
        else:
            el.text = str(self.foreign)
        return el
