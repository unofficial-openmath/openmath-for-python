from .om.ombase import OMBase
from .om.omattribution import OMAttribution
from .om.omapplication import OMApplication
from .om.ombinding import OMBinding
from .cd.parser import parseXML as parseCD
from enum import Enum
import pathlib
import os

OM_CD_PATH_VAR="OM_CD_PATH"
cds = []

class ValidationResult(Enum):
    OK = 0
    WARNING = -1
    ERROR = -2


def validate(omobj: OMBase, **kargs):
    
    symbolsWithInvalidRole = []
    symbolsFromExperimentalCD = []
    symbolsNotFound = []
    
    def singleValidate(obj):
        if obj.kind == OMSymbol.kind:
            cd, symbolDefinition = _getCDAndSymbolDefinition(obj)
            
            if symbolDefinition is None: 
                symbolsNotFound.append(obj.applicant)
                return

            if cd.status == "experimental": symbolsFromExperimentalCD(obj.applicant)

            if symbolDefinition.role is None or symbolDefinition.role == "":
                return

            if obj.parent.kind == OMApplication.kind and obj is obj.parent.applicant:
                if symbolDefinition.role != "application":
                    symbolsWithInvalidRole.append((obj, "application"))
    
            elif obj.parent.kind == OMAttribution.kind and obj is not obj.parent.object:
                if symbolDefinition.role not in ("attribution", "semantic-attribution"): 
                    symbolsWithInvalidRole.append((attr, "attribution"))

            elif obj.parent.kind == OMBinding.kind and obj is obj.parent.binder:
                if symbolDefinition.role != "binder":
                    symbolsWithInvalidRole.append((obj, "binder"))
            
            elif obj.parent.kind == OMError.kind and obj is obj.parent.error:
                if symbolDefinition.role != "error":
                    symbolsWithInvalidRole.append((obj, "error"))

    returnValues = {
        "pass": ValidationResult.OK,
        "warning": ValidationResult.WARNING,
        "error": ValidationResult.ERROR
    }
    returnConfig = {
        ""
        **kargs
    }

    omobj.apply(singleValidate)
    if len(symbolsWithInvalidRole) > 0:
        return ValidationResult.ERROR
    
    if len(symbolsFromExperimentalCD) > 0:
        return ValidationResult.WARNING
    
    return ValidationResult.OK


def _getCDAndSymbolDefinition(symbol):
    for cd in cds:
        if symbol in cd:
            return cd, cd[symbol]
    return (None, None)
        

def _loadCDFromFile(filepath):
    with open(filepath) as fh:
        cd.append(
            parseCD(fh.read())
        )


def _loadCDs(cd_paths, on_experimental, on_obsolete):
    argPath = argPath if argPath is not None else []
    envPath = os.environ.get(OM_CD_PATH_VAR, "").split(";")
    routeNames = [
        *argPath,
        *envPath,
        "./cd",
        "./"
    ]

    routeNames = [x.strip() for x in routeNames if len(x.strip()) > 0]

    for routeName in routeNames:
        route = pathlib.Path(route)
    
        if route.exists and route.is_dir:
    
            for filepath in route:
                if filepath.suffix.lower() == ".ocd":
                    _loadCDFromFile(filepath)