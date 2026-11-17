import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from install_skill import install, integrity, tree_hashes
from check_release import check
from export_release import scan_text

SKILLS = sorted(p for p in (ROOT / 'skills').iterdir() if (p / 'SKILL.md').is_file())


class FieldSkillTests(unittest.TestCase):
    def test_every_skill_standalone_zip_and_relocated_install(self):
        with tempfile.TemporaryDirectory(prefix='x2 field space ') as temp:
            base = Path(temp)
            for source in SKILLS:
                with self.subTest(skill=source.name):
                    extracted = base / 'extracted' / source.name
                    with zipfile.ZipFile(ROOT / 'dist' / (source.name + '.zip')) as archive:
                        self.assertEqual({Path(n).parts[0] for n in archive.namelist()}, {source.name})
                        archive.extractall(extracted.parent)
                    result = subprocess.run([sys.executable, str(extracted / 'scripts/verify.py'),
                                             '--expected-version', (ROOT / 'VERSION').read_text().strip()], cwd=base,
                                            text=True, capture_output=True)
                    self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                    for client, directory in [('codex', '.agents'), ('claude', '.claude'), ('cursor', '.cursor')]:
                        project = base / client
                        install(client, project, source=extracted)
                        target = project / directory / 'skills' / source.name
                        self.assertEqual(tree_hashes(target), tree_hashes(source))
                        self.assertIn('already identical', install(client, project, source=extracted))
                    if source.name != 'agibot-x2-interfaces':
                        self.assertFalse((extracted / 'scripts/lookup.py').exists())

    def test_specialist_conflict_backup_and_shared_cursor_discovery(self):
        source = ROOT / 'skills/agibot-x2-sensors'
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            install('codex', base, source=source)
            self.assertIn('shared discovery', install('cursor', base, source=source))
            target = base / '.agents/skills' / source.name
            (target / 'local-note.txt').write_text('preserve local work')
            before = tree_hashes(target)
            with self.assertRaises(ValueError):
                install('codex', base, source=source)
            install('codex', base, source=source, backup_existing=True)
            backup = next((base / '.agibot-x2-backups/codex').glob('*/' + source.name))
            self.assertEqual(tree_hashes(backup), before)
            self.assertEqual(tree_hashes(target), tree_hashes(source))

    def test_selected_skill_cli_does_not_install_interface(self):
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run([sys.executable, str(ROOT / 'tools/install_skill.py'),
                                     '--client', 'codex', '--project', temp,
                                     '--skill', 'agibot-x2-voice'], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((Path(temp) / '.agents/skills/agibot-x2-voice/SKILL.md').is_file())
            self.assertFalse((Path(temp) / '.agents/skills/agibot-x2-interfaces').exists())

    def test_specialist_identity_and_tamper_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / 'agibot-x2-sensors'
            shutil.copytree(ROOT / 'skills' / source.name, source)
            manifest = source / 'package-manifest.json'
            original = manifest.read_text()
            data = json.loads(original)
            data['name'] = 'agibot-x2-voice'
            manifest.write_text(json.dumps(data))
            self.assertFalse(integrity.verify(source)['passed'])
            manifest.write_text(original)
            (source / 'references/lessons.md').write_text('tampered')
            with self.assertRaisesRegex(ValueError, 'integrity'):
                install('codex', Path(temp) / 'project', source=source)
            self.assertFalse((Path(temp) / 'project').exists())

    def test_deterministic_rebuild_all_archives(self):
        before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in (ROOT / 'dist').glob('*.zip')}
        subprocess.run([sys.executable, str(ROOT / 'tools/package_skill.py')],
                       check=True, capture_output=True)
        after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in (ROOT / 'dist').glob('*.zip')}
        self.assertEqual(before, after)

    def test_mac_author_path_scanned(self):
        self.assertIn('local author path', scan_text('/Us' + 'ers/' + 'example' + '/private/file'))

    def test_specialist_archive_corruption_is_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            copied = Path(temp) / 'repo'
            shutil.copytree(ROOT, copied, ignore=shutil.ignore_patterns('.git', '__pycache__'))
            archive = copied / 'dist/agibot-x2-sensors.zip'
            with zipfile.ZipFile(archive, 'a') as zf:
                zf.writestr('agibot-x2-sensors/extra.txt', 'unexpected')
            report = check(copied)
            self.assertFalse(report['passed'])
            self.assertTrue(any('ZIP file set mismatch' in e for e in report['errors']))


if __name__ == '__main__':
    unittest.main(verbosity=2)
