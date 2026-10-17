"""Validate a judge report's structure and cross-field invariants (not its truth)."""
import argparse
import json
from pathlib import Path
import sys
from jsonschema import Draft202012Validator

SCHEMA = Path(__file__).resolve().parents[1] / 'references/report.schema.json'

def validate(report):
    schema = json.loads(SCHEMA.read_text())
    errors = [f"{'.'.join(map(str, e.absolute_path))}: {e.message}"
              for e in Draft202012Validator(schema).iter_errors(report)]
    if errors:
        return errors
    scores = [c['score'] for c in report['criteria'].values()]
    expected = None if None in scores else sum(scores)
    if report['total'] != expected:
        errors.append('total: must equal the four criterion scores, or null if missing')
    all_scores = scores + [report['theme']['score']]
    status = report['assessment']
    if status == 'unavailable' and any(v is not None for v in all_scores):
        errors.append('unavailable: all scores must be null')
    if status == 'scored' and None in all_scores:
        errors.append('scored: scores cannot be null')
    if status == 'partial' and None not in all_scores:
        errors.append('partial: at least one score must be null')
    theme = report['theme']['score']
    match = ('undetermined' if theme is None else 'mismatch' if theme <= 2
             else 'weak' if theme <= 4 else 'partial' if theme <= 6 else 'strong')
    if report['theme']['match'] != match:
        errors.append('theme.match: inconsistent with theme.score')
    ids = [e['id'] for e in report['evidence']]
    if len(set(ids)) != len(ids):
        errors.append('evidence: duplicate IDs')
    for group in [*report['criteria'].values(), *report['theme']['mappings']]:
        for eid in group['evidence_ids']:
            if eid not in ids:
                errors.append(f'evidence_ids: undefined {eid}')
    policy = report['event_policy']
    if bool(policy['rules']) == (policy['eligibility'] == 'not_specified'):
        errors.append('event_policy: rules and eligibility disagree')
    return errors

def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate JSON key: {key}')
        result[key] = value
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    args = parser.parse_args()
    try:
        report = json.loads(args.report.read_text(), object_pairs_hook=unique_object,
                            parse_constant=lambda v: (_ for _ in ()).throw(ValueError(f'invalid JSON: {v}')))
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
