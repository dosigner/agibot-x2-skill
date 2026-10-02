#!/usr/bin/env python3
"""Export an allowlisted GitHub source tree and deterministic source ZIP.

Never uploads files. Raw evidence and historical authoring documents stay local.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def public_paths(root):
    paths = set()
    for pattern in json.loads((root / 'public_files.json').read_text(encoding='utf-8')):
        matches = [p for p in root.glob(pattern) if p.is_file() or p.is_symlink()]
        if not matches:
            raise ValueError('Public file pattern has no matches: ' + pattern)
        for path in matches:
            if path.is_symlink():
                raise ValueError('Symlink in public files: ' + str(path))
            if '__pycache__' not in path.parts and path.suffix != '.pyc':
                paths.add(path.relative_to(root))
    return sorted(paths)


def scan_text(text):
    patterns = {
        'local author path': r'/(?:home/d[j]|tmp/agibot[-])[^\s)"\x27]*',
        'GitHub token': r'\b(?:gh[pousr]_|github_pat_)[A-Za-z0-9_]{20,}',
        'API key': r'\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{24,}',
        'private key': r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
        'embedded credential URL': r'https?://[^\s/@]+:[^\s/@]+@',
        'authorization credential': r'(?i)authorization\s*[:=]\s*["\x27]?(?:bearer|token)\s+[A-Za-z0-9_.-]{20,}',
    }
    return [label for label, pattern in patterns.items() if re.search(pattern, text)]


def scan_files(root, paths):
    findings = []
    for rel in paths:
        path = root / rel
        if path.suffix == '.zip':
            with zipfile.ZipFile(path) as archive:
                for name in archive.namelist():
                    for kind in scan_text(archive.read(name).decode('utf-8', errors='replace')):
                        findings.append({'file': rel.as_posix() + ':' + name, 'kind': kind})
        else:
            for kind in scan_text(path.read_text(encoding='utf-8')):
                findings.append({'file': rel.as_posix(), 'kind': kind})
    return findings


def export(root, output):
    paths = public_paths(root)
    findings = scan_files(root, paths)
    if findings:
        raise ValueError('Publication scan found: ' + json.dumps(findings))
    if output.exists():
        raise ValueError('Output already exists; choose a new directory: ' + str(output))
    output.mkdir(parents=True)
    hashes = {}
    for rel in paths:
        target = output / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / rel, target)
        hashes[rel.as_posix()] = hashlib.sha256(target.read_bytes()).hexdigest()
    version = (root / 'VERSION').read_text(encoding='utf-8').strip()
    inventory = {'version': version, 'files': hashes, 'excluded': [
        'manufacturer definitions, source HTML caches, joint and FOV specification tables',
        'raw evaluation evidence and full client transcripts',
        'historical local README_KO.md, VALIDATION_KO.md, COMPATIBILITY_KO.md',
        'historical 1.0.0 ZIP (preserved in authoring workspace)',
    ], 'scan': {'findings': findings, 'scope': 'selected text files and skill ZIP contents; pattern scan plus maintainer review, not a complete secret audit'}}
    (output / 'PUBLIC_MANIFEST.json').write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    archive = output.parent / ('agibot-x2-github-source-' + version + '.zip')
    if archive.exists():
        raise ValueError('Source ZIP already exists; choose a new output parent')
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(p for p in output.rglob('*') if p.is_file()):
            info = zipfile.ZipInfo('agibot-x2-skill/' + path.relative_to(output).as_posix(), (2026, 10, 2, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            zf.writestr(info, path.read_bytes())
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix('.zip.sha256').write_text(digest + '  ' + archive.name + '\n', encoding='utf-8')
    return dict(source_tree=str(output), source_zip=str(archive), files=len(hashes)+1, sha256=digest)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path, help='New directory for curated source tree')
    args = parser.parse_args()
    try:
        print(json.dumps(export(ROOT, args.output.resolve()), indent=2))
    except (ValueError, OSError) as exc:
        parser.exit(2, str(exc) + '\n')


if __name__ == '__main__':
    main()
