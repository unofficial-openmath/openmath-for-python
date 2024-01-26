import unittest
from openmath import *
from openmath.util import *
import test.om_mother as om_mother

ATTRIBUTES = ((om_mother.of("OMS"), om_mother.of("OMOBJ")),)
ATTRIBUTED_OBJ = om_mother.of("OMOBJ")


class TestOMAttribution(unittest.TestCase):

    def setUp(self):
        self.omattr = OMAttribution(ATTRIBUTES, ATTRIBUTED_OBJ)

    def test_value(self):
        self.assertEqual(ATTRIBUTED_OBJ, self.omattr.object)
        self.assertTupleEqual(ATTRIBUTES, self.omattr.attributes)
        self.assertTrue(isOM(self.omattr), f"OMATTR should be OM")
        self.assertIsNone(self.omattr.id)

    def test_dict(self):
        out = self.omattr.toDict()
        expected = {
            "kind": "OMATTR",
            "attributes": [[k.toDict(), v.toDict()] for (k, v) in ATTRIBUTES],
            "object": ATTRIBUTED_OBJ.toDict(),
        }
        self.assertDictEqual(expected, out)

    def test_with_id(self):
        id = "my_id"
        self.omattr = OMAttribution(ATTRIBUTES, ATTRIBUTED_OBJ, id=id)

        self.assertEqual(id, self.omattr.id)
        self.assertEqual(id, self.omattr.toDict()["id"])

    def test_setters(self):
        new_attributes = (
            (om_mother.of("OMS"), om_mother.of("OMOBJ")),
            (om_mother.of("OMS"), om_mother.of("OMOBJ")),
        )
        new_object = om_mother.of("OMOBJ")
        self.omattr.setAttributes(new_attributes)
        self.omattr.setObject(new_object)
        self.assertTupleEqual(new_attributes, self.omattr.attributes)
        self.assertEqual(new_object, self.omattr.object)

    def test_fail_on_attribute_not_symbol(self):
        self.assertRaises(
            TypeError,
            self.omattr.setAttributes,
            ((om_mother.of("OMI"), om_mother.of("OMOBJ")),),
        )


if __name__ == "__main__":
    unittest.main()
