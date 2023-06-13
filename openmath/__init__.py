"""OpenMath standard implementation

This module provides class and functions to
work with OpenMath mathematical objects
"""
import json
import urllib.request, urllib.error
import xml.etree.ElementTree as ET
from xml.dom import minidom
from copy import deepcopy
from base64 import b64encode, b64decode


class _OMFound(BaseException):
    def __init__(self, object_):
        self.object = object_


def _removeNoneAttrib(elem):
    """Remove None attributes from XML tree"""
    elem.attrib = {k: elem.attrib[k] for k in elem.attrib if elem.attrib[k] is not None}
    for subelem in elem:
        _removeNoneAttrib(subelem)


def _assertType(x, types):
    if not isinstance(x, types):
        raise ValueError("Expected %s, but got %s" % (" or ".join(t.__name__ for t in types), type(x).__name__))


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


class _OMBase:
    """Base class for OpenMath objects"""

    kind = None
    id = None
    parent = None

    def toDict(self) -> dict:
        """Get a dictionary with the attributes of the math object"""
        d = self.__dict__
        return {
            "kind": self.kind,
            **{
                k: d[k].toDict() 
                    if isOM(d[k]) 
                    else [x.toDict() if isOM(x) else x for x in d[k]]
                        if type(d[k]) is not str and hasattr(d[k], "__iter__")
                        else d[k]
                for k 
                in sorted(d.keys()) 
                if d[k] is not None and k != "parent"
            },
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
        _removeNoneAttrib(root)
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
        d = {**self.__dict__}
        d["parent"] = None

        for k in list(d.keys())[::-1]:  # reversed keys
            value = d[k]
            if isOM(value):  # level of depth 0
                value.apply(f, accumulator)

            elif type(value) is not str and hasattr(value, "__iter__"):  # level of depth 1
                for subval in value:
                    if isOM(subval):
                        subval.apply(f, accumulator)
                    elif type(subval) is not str and hasattr(subval, "__iter__"):  # level of depth 2 (for OMATTR)
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

    def getRoot(self):
        """Get the root object"""
        if self.parent is None:
            return self
        return self.parent.getRoot()

    def getByID(self, id):
        """Get an object by its ID"""

        def checkID(object_):
            if object_.id == id:
                raise _OMFound(object_)
            
        try:
            self.apply(checkID)
        except _OMFound as e:
            return e.object

        return None

    def clone(self):
        """Return a deep copy of the object."""
        return deepcopy(self)

    def dereference(self, derefStack=None):
        """Resolve all references in the object"""
        if derefStack is None:
            derefStack = []

        def singleDereference(object_):
            if object_.kind != "OMR":
                return
            href = object_.href
            if href in derefStack:
                raise RuntimeError(
                    "Cycle reference: " + " > ".join(derefStack) + " > " + href
                )
            target = object_.resolve()
            derefStack.append(href)
            target.dereference(derefStack)
            derefStack.pop()

        self.apply(singleDereference)

    def _replace(self, obj1, obj2) -> None:
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
            elif type(d[k]) is tuple:  # depth level 1
                attr = list(d[k])
                for i, elem in enumerate(attr):
                    if obj1 is elem:
                        attr[i] = obj2.clone()
                        attr[i].parent = self
                    elif type(elem) is tuple:  # depth level 2 (for OMATTR)
                        elem = tuple(
                            obj2.clone() if subelem is obj1 else subelem
                            for subelem in elem
                        )
                d[k] = tuple(attr)

    def __contains__(self, item) -> bool:
        def checkItem(object_):
            if object_ == item:
                raise _OMFound(object_)

        try:
            self.apply(checkItem)
        except _OMFound as e:
            return True

        return False

    def __eq__(self, other) -> bool:
        """Return true if all attributes are present and equal in both instances"""
        # The object must be OM
        if not isOM(other):
            return False

        a = self.toDict()
        b = other.toDict()
        allkeys = set([*a, *b])

        # The cdbase must be the same
        if "cdbase" in allkeys:
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
        return "%s(%s)" % (
            self.__class__.__name__,
            " ".join(
                "=".join(str(x) for x in kv)
                for kv in self.__dict__.items()
                if kv[1] is not None
            ),
        )

    def __str__(self):
        return "%s(%s)" % (
            self.__class__.__name__,
            " ".join(
                "=".join(str(x) for x in kv)
                for kv in self.__dict__.items()
                if kv[1] is not None and kv[0] != "parent"
            )
        )


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
    __match_args__ = ("object",)

    def __init__(self, object_, **kwargs):
        self.xmlns = None
        self.version = "2.0"
        self.cdbase = None
        self.__dict__.update(kwargs)
        self.setObject(object_)

    def setObject(self, object_):
        _setattrOM(self, "object", object_)

    def toElement(self):
        el = ET.Element(self.kind)
        el.set("xmlns", self.__dict__.get("xmlns"))
        el.set("version", self.__dict__.get("version"))
        el.set("cdbase", self.__dict__.get("cdbase"))
        el.set("id", self.__dict__.get("id"))
        el.append(self.object.toElement())
        return el


class OMInteger(_OMBase):
    """Implementation of the OMInteger object

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_basic
    """

    kind = "OMI"
    __match_args__ = ("integer",)

    def __init__(self, integer: int, id=None):
        _setattrType(self, "id", id, (str, type(None)))
        _setattrType(self, "integer", integer, int)

    def toElement(self):
        el = ET.Element(self.kind)
        el.set("id", self.__dict__.get("id"))
        el.text = str(self.integer)
        return el


class OMFloat(_OMBase):
    """Implementation of the OMFloat object

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_basic
    """

    kind = "OMF"
    __match_args__ = ("float",)

    def __init__(self, float_: float, id=None):
        _setattrType(self, "id", id, (str, type(None)))
        _setattrType(self, "float", float_, float)

    def toElement(self):
        el = ET.Element(self.kind)
        el.set("id", self.__dict__.get("id"))
        el.text = str(self.float)
        return el


class OMString(_OMBase):
    """Implementation of the OMString object

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_basic
    """

    kind = "OMSTR"
    __match_args__ = ("string",)

    def __init__(self, string, id=None):
        _setattrType(self, "id", id, (str, type(None)))
        _setattrType(self, "string", string, str)

    def toElement(self):
        el = ET.Element(self.kind)
        el.set("id", self.__dict__.get("id"))
        el.text = self.string
        return el


class OMBytearray(_OMBase):
    """Implementation of the OMBytearray object

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_basic
    """

    kind = "OMB"
    __match_args__ = ("bytes",)

    def __init__(self, bytes_: list, id=None):
        _setattrType(self, "id", id, (str, type(None)))
        self.bytes = bytes(bytes_)

    def toElement(self):
        el = ET.Element(self.kind)
        el.set("id", self.__dict__.get("id"))
        el.text = b64encode(self.bytes).decode("ascii")


class OMSymbol(_OMBase):
    """Implementation of the OMSymbol object

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_basic
    """

    kind = "OMS"
    __match_args__ = ("name", "cd")

    def __init__(self, name: str, cd: str, cdbase=None, id=None):
        _setattrType(self, "id", id, (str, type(None)))
        _setattrType(self, "cdbase", cdbase, (str, type(None)))
        _setattrType(self, "cd", cd, str)
        _setattrType(self, "name", name, str)

    def toElement(self):
        el = ET.Element(self.kind)
        el.set("id", self.__dict__.get("id"))
        el.set("name", self.name)
        el.set("cd", self.cd)
        if self.cdbase is not None:
            el.set("cdbase", self.cdbase)
        return el


class OMVariable(_OMBase):
    """Implementation of the OMVariable object

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_basic
    """

    kind = "OMV"
    __match_args__ = ("name",)

    def __init__(self, name: str, id=None):
        _setattrType(self, "id", id, (str, type(None)))
        _setattrType(self, "name", name, str)

    def toElement(self):
        el = ET.Element(self.kind)
        el.set("id", self.__dict__.get("id"))
        el.set("name", self.name)
        return el


class OMApplication(_OMBase):
    """Implementation of the OMApplication object

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_compound
    """

    kind = "OMA"
    __match_args__ = ("applicant", "arguments")

    def __init__(self, applicant: OMSymbol, arguments, cdbase: str = None, id=None):
        _setattrType(self, "id", id, (str, type(None)))
        _setattrType(self, "cdbase", cdbase, (str, type(None)))
        self.setApplicant(applicant)
        self.setArguments(arguments)

    def setApplicant(self, applicant):
        # The standard doesn't specify the kind of the applicant
        _setattrOM(self, "applicant", applicant)

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


class OMAttribution(_OMBase):
    """Implementation of the OMAttribution object

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_compound
    """

    kind = "OMATTR"
    __match_args__ = ("attributes", "object")

    def __init__(self, attributes, object_, cdbase=None, id=None):
        _setattrType(self, "id", id, (str, type(None)))
        _setattrType(self, "cdbase", cdbase, (str, type(None)))
        self.setObject(object_)
        self.setAttributes(attributes)

    def setObject(self, object_):
        _setattrOM(self, "object", object_)

    def setAttributes(self, attrs):
        for attr in attrs:
            _assertType(attr, tuple)
            _valueAssert(len(attr) == 2, "Attributes must be two values")
            assertOM(attr[0], "OMS")
            assertOM(attr[1])
            attr[0].parent = self
            attr[1].parent = self
        self.attributes = tuple(attrs)

    def toElement(self):
        el = ET.Element(self.kind)
        el.set("id", self.__dict__.get("id"))
        el.set("cdbase", self.__dict__.get("cdbase"))
        attrs = ET.Element("OMATP")
        for (a, b) in self.attributes:
            attrs.append(a.toElement(), b.toElement())
        el.append(attrs)
        el.append(self.object.toElement())
        return el


class OMBinding(_OMBase):
    """Implementation of the OMBinding object

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_compound
    """

    kind = "OMBIND"
    __match_args__ = ("binder", "variables", "object")

    def __init__(self, binder, variables, object_, cdbase=None, id=None):
        _setattrType(self, "id", id, (str, type(None)))
        _setattrType(self, "cdbase", cdbase, (str, type(None)))
        self.setObject(object_)
        self.setBinder(binder)
        self.setVariables(variables)
        self.variables = variables
        for v in self.variables:
            v.parent = self

    def setObject(self, object_):
        _setattrOM(self, "object", object_)

    def setBinder(self, binder):
        _setattrOM(self, "binder", binder)

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


class OMError(_OMBase):
    """Implementation of the OMError object

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_compound
    """

    kind = "OME"
    __match_args__ = ("error", "arguments")

    def __init__(self, error, arguments, id=None):
        _setattrType(self, "id", id, (str, type(None)))
        self.setError(error)
        self.setArguments(arguments)

    def setError(self, error):
        _setattrOM(self, "error", error, "OMS")

    def setArguments(self, arguments):
        for arg in arguments:
            assertOM(arg)
            arg.parent = self
        self.arguments = tuple(arguments)

    def toElement(self):
        el = ET.Element(self.kind)
        el.set("id", self.__dict__.get("id"))
        el.append(self.error.toElement())
        for a in self.arguments:
            el.append(a.toElement())
        return el


class OMForeign(_OMBase):
    """Implementation of OMFOREIGN objects

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_json-omforeign---foreign-objects
    """

    kind = "OMFOREIGN"
    __match_args__ = ("foreign", "encoding")

    def __init__(self, foreign, encoding=None, id=None):
        _setattrType(self, "id", id, (str, type(None)))
        _setattrType(self, "encoding", encoding, (str, type(None)))
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


class OMReference(_OMBase):
    """Implementation of references for structure sharing

    Reference: https://openmath.org/standard/om20-2019-07-01/omstd20.html#sec_json-omrs-and-structure-sharing
    """

    kind = "OMR"

    def __init__(self, href, id=None):
        _setattrType(self, "id", id, (str, type(None)))
        _setattrType(self, "href", href, str)

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
            return OMObject(
                fromDict(kwargs["object"]),
                cdbase=kwargs.get("cdbase"),
                version=kwargs.get("version"),
                xmlns=kwargs.get("xmlns"),
                **kwargs
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
            return OMBytearray(kwargs["string"], id=kwargs.get("id"))

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
            recFromDict = (
                lambda x: fromDict(x)
                if type(x) is not list
                else [recFromDict(xx) for xx in x]
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
            else:
                return OMFloat(float(elem.attrib["hex"]), id=elem.attrib.get("id"))

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
