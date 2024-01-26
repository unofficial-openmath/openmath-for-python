import unittest
from openmath import *
from openmath.util import *


class TestOMSymbol(unittest.TestCase):

    def test_name(self):
        name = "my_var"
        cd = "my_dict"
        omv = OMSymbol(name, cd)

        self.assertEqual(name, omv.name)
        self.assertEqual(cd, omv.cd)
        self.assertTrue(isOM(omv), f"OMS should be OM")
        self.assertIsNone(omv.id)

    def test_dict(self):
        omv = OMSymbol("name", "dict")
        out = omv.toDict()
        expected = {"kind": "OMS", "name": omv.name, "cd": omv.cd}

        self.assertDictEqual(expected, out)

    def test_with_id(self):
        id = "my_id"
        omv = OMSymbol("name", "cd", id=id)

        self.assertEqual(id, omv.id)
        self.assertEqual(id, omv.toDict()["id"])


if __name__ == "__main__":
    unittest.main()
