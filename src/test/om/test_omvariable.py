import unittest
from openmath import *
from openmath.util import *

class TestOMVariable(unittest.TestCase):

    def test_name(self):
        name = "my_var"
        omv = OMVariable(name)

        self.assertEqual(name, omv.name)
        self.assertTrue(isOM(omv), f"OMV should be OM")
        self.assertIsNone(omv.id)
    
    def test_dict(self):
        omv = OMVariable("abc")
        out = omv.toDict()
        expected = {"kind": "OMV", "name": omv.name}

        self.assertDictEqual(expected, out)

    def test_with_id(self):
        id = "my_id"
        omv = OMVariable("abc", id)

        self.assertEqual(id, omv.id)
        self.assertEqual(id, omv.toDict()["id"])

if __name__ == '__main__':
    unittest.main()