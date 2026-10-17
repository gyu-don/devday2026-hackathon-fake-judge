"""Check that each standalone judge ships identical shared contracts and validator."""
from pathlib import Path
import sys
root = Path(__file__).resolve().parents[1]
skills = [root / 'skills' / ('devday-judge-' + n) for n in ('evidence', 'journey', 'challenge')]
files = ['references/' + n for n in ('rubric.md', 'devday-2026.md', 'report.md', 'report.schema.json')]
files += ['scripts/validate_report.py']
errors = []
for name in files:
    try:
        if len({(p / name).read_bytes() for p in skills}) != 1:
            errors.append('Mismatch: ' + name)
    except OSError as exc:
        errors.append(str(exc))
print('\n'.join(errors) if errors else 'All three standalone contracts match.')
sys.exit(bool(errors))
