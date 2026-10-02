#!/usr/bin/env python3
"""Check release checksums, file sets, links and publication scan, offline."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
from urllib.parse import unquote, urldefrag, urlsplit
import zipfile
from export_release import public_paths, scan_files
from validate_package import validate

ROOT = Path(__file__).resolve().parents[1]


def check(root):
    errors = []
    skill = root / 'skills/agibot-x2-interfaces'
    version = (root / 'VERSION').read_text(encoding='utf-8').strip()
    spec = importlib.util.spec_from_file_location('x2_verify', skill / 'scripts/verify.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    integrity = module.verify(skill, version)
    errors.extend(integrity['errors'])
    validation = validate(skill)
    errors.extend(validation['errors'])
    paths = public_paths(root)
    errors.extend(str(finding) for finding in scan_files(root, paths))
    inventory_path = root / 'PUBLIC_MANIFEST.json'
    if inventory_path.is_file():
        inventory = json.loads(inventory_path.read_text(encoding='utf-8'))
        observed = {rel.as_posix(): hashlib.sha256((root / rel).read_bytes()).hexdigest() for rel in paths}
        if inventory.get('version') != version or inventory.get('files') != observed:
            errors.append('Public source inventory does not match selected files')
    expected = {p.relative_to(skill).as_posix(): p.read_bytes() for p in skill.rglob('*')
                if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}
    digests = []
    for name in ('agibot-x2-interfaces.zip', 'agibot-x2-interfaces-' + version + '.zip'):
        archive = root / 'dist' / name
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        digests.append(digest)
        if archive.with_suffix('.zip.sha256').read_text(encoding='utf-8').strip() != digest + '  ' + name:
            errors.append('ZIP checksum mismatch: ' + name)
        with zipfile.ZipFile(archive) as zf:
            names = zf.namelist()
            wanted = [skill.name + '/' + name for name in expected]
            if len(names) != len(set(names)) or set(names) != set(wanted):
                errors.append('ZIP file set mismatch: ' + name)
            for rel, data in expected.items():
                member = skill.name + '/' + rel
                if member not in names or zf.read(member) != data:
                    errors.append('ZIP content mismatch: ' + member)
    if len(set(digests)) != 1:
        errors.append('Stable and versioned skill ZIPs differ')
    links = 0
    for rel in paths:
        if rel.suffix != '.md':
            continue
        file = root / rel
        for target in re.findall(r'\[[^\]]*\]\(([^\s)]+)\)', file.read_text(encoding='utf-8')):
            parsed = urlsplit(target)
            if parsed.scheme:
                continue
            path = unquote(urldefrag(target)[0])
            if not path:
                continue
            links += 1
            resolved = (file.parent / path).resolve()
            if not resolved.is_relative_to(root.resolve()) or not resolved.exists():
                errors.append('Broken/local link: ' + rel.as_posix() + ' -> ' + target)
    return dict(passed=not errors, version=version, skill_files=len(expected), public_files=len(paths),
                relative_links_checked=links, privacy_pattern_findings=scan_files(root, paths),
                raw_source_audit='not_run', errors=errors)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        report = check(args.root.resolve())
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        report = dict(passed=False, errors=[str(exc)])
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
