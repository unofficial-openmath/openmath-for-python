import unittest
from openmath import *
from openmath.util import *
import test.om_mother as mother

class TestInteger(unittest.TestCase):

    def test_is_om(self):

        allOMKinds = [
            OMInteger.kind,
            OMFloat.kind,
            OMBytearray.kind,
            OMString.kind,
            OMVariable.kind,
            OMSymbol.kind,
            OMApplication.kind,
            OMAttribution.kind,
            OMBinding.kind,
        ]
        for kind in allOMKinds:
            self.assertTrue(isOM(mother.of(kind)), f"{kind} should be OM")
            self.assertTrue(isOM(mother.of(kind), kind), f"{kind} should be OM of kind {kind}")
    
    def test_is_not_om(self):

        self.assertFalse(isOM(1))
        self.assertFalse(isOM(1.5))
        self.assertFalse(isOM("foo"))
        self.assertFalse(isOM(bytearray(b'bar')))
        self.assertFalse(isOM(object()))
        
    