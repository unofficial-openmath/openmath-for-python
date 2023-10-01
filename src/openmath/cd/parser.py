from .contentdictionary import ContentDictionary
from .symboldefinition import SymbolDefinition
import xml.etree.ElementTree as ET

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
