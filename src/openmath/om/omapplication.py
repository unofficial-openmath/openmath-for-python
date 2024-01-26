from .ombase import OMBase
from .omsymbol import OMSymbol
from ..util import setattrType, setattrOM, assertOM
import xml.etree.ElementTree as ET

class OMApplication(OMBase):
    """Implementation of the OMApplication object

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_compound
    """

    kind = "OMA"
    __match_args__ = ("applicant", "arguments")

    def __init__(self, applicant: OMSymbol, arguments, cdbase: str = None, id=None):
        setattrType(self, "id", id, (str, type(None)))
        setattrType(self, "cdbase", cdbase, (str, type(None)))
        self.setApplicant(applicant)
        self.setArguments(arguments)

    def setApplicant(self, applicant):
        # The standard doesn't specify the kind of the applicant
        setattrOM(self, "applicant", applicant)

    def setArguments(self, arguments):
        for arg in arguments:
            assertOM(arg)
            arg.parent = self
        self.arguments = tuple(arguments)

    def toElement(self):
        el = ET.Element(self.kind)
        el.set("id", self.__dict__.get("id"))
        el.set("cdbase", self.__dict__.get("cdbase"))
        el.append(self.applicant.toElement())
        for a in self.arguments:
            el.append(a.toElement())
        return el
