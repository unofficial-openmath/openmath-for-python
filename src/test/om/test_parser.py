import unittest
from openmath import *
from openmath.util import *
import test.om_mother as om_mother
from openmath.om import parser

TEST_OMS = [
    om_mother.of("OMOBJ"),
    om_mother.of("OMI"),
    om_mother.of("OMF"),
    om_mother.of("OMSTR"),
    om_mother.of("OMB"),
    om_mother.of("OMV"),
    om_mother.of("OMS"),
    om_mother.of("OMA"),
    om_mother.of("OMATTR"),
    om_mother.of("OMBIND"),
]


class TestOMParser(unittest.TestCase):

    def test_basic_parse_errors(self):
        self.assertRaises(ValueError, parser.parse, "")
        self.assertRaises(ValueError, parser.parse, "abc")
        self.assertRaises(ValueError, parser.parse, "{}")
        self.assertRaises(ValueError, parser.parse, '{"kind": "_"}')
        self.assertRaises(ValueError, parser.parse, "<>")
        self.assertRaises(ValueError, parser.parse, "<NO/>")

    def test_serialization_json(self):
        for om in TEST_OMS:
            with self.subTest(om.kind):
                jsonstr = om.toJSON()
                parsed = parser.parseJSON(jsonstr)
                self.assertEqual(om, parsed)

    def test_serialization_xml(self):
        for om in TEST_OMS:
            with self.subTest(om.kind):
                xmlstr = om.toXML()
                parsed = parser.parseXML(xmlstr)
                self.assertEqual(om, parsed)


if __name__ == "__main__":
    unittest.main()
