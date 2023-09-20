from .ombase import OMBase
from ..util import setattrType, setattrOM, assertOM
import xml.etree.ElementTree as ET

class OMBinding(OMBase):
    """Implementation of the OMBinding object

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_compound
    """

    kind = "OMBIND"
    __match_args__ = ("binder", "variables", "object")

    def __init__(self, binder, variables, object_, cdbase=None, id=None):
        setattrType(self, "id", id, (str, type(None)))
        setattrType(self, "cdbase", cdbase, (str, type(None)))
        self.setObject(object_)
        self.setBinder(binder)
        self.setVariables(variables)
        self.variables = variables
        for v in self.variables:
            v.parent = self

    def setObject(self, object_):
        setattrOM(self, "object", object_)

    def setBinder(self, binder):
        setattrOM(self, "binder", binder)

    def setVariables(self, variables):
        for v in variables:
            assertOM(v, ["OMV", "OMATTR"])
            if v.kind == "OMATTR":
                _valueAssert(
                    v.object.kind == "OMV",
                    "Attributed variable binding must be a variable",
                )
            v.parent = self
        self.variables = tuple(variables)

    def toElement(self):
        el = ET.Element(self.kind)
        el.set("id", self.__dict__.get("id"))
        el.set("cdbase", self.__dict__.get("cdbase"))
        el.append(self.binder.toElement())
        variables = ET.Element("OMBVAR")
        for v in self.variables:
            variables.append(v.toElement())
        el.append(variables)
        el.append(self.object.toElement())

        return el
