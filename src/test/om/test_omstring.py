import unittest
from openmath import *
from openmath.util import *


class TestOMString(unittest.TestCase):

    def test_value(self):
        value = "testing..."
        omstr = OMString(value)

        self.assertEqual(value, omstr.string)
        self.assertTrue(isOM(omstr), f"OMSTR should be OM")
        self.assertIsNone(omstr.id)

    def test_dict(self):
        omstr = OMString("abc")
        out = omstr.toDict()
        expected = {"kind": "OMSTR", "string": omstr.string}

        self.assertDictEqual(expected, out)

    def test_with_id(self):
        id = "my_id"
        omstr = OMString("abc", id)

        self.assertEqual(id, omstr.id)
        self.assertEqual(id, omstr.toDict()["id"])


if __name__ == "__main__":
    unittest.main()
