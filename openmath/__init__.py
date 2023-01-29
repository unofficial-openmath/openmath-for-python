"""OpenMath standard implementation

This module provides class and functions to
work with OpenMath mathematical objects
"""
import json
import xml.etree.ElementTree as ET
from copy import deepcopy
from xml.dom import minidom


def isOM(x, kinds=None):
    if not isinstance(x, _OMBase):
        return False
    if kinds is not None and type(kinds) is not list:
        kinds = [kinds]

    return kinds is None or x.kind in kinds


def assertOM(x, kinds=None):
    if not isOM(x):
        raise ValueError("Expected an OM object")

    if kinds is not None and type(kinds) is not list:
        kinds = [kinds]

    if kinds is not None and x.kind not in kinds:
        raise ValueError(
            "Expected %s object, but got %s" % (" or ".join(kinds), x.kind)
        )


def _assertType(x, types):
    if not isinstance(x, types):
        raise ValueError("Expected %s, but got %s" % ("or".join(types), type(x)))


def _setattrType(obj, attr, value, types):
    _assertType(value, types)
    setattr(obj, attr, value)


def _setattrOM(obj, attr, value, kinds=None):
    assertOM(value, kinds)
    setattr(obj, attr, value)
    value.parent = obj


def _valueAssert(condition, msg):
    if not condition:
        raise ValueError(msg)


class _OMBase:
    """Base class for OpenMath objects"""

    kind = None
    parent = None

    def toDict(self) -> dict:
        """Get a dictionary with the attributes of the math object"""
        d = self.__dict__
        return {
            "kind": self.kind,
            **{k: d[k] for k in sorted(d.keys()) if d[k] is not None and k != "parent"},
        }

    def toJSON(self, *args, **kwargs) -> str:
        """Serialize the object to a JSON string

        All arguments are passed directly to the json.dumps function
        """
        return json.dumps(self, default=_OMBase.toDict, *args, **kwargs)

    def toElement(self):
        """Return the object as an XML element from the xml.etree module"""
        raise NotImplementedError("OpenMath XML encoding for " + self.kind)

    def toXML(self, *args, **kwargs) -> str:
        """Serialize the object to a XML string

        The arguments can be any of those accepted by either the
        xml.etree.ElementTree.toString function or minidom.prettyxml
        """
        # First get the XML string itself
        tostringaccepted = [  # named args taken by ET.tostring
            "encoding",
            "method",
            "xml_declaration",
            "default_namespace",
            "short_empty_elements",
        ]
        tostringkwargs = {k: kwargs[k] for k in kwargs if k in tostringaccepted}
        root = self.toElement()
        root.set("xmlns", "http://www.openmath.org/OpenMath")
        xmlstr = ET.tostring(root, *args, **tostringkwargs).decode("utf8")

        # Then prettify it, if necessary
        toprettyaccepted = [  # named args taken by minidom.toprettyxml
            "indent",
            "newl",
            "encoding",
            "standalone",
        ]
        toprettykwargs = {k: kwargs[k] for k in kwargs if k in toprettyaccepted}
        if any(
            x in kwargs for x in toprettykwargs if x != "encoding"
        ):  # because encoding is named arg in common with ET.tostring
            if type(kwargs.get("indent")) is int:
                toprettykwargs["indent"] *= " "
            xmlstr = minidom.parseString(xmlstr).toprettyxml(**toprettykwargs)

        return xmlstr

    def apply(self, f, accumulator=None) -> None:
        """Traverse the object tree and apply a function to each node

        Arguments:
            f -- function to be applied
            accumulator -- list of visited nodes (used to prevent cycles)
        """
        if accumulator is None:
            accumulator = []

        if self in accumulator:
            return

        accumulator.append(self)
        # First apply to self and then to attributes
        f(self)
        d = self.toDict()

        for k in list(d.keys())[::-1]:  # reversed keys
            value = d[k]
            if isOM(value):  # level of depth 0
                value.apply(f, accumulator)

            elif type(value) is list:  # level of depth 1
                for subval in value:
                    if isOM(subval):
                        subval.apply(f, accumulator)
                    elif type(subval) is tuple:  # level of depth 2 (for OMATTR)
                        for subsubval in subval:
                            if isOM(subsubval):
                                subsubval.apply(f, accumulator)

    def getCDBase(self) -> str:
        """Get a valid cdbase attribute from an object or its ancestors"""
        if "cdbase" not in dir(self) or self.cdbase is None:
            if self.parent is None:
                return None
            return self.parent.getCDBase()
        return self.cdbase

    def clone(self):
        "Return a deep copy of the object."
        return deepcopy(self)

    def replace(self, obj1, obj2) -> None:
        """Replace the instances of an object with another one

        Identical instances are replaced, not equivalent ones

        Arguments:
        obj1 -- object to be replaced
        obj2 -- object to replace
        """
        d = self.__dict__
        for k in d:
            if obj1 is d[k]:  # depth level 1
                d[k] = obj2.clone()
                d[k].parent = self
            elif type(d[k]) is list:  # depth level 1
                for i, elem in enumerate(d[k]):
                    if obj1 is elem:
                        d[k][i] = obj2.clone()
                        d[k][i].parent = self
                    elif type(elem) is tuple:  # depth level 2 (for OMATTR)
                        elem = tuple(
                            obj2.clone() if subelem is obj1 else subelem
                            for subelem in elem
                        )

    def __eq__(self, other) -> bool:
        """Return true if all attributes are present and equal in both instances"""
        # The object must be OM
        if not isOM(other):
            return False

        a = self.toDict()
        b = other.toDict()
        allkeys = set([*a, *b])

        # The cdbase must be the same
        allkeys.remove("cdbase")
        if self.getCDBase() != self.getCDBase():
            return False

        def compare(x, y):
            """Compare a single value that may be a list"""
            ret = None
            if type(x) is list and type(y) is list:
                ret = len(x) == len(y) and all(
                    compare(x[i], y[i]) for i in range(len(x))
                )
            else:
                ret = x == y
            return ret

        return all(compare(a.get(k), b.get(k)) for k in allkeys)

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)


