import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from install_skill import SOURCE, install, integrity, tree_hashes
from export_release import export, public_paths, scan_text
from check_release import check
from validate_package import validate


class ReleaseTests(unittest.TestCase):
    def test_current_release(self):
        report = check(ROOT)
        self.assertTrue(report['passed'], report['errors'])

    def test_integrity_detects_modification_extra_missing_and_version(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / SOURCE.name
            shutil.copytree(SOURCE, source)
            self.assertFalse(integrity.verify(source, '0.0.0')['passed'])
            entry = source / 'SKILL.md'
            original = entry.read_bytes()
            entry.write_bytes(original + b'changed')
            self.assertFalse(integrity.verify(source)['passed'])
            with self.assertRaisesRegex(ValueError, 'integrity'):
                install('codex', Path(temp) / 'target', source=source)
            self.assertFalse((Path(temp) / 'target').exists())
            entry.write_bytes(original)
            extra = source / 'user-file.txt'
            extra.write_text('preserve')
            self.assertFalse(integrity.verify(source)['passed'])
            extra.unlink()
            entry.unlink()
            self.assertFalse(integrity.verify(source)['passed'])

    def test_backup_update_and_idempotency(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            install('claude', base)
            target = base / '.claude/skills' / SOURCE.name
            marker = target / 'my-notes.txt'
            marker.write_text('user edits', encoding='utf-8')
            before = tree_hashes(target)
            with self.assertRaises(ValueError):
                install('claude', base)
            self.assertEqual(tree_hashes(target), before)
            dry = install('claude', base, True, backup_existing=True)
            self.assertIn('would back up', dry)
            self.assertFalse((base / '.agibot-x2-backups').exists())
            install('claude', base, backup_existing=True)
            backups = list((base / '.agibot-x2-backups/claude').glob('*/' + SOURCE.name))
            self.assertEqual(len(backups), 1)
            self.assertEqual(tree_hashes(backups[0]), before)
            self.assertEqual(tree_hashes(target), tree_hashes(SOURCE))
            self.assertIn('already identical', install('claude', base, backup_existing=True))
            self.assertEqual(len(list((base / '.agibot-x2-backups/claude').glob('*'))), 1)

    def test_failed_replacement_restores_existing_install(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            install('codex', base)
            target = base / '.agents/skills' / SOURCE.name
            (target / 'keep.txt').write_text('keep me')
            before = tree_hashes(target)
            original = Path.rename
            def fail_stage(path, destination):
                if path.parent.name.startswith('.x2-stage-'):
                    raise OSError('simulated replacement failure')
                return original(path, destination)
            with patch.object(Path, 'rename', fail_stage):
                with self.assertRaises(OSError):
                    install('codex', base, backup_existing=True)
            self.assertEqual(tree_hashes(target), before)

    def test_cursor_shared_install_reuse_and_conflict(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            install('codex', base)
            self.assertIn('shared discovery', install('cursor', base))
            self.assertFalse((base / '.cursor').exists())
            install('claude', base)
            (base / '.claude/skills' / SOURCE.name / 'custom.txt').write_text('different')
            with self.assertRaisesRegex(ValueError, 'shared copy'):
                install('cursor', base)
            self.assertFalse((base / '.cursor').exists())

    def test_symlink_source_and_target_are_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            linked = base / 'source-link'
            linked.symlink_to(SOURCE, target_is_directory=True)
            with self.assertRaises(ValueError):
                install('codex', base / 'project', source=linked)
            elsewhere = base / 'elsewhere'
            elsewhere.mkdir()
            target = base / '.agents'
            target.symlink_to(elsewhere, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'symlink'):
                install('codex', base)
            self.assertEqual(list(elsewhere.iterdir()), [])

    def test_standalone_zip_extraction_and_lookup_from_elsewhere(self):
        with tempfile.TemporaryDirectory(prefix='x2 ZIP space ') as temp:
            base = Path(temp)
            with zipfile.ZipFile(ROOT / 'dist/agibot-x2-interfaces.zip') as archive:
                archive.extractall(base)
            skill = base / SOURCE.name
            self.assertTrue(integrity.verify(skill)['passed'])
            result = subprocess.run([sys.executable, str(skill / 'scripts/lookup.py'),
                                     '--feature', '4.1', '--sensor', 'rgbd', '--language', 'python'],
                                    cwd=base.parent, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['id'], '4.1')
            self.assertFalse((base / 'tools/install_skill.py').exists())

    def test_basic_validation_explicitly_skips_private_audit(self):
        report = validate(SOURCE)
        self.assertTrue(report['passed'])
        self.assertEqual(report['raw_source_audit'], 'not_run')
        result = subprocess.run([sys.executable, str(ROOT / 'tools/validate_package.py'),
                                 '--evidence', str(ROOT / 'definitely-missing-evidence')], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(json.loads(result.stdout)['passed'])

    def test_public_export_preserves_scope_and_refuses_existing_output(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / 'github-source'
            report = export(ROOT, out)
            self.assertTrue(Path(report['source_zip']).is_file())
            self.assertFalse((out / 'evidence').exists())
            self.assertFalse((out / 'VALIDATION_KO.md').exists())
            self.assertFalse((out / 'dist/agibot-x2-interfaces-1.0.0.zip').exists())
            self.assertEqual(set(json.loads((out / 'PUBLIC_MANIFEST.json').read_text())['files']),
                             {p.as_posix() for p in public_paths(ROOT)})
            self.assertTrue(check(out)['passed'])
            with self.assertRaises(ValueError):
                export(ROOT, out)

    def test_publication_scan_detects_representative_credentials(self):
        token = 'gh' + 'p_' + 'A' * 30
        self.assertIn('GitHub token', scan_text(token))
        self.assertIn('local author path', scan_text('/home/' + 'dj' + '/example/file'))
        self.assertIn('private key', scan_text('-----BEGIN ' + 'PRIVATE KEY-----'))
        self.assertEqual(scan_text('AGIBOT X2 package'), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
