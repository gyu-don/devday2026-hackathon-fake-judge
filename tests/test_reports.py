import copy
import importlib.util
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/devday-judge-evidence'
spec = importlib.util.spec_from_file_location('validator', SKILL / 'scripts/validate_report.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

class ReportTests(unittest.TestCase):
    def setUp(self):
        self.report = json.loads((SKILL / 'references/report.md').read_text().split('```json\n')[1].split('```')[0])

    def test_schema_and_documented_template(self):
        Draft202012Validator.check_schema(json.loads(v.SCHEMA.read_text()))
        self.assertEqual(v.validate(self.report), [])

    def test_theme_missing_does_not_erase_total(self):
        self.report['theme'].update(score=None, match='undetermined')
        self.report['assessment'] = 'partial'
        self.assertEqual(v.validate(self.report), [])

    def test_criterion_missing_requires_null_total(self):
        self.report['criteria']['ux']['score'] = None
        self.report['assessment'] = 'partial'
        self.assertTrue(v.validate(self.report))
        self.report['total'] = None
        self.assertEqual(v.validate(self.report), [])

    def test_inconsistent_values_rejected(self):
        mutations = [lambda r: r.update(total=10), lambda r: r['theme'].update(match='strong'),
                     lambda r: r['criteria']['technical'].update(score=True),
                     lambda r: r['criteria']['technical'].update(evidence_ids=['missing']),
                     lambda r: r.update(assessment='unavailable'),
                     lambda r: r['event_policy'].update(eligibility='met'),
                     lambda r: r.update(extra='unexpected')]
        for change in mutations:
            with self.subTest(change=change):
                r = copy.deepcopy(self.report)
                change(r)
                self.assertTrue(v.validate(r))

    def test_duplicate_evidence_and_json_keys(self):
        e = dict(id='E1', path='README.md', locator='1', kind='docs', basis='observed', observation='text')
        self.report['evidence'] = [e, e]
        self.assertTrue(v.validate(self.report))
        with self.assertRaises(ValueError):
            json.loads('{"total": 0, "total": 40}', object_pairs_hook=v.unique_object)

    def test_high_theme_with_mock_is_valid(self):
        self.report['theme'].update(score=8, match='strong')
        self.report['theme']['mappings'] = [dict(announcement_id='DD15', announcement='MCP events for plugin automations', relationship='core', basis='experience_application', implementation='mock', evidence_ids=[], contribution='発表固有のイベント連携設計')]
        self.assertEqual(v.validate(self.report), [])

if __name__ == '__main__':
    unittest.main()
