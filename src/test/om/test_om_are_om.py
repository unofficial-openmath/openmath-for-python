import unittest
from openmath import *
from openmath.util import *
import test.om_mother as mother


class TestOMareOM(unittest.TestCase):
    def test_is_not_om(self):
        self.assertFalse(isOM(1))
        self.assertFalse(isOM(1.5))
        self.assertFalse(isOM("foo"))
        self.assertFalse(isOM({}))
        self.assertFalse(isOM([]))
        self.assertFalse(isOM(bytearray(b'bar')))
        self.assertFalse(isOM(object()))


if __name__ == '__main__':
    unittest.main()