class OMObject(_OMBase):
    """Implementation of the OpenMath object constructor OMOBJ

    Arguments:
        object -- The OpenMath object

    Keyword arguments:
        xmlns -- XML namespace, usually "http://www.openmath.org/OpenMath"
        version -- OpenMath version (default="2.0")
        cdbase -- Base CD URI (default=None)
    """

    kind = "OMOBJ"

    def __init__(self, object, **kwargs):
        _setattrOM(self, "object", object)
        self.xmlns = None
        self.version = "2.0"
        self.cdbase = None
        self.__dict__.update(kwargs)

    def toElement(self):
        el = ET.Element(self.kind)
        el.set("xmlns", self.xmlns) if self.xmlns is not None else None
        el.set("version", self.version) if self.version is not None else None
        el.set("cdbase", self.cdbase) if self.cdbase is not None else None
        el.append(self.object.toElement())
        return el


class OMInteger(_OMBase):
    """Implementation of the Integer object

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_basic
    """

    kind = "OMI"

    def __init__(self, integer: int):
        _setattrType(self, "integer", integer, int)

    def toElement(self):
        el = ET.Element(self.kind)
        el.text = str(self.integer)
        return el


class OMFloat(_OMBase):
    """Implementation of the Float object

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_basic
    """

    kind = "OMF"

    def __init__(self, float_: float):
        _setattrType(self, "float", float_, float)

    def toElement(self):
        el = ET.Element(self.kind)
        el.text = str(self.float)
        return el


class OMString(_OMBase):
    """Implementation of the String object

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_basic
    """

    kind = "OMSTR"

    def __init__(self, string):
        _setattrType(self, "string", string, str)

    def toElement(self):
        el = ET.Element(self.kind)
        el.text = self.string
        return el


class OMBytearray(_OMBase):
    """Implementation of the Bytearray object

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_basic
    """

    kind = "OMB"

    def __init__(self, bytes_: list):
        _assertType(bytes_, list)
        for x in bytes_:
            _assertType(x, int)
            _valueAssert(x >= 0 and x < 256, "byte value too high")
        self.bytes = bytes_


class OMSymbol(_OMBase):
    """Implementation of the Symbol object

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_basic
    """

    kind = "OMS"

    def __init__(self, name: str, cd: str, cdbase: str|None = None):
        _setattrType(self, "cdbase", cdbase, [str, type(None)])
        _setattrType(self, "cd", cd, str)
        _setattrType(self, "name", name, str)

    def toElement(self):
        el = ET.Element(self.kind)
        el.set("name", self.name)
        el.set("cd", self.cd)
        if self.cdbase is not None:
            el.set("cdbase", self.cdbase)
        return el


