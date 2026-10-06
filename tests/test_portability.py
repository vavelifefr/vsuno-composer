"""Archive integrity and honest operation across resource/storage capabilities."""
import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_chunk import ROOT, chunk, runtime


class PortabilityTests(unittest.TestCase):
    def write_record(self, root, item):
        path = root / 'personal' / 'tracks' / (item['id'] + '.json')
        path.write_text(json.dumps(item, ensure_ascii=False), encoding='utf-8', newline='\n')
        return path

    def run_cli(self, skill_root, args):
        out, err = io.StringIO(), io.StringIO()
        with patch.object(runtime, 'ROOT', skill_root), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = runtime.main(args)
        return code, out.getvalue(), err.getvalue()

    def test_selected_record_rejects_embedded_other_id_without_rewriting(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            item = runtime.archive_chunk(root, chunk())
            item['chunk'] = item['chunk'].replace(item['id'], 'abcdef_20261005T123456123456Z')
            path = self.write_record(root, item)
            before = path.read_bytes()
            with self.assertRaises(ValueError):
                runtime.get_track(root, item['id'])
            self.assertEqual(path.read_bytes(), before)

    def test_selected_record_rejects_non_chunk_and_over_limit_payload(self):
        for damaged in ('not a chunk', chunk(lyrics='a' * 5001)):
            with self.subTest(damaged=damaged[:20]), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                item = runtime.archive_chunk(root, chunk())
                item['chunk'] = damaged
                self.write_record(root, item)
                with self.assertRaises(ValueError):
                    runtime.get_track(root, item['id'])

    def test_record_title_and_parent_must_match_present_chunk_metadata(self):
        for key, value in [('title', 'Another title'), ('parent', 'a' * 32)]:
            with self.subTest(key=key), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                item = runtime.archive_chunk(root, chunk())
                item[key] = value
                self.write_record(root, item)
                with self.assertRaises(ValueError):
                    runtime.get_track(root, item['id'])

    def test_new_record_requires_identity_but_legacy_version_only_stays_readable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            modern = runtime.archive_chunk(root, chunk())
            modern['chunk'] = chunk()
            self.write_record(root, modern)
            with self.assertRaises(ValueError):
                runtime.get_track(root, modern['id'])
            legacy = {'id': 'a' * 32, 'title': 'Test composition', 'created_at': '2026-01-01T00:00:00Z',
                      'chunk': chunk() + '; version: ' + 'a' * 32, 'state': {}, 'parent': None}
            path = self.write_record(root, legacy)
            before = path.read_bytes()
            self.assertEqual(runtime.get_track(root, legacy['id']), legacy)
            self.assertEqual(path.read_bytes(), before)

    def test_listing_reports_corrupt_record_but_retains_valid_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            good = runtime.archive_chunk(root, chunk(title='Selected work'))
            bad = runtime.archive_chunk(root, chunk(title='PRIVATE_RECORD_TITLE'))
            bad['chunk'] = 'not a chunk'
            self.write_record(root, bad)
            with contextlib.redirect_stderr(io.StringIO()) as err:
                rows = runtime.list_tracks(root)
            self.assertEqual([row['id'] for row in rows], [good['id']])
            self.assertIn(bad['id'], err.getvalue())
            self.assertNotIn('PRIVATE_RECORD_TITLE', err.getvalue())

    def test_explicit_data_root_roundtrip_never_writes_skill_resources(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            skill_root, data_root = workspace / 'installed', workspace / 'data'
            skill_root.mkdir()
            source = workspace / 'input.txt'
            source.write_text(chunk(title='Separate storage'), encoding='utf-8')
            code, out, err = self.run_cli(skill_root, ['archive', str(source), '--data-root', str(data_root)])
            self.assertEqual(code, 0, err)
            identity = json.loads(out)['id']
            self.assertEqual(list(skill_root.iterdir()), [])
            self.assertEqual(len(list((data_root / 'prompts').glob('*.txt'))), 1)
            code, out, err = self.run_cli(skill_root, ['get', identity, '--json', '--data-root', str(data_root)])
            self.assertEqual(code, 0, err)
            item = json.loads(out)
            self.assertEqual(item['id'], identity)
            code, out, err = self.run_cli(skill_root, ['list', '--query', 'Separate', '--data-root', str(data_root)])
            self.assertEqual(code, 0, err)
            self.assertEqual([row['id'] for row in json.loads(out)], [identity])

    def test_reading_missing_data_root_does_not_create_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            missing = root / 'absent'
            code, out, err = self.run_cli(root, ['list', '--data-root', str(missing)])
            self.assertEqual(code, 0, err)
            self.assertEqual(json.loads(out), [])
            self.assertFalse(missing.exists())

    def test_explicit_data_root_never_falls_back_to_resource_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            parent = runtime.archive_chunk(root, chunk())
            source = root / 'input.txt'
            source.write_text(parent['chunk'], encoding='utf-8')
            data_root = root / 'empty-data'
            code, _, _ = self.run_cli(root, ['archive', str(source), '--parent', parent['id'], '--data-root', str(data_root)])
            self.assertEqual(code, 2)
            self.assertFalse(data_root.exists())
            self.assertEqual(runtime.get_track(root, parent['id']), parent)

    def test_record_state_validation_does_not_echo_private_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            item = runtime.archive_chunk(root, chunk(lyrics='PRIVATE_SYNTHETIC_WORD'))
            item['state']['banned_words'] = ['PRIVATE_SYNTHETIC_WORD']
            self.write_record(root, item)
            with self.assertRaises(ValueError) as caught:
                runtime.get_track(root, item['id'])
            self.assertNotIn('PRIVATE_SYNTHETIC_WORD', str(caught.exception))

    def test_invalid_record_filename_does_not_leak_a_private_title(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            good = runtime.archive_chunk(root, chunk())
            path = root / 'personal' / 'tracks' / 'PRIVATE_SYNTHETIC_TITLE.json'
            path.write_text('{}', encoding='utf-8')
            with contextlib.redirect_stderr(io.StringIO()) as err:
                self.assertEqual([row['id'] for row in runtime.list_tracks(root)], [good['id']])
            self.assertIn('invalid archive record', err.getvalue())
            self.assertNotIn('PRIVATE_SYNTHETIC_TITLE', err.getvalue())

    def test_context_only_chunk_without_fake_id_or_counts_is_valid_and_explicit(self):
        source = chunk() + '; storage: context-only; identity: unavailable; counting: unavailable; context_ref: C1'
        checked = runtime.validate_chunk(source)
        self.assertEqual(checked['errors'], [])
        self.assertTrue(any('context-only' in item for item in checked['warnings']))
        for key in ('ID', 'version', 'lyrics_chars', 'styles_chars'):
            self.assertEqual(runtime.info_values(runtime.parse_chunk(source)['INFO'], key), [])

    def test_unavailable_metadata_cannot_claim_ids_or_counts(self):
        identity = 'abcdef_20261005T123456123456Z'
        for suffix in (
            '; identity: unavailable; ID: ' + identity,
            '; counting: unavailable; lyrics_chars: 22',
            '; identity: verified',
            '; counting: verified',
        ):
            with self.subTest(suffix=suffix):
                self.assertTrue(runtime.validate_chunk(chunk() + suffix)['errors'])

    def test_archiving_context_only_result_upgrades_metadata_without_changing_payload(self):
        source = chunk() + '; storage: context-only; identity: unavailable; counting: unavailable; context_ref: C1'
        with tempfile.TemporaryDirectory() as tmp:
            item = runtime.archive_chunk(Path(tmp), source)
            before, after = runtime.parse_chunk(source), runtime.parse_chunk(item['chunk'])
            for key in runtime.KEYS[:-1]:
                self.assertEqual(before[key], after[key])
            self.assertEqual(runtime.info_values(after['INFO'], 'identity'), ['verified'])
            self.assertEqual(runtime.info_values(after['INFO'], 'counting'), ['verified'])
            self.assertEqual(runtime.info_values(after['INFO'], 'storage'), ['saved'])
            self.assertEqual(runtime.info_values(after['INFO'], 'context_ref'), ['C1'])

    def test_native_manifest_name_matches_directory_and_rejects_mismatch(self):
        spec = importlib.util.spec_from_file_location('portability_verifier', ROOT / 'scripts' / 'verify_files.py')
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        entry = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
        self.assertEqual(verifier.metadata_errors(entry, ROOT.name), [])
        self.assertTrue(verifier.metadata_errors(entry, 'incorrect-skill-directory'))
        self.assertTrue(verifier.metadata_errors(entry.replace('name: vsuno-composer', 'name: wrong'), ROOT.name))


if __name__ == '__main__':
    unittest.main()
