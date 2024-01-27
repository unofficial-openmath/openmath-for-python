import unittest
from openmath import OMSymbol
from openmath.cd import *
from openmath.util import *
import test.cd_mother as cd_mother
import test.sd_mother as sd_mother

SYMBOL_DEFINITION = sd_mother.of()


class TestContentDictionary(unittest.TestCase):
    def setUp(self):
        self.cd = cd_mother.of(definitions=[SYMBOL_DEFINITION])

    def test_access(self):
        oms_without_base = OMSymbol(SYMBOL_DEFINITION.name, self.cd.name)
        oms_with_base = OMSymbol(SYMBOL_DEFINITION.name, self.cd.name, self.cd.base)
        accessors = [0, SYMBOL_DEFINITION.name, oms_without_base, oms_with_base]
        for accessor in accessors:
            with self.subTest(f"accessor: {accessor}"):
                self.assertEqual(SYMBOL_DEFINITION, self.cd[accessor])

    def test_contains(self):
        oms_without_base = OMSymbol(SYMBOL_DEFINITION.name, self.cd.name)
        oms_with_base = OMSymbol(SYMBOL_DEFINITION.name, self.cd.name, self.cd.base)
        accessors = [SYMBOL_DEFINITION.name, oms_with_base, oms_without_base]
        for accessor in accessors:
            with self.subTest(f"accessor: {accessor}"):
                self.assertTrue(accessor in self.cd)

    def test_fail_access_and_contains(self):
        oms_with_bad_base = OMSymbol(SYMBOL_DEFINITION.name, self.cd.name, "bad base")
        oms_with_bad_cd = OMSymbol(SYMBOL_DEFINITION.name, "bad cd")
        oms_with_bad_name = OMSymbol("bad name", self.cd.name)
        accessors = [
            oms_with_bad_base,
            oms_with_bad_cd,
            oms_with_bad_name,
            "bad string",
        ]
        for accessor in accessors:
            self.assertRaises(KeyError, self.cd.__getitem__, accessor)
            self.assertFalse(accessor in self.cd)


if __name__ == "__main__":
    unittest.main()
