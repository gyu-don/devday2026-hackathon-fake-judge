import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
METHODS = ('evidence', 'journey', 'challenge')
SKILLS = {name: ROOT / 'skills' / ('devday-judge-' + name) for name in METHODS}


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATORS = {name: load_module('validator_' + name, path / 'scripts/validate_report.py')
              for name, path in SKILLS.items()}
v = VALIDATORS['evidence']
comparison = load_module('comparison', ROOT / 'scripts/compare_reports.py')
condition_a = load_module('condition_a', ROOT / 'scripts/prepare_condition_a.py')


def template():
    return json.loads((SKILLS['evidence'] / 'references/report.md').read_text().split('```json\n')[1].split('```')[0])


def example_report(method='evidence'):
    """Synthetic contract example, not a calibrated score or a model review."""
    report = template()
    report['target'].update(path='/fixed/submission', dirty=False, changed_during_review=False)
    report['judge'] = 'devday-judge-' + method
    report['evidence'] = [dict(id='E1', path='main.py', locator='plan', kind='code', basis='observed',
                               observation='模擬イベントIDの重複を除き、固定の下書き手順を返す')]
    for item in report['criteria'].values():
        item.update(score=6, confidence='medium', reason='静的証拠が支持する範囲の判断（E1）', evidence_ids=['E1'])
    report['total'] = 24
    report['feature_use'].update(counterfactual='イベント起点の設計を外すと受信後の下書き作成がなくなる（E1）',
                                mappings=[dict(announcement_id='DD15', announcement='MCP events for plugin automations',
                                               relationship='core', basis='experience_application', implementation='mock',
                                               evidence_ids=['E1'], contribution='イベントを契機に計画案を作る応用設計。外部購読は未実装')])
    report['review_scope']['inspected_paths'] = ['main.py']
    if method == 'evidence':
        for row in report['method_observations']['coverage'].values():
            row.update(claims=[dict(claim='イベント起点の下書き設計', evidence_ids=['E1'])], inspected_paths=['main.py'])
    elif method == 'journey':
        step = dict(stage='計画案を返す', path='main.py', locator='plan', observation='固定の下書き手順を返す',
                    implementation='mock', evidence_ids=['E1'], affected_criteria=list(v.CRITERIA))
        report['method_observations'] = dict(
            kind='journey', scenarios=[dict(id='S1', user='制作担当者', goal='新規タスクの下書き取得', scenario_type='normal',
                                           selection_basis='資料に示された主価値', steps=[step], breaks=[], outcome='模擬下書きまで静的に確認')],
            supplemental_checks=[], completion_check='主シナリオの到達範囲を確認。実動作は未確認')
    else:
        report['method_observations'] = dict(
            kind='challenge', claim_tests=[dict(
                claim='イベント起点で計画を作る', counter_hypothesis='入力にかかわらず同じ固定手順を返す',
                discriminating_check='main.pyのplanが返す値とイベントIDの利用を確認',
                supporting_evidence_ids=['E1'], opposing_evidence_ids=['E1'],
                alternative_explanations_checked=['現状は明示されたモックの範囲'], result='mixed',
                finding='イベントIDによる分岐はあるが下書きの手順は固定', affected_criteria=list(v.CRITERIA))],
            additional_checks=[], completion_check='主張の支持と制約を確認。接続・実動作は未確認')
    return report


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.report = template()

    def assert_invalid(self, report):
        for method, validator in VALIDATORS.items():
            with self.subTest(validator=method):
                self.assertTrue(validator.validate(report))

    def test_schema_and_documented_template(self):
        for validator in VALIDATORS.values():
            Draft202012Validator.check_schema(json.loads(validator.SCHEMA.read_text()))
            self.assertEqual(validator.validate(self.report), [])

    def test_positive_examples_for_all_methods(self):
        for method in METHODS:
            for validator in VALIDATORS.values():
                self.assertEqual(validator.validate(example_report(method)), [])

    def test_each_official_criterion_required_and_no_old_keys(self):
        self.assertEqual(set(self.report['criteria']), set(v.CRITERIA))
        for key in v.CRITERIA:
            report = copy.deepcopy(self.report)
            del report['criteria'][key]
            self.assert_invalid(report)
        for old in ('technical', 'ux', 'impact', 'idea'):
            report = copy.deepcopy(self.report)
            report['criteria'][old] = copy.deepcopy(report['criteria']['utility'])
            self.assert_invalid(report)

    def test_score_integer_range_and_type(self):
        for key in v.CRITERIA:
            for bad in (-1, 11, True, False, 2.5, 1.0, '5', [], {}):
                report = copy.deepcopy(self.report)
                report['criteria'][key]['score'] = bad
                self.assert_invalid(report)

    def test_score_boundaries_and_sum(self):
        for key in v.CRITERIA:
            for score in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10):
                report = example_report()
                report['criteria'][key]['score'] = score
                report['total'] = sum(c['score'] for c in report['criteria'].values())
                self.assertEqual(v.validate(report), [])
        report = example_report()
        for item in report['criteria'].values():
            item['score'] = 10
        report['total'] = 40
        self.assertEqual(v.validate(report), [])

    def test_criterion_missing_requires_null_total(self):
        for key in v.CRITERIA:
            report = example_report()
            report['criteria'][key]['score'] = None
            report['criteria'][key]['unknowns'] = ['必要資料が読めない']
            report['assessment'] = 'partial'
            self.assert_invalid(report)
            report['total'] = None
            self.assertEqual(v.validate(report), [])
            report['assessment'] = 'scored'
            self.assert_invalid(report)

    def test_new_feature_missing_also_erases_total(self):
        # Replaces the old test where an independent theme could be null with a full total.
        report = example_report()
        report['criteria']['new_feature']['score'] = None
        report['total'] = None
        report['assessment'] = 'partial'
        self.assertEqual(v.validate(report), [])

    def test_unavailable_and_partial_states(self):
        for item in self.report['criteria'].values():
            item['score'] = None
            item['unknowns'] = ['対象にアクセス不能']
        self.report.update(total=None, assessment='unavailable')
        self.assertEqual(v.validate(self.report), [])
        for state in ('scored', 'partial'):
            report = copy.deepcopy(self.report)
            report['assessment'] = state
            self.assert_invalid(report)
        report = template()
        report['assessment'] = 'unavailable'
        self.assert_invalid(report)
        report['assessment'] = 'partial'
        self.assert_invalid(report)

    def test_inconsistent_values_rejected(self):
        mutations = [lambda r: r.update(total=10), lambda r: r.update(total=0.0),
                     lambda r: r.update(max_total=50), lambda r: r.update(extra='unexpected'),
                     lambda r: r['criteria']['usability'].update(confidence='certain'),
                     lambda r: r['review_scope'].update(execution='passed'),
                     lambda r: r['review_scope'].update(mode='dynamic'),
                     lambda r: r['target'].update(scope='HEAD')]
        for change in mutations:
            report = copy.deepcopy(self.report)
            change(report)
            self.assert_invalid(report)

    def test_legacy_top_level_and_feature_scores_rejected(self):
        for key, value in [('theme', dict(score=8)), ('event_policy', {}), ('method_notes', [])]:
            report = copy.deepcopy(self.report)
            report[key] = value
            self.assert_invalid(report)
        for key in ('score', 'max_score', 'match'):
            report = copy.deepcopy(self.report)
            report['feature_use'][key] = 0
            self.assert_invalid(report)

    def test_old_v11_shape_is_rejected_by_schema_itself(self):
        report = template()
        report.update(schema_version='1.1', rubric_version='1.1', theme=dict(score=0),
                      event_policy=dict(rules=[], eligibility='not_specified'), method_notes=[])
        report['criteria'] = {old: report['criteria'][new] for old, new in zip(
            ('technical', 'ux', 'impact', 'idea'), v.CRITERIA)}
        del report['feature_use']
        del report['method_observations']
        schema = Draft202012Validator(json.loads(v.SCHEMA.read_text()))
        self.assertFalse(schema.is_valid(report))
        self.assert_invalid(report)
        for field in ('schema_version', 'rubric_version'):
            report = template()
            report[field] = '1.1'
            self.assertFalse(schema.is_valid(report))

    def test_duplicate_evidence_and_json_keys(self):
        report = example_report()
        report['evidence'].append(copy.deepcopy(report['evidence'][0]))
        self.assert_invalid(report)
        with self.assertRaises(ValueError):
            json.loads('{"total": 0, "total": 40}', object_pairs_hook=v.unique_object)

    def test_all_method_evidence_references_checked(self):
        reports = [example_report(method) for method in METHODS]
        reports[0]['method_observations']['coverage']['utility']['claims'][0]['evidence_ids'] = ['missing']
        reports[1]['method_observations']['scenarios'][0]['steps'][0]['evidence_ids'] = ['missing']
        reports[2]['method_observations']['claim_tests'][0]['opposing_evidence_ids'] = ['missing']
        for report in reports:
            self.assert_invalid(report)
        for method in METHODS:
            report = example_report(method)
            check = dict(trigger='主張と記録の不一致', scope=['main.py'], finding='追加確認',
                         evidence_ids=['missing'], affected_criteria=['utility'])
            key = 'supplemental_checks' if method == 'journey' else 'additional_checks'
            report['method_observations'][key] = [check]
            self.assert_invalid(report)
        for method in METHODS:
            report = example_report(method)
            report['criteria']['utility']['evidence_ids'] = ['missing']
            self.assert_invalid(report)

    def test_positive_criteria_need_evidence(self):
        for key in v.CRITERIA:
            report = example_report()
            report['criteria'][key]['evidence_ids'] = []
            self.assert_invalid(report)

    def test_new_feature_mapping_consistency(self):
        report = example_report()
        report['feature_use']['mappings'] = []
        self.assert_invalid(report)
        report = example_report()
        report['feature_use']['mappings'][0]['evidence_ids'] = []
        self.assert_invalid(report)
        report = example_report()
        report['feature_use']['mappings'][0]['evidence_ids'] = ['missing']
        self.assert_invalid(report)
        report = example_report()
        report['evidence'].append(dict(report['evidence'][0], id='E2'))
        report['feature_use']['mappings'][0]['evidence_ids'] = ['E2']
        self.assert_invalid(report)  # Defined but not referenced by new_feature.
        report['criteria']['new_feature']['evidence_ids'].append('E2')
        self.assertEqual(v.validate(report), [])

    def test_mentions_alone_cannot_support_deep_use(self):
        report = example_report()
        report['feature_use']['mappings'][0].update(relationship='mention_only', basis='concept_only',
                                                   implementation='not_applicable', contribution='名称の記載のみ')
        self.assert_invalid(report)
        report['criteria']['new_feature']['score'] = 2
        report['total'] = 20
        self.assertEqual(v.validate(report), [])

    def test_high_new_feature_with_mock_plan_or_development_valid(self):
        # Preserve the important v1.1 no-cap test under the new scoring contract.
        for implementation in ('mock', 'planned', 'connected', 'implemented_unverified', 'not_applicable'):
            for relationship in ('core', 'supporting', 'development_only', 'inspiration'):
                report = example_report()
                report['criteria']['new_feature']['score'] = 10
                report['total'] = 28
                report['feature_use']['mappings'][0].update(implementation=implementation, relationship=relationship)
                self.assertEqual(v.validate(report), [])

    def test_mapping_does_not_force_positive_score(self):
        for score, status in ((0, 'scored'), (None, 'partial')):
            report = example_report()
            report['criteria']['new_feature']['score'] = score
            report.update(total=18 if score == 0 else None, assessment=status)
            self.assertEqual(v.validate(report), [])

    def test_mapping_values(self):
        for key, value in [('announcement_id', 'DD00'), ('announcement_id', 'DD26'),
                           ('relationship', 'required'), ('basis', 'verified'), ('implementation', 'executed')]:
            report = example_report()
            report['feature_use']['mappings'][0][key] = value
            self.assert_invalid(report)
        for key, value in [('reference_version', 'devday-2026-v1.1'), ('source_url', 'https://example.com')]:
            report = template()
            report['feature_use'][key] = value
            self.assert_invalid(report)

    def test_judge_method_pairing_is_enforced_by_schema(self):
        schema = Draft202012Validator(json.loads(v.SCHEMA.read_text()))
        for judge in METHODS:
            for observations in METHODS:
                report = example_report(observations)
                report['judge'] = 'devday-judge-' + judge
                self.assertEqual(schema.is_valid(report), judge == observations)

    def test_method_specific_shapes_and_extra_fields(self):
        for method in METHODS:
            report = example_report(method)
            report['method_observations'] = dict(kind=method)
            self.assert_invalid(report)
            report = example_report(method)
            report['method_observations']['unrequested_thought_process'] = 'text'
            self.assert_invalid(report)
        report = example_report()
        del report['method_observations']['coverage']['originality']
        self.assert_invalid(report)
        report = example_report('journey')
        report['method_observations']['scenarios'].append(copy.deepcopy(report['method_observations']['scenarios'][0]))
        self.assert_invalid(report)
        report = example_report('challenge')
        report['method_observations']['claim_tests'][0]['affected_criteria'] = ['technical']
        self.assert_invalid(report)

    def test_positive_scores_cannot_have_empty_method_observations(self):
        for method in METHODS:
            report = example_report(method)
            if method == 'evidence':
                report['method_observations']['coverage']['utility']['claims'] = []
            elif method == 'journey':
                report['method_observations']['scenarios'] = []
            else:
                report['method_observations']['claim_tests'] = []
            self.assert_invalid(report)

    def test_positive_scores_need_observations_for_the_affected_criterion(self):
        for method in ('journey', 'challenge'):
            report = example_report(method)
            if method == 'journey':
                item = report['method_observations']['scenarios'][0]['steps'][0]
            else:
                item = report['method_observations']['claim_tests'][0]
            item['affected_criteria'].remove('utility')
            self.assert_invalid(report)
        report = example_report('journey')
        report['method_observations']['scenarios'][0]['scenario_type'] = 'exception'
        self.assert_invalid(report)

    def test_unavailable_and_empty_targets_do_not_need_fabricated_observations(self):
        for method in METHODS:
            report = template()
            report['judge'] = 'devday-judge-' + method
            if method == 'journey':
                report['method_observations'] = dict(kind='journey', scenarios=[], supplemental_checks=[],
                                                    completion_check='読める空の対象。確認した経路なし')
            elif method == 'challenge':
                report['method_observations'] = dict(kind='challenge', claim_tests=[], additional_checks=[],
                                                    completion_check='読める空の対象。検証する主張なし')
            self.assertEqual(v.validate(report), [])
            for item in report['criteria'].values():
                item['score'] = None
            report.update(total=None, assessment='unavailable')
            self.assertEqual(v.validate(report), [])

    def test_standalone_validator_cli_all_three_skills(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for method, skill in SKILLS.items():
                isolated = root / method
                shutil.copytree(skill, isolated)
                report_path = root / (method + '.json')
                report_path.write_text(json.dumps(example_report(method)))
                result = subprocess.run([sys.executable, str(isolated / 'scripts/validate_report.py'), str(report_path)],
                                        cwd=root, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                invalid = example_report(method)
                invalid['total'] += 1
                report_path.write_text(json.dumps(invalid))
                result = subprocess.run([sys.executable, str(isolated / 'scripts/validate_report.py'), str(report_path)],
                                        cwd=root, capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)

    def test_cli_rejects_invalid_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'bad.json'
            for bad in ('{"total": 0, "total": 40}', '{"score": NaN}', '{"score": Infinity}',
                        '{"score": -Infinity}', '[]', '{', 'null'):
                path.write_text(bad)
                result = subprocess.run([sys.executable, str(SKILLS['evidence'] / 'scripts/validate_report.py'), str(path)],
                                        capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0, bad)
                self.assertNotIn('Traceback', result.stderr)


class ComparisonTests(unittest.TestCase):
    def test_equal_scores_and_paths_do_not_hide_different_facts(self):
        left, right = example_report(), example_report('journey')
        right['evidence'][0]['observation'] = '資料が空のときは入力を追加するよう促す'
        result = comparison.compare(left, right)
        self.assertTrue(all(p['delta'] == 0 for p in result['criterion_scores'].values()))
        self.assertEqual(result['evidence_overlap']['paths']['jaccard'], 1)
        self.assertEqual(result['evidence_overlap']['literal_observations']['jaccard'], 0)
        self.assertEqual(len(result['candidate_unique_evidence']['right']), 1)
        self.assertNotIn('independent', result)

    def test_ids_are_local_and_locator_and_effects_matter(self):
        left, right = example_report(), example_report()
        serialized = json.dumps(right).replace('E1', 'E9')
        right = json.loads(serialized)
        result = comparison.compare(left, right)
        self.assertEqual(result['evidence_overlap']['observations_with_effects']['jaccard'], 1)
        right['evidence'][0]['locator'] = 'different_symbol'
        result = comparison.compare(left, right)
        self.assertEqual(result['evidence_overlap']['paths']['jaccard'], 1)
        self.assertEqual(result['evidence_overlap']['locations']['jaccard'], 0)
        right = example_report()
        right['criteria']['utility'].update(score=0, evidence_ids=[])
        right['total'] = 18
        right['method_observations']['coverage']['utility']['claims'] = []
        result = comparison.compare(left, right)
        self.assertEqual(result['evidence_overlap']['literal_observations']['jaccard'], 1)
        self.assertEqual(result['evidence_overlap']['observations_with_effects']['jaccard'], 0)

    def test_unknown_scores_and_empty_evidence_not_zero_overlap(self):
        left, right = template(), template()
        left['criteria']['utility']['score'] = None
        left.update(total=None, assessment='partial')
        result = comparison.compare(left, right)
        self.assertIsNone(result['criterion_scores']['utility']['delta'])
        self.assertIsNone(result['evidence_overlap']['paths']['jaccard'])

    def test_different_targets_and_invalid_reports_rejected(self):
        left, right = example_report(), example_report()
        right['target']['commit'] = 'different'
        with self.assertRaises(ValueError):
            comparison.compare(left, right)
        right = example_report()
        right['target']['changed_during_review'] = True
        left['target']['changed_during_review'] = True
        with self.assertRaises(ValueError):
            comparison.compare(left, right)
        right = example_report()
        right['total'] = 1
        with self.assertRaises(ValueError):
            comparison.compare(example_report(), right)


class ConditionATests(unittest.TestCase):
    def test_only_method_instructions_change_and_skills_stay_standalone(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / 'condition-a'
            condition_a.prepare(destination)
            for method, source in SKILLS.items():
                target = destination / source.name
                for relative in ('references/rubric.md', 'references/devday-2026.md', 'references/report.md',
                                 'references/report.schema.json', 'scripts/validate_report.py', 'agents/openai.yaml'):
                    self.assertEqual((source / relative).read_bytes(), (target / relative).read_bytes())
                self.assertNotEqual((source / 'SKILL.md').read_bytes(), (target / 'SKILL.md').read_bytes())
                report_path = Path(directory) / (method + '.json')
                report_path.write_text(json.dumps(example_report(method)))
                result = subprocess.run([sys.executable, str(target / 'scripts/validate_report.py'), str(report_path)],
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            with self.assertRaises(FileExistsError):
                condition_a.prepare(destination)

    def test_preparation_cannot_overwrite_distributed_skills(self):
        with self.assertRaises(ValueError):
            condition_a.prepare(ROOT / 'skills')


if __name__ == '__main__':
    unittest.main()
