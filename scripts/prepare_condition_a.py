"""Prepare an isolated v2 scoring control with the previous exploration workflow."""
import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
METHODS = ('evidence', 'journey', 'challenge')


def prepare(destination):
    destination = Path(destination).resolve()
    # Never merge into an existing directory or replace a distributed Skill.
    if destination == ROOT or ROOT in destination.parents:
        raise ValueError('use a new directory outside this repository')
    destination.mkdir(parents=True, exist_ok=False)
    for method in METHODS:
        source = ROOT / 'skills' / ('devday-judge-' + method)
        target = destination / source.name
        shutil.copytree(source, target, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        skill = (source / 'SKILL.md').read_text(encoding='utf-8')
        before, remainder = skill.split('## 調査方法', 1)
        _, after = remainder.split('## 完了と出力', 1)
        workflow = (ROOT / 'calibration/condition-a' / (method + '.md')).read_text(encoding='utf-8')
        (target / 'SKILL.md').write_text(before + workflow + '## 完了と出力' + after, encoding='utf-8')
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    try:
        destination = prepare(args.destination)
    except (OSError, ValueError) as exc:
        parser.exit(1, f'{exc}\n')
    print(f'Condition A prepared at {destination}; audit and hash A/B before model trials.')


if __name__ == '__main__':
    main()
