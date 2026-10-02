import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/agibot-x2-interfaces'
LOOKUP=SKILL/'scripts/lookup.py'
sys.path.insert(0,str(ROOT/'tools'))
from install_skill import install,tree_hashes
from validate_package import validate

class PackageTests(unittest.TestCase):
    def lookup(self,*args,script=LOOKUP,ok=True):
        result=subprocess.run([sys.executable,str(script),*args],cwd=tempfile.gettempdir(),text=True,capture_output=True)
        self.assertEqual(result.returncode,0 if ok else 2,result.stderr)
        return json.loads(result.stdout) if ok else result

    def test_links_only_scope(self):
        report=validate(SKILL)
        self.assertTrue(report['passed'],report['errors'])
        self.assertEqual(report['bundled_type_definitions'],0)
        self.assertEqual(report['bundled_robot_spec_tables'],0)

    def test_every_feature_both_languages(self):
        index=self.lookup('--index');self.assertEqual(len(index),23)
        for item in index:
            for lang in ('python','cpp'):
                record=self.lookup('--feature',item['id'],'--language',lang)
                self.assertFalse(record['contracts_included'])
                self.assertNotIn('endpoints',record)
                self.assertTrue(record['sources'])
                for example in record['examples']:self.assertEqual(set(example['urls']),{lang})

    def test_every_example_and_camera_subexamples(self):
        for number in range(1,37):
            for lang in ('python','cpp'):
                self.assertEqual(self.lookup('--example',str(number),'--language',lang)['official_number'],number)
        for sensor,tail in [('rgbd','rgbd'),('stereo','stereo'),('rear','head-rear')]:
            for lang,prefix in [('python','py'),('cpp','cpp')]:
                row=self.lookup('--example','14','--sensor',sensor,'--language',lang)
                self.assertTrue(row['urls'][lang].endswith('#'+prefix+'-echo-camera-'+tail))

    def test_sensor_scope(self):
        for feature,sensor,number in [('4.1','rgbd',14),('4.2','chest',17),('4.2','lidar',16),('4.3','lidar',16),('4.3','gnss',34),('4.3','touch',15)]:
            row=self.lookup('--feature',feature,'--sensor',sensor)
            self.assertEqual([x['official_number'] for x in row['examples']],[number])
            self.assertLess(len(json.dumps(row,ensure_ascii=False).encode()),5000)

    def test_all_type_routes_have_no_definitions(self):
        routes=json.loads((SKILL/'references/data/routes.json').read_text())
        self.assertEqual(len(routes['types']),93)
        for name,row in routes['types'].items():
            self.assertFalse(row['definition_included'])
            self.assertEqual(set(row),{'name','sources','definition_included'})
        row=self.lookup('--type','GetAllJointState')
        self.assertFalse(row['definition_included'])
        self.assertNotIn('variants',row)
        self.assertTrue(row['sources'])

    def test_search_and_invalid_queries(self):
        self.assertEqual(self.lookup('--search','RGB-D')[0]['id'],'4.1')
        self.assertIn('4.2',[x['id'] for x in self.lookup('--search','IMU')])
        for args in [('--feature','6.1'),('--example','99'),('--type','../../secret'),('--feature','1.1','--sensor','rgbd'),('--example','14','--sensor','lidar'),('--index','--language','cpp')]:
            self.lookup(*args,ok=False)

    def test_relocation_and_preservation(self):
        with tempfile.TemporaryDirectory(prefix='x2 links space ') as temp:
            for client,directory in [('codex','.agents'),('claude','.claude'),('cursor','.cursor')]:
                base=Path(temp)/client;install(client,base,True);self.assertFalse(base.exists());install(client,base)
                target=base/directory/'skills'/SKILL.name
                self.assertEqual(tree_hashes(SKILL),tree_hashes(target))
                self.assertEqual(self.lookup('--feature','4.1','--sensor','rgbd',script=target/'scripts/lookup.py')['id'],'4.1')
                self.assertTrue(validate(target)['passed'])
                self.assertIn('already identical',install(client,base))
                (target/'user.txt').write_text('preserved')
                with self.assertRaises(ValueError):install(client,base)
                self.assertEqual((target/'user.txt').read_text(),'preserved')

    def test_missing_feature_reference_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp)/SKILL.name;shutil.copytree(SKILL,target)
            (target/'references/features/4.1.md').unlink()
            self.assertFalse(validate(target)['passed'])

    def test_restored_manufacturer_snapshot_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp)/SKILL.name;shutil.copytree(SKILL,target)
            data=target/'references/data/routes.json';routes=json.loads(data.read_text())
            routes['types']['TouchState']['definition']='unexpected payload'
            data.write_text(json.dumps(routes))
            self.assertFalse(validate(target)['passed'])

if __name__=='__main__':unittest.main(verbosity=2)
