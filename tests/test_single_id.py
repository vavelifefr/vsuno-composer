"""One new INFO identity, parent continuity and immutable legacy reads."""
import json
import tempfile
import unittest
from pathlib import Path

from test_chunk import chunk, runtime
from test_info_categories import grouped_info, with_info


class SingleIdTests(unittest.TestCase):
    def test_verified_identity_requires_id_without_redundant_version(self):
        identity = 'abcdef_20261005T123456123456Z'
        source = with_info(grouped_info() + '\nUnique version ID (ID): ' + identity +
                           '\nArchive identity status (identity): verified')
        self.assertEqual(runtime.validate_chunk(source)['errors'], [])
        self.assertTrue(runtime.validate_chunk(source.replace(
            'Unique version ID (ID): ' + identity + '\n', ''))['errors'])

    def test_archive_emits_one_id_keeps_parent_and_payloads(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = runtime.archive_chunk(root, with_info(grouped_info()))
            # Old duplicate identity remains an accepted input for a new revision.
            source = '\n'.join(line for line in first['chunk'].splitlines()
                               if not line.startswith('Version ID (version):'))
            source += '\nVersion ID (version): ' + first['id']
            second = runtime.archive_chunk(root, source, parent=first['id'])
            before, after = runtime.parse_chunk(source), runtime.parse_chunk(second['chunk'])
            self.assertEqual(runtime.info_values(after['INFO'], 'ID'), [second['id']])
            self.assertEqual(runtime.info_values(after['INFO'], 'version'), [])
            self.assertEqual(runtime.info_values(after['INFO'], 'parent'), [first['id']])
            for key in runtime.KEYS[:-1]:
                self.assertEqual(after[key], before[key])
            self.assertEqual(runtime.get_track(root, second['id']), second)
            export = root / 'prompts' / (second['title'] + '_' + second['id'] + '.txt')
            self.assertEqual(export.read_bytes(), second['chunk'].encode('utf-8'))

    def test_new_record_with_id_only_roundtrips_without_rewriting(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            identity = 'abcdef_20261005T123456123456Z'
            item = {'schema_version': 1, 'id': identity, 'created_at': '2026-10-05T12:34:56Z',
                    'title': 'Test composition', 'parent': None, 'state': {},
                    'chunk': with_info(grouped_info() + '\nUnique version ID (ID): ' + identity +
                                       '\nParent version (parent): none')}
            folder = root / 'personal/tracks'
            folder.mkdir(parents=True)
            path = folder / (identity + '.json')
            path.write_text(json.dumps(item), encoding='utf-8')
            original = path.read_bytes()
            self.assertEqual(runtime.get_track(root, identity), item)
            self.assertEqual([row['id'] for row in runtime.list_tracks(root)], [identity])
            self.assertEqual(path.read_bytes(), original)

    def test_old_dual_id_record_remains_readable_and_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            saved = runtime.archive_chunk(root, chunk())
            # Construct the historical form regardless of the current writer.
            fields = runtime.parse_chunk(saved['chunk'])
            entries = [entry for entry in runtime.parse_info(fields['INFO']) if entry[0] != 'version']
            fields['INFO'] = runtime.format_info(entries + [('version', saved['id'], None)])
            saved['chunk'] = '\n\n'.join(key + ':->\n\n' + fields[key] for key in runtime.KEYS)
            path = root / 'personal/tracks' / (saved['id'] + '.json')
            path.write_text(json.dumps(saved), encoding='utf-8')
            original = path.read_bytes()
            self.assertEqual(runtime.get_track(root, saved['id']), saved)
            self.assertEqual(path.read_bytes(), original)
            saved['chunk'] = saved['chunk'].replace('Version ID (version): ' + saved['id'],
                                                  'Version ID (version): ' + 'a' * 32)
            path.write_text(json.dumps(saved), encoding='utf-8')
            with self.assertRaises(ValueError):
                runtime.get_track(root, saved['id'])


if __name__ == '__main__':
    unittest.main()
