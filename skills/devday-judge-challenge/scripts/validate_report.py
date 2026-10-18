"""Validate a v2.0 report's structure and invariants, not evidence truth or quality."""
import argparse
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator

SCHEMA = Path(__file__).resolve().parents[1] / 'references/report.schema.json'
CRITERIA = ('new_feature', 'usability', 'utility', 'originality')


def evidence_references(value, path=''):
    """Include references in every method-specific observation, not only scores."""
    if isinstance(value, dict):
        for key, child in value.items():
            location = f'{path}.{key}' if path else key
            if key.endswith('evidence_ids'):
                for eid in child:
                    yield location, eid
            else:
                yield from evidence_references(child, location)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from evidence_references(child, f'{path}.{index}')


def validate(report):
    schema = json.loads(SCHEMA.read_text(encoding='utf-8'))
    errors = [f"{'.'.join(map(str, e.absolute_path))}: {e.message}"
              for e in Draft202012Validator(schema).iter_errors(report)]
    if errors:
        return errors

    scores = [report['criteria'][key]['score'] for key in CRITERIA]
    # JSON Schema also treats 1.0 as integral; this contract requires integer tokens.
    for key, score in zip(CRITERIA, scores):
        if score is not None and type(score) is not int:
            errors.append(f'criteria.{key}.score: must be an integer or null')
        if score is not None and score > 0 and not report['criteria'][key]['evidence_ids']:
            errors.append(f'criteria.{key}.evidence_ids: positive scores need evidence')
    expected = None if None in scores else sum(scores)
    if report['total'] != expected:
        errors.append('total: must equal the four criterion scores, or null if missing')
    if report['total'] is not None and type(report['total']) is not int:
        errors.append('total: must be an integer or null')
    status = ('unavailable' if all(v is None for v in scores)
              else 'partial' if None in scores else 'scored')
    if report['assessment'] != status:
        errors.append(f'assessment: must be {status} for these four scores')

    ids = [e['id'] for e in report['evidence']]
    defined = set(ids)
    if len(defined) != len(ids):
        errors.append('evidence: duplicate IDs')
    for path, eid in evidence_references(report):
        if eid not in defined:
            errors.append(f'{path}: undefined {eid}')

    new_feature = report['criteria']['new_feature']
    mappings = report['feature_use']['mappings']
    feature_ids = set(new_feature['evidence_ids'])
    for index, mapping in enumerate(mappings):
        if not set(mapping['evidence_ids']).issubset(feature_ids):
            errors.append(f'feature_use.mappings.{index}: evidence must also support new_feature')
    score = new_feature['score']
    if score is not None and score > 0 and not mappings:
        errors.append('feature_use.mappings: positive new_feature score needs a supported mapping')
    if score is not None and score >= 3 and not any(
            m['relationship'] != 'mention_only' for m in mappings):
        errors.append('feature_use.mappings: scores >= 3 need more than name mentions')
    # No caps for mock, planned, development_only, or any implementation category.
    method = report['method_observations']
    positive = {key for key in CRITERIA
                if report['criteria'][key]['score'] is not None
                and report['criteria'][key]['score'] > 0}
    if method['kind'] == 'evidence':
        for key in positive:
            claims = method['coverage'][key]['claims']
            criterion_ids = set(report['criteria'][key]['evidence_ids'])
            if not any(criterion_ids.intersection(c['evidence_ids']) for c in claims):
                errors.append(f'method_observations.coverage.{key}: positive score needs a supported claim')
    if method['kind'] == 'journey':
        scenario_ids = [s['id'] for s in method['scenarios']]
        if len(scenario_ids) != len(set(scenario_ids)):
            errors.append('method_observations.scenarios: duplicate IDs')
        if positive and not any(s['scenario_type'] == 'normal' and any(
                step['evidence_ids'] for step in s['steps']) for s in method['scenarios']):
            errors.append('method_observations.scenarios: positive scores need an evidenced normal path')
        observations = [step for scenario in method['scenarios'] for step in scenario['steps']]
        observations += method['supplemental_checks']
        for key in positive:
            criterion_ids = set(report['criteria'][key]['evidence_ids'])
            if not any(key in item['affected_criteria'] and criterion_ids.intersection(item['evidence_ids'])
                       for item in observations):
                errors.append(f'method_observations: no evidenced journey observation for {key}')
    if method['kind'] == 'challenge':
        for key in positive:
            criterion_ids = set(report['criteria'][key]['evidence_ids'])
            if not any(key in item['affected_criteria']
                       and criterion_ids.intersection(item['supporting_evidence_ids'])
                       for item in method['claim_tests']):
                errors.append(f'method_observations.claim_tests: no supported test for {key}')
    return errors


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate JSON key: {key}')
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f'invalid JSON: {value}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    args = parser.parse_args()
    try:
        report = json.loads(args.report.read_text(encoding='utf-8'),
                            object_pairs_hook=unique_object, parse_constant=reject_constant)
        errors = validate(report)
    except (OSError, ValueError) as exc:
        errors = [str(exc)]
    for error in errors:
        print(error, file=sys.stderr)
    if not errors:
        print('Report contract valid; evidence and scores still require review.')
    return bool(errors)


if __name__ == '__main__':
    sys.exit(main())
