import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from server import validate_ai_insight

class AIValidationTests(unittest.TestCase):
    def setUp(self):
        self.entries=[{'id':5,'happened_on':'2026-09-01'},{'id':8,'happened_on':'2026-09-04'},{'id':9,'happened_on':'2026-09-04'}]
        self.item={'state':'pattern','title':'Possible delegation theme','description':'Two reflections suggest a possible recurring delegation challenge.','citations':[5,8]}
    def test_valid_pattern(self):
        self.assertEqual(validate_ai_insight(self.item,self.entries)['citations'],[5,8])
    def test_foreign_citation_rejected(self):
        with self.assertRaises(ValueError):validate_ai_insight({**self.item,'citations':[5,999]},self.entries)
    def test_same_day_pattern_rejected(self):
        with self.assertRaises(ValueError):validate_ai_insight({**self.item,'citations':[8,9]},self.entries)
    def test_single_event_pattern_rejected(self):
        with self.assertRaises(ValueError):validate_ai_insight({**self.item,'citations':[5]},self.entries)
    def test_insufficient_with_citation_rejected(self):
        with self.assertRaises(ValueError):validate_ai_insight({**self.item,'state':'insufficient_evidence','citations':[5]},self.entries)
    def test_valid_observation(self):
        res=validate_ai_insight({**self.item,'state':'observation','citations':[5]},self.entries)
        self.assertEqual(res['state'],'observation')
    def test_duplicate_citations_rejected(self):
        with self.assertRaises(ValueError):validate_ai_insight({**self.item,'citations':[5,5]},self.entries)
if __name__=='__main__':unittest.main()
