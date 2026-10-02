#!/usr/bin/env python3
"""Install a verified skill, preserving different existing content by default.

--backup-existing requests an update with a backup outside skill discovery.
No client settings or dependencies are changed.
"""
import argparse
from datetime import datetime, timezone
import importlib.util
from pathlib import Path
import shutil
import sys
import tempfile
import uuid

NAME = 'agibot-x2-interfaces'
SOURCE = Path(__file__).resolve().parents[1] / 'skills' / NAME
CLIENT_DIR = {'codex': '.agents', 'cursor': '.cursor', 'claude': '.claude'}
spec = importlib.util.spec_from_file_location('x2_integrity', SOURCE / 'scripts/verify.py')
integrity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(integrity)
tree_hashes = integrity.tree_hashes


def install(client, base, dry_run=False, source=SOURCE, backup_existing=False):
    base = Path(base).expanduser().resolve()
    source = Path(source).expanduser().absolute()
    report = integrity.verify(source)
    if not report['passed']:
        raise ValueError('Source integrity check failed: ' + '; '.join(report['errors']))
    target = base / CLIENT_DIR[client] / 'skills' / NAME
    expected = tree_hashes(source)
    if client == 'cursor':
        identical_shared = None
        for shared in ('.agents', '.claude'):
            other = base / shared / 'skills' / NAME
            if other.exists() or other.is_symlink():
                if not other.is_symlink() and other.is_dir() and tree_hashes(other) == expected:
                    identical_shared = other
                else:
                    raise ValueError('Cursor has a different shared copy; left untouched: ' + str(other))
        if identical_shared and not target.exists() and not target.is_symlink():
            return 'already identical (shared discovery path): ' + str(identical_shared)
    for parent in (target, *target.parents):
        if parent == base:
            break
        if parent.is_symlink():
            raise ValueError('Destination uses a symlink; left untouched: ' + str(parent))
    exists = target.exists()
    if exists:
        if target.is_dir() and tree_hashes(target) == expected:
            return 'already identical: ' + str(target)
        if not backup_existing or not target.is_dir():
            raise ValueError('Existing installation differs; left untouched: ' + str(target))
    if dry_run:
        return ('would back up and install: ' if exists else 'would copy to: ') + str(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    backup = None
    with tempfile.TemporaryDirectory(prefix='.x2-stage-', dir=base) as temp:
        stage = Path(temp) / NAME
        shutil.copytree(source, stage, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        if tree_hashes(stage) != expected:
            raise ValueError('Staged copy failed integrity check')
        if exists:
            backup = base / '.agibot-x2-backups' / client / (
                datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]) / NAME
            for parent in backup.parents:
                if parent == base:
                    break
                if parent.is_symlink():
                    raise ValueError('Backup uses a symlink; left untouched: ' + str(parent))
            backup.parent.mkdir(parents=True, exist_ok=False)
            target.rename(backup)
        elif target.exists() or target.is_symlink():
            raise ValueError('Destination appeared while staging; left untouched')
        try:
            stage.rename(target)
        except OSError:
            if backup is not None and not target.exists() and not target.is_symlink():
                backup.rename(target)
            raise
    return 'installed: ' + str(target) + ('\nbackup: ' + str(backup) if backup else '')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--client', choices=tuple(CLIENT_DIR), required=True)
    where = parser.add_mutually_exclusive_group(required=True)
    where.add_argument('--project', type=Path, help='Target project root')
    where.add_argument('--user', action='store_true', help='Current OS user, all projects')
    parser.add_argument('--source', type=Path, default=SOURCE, help='An extracted skill folder')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--backup-existing', action='store_true')
    args = parser.parse_args()
    try:
        print(install(args.client, Path.home() if args.user else args.project,
                      args.dry_run, args.source, args.backup_existing))
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2)


if __name__ == '__main__':
    main()
