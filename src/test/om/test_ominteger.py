import unittest
from openmath import *
from openmath.util import *

class TestOMInteger(unittest.TestCase):

    def test_value(self):
        value = 42
        omi = OMInteger(value)

        self.assertEqual(value, omi.integer)
        self.assertTrue(isOM(omi), f"OMI should be OM")
        self.assertIsNone(omi.id)
    
    def test_dict(self):
        value = -42
        omi = OMInteger(value)
        out = omi.toDict()
        expected = {"kind": "OMI", "integer": value}

        self.assertDictEqual(expected, out)

    def test_with_id(self):
        id = "my_id"
        omi = OMInteger(42, id)

        self.assertEqual(id, omi.id)
        self.assertEqual(id, omi.toDict()["id"])

if __name__ == '__main__':
    unittest.main()