class OMVariable(_OMBase):
    """Implementation of the Variable object

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_basic
    """

    kind = "OMV"

    def __init__(self, name: str):
        _setattrType(self, "name", name, str)

    def toElement(self):
        el = ET.Element(self.kind)
        el.set("name", self.name)
        return el


class OMApplication(_OMBase):
    """Implementation of the Application object

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_compound
    """

    kind = "OMA"

    def __init__(self, applicant: OMSymbol, arguments: list, cdbase: str=None):
        _setattrType(self, "cdbase", cdbase, [str, type(None)])
        # The standard doesn't specify the kind of the applicant
        _setattrOM(self, "applicant", applicant)
        _assertType(arguments, list)
        for arg in arguments:
            assertOM(arg)

        self.arguments = arguments
        for a in self.arguments:
            a.parent = self
        
    def insertArg(index, arg):
        _assertOM(arg)
        arg.parent = self
        self.arguments.insert(index, arg)

    def appendArg(arg):
        _assertOM(arg)
        arg.parent = self
        self.arguments.append(arg)

    def isValid(self):
        return (
            self.hasValidCDBase()
            and self.applicant.isValid()
            and all(a.isValid() for a in self.arguments)
        )

    def toElement(self):
        el = ET.Element(self.kind)
        if self.cdbase is not None:
            el.set("cdbase", self.cdbase)
        el.append(self.applicant.toElement())
        for a in self.arguments:
            el.append(a.toElement())
        return el


class OMAttribution(_OMBase):
    """Implementation of the Attribution object

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_compound
    """

    kind = "OMATTR"

    def __init__(self, attributes, object, cdbase=None):
        self.cdbase = attributes
        self.attributes = attributes
        for pair in self.attributes:
            for elem in pair:
                elem.parent = self
        self.object = object
        object.parent = self

    def isValid(self):
        return (
            self.hasValidCDBase()
            and self.object.isValid()
            and all(
                isinstance(a, Symbol) and a.isValid() and b.isValid()
                for [a, b] in attributes
            )
        )

    def toElement(self):
        el = ET.Element(self.kind)
        if self.cdbase is not None:
            el.set("cdbase", self.cdbase)
        attrs = ET.Element("OMATP")
        for [a, b] in self.attributes:
            attrs.append(a.toElement(), b.toElement())
        el.append(attrs)
        el.append(self.object.toElement())
        return el


class OMBinding(_OMBase):
    """Implementation of the Binding object

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_compound
    """

    kind = "OMBIND"

    def __init__(self, binder, variables, object, cdbase=None):
        self.cdbase = cdbase
        self.binder = binder
        self.variables = variables
        self.object = object
        binder.parent = self
        for v in self.variables:
            v.parent = self
        object.parent = self

    def isValid(self):
        if len(self.variables) == 0 or (
            self.cdbase is not None and type(self.cdbase) is not str
        ):
            return False
        for v in self.variables:
            isVariable = type(v) is Variable
            isAttributedVariable = type(v) is Attribution and type(v.object) is Variable
            if not isVariable and not isAttributedVariable:
                return False
        return self.hasValidCDBase()

    def toElement(self):
        el = ET.Element(self.kind)
        if self.cdbase is not None:
            el.set("cdbase", self.cdbase)
        el.append(self.binder.toElement())
        variables = ET.Element("OMBVAR")
        for v in self.variables:
            variables.append(v.toElement())
        el.append(variables)
        el.append(self.object.toElement())

        return el


class OMError(_OMBase):
    """Implementation of the Error object

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_compound
    """

    kind = "OME"

    def __init__(self, error, arguments):
        self.error = error
        error.parent = self
        self.arguments = arguments
        for a in arguments:
            a.parent = self

    def isValid(self):
        return type(self.error) is Symbol

    def toElement(self):
        el = ET.Element(self.kind)
        el.append(self.error.toElement())
        for a in self.arguments:
            el.append(a.toElement())
        return el


def parse(text):
    """Parse either JSON or XML strings into a mathematical object

    See parseJSON and parseXML
    """
    try:
        return parseJSON(text)
    except json.JSONDecodeError:
        return parseXML(text)


