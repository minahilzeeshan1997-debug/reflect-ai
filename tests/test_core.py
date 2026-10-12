import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from server import detector,hash_password,verify_password
class CoreTests(unittest.TestCase):
    def test_password(self):
        h=hash_password('ExampleSecret123')
        self.assertTrue(verify_password('ExampleSecret123',h))
        self.assertFalse(verify_password('ExampleSecret12',h))
    def test_insufficient(self):
        d=detector([dict(id=1,situation='Bad week',response='',learning='',happened_on='2026-10-01')]);self.assertEqual(d['state'],'insufficient_evidence')
    def test_observation(self):
        d=detector([dict(id=1,situation='A customer review ran overtime and I stayed late to clarify next steps for the delivery team.',response='I summarized the conversation.',learning='I want to leave additional time for closing questions.',happened_on='2026-10-01')]);self.assertEqual(d['state'],'observation');self.assertEqual(d['citations'],[1])
    def test_same_day_not_pattern(self):
        a=[dict(id=i,situation='We had no owner for the deliverable and the handoff was confusing.',response='',learning='',happened_on='2026-10-01') for i in (1,2)]
        self.assertNotEqual(detector(a)['state'],'pattern')
    def test_pattern_distinct_days_and_real_citations(self):
        a=[dict(id=i,situation='There was no owner for the handoff.',response='We discussed responsibilities.',learning='',happened_on=d) for i,d in [(12,'2026-10-01'),(17,'2026-10-05')]]
        d=detector(a);self.assertEqual(d['state'],'pattern');self.assertEqual(set(d['citations']),{12,17})
if __name__=='__main__':unittest.main()
