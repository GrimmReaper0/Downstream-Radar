from pathlib import Path
import tempfile
import unittest
from downstream_radar.cli import check, classify, expand, markdown, read_manifest

ROOT = Path(__file__).parents[1]


class RadarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = check(ROOT/'examples/radar.toml', ROOT/'examples/packages/v1', ROOT/'examples/packages/v2', jobs=2)

    def test_real_regression(self):
        self.assertEqual(self.report['regressions'], 1)
        self.assertEqual(self.report['compatible'], 1)
        self.assertEqual(self.report['compatibility_percent'], 50.0)

    def test_baseline_evidence(self):
        self.assertTrue(all(r['baseline']['test']['exit_code'] == 0 for r in self.report['results']))

    def test_unchanged_package(self):
        r = check(ROOT/'examples/radar.toml', ROOT/'examples/packages/v1', ROOT/'examples/packages/v1')
        self.assertEqual(r['compatible'], 2)

    def test_preexisting_failure(self):
        r = check(ROOT/'examples/radar.toml', ROOT/'examples/packages/v2', ROOT/'examples/packages/v2')
        self.assertEqual(r['regressions'], 0); self.assertEqual(r['inconclusive'], 1)

    def test_missing_package(self):
        with self.assertRaises(ValueError): check(ROOT/'examples/radar.toml', ROOT/'missing', ROOT)

    def test_empty_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'radar.toml'; p.write_text('version=1\nprojects=[]')
            with self.assertRaises(ValueError): read_manifest(p)

    def test_no_implicit_shell(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'radar.toml'
            p.write_text('version=1\n[[projects]]\nname="a"\npath="."\ntest="echo bad"')
            with self.assertRaises(ValueError): read_manifest(p)

    def test_classifications(self):
        ok = {'ready': True, 'test': {'status':'completed','exit_code':0}}
        bad = {'ready': True, 'test': {'status':'completed','exit_code':1}}
        unavailable = {'ready': False, 'test': None}
        self.assertEqual(classify(ok, bad), 'regression')
        self.assertEqual(classify(bad, ok), 'baseline-failed')
        self.assertEqual(classify(unavailable, ok), 'baseline-unavailable')
        self.assertEqual(classify(ok, unavailable), 'candidate-unavailable')

    def test_missing_consumer_inconclusive(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'radar.toml'
            p.write_text('version=1\n[[projects]]\nname="missing"\npath="missing"\ntest=["python"]')
            r = check(p, ROOT/'examples/packages/v1', ROOT/'examples/packages/v1')
            self.assertEqual(r['inconclusive'], 1); self.assertIsNone(r['compatibility_percent'])

    def test_markdown(self):
        text = markdown(self.report)
        self.assertIn('legacy-string-consumer', text); self.assertIn('regression', text)

    def test_paths_with_spaces(self):
        self.assertEqual(expand(['{package}'], Path('/a directory/pkg'), Path('/work')), ['/a directory/pkg'])

    def test_parallel_limit(self):
        with self.assertRaises(ValueError): check(ROOT/'examples/radar.toml', ROOT, ROOT, jobs=99)


if __name__ == '__main__':
    unittest.main()
