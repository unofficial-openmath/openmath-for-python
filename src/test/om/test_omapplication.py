import unittest
from openmath import *
from openmath.util import *
import test.om_mother as om_mother

APPLICANT = om_mother.of("OMS")
NARG = 3
ARGUMENTS = tuple(om_mother.of("OMOBJ") for _ in range(NARG))

class TestOMApplication(unittest.TestCase):

    def setUp(self):
        self.oma = OMApplication(APPLICANT, ARGUMENTS)
        self.maxDiff = None

    def test_value(self):
        self.assertEqual(APPLICANT, self.oma.applicant)
        self.assertTupleEqual(ARGUMENTS, self.oma.arguments)
        self.assertTrue(isOM(self.oma), f"OMA should be OM")
        self.assertIsNone(self.oma.id)
    
    def test_dict(self):
        out = self.oma.toDict()
        expected = {"kind": "OMA", "applicant": APPLICANT.toDict(), "arguments": [arg.toDict() for arg in ARGUMENTS]}
        self.assertDictEqual(expected, out)

    def test_with_id(self):
        id = "my_id"
        self.oma = OMApplication(APPLICANT, ARGUMENTS, id=id)

        self.assertEqual(id, self.oma.id)
        self.assertEqual(id, self.oma.toDict()["id"])
    
    def test_setters(self):
        new_applicant = om_mother.of("OMOBJ")
        new_args = (om_mother.of("OMOBJ"),)
        self.oma.setApplicant(new_applicant)
        self.oma.setArguments(new_args)
        self.assertEqual(new_applicant, self.oma.applicant)
        self.assertTupleEqual(new_args, self.oma.arguments)

if __name__ == '__main__':
    unittest.main()