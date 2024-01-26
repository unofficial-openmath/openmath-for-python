import unittest
from openmath import *
from openmath.util import *
import test.om_mother as om_mother

BINDER = om_mother.of("OMS")
VARIABLES = (om_mother.of("OMV"), om_mother.of("OMV"))
OBJECT = om_mother.of("OMOBJ")

class TestOMBinding(unittest.TestCase):

    def setUp(self):
        self.ombind = OMBinding(BINDER, VARIABLES, OBJECT)

    def test_value(self):
        self.assertEqual(BINDER, self.ombind.binder)
        self.assertTupleEqual(VARIABLES, self.ombind.variables)
        self.assertEqual(OBJECT, self.ombind.object)
        self.assertTrue(isOM(self.ombind), f"OMBIND should be OM")
        self.assertIsNone(self.ombind.id)
    
    def test_dict(self):
        out = self.ombind.toDict()
        expected = {
            "kind": "OMBIND",
            "binder": BINDER.toDict(),
            "variables": [v.toDict() for v in VARIABLES],
            "object": OBJECT.toDict()
        }
        self.assertDictEqual(expected, out)

    def test_with_id(self):
        id = "my_id"
        self.ombind = OMBinding(BINDER, VARIABLES, OBJECT, id=id)

        self.assertEqual(id, self.ombind.id)
        self.assertEqual(id, self.ombind.toDict()["id"])
    
    def test_setters(self):
        new_binder = om_mother.of("OMS")
        new_variables = (om_mother.of("OMV"),)
        new_object = om_mother.of("OMOBJ")
        self.ombind.setBinder(new_binder)
        self.ombind.setVariables(new_variables)
        self.ombind.setObject(new_object)
        self.assertEqual(new_binder, self.ombind.binder)
        self.assertTupleEqual(new_variables, self.ombind.variables)
        self.assertEqual(new_object, self.ombind.object)
    
    def test_set_attributed_variable(self):
        attr_var = (om_mother.of("OMATTR", object_=om_mother.of("OMV")),)
        self.ombind.setVariables(attr_var)
        self.assertEqual(attr_var, self.ombind.variables)
    
    def test_fail_on_attribute_other(self):
        attr_other = om_mother.of("OMATTR", object_=om_mother.of("OMI"))
        self.assertRaises(
            ValueError,
            self.ombind.setVariables,
            (attr_other,)
        )
    
    def test_fail_on_variables_not_symbol(self):
        self.assertRaises(
            TypeError,
            self.ombind.setBinder,
            ((om_mother.of("OMI"), om_mother.of("OMOBJ")),)
        )
        
if __name__ == '__main__':
    unittest.main()