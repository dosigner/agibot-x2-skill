#!/usr/bin/env python3
"""Check skill file integrity offline, independently of client or robot tests."""
import argparse
import hashlib
import json
from pathlib import Path
import re

NAME = 'agibot-x2-interfaces'


def tree_hashes(root):
    root = Path(root)
    result = {}
    if root.is_symlink():
        raise ValueError('Skill root is a symlink: ' + str(root))
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError('Symlink in skill: ' + str(path))
        if '__pycache__' in path.parts or path.suffix == '.pyc':
            continue
        if path.is_file():
            result[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def verify(root, expected_version=None):
    root = Path(root)
    errors = []
    try:
        manifest = json.loads((root / 'package-manifest.json').read_text(encoding='utf-8'))
        if manifest.get('name') != NAME:
            errors.append('Unexpected package name')
        version = manifest.get('version')
        if not isinstance(version, str) or not re.fullmatch(r'\d+\.\d+\.\d+', version):
            errors.append('Invalid package version')
        if expected_version and version != expected_version:
            errors.append('Package version does not match selected release')
        expected = manifest['files']
        if not isinstance(expected, dict) or not expected:
            raise ValueError('Manifest has no file map')
        actual = tree_hashes(root)
        actual.pop('package-manifest.json', None)
        for name in sorted(expected.keys() - actual.keys()):
            errors.append('Missing file: ' + name)
        for name in sorted(actual.keys() - expected.keys()):
            errors.append('Unexpected file: ' + name)
        for name in sorted(actual.keys() & expected.keys()):
            if actual[name] != expected[name]:
                errors.append('Hash mismatch: ' + name)
        for required in ('SKILL.md', 'scripts/lookup.py', 'references/index.md'):
            if required not in expected:
                errors.append('Required file absent from manifest: ' + required)
        return dict(passed=not errors, name=NAME, version=version, files_checked=len(actual), errors=errors)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        return dict(passed=False, errors=[str(exc)])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skill', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--expected-version')
    args = parser.parse_args()
    report = verify(args.skill, args.expected_version)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
