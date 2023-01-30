import json
import openmath as om
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, asdict

CDBASEOFFICIAL = "http://www.openmath.org/cd"


@dataclass
class SymbolDefinition:
    name: str = None
    description: str = None
    role: str = None
    cmp: list[str] = field(default_factory=list)
    fmp: list[om._OMBase] = field(default_factory=list)
    examples: list = field(default_factory=list)


@dataclass
class ContentDictionary:
    name: str = None
    description: str = None
    revision: str = None
    review: str = None
    version: str = None
    status: str = None
    base: str = None
    url: str = None
    comment: str = field(default=None, repr=False)
    definitions: list = field(default_factory=list)

    def __getitem__(self, key):
        if type(key) == int:
            return self.definitions[key]

        if type(key) == str:
            for d in self.definitions:
                if d.name == key:
                    return d
            raise KeyError(key)

        if isinstance(key, om.OMSymbol):
            if key.getCDBase != self.cdbase or k.cd != self.name:
                raise KeyError(key)

        raise TypeError(
            "ContentDictionary indices must be integers, strings or openmath.OMSymbol"
        )

    def __contains__(self, key):
        if type(key) == str:
            for d in self.definitions:
                if key == d.name:
                    return True
            return False

        if isinstance(key, om.OMSymbol):
            return (
                key.getCDBase() == self.base
                and key.cd == self.name
                and key.name in self
            )

        return key in definitions

    def symbol(self, key, alsobase=False):
        if key not in self:
            raise KeyError(key)
        return om.OMSymbol(key, self.name, self.base if alsobase else None)


def parseXML(text):
    """Parse a XML string into a Content Dictionary

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#cha_cd
    """
    return fromTree(ET.fromstring(text))


def fromTree(tree):
    """Build a Content Dictionary from a xml.etree.Element

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#cha_cd
    """
    root = tree.getroot()
    # handle xml namespaces
    if root.tag[0] == "{":
        [ns, tag] = root.tag[1:].split("}")
    else:
        ns = None
        tag = root.tag

    def qname(t):
        return t if ns is None else ("{%s}%s" % (ns, t))

    if tag != "CD":
        raise ValueError("Root tag must be CD, not " + tag)

    cd = ContentDictionary()
    strfields = [
        ("CDName", "name"),
        ("Description", "description"),
        ("CDReviewDate", "review"),
        ("CDDate", "revision"),
        ("CDVersion", "version"),
        ("CDStatus", "status"),
        ("CDBase", "base"),
        ("CDURL", "url"),
        ("CDComment", "comment"),
    ]
    for tag, field in strfields:
        setattr(cd, field, root.find(qname(tag)).text.strip())

    for element in root.findall(qname("CDDefinition")):
        symboldef = SymbolDefinition()
        strfields = [
            ("Name", "name"),
            ("Description", "description"),
            ("Role", "role"),
        ]
        for tag, field in strfields:
            setattr(symboldef, field, element.find(qname(tag)).text.strip())
        symboldef.cmp = [x.text for x in element.findall(qname("CMP"))]
        symboldef.fmp = [x.text for x in element.findall(qname("FMP"))]
        symboldef.examples = [
            (x.text, [om.fromElement(c) for c in x])
            for x in element.findall(qname("Example"))
        ]
        cd.definitions.append(symboldef)

    return cd


tree = ET.parse("arith1.cd")
cd = fromTree(tree)
print(cd[1].description)
print([x.description for x in cd if x.name == "minus"])
print("sum" in cd)
print(om.OMSymbol("sum", "arith1", cdbase=CDBASEOFFICIAL) in cd)
print(om.OMSymbol("productt", "arith1", cdbase=CDBASEOFFICIAL) in cd)
print(cd.symbol("unary_minus", alsobase=True))
