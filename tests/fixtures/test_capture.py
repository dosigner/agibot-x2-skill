import json
from pathlib import Path
import tempfile
import unittest

import capture


class CaptureTests(unittest.TestCase):
    def test_existing_description(self):
        self.assertEqual(capture.describe_frame(b'12',b'1234',9),
                         {'timestamp_ns':9,'rgb_bytes':2,'depth_bytes':4})

    def test_stores_bytes_and_metadata(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'nested'/'frames'
            output=capture.save_frame(root,b'\x00\xff\x01',b'\x10\x00\x20\x00',123)
            self.assertIsInstance(output,Path)
            self.assertEqual(output,root/'123')
            self.assertEqual((output/'rgb.bin').read_bytes(),b'\x00\xff\x01')
            self.assertEqual((output/'depth.bin').read_bytes(),b'\x10\x00\x20\x00')
            self.assertEqual(json.loads((output/'metadata.json').read_text()),
                             capture.describe_frame(b'\x00\xff\x01',b'\x10\x00\x20\x00',123))

    def test_collision_preserves_existing_frame(self):
        with tempfile.TemporaryDirectory() as d:
            output=capture.save_frame(d,b'rgb',b'depth',88)
            before={p.name:p.read_bytes() for p in output.iterdir()}
            with self.assertRaises(FileExistsError):
                capture.save_frame(d,b'new',b'other',88)
            self.assertEqual(before,{p.name:p.read_bytes() for p in output.iterdir()})

    def test_zero_and_multiple_timestamps(self):
        with tempfile.TemporaryDirectory() as d:
            for n in (0,1,2000000000):
                self.assertEqual(capture.save_frame(d,b'a',b'b',n),Path(d)/str(n))


if __name__=='__main__':
    unittest.main(verbosity=2)
