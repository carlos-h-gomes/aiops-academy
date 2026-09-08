"""Bounded synthetic unit checks for the learner's pure functions."""
import sys
import unittest
if '--solution' in sys.argv:
    import solution as candidate
    sys.argv.remove('--solution')
else:import exercise as candidate

class EventTests(unittest.TestCase):
    def test_duplicates_and_invalid(self):
        events=[{'id':'a','status':503},{'id':'b','status':200},{'id':'a','status':503},{'id':'c','status':200},{'id':'d','status':'erro'},{'id':'e','status':500}]
        self.assertEqual(candidate.normalize(events),dict(unique_valid=4,invalid=1,duplicates=1,error_rate=50))
    def test_empty_is_not_healthy(self):
        self.assertIsNone(candidate.normalize([])['error_rate'])
    def test_invalid_does_not_reserve_id(self):
        self.assertEqual(candidate.normalize([{'id':'a','status':True},{'id':'a','status':500}]),dict(unique_valid=1,invalid=1,duplicates=0,error_rate=100))
    def test_boundaries_and_shape(self):
        self.assertEqual(candidate.normalize([None,{}, {'id':'','status':200},{'id':'a','status':99},{'id':'b','status':600}])['invalid'],5)
    def test_summary(self):
        self.assertEqual(candidate.summarize([{'service.name':'quotes','loglevel':'ERROR'},{'service.name':'quotes','loglevel':'INFO'},{'service.name':'orders','loglevel':'ERROR'}]),{'quotes':1,'orders':1})
    def test_z_score(self):
        self.assertEqual(candidate.z_score(180,100,20),4)
        self.assertIsNone(candidate.z_score(10,10,0))
        with self.assertRaises(ValueError):candidate.z_score(10,10,-1)

if __name__=='__main__':unittest.main(verbosity=2)
