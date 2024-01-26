import unittest
from openmath import *
from openmath.util import *

BYTEARRAY = bytearray([0x01, 0x02, 0xff])

class TestOMBytearray(unittest.TestCase):

    def test_value(self):
        omb = OMBytearray(BYTEARRAY)

        self.assertEqual(BYTEARRAY, omb.bytes)
        self.assertTrue(isOM(omb), f"OMB should be OM")
        self.assertIsNone(omb.id)

    def test_dict(self):
        omb = OMBytearray(BYTEARRAY)
        out = omb.toDict()
        expected = {"kind": "OMB", "bytes": list(BYTEARRAY)}

        self.assertDictEqual(expected, out)

    def test_with_id(self):
        id = "my_id"
        omb = OMBytearray(BYTEARRAY, id)

        self.assertEqual(id, omb.id)
        self.assertEqual(id, omb.toDict()["id"])

if __name__ == '__main__':
    unittest.main()