def parseJSON(text):
    """Parse a JSON string into a mathematical object

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_json-the-json-encoding
    """
    return fromDict(json.loads(text))


def parseXML(text):
    """Parse a XML string into a mathematical object

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_xml
    """
    return fromElement(ET.fromstring(text))


def fromDict(dictionary):
    """Build a mathematical object from a python dictionary

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_json-the-json-encoding
    """
    match (dictionary):

        case {"kind": "OMOBJ", **kwargs}:
            return Object(
                fromDict(kwargs["object"]),
                cdbase=kwargs.get("cdbase"),
                version=kwargs.get("version"),
                xmlns=kwargs.get("xmlns"),
            )

        case {"kind": "OMI", "integer": x, **kwargs}:
            return Integer(int(x))

        case {"kind": "OMI", "decimal": x, **kwargs}:
            return Integer(int(x))

        case {"kind": "OMI", "hexadecimal": x, **kwargs}:
            return Integer(int(x, 16))

        case {"kind": "OMF", "integer": x, **kwargs}:
            return Float(float(x))

        case {"kind": "OMF", "decimal": x, **kwargs}:
            return Float(float(x))

        case {"kind": "OMF", "hexadecimal": x, **kwargs}:
            return Float(float(x, 16))

        case {"kind": "OMSTR", **kwargs}:
            return Bytearray(kwargs["string"])

        case {"kind": "OMB", **kwargs}:
            return Bytearray(kwargs["bytes"])

        case {"kind": "OMA", **kwargs}:
            return Application(
                fromDict(kwargs["applicant"]),
                *[fromDict(a) for a in kwargs.get("arguments", [])],
                cdbase=kwargs.get("cdbase")
            )

        case {"kind": "OMV", **kwargs}:
            return Variable(kwargs["name"])

        case {"kind": "OMS", **kwargs}:
            return Symbol(kwargs["name"], kwargs["cd"], cdbase=kwargs.get("cdbase"))

        case {"kind": "OMBIND", **kwargs}:
            return Binding(
                fromDict(kwargs["binder"]),
                [fromDict(v) for v in kwargs["variables"]],
                fromDict(kwargs["object"]),
                cdbase=kwargs.get("cdbase"),
            )

        case {"kind": "OMATTR", **kwargs}:
            recFromDict = (
                lambda x: fromDict(x)
                if type(x) is not list
                else [recFromDict(xx) for xx in x]
            )
            return Attribution(
                recFromDict(kwargs["attributes"]),
                fromDict(kwargs["object"]),
                kwargs.get("cdbase"),
            )

        case {"kind": "OME", **kwargs}:
            return Error(kwargs["error"], kwargs.get("arguments"))

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
            return Object(fromElement(elem[0]), **elem.attrib)

        case "OMI":
            if elem.text.strip()[0] == "x":
                return Integer(int(elem.text.strip()[1:]))
            elif elem.text.strip()[:2] == "-x":
                return Integer(-int(elem.text.strip()[2:]))
            else:
                return Integer(int(elem.text.strip()))

        case "OMF":
            if "dec" in elem.attrib:
                return Float(float(elem.attrib["dec"]))
            else:
                return Float(float(elem.attrib["hex"]))

        case "OMS":
            return Symbol(
                elem.attrib["name"], elem.attrib["cd"], elem.attrib.get("cdbase")
            )

        case "OMV":
            return Variable(elem.attrib["name"])

        case "OMSTR":
            return String(elem.text)

        case "OMB":
            raise NotImplementedError("XML encoded OpenMath Bytearrays")

        case "OMA":
            return Application(
                fromElement(elem[0]),
                *[fromElement(x) for x in elem[1:]],
                cdbase=elem.attrib.get("cdbase")
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
            return Attribution(attrs, obj, cdbase=elem.attrib.get("cdbase"))

        case "OME":
            return Error(fromElement(elem[0]), [fromElement(x) for x in elem[1:]])

        case "OMBIND":
            return Binding(
                fromElement(elem[0]),
                [fromElement(x) for x in elem.find(qname("OMBVAR"))],
                fromElement(elem[2]),
            )

        case _:
            raise ValueError("A valid ElementTree is required: %s" % elem)
