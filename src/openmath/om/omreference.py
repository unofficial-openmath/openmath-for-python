
from .ombase import OMBase
from ..util import setattrType
import xml.etree.ElementTree as ET
import urllib.request, urllib.error

class OMReference(OMBase):
    """Implementation of references for structure sharing

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_json-omrs-and-structure-sharing
    """

    kind = "OMR"

    def __init__(self, href, id=None):
        setattrType(self, "id", id, (str, type(None)))
        setattrType(self, "href", href, str)

    def resolve(self):
        # Decompose URI into URL and ID
        target = None
        uri = self.href.split("#")
        url = uri[0]
        id = uri[1] if len(uri) == 2 else None

        # Get the whole mathematical object first
        if url == "":  # relative reference
            target = self.getRoot()
            if target is None:
                raise RuntimeError("Could not resolve " + self.href)

        else:  # external reference
            objectStr = None

            if url.startswith("http"):  # remote reference
                try:
                    with urllib.request.open(url) as urlh:
                        objectStr = urlh.read()
                except urllib.error.URLError as e:
                    raise RuntimeError("Could not resolve %s (%s)" % (self.href, e))

            else:  # local reference
                try:
                    with open(url, "r") as fh:
                        objectStr = fh.read()
                except (FileNotFoundError, IsADirectoryError) as e:
                    raise RuntimeError("Could not resolve %s (%s)" % (self.href, e))

            if url.endswith(".om") or url.endswith(".xml"):
                target = parseXML(objectStr)
            elif url.endswith(".json"):
                target = parseJSON(objectStr)
            else:
                target = parse(objectStr)

        # Now, with the mathematical object, get the sub-object by ID
        if id:
            target = target.getByID(id)
            if target is None:
                raise RuntimeError("Could not resolve ID " + id)

        # Finally, resolve it and return it
        if self.parent is not None:
            self.parent._replace(self, target)

        return target

    def toElement(self):
        el = ET.Element(self.kind)
        el.set("id", self.__dict__.get("id"))
        el.set("href", self.href)
        return el

