from . import *
from base64 import b64decode
import xml.etree.ElementTree as ET
import struct
import json


def parse(text):
    """Parse either JSON or XML strings into a mathematical object

    See parseJSON and parseXML
    """
    text = text.lstrip()
    if len(text) > 0:
        if text[0] == "{":
            return parseJSON(text)
        elif text[0] == "<":
            return parseXML(text)

    raise ValueError("Unable to detect encoding")


def parseJSON(text):
    """Parse a JSON string into a mathematical object

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_json-the-json-encoding
    """
    return fromDict(json.loads(text))


def parseXML(text):
    """Parse a XML string into a mathematical object

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_xml
    """
    try:
        return fromElement(ET.fromstring(text))
    except ET.ParseError as e:
        raise ValueError(f"Invalid XML - {e}")


def fromDict(dictionary):
    """Build a mathematical object from a python dictionary

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_json-the-json-encoding
    """
    match (dictionary):

        case {"kind": "OMOBJ", **kwargs}:
            return OMObject(
                fromDict(kwargs["object"]),
                **kwargs,
            )

        case {"kind": "OMI", "integer": x, **kwargs}:
            return OMInteger(int(x), id=kwargs.get("id"))

        case {"kind": "OMI", "decimal": x, **kwargs}:
            return OMInteger(int(x), id=kwargs.get("id"))

        case {"kind": "OMI", "hexadecimal": x, **kwargs}:
            return OMInteger(int(x, 16), id=kwargs.get("id"))

        case {"kind": "OMF", "integer": x, **kwargs}:
            return OMFloat(float(x), id=kwargs.get("id"))

        case {"kind": "OMF", "decimal": x, **kwargs}:
            return OMFloat(float(x), id=kwargs.get("id"))

        case {"kind": "OMF", "hexadecimal": x, **kwargs}:
            return OMFloat(float(x, 16), id=kwargs.get("id"))

        case {"kind": "OMSTR", **kwargs}:
            return OMString(kwargs["string"], id=kwargs.get("id"))

        case {"kind": "OMB", **kwargs}:
            return OMBytearray(kwargs["bytes"], id=kwargs.get("id"))

        case {"kind": "OMA", **kwargs}:
            return OMApplication(
                fromDict(kwargs["applicant"]),
                [fromDict(a) for a in kwargs.get("arguments", [])],
                cdbase=kwargs.get("cdbase"),
                id=kwargs.get("id"),
            )

        case {"kind": "OMV", **kwargs}:
            return OMVariable(kwargs["name"], id=kwargs.get("id"))

        case {"kind": "OMS", **kwargs}:
            return OMSymbol(
                kwargs["name"],
                kwargs["cd"],
                cdbase=kwargs.get("cdbase"),
                id=kwargs.get("id"),
            )

        case {"kind": "OMBIND", **kwargs}:
            return OMBinding(
                fromDict(kwargs["binder"]),
                [fromDict(v) for v in kwargs["variables"]],
                fromDict(kwargs["object"]),
                cdbase=kwargs.get("cdbase"),
                id=kwargs.get("id"),
            )

        case {"kind": "OMATTR", **kwargs}:
            recFromDict = lambda x: (
                fromDict(x)
                if not isinstance(x, (list, tuple, set))
                else tuple(recFromDict(xx) for xx in x)
            )
            return OMAttribution(
                recFromDict(kwargs["attributes"]),
                fromDict(kwargs["object"]),
                kwargs.get("cdbase"),
                id=kwargs.get("id"),
            )

        case {"kind": "OME", **kwargs}:
            return OMError(
                kwargs["error"], kwargs.get("arguments"), id=kwargs.get("id")
            )

        case {"kind": "OMR", "href": href, **kwargs}:
            return OMReference(href, id=kwargs.get("id"))

        case {"kind": "OMFOREIGN", "foreign": foreign, **kwargs}:
            return OMForeign(
                foreign, encoding=kwargs.get("encoding"), id=kwargs.get("id")
            )

        case _:
            raise ValueError("A valid dictionary is required")


def fromElement(elem):
    """Build a mathematical object from a xml.etree.Element

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_xml
    """
    # handle xml namespaces
    if elem.tag[0] == "{":
        [ns, tag] = elem.tag[1:].split("}")
    else:
        ns = None
        tag = elem.tag

    def qname(t):
        return t if ns is None else ("{%s}%s" % (ns, t))

    match tag:
        case "OMOBJ":
            return OMObject(fromElement(elem[0]), **elem.attrib)

        case "OMI":
            if elem.text.strip()[0] == "x":
                return OMInteger(int(elem.text.strip()[1:]), id=elem.attrib.get("id"))
            elif elem.text.strip()[:2] == "-x":
                return OMInteger(-int(elem.text.strip()[2:]), id=elem.attrib.get("id"))
            else:
                return OMInteger(int(elem.text.strip()), id=elem.attrib.get("id"))

        case "OMF":
            if "dec" in elem.attrib:
                return OMFloat(float(elem.attrib["dec"]), id=elem.attrib.get("id"))
            elif "hex" in elem.attrib:
                return OMFloat(
                    struct.unpack("!d", bytes.fromhex(elem.attrib["hex"])),
                    id=elem.attrib.get("id"),
                )
            else:
                raise ValueError("OMF tag requires a 'dec' or 'hex' attribute")

        case "OMS":
            return OMSymbol(
                elem.attrib["name"],
                elem.attrib["cd"],
                elem.attrib.get("cdbase"),
                id=elem.attrib.get("id"),
            )

        case "OMV":
            return OMVariable(elem.attrib["name"], id=elem.attrib.get("id"))

        case "OMSTR":
            return OMString(elem.text, id=elem.attrib.get("id"))

        case "OMB":
            return OMBytearray(b64decode(elem.text), id=elem.attrib.get("id"))

        case "OMA":
            return OMApplication(
                fromElement(elem[0]),
                [fromElement(x) for x in elem[1:]],
                cdbase=elem.attrib.get("cdbase"),
                id=elem.attrib.get("id"),
            )

        case "OMATTR":
            obj = None
            attrs = []
            for child in elem:
                if child.tag == "OMATP":
                    key = None
                    for i, x in enumerate(child):
                        if i % 2 == 0 and key is not None:
                            attrs.append([fromElement(key), fromElement(x)])
                        else:
                            key = x
                else:
                    obj = fromElement(child)
            return OMAttribution(
                attrs, obj, cdbase=elem.attrib.get("cdbase"), id=elem.attrib.get("id")
            )

        case "OME":
            return OMError(
                fromElement(elem[0]),
                [fromElement(x) for x in elem[1:]],
                id=elem.attrib.get("id"),
            )

        case "OMBIND":
            return OMBinding(
                fromElement(elem[0]),
                [fromElement(x) for x in elem.find(qname("OMBVAR"))],
                fromElement(elem[2]),
                id=elem.attrib.get("id"),
            )

        case "OMR":
            return OMReference(elem.attrib["href"], id=elem.attrib.get("id"))

        case "OMFOREIGN":
            childcount = len(list(elem))
            if childcount > 1:
                raise ValueError("OMFOREIGN objects can't have multiple children")
            return OMForeign(
                elem[0] if childcount == 1 else elem.text,
                elem.attrib.get("encoding"),
                id=elem.attrib.get("id"),
            )

        case _:
            raise ValueError("A valid ElementTree is required: %s" % elem)
