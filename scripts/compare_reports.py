"""Compare two v2 reports; overlap is descriptive, never an independence verdict."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    'report_validator', ROOT / 'skills/devday-judge-evidence/scripts/validate_report.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def normalize(value):
    return ' '.join(value.split())


def cited_evidence(report):
    """Track score effects separately from location and observed fact."""
    effects = {e['id']: set() for e in report['evidence']}
    used = {eid for _, eid in validator.evidence_references(report)}
    for criterion, item in report['criteria'].items():
        for eid in item['evidence_ids']:
            effects[eid].add(criterion)

    def walk(value, inherited=()):
        if isinstance(value, dict):
            affected = value.get('affected_criteria', inherited)
            for key, child in value.items():
                if key.endswith('evidence_ids'):
                    for eid in child:
                        effects[eid].update(affected)
                else:
                    walk(child, affected)
        elif isinstance(value, list):
            for child in value:
                walk(child, inherited)

    method = report['method_observations']
    if method['kind'] == 'evidence':
        for criterion, coverage in method['coverage'].items():
            walk(coverage, (criterion,))
        walk(method['additional_checks'])
    else:
        walk(method)
    return [dict(e, affected_criteria=sorted(effects[e['id']]))
            for e in report['evidence'] if e['id'] in used]


def overlap(left, right):
    union = left | right
    return dict(left_count=len(left), right_count=len(right), shared_count=len(left & right),
                jaccard=len(left & right) / len(union) if union else None)


def compare(left, right):
    for report in (left, right):
        errors = validator.validate(report)
        if errors:
            raise ValueError('\n'.join(errors))
    if left['target'] != right['target']:
        raise ValueError('target metadata differs; use reports from the same fixed snapshot')
    if left['target']['changed_during_review'] or right['target']['changed_during_review']:
        raise ValueError('target changed during review; comparison needs a fixed snapshot')
    a, b = cited_evidence(left), cited_evidence(right)
    keys = {
        'paths': lambda e: e['path'],
        'locations': lambda e: (e['path'], normalize(e['locator'])),
        'literal_observations': lambda e: (e['path'], normalize(e['locator']), normalize(e['observation'])),
        'observations_with_effects': lambda e: (e['path'], normalize(e['locator']), normalize(e['observation']),
                                                tuple(e['affected_criteria'])),
    }
    sets = {name: ({key(e) for e in a}, {key(e) for e in b}) for name, key in keys.items()}
    fact_key = keys['literal_observations']
    score_pairs = {}
    for criterion in validator.CRITERIA:
        x, y = left['criteria'][criterion]['score'], right['criteria'][criterion]['score']
        score_pairs[criterion] = dict(left=x, right=y, delta=None if x is None or y is None else y - x)
    return dict(
        judges=[left['judge'], right['judge']], criterion_scores=score_pairs,
        evidence_overlap={name: overlap(*pair) for name, pair in sets.items()},
        candidate_unique_evidence={
            'left': [e for e in a if fact_key(e) not in sets['literal_observations'][1]],
            'right': [e for e in b if fact_key(e) not in sets['literal_observations'][0]],
        },
        method_observations=[left['method_observations'], right['method_observations']],
        limitations=[
            'Overlap uses literal observations with whitespace normalization, not semantic equivalence.',
            'Empty unions have null overlap. Matching paths or scores do not establish independence.',
            'Target metadata does not prove identical contents; verify the fixed snapshot externally.',
            'Humans must match equivalent facts, check citations, importance, omissions, and score effects.',
        ])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('left', type=Path)
    parser.add_argument('right', type=Path)
    args = parser.parse_args()
    try:
        reports = [json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=validator.unique_object,
                              parse_constant=validator.reject_constant) for path in (args.left, args.right)]
        result = compare(*reports)
    except (OSError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
