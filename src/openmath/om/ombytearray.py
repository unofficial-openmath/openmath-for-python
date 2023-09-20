from .ombase import OMBase
from ..util import setattrType
from base64 import b64encode
import xml.etree.ElementTree as ET

class OMBytearray(OMBase):
    """Implementation of the OMBytearray object

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_basic
    """

    kind = "OMB"
    __match_args__ = ("bytes",)

    def __init__(self, bytes_: list, id=None):
        setattrType(self, "id", id, (str, type(None)))
        self.bytes = bytes(bytes_)

    def toElement(self):
        el = ET.Element(self.kind)
        el.set("id", self.__dict__.get("id"))
        el.text = b64encode(self.bytes).decode("ascii")

