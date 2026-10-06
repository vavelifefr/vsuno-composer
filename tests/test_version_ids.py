"""Stable chunk identity and backward-compatible version lookup."""
import json
import re
import tempfile
import unittest
from pathlib import Path

from test_chunk import chunk, runtime


class VersionIdTests(unittest.TestCase):
    def test_new_id_letters_timestamp_matches_info_record_and_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            item = runtime.archive_chunk(root, chunk())
            self.assertRegex(item['id'], r'^[a-z]{6}_\d{8}T\d{12}Z$')
            info = runtime.parse_chunk(item['chunk'])['INFO']
            self.assertEqual(runtime.info_values(info, 'ID'), [item['id']])
            self.assertEqual(runtime.info_values(info, 'version'), [])
            self.assertEqual(runtime.get_track(root, item['id']), item)
            self.assertEqual(runtime.list_tracks(root)[0]['id'], item['id'])
            self.assertTrue((root/'prompts'/('Test composition_'+item['id']+'.txt')).exists())

    def test_archive_replaces_incoming_id_and_version_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = runtime.archive_chunk(root, chunk())
            second = runtime.archive_chunk(root, first['chunk'], parent=first['id'])
            info = runtime.parse_chunk(second['chunk'])['INFO']
            self.assertNotEqual(first['id'], second['id'])
            self.assertEqual(runtime.info_values(info, 'ID'), [second['id']])
            self.assertEqual(runtime.info_values(info, 'parent'), [first['id']])

    def test_legacy_uuid_records_can_be_read_and_parent_new_versions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old_id = 'a'*32
            item = {'schema_version': 1, 'id': old_id, 'title': 'Old song',
                    'created_at': '2026-01-01T00:00:00+00:00', 'parent': None,
                    'chunk': chunk(title='Old song'), 'state': {'music_mode': 'strict'}}
            folder = root/'personal'/'tracks'
            folder.mkdir(parents=True)
            path = folder/(old_id+'.json')
            path.write_text(json.dumps(item, ensure_ascii=False), encoding='utf-8')
            original = path.read_bytes()
            self.assertEqual(runtime.get_track(root, old_id), item)
            new = runtime.archive_chunk(root, item['chunk'], parent=old_id)
            self.assertRegex(new['id'], r'^[a-z]{6}_\d{8}T\d{12}Z$')
            self.assertEqual(new['state']['music_mode'], 'strict')
            self.assertEqual(path.read_bytes(), original)

    def test_optional_id_rejects_duplicate_invalid_or_mismatching_metadata(self):
        good_id = 'abcdef_20261003T123456123456Z'
        for suffix in ['; ID: ../escape', '; ID: '+good_id+'; ID: '+good_id,
                       '; ID: '+good_id+'; version: '+'b'*32]:
            with self.subTest(suffix=suffix):
                self.assertTrue(runtime.validate_chunk(chunk()+suffix)['errors'])
        self.assertFalse(runtime.validate_chunk(chunk()+'; ID: '+good_id)['errors'])
        self.assertFalse(runtime.validate_chunk(chunk())['errors'])

    def test_new_id_path_traversal_and_invalid_timestamp_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            for bad in ['abcdef_20269999T123456123456Z', '../abcdef_20261003T123456123456Z', 'ABCDEF_20261003T123456123456Z']:
                with self.subTest(bad=bad), self.assertRaises(ValueError):
                    runtime.get_track(Path(tmp), bad)


if __name__ == '__main__':
    unittest.main()
