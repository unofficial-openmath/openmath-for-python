from copy import deepcopy
from xml.dom import minidom
import xml.etree.ElementTree as ET
import json

class OMBase:
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
        return json.dumps(self, default=OMBase.toDict, *args, **kwargs)

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
            if hasattr(x, "__iter__") and hasattr(y, "__iter__"):
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
