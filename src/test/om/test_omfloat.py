import unittest
from openmath import *
from openmath.util import *


class TestOMFloat(unittest.TestCase):

    def test_value(self):
        value = 3.14
        omi = OMFloat(value)

        self.assertEqual(value, omi.float)
        self.assertTrue(isOM(omi), f"OMF should be OM")
        self.assertIsNone(omi.id)

    def test_dict(self):
        value = -1e-10
        omi = OMFloat(value)
        out = omi.toDict()
        expected = {"kind": "OMF", "decimal": value}

        self.assertDictEqual(expected, out)

    def test_with_id(self):
        id = "my_id"
        omi = OMFloat(42.0, id)

        self.assertEqual(id, omi.id)
        self.assertEqual(id, omi.toDict()["id"])


if __name__ == "__main__":
    unittest.main()
