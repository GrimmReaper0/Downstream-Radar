import unittest
from pathlib import Path
from downstream_radar.cli import check
ROOT=Path(__file__).parents[1]
class Tests(unittest.TestCase):
 def test_real_regression(self):
  r=check(ROOT/'examples/radar.toml',ROOT/'examples/packages/v1',ROOT/'examples/packages/v2',jobs=2); self.assertEqual(r['compatible'],1); self.assertEqual(r['regressions'],1); self.assertEqual(r['inconclusive'],0)
 def test_jobs_validation(self):
  with self.assertRaises(ValueError): check(ROOT/'examples/radar.toml',ROOT/'examples/packages/v1',ROOT/'examples/packages/v2',jobs=0)
if __name__=='__main__': unittest.main()
