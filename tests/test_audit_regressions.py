"""Observable regressions: no lyric loss, safe revisions and portable checks."""
import contextlib
import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_chunk import ROOT, chunk, runtime


class AuditRegressions(unittest.TestCase):
    def test_section_quotes_keep_all_words_in_both_views(self):
        source = chunk('[Verse]\n[Male Vocal]\nKeep this line\n[Chorus: "Do not lose me"]')
        for plain in (False, True):
            viewed = runtime.lyrics_view(source, plain=plain)
            self.assertIn('Keep this line', viewed)
            self.assertIn('Do not lose me', viewed)

    def test_combined_section_keeps_voice_delivery_not_instrument(self):
        viewed = runtime.lyrics_view(chunk('[Verse: female vocals, whispering, sparse piano]\nНаш ответ'))
        self.assertIn('[Verse]', viewed)
        self.assertIn('Female Vocal', viewed)
        self.assertIn('whispering', viewed)
        self.assertNotIn('piano', viewed)

    def test_library_sections_and_delivery_survive_view(self):
        viewed = runtime.lyrics_view(chunk('[Verse - whispered]\n[Male Vocal]\nFirst line\n[Guitar Solo]\n[Chorus]\n[Male Vocal]\n[Belted]\nSecond line'))
        for value in ('[Verse]', 'whispered', '[Guitar Solo]', '[Belted]'):
            self.assertIn(value, viewed)

    def test_inline_voice_switch_retains_event_order(self):
        viewed = runtime.lyrics_view(chunk('[Verse]\n[Male Vocal]\nFirst phrase [Female Vocal] second phrase'))
        self.assertLess(viewed.index('First phrase'), viewed.index('[Female Vocal]'))
        self.assertLess(viewed.index('[Female Vocal]'), viewed.index('second phrase'))

    def test_unknown_cue_requires_review_instead_of_silent_loss(self):
        with self.assertRaises(ValueError):
            runtime.lyrics_view(chunk('[Verse]\n[Unknown Delivery]\nKeep these words'))

    def test_mixed_voice_instrument_clause_requires_review(self):
        with self.assertRaises(ValueError):
            runtime.lyrics_view(chunk('[Verse: female vocals whispering over sparse piano]\nKeep these words'))

    def test_quoted_instrument_content_is_not_silently_removed(self):
        with self.assertRaises(ValueError):
            runtime.lyrics_view(chunk('[Verse]\nKeep these words\n[Synth: "possible vocal sample"]'))

    def test_wordless_events_separate_assigned_voices(self):
        lyrics = '[Intro]\n[Male Vocal]\n[Humming: soft motif]\n[Female Vocal]\n[Vocal Chops: response]'
        self.assertEqual(runtime.vocal_assignment_errors(lyrics, 'Male and female wordless vocals'), [])

    def test_delivery_cue_does_not_replace_missing_performance(self):
        lyrics = '[Verse]\n[Male Vocal]\n[Whisper]\n[Female Vocal]\nWords belong here'
        self.assertTrue(runtime.vocal_assignment_errors(lyrics, 'Male and female vocals'))

    def test_combined_source_wordless_cue_completes_performance(self):
        lyrics = '[Intro]\n[Male Vocal Chops: wordless motif]\n[Female Vocal]\n[Humming: response]'
        self.assertEqual(runtime.vocal_assignment_errors(lyrics, 'Male and female wordless voices'), [])

    def test_supported_solo_resets_voice_owner(self):
        lyrics = '[Verse]\n[Male Vocal]\nFirst line\n[Guitar Solo]\nSecond line'
        self.assertTrue(runtime.vocal_assignment_errors(lyrics, 'Male and female vocals'))

    def test_nonverbal_event_in_duet_requires_source(self):
        self.assertTrue(runtime.vocal_assignment_errors('[Intro]\n[Humming: soft motif]', 'Male and female voices'))

    def test_metadata_is_read_only_from_info(self):
        for model in ('v6-wild', 'v6-mini'):
            self.assertFalse(runtime.validate_chunk(chunk('[Intro]\n[Instrumental: motif; model: '+model+']'))['errors'])

    def test_indented_info_marker_still_selects_metadata(self):
        text = chunk('[Intro]\n[Instrumental: motif; model: v6-mini]').replace('summary: fixture; ', '').replace('INFO:->', '  INFO:->')
        self.assertFalse(runtime.validate_chunk(text)['errors'])

    def test_empty_exclude_items_rejected(self):
        for value in (', ,', '---', 'ambient, , trap', 'none, trap'):
            self.assertTrue(runtime.validate_chunk(chunk().replace('Exclude: ambient', 'Exclude: '+value))['errors'])

    def test_revision_inherits_state_and_enforces_word_bans(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = {'banned_words': ['spark'], 'music_mode': 'strict', 'locks': ['STYLES']}
            parent = runtime.archive_chunk(root, chunk(), state=state)
            child = runtime.archive_chunk(root, chunk('[Verse]\nNew subject'), parent=parent['id'])
            self.assertEqual(child['state'], state)
            with self.assertRaises(ValueError):
                runtime.archive_chunk(root, chunk('[Verse]\nspark'), parent=parent['id'])
            self.assertEqual(runtime.get_track(root, parent['id'])['state'], state)

    def test_field_lock_and_explicit_unlock(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            parent = runtime.archive_chunk(root, chunk(), state={'locks': ['STYLES'], 'music_mode': 'strict'})
            changed = chunk(styles='Different style')
            with self.assertRaises(ValueError):
                runtime.archive_chunk(root, changed, parent=parent['id'])
            child = runtime.archive_chunk(root, changed, parent=parent['id'], state={'locks': []})
            self.assertEqual(child['state'], {'locks': [], 'music_mode': 'strict'})

    def test_bad_record_does_not_hide_usable_versions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            good = runtime.archive_chunk(root, chunk())
            (root/'personal/tracks/bad.json').write_text('{}', encoding='utf-8')
            with contextlib.redirect_stderr(io.StringIO()) as notices:
                rows = runtime.list_tracks(root)
            self.assertEqual([row['id'] for row in rows], [good['id']])
            self.assertIn('invalid archive record', notices.getvalue())

    def test_get_incomplete_record_reports_value_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root/'personal/tracks'; folder.mkdir(parents=True)
            version_id = 'a'*32
            (folder/(version_id+'.json')).write_text('{}', encoding='utf-8')
            with self.assertRaises(ValueError):
                runtime.get_track(root, version_id)

    def test_clean_shared_package_verifies_without_author_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)/'vsuno-composer'
            shutil.copytree(ROOT, package, ignore=shutil.ignore_patterns('personal', 'prompts', 'work', '__pycache__', '.git'))
            spec = importlib.util.spec_from_file_location('portable_verifier', package/'scripts/verify_files.py')
            verifier = importlib.util.module_from_spec(spec); spec.loader.exec_module(verifier)
            report = verifier.verify()
            self.assertTrue(report['ok'], report['errors'])
            self.assertFalse((package/'work').exists())

    def test_portable_verifier_cli_does_not_rewrite_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)/'vsuno-composer'
            shutil.copytree(ROOT, package, ignore=shutil.ignore_patterns('personal', 'prompts', 'work', '__pycache__', '.git'))
            before = {str(p.relative_to(package)):p.read_bytes() for p in package.rglob('*') if p.is_file()}
            result = subprocess.run([sys.executable, '-X', 'utf8', '-B', str(package/'scripts/verify_files.py')], capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr.decode('utf-8'))
            self.assertTrue(json.loads(result.stdout.decode('utf-8'))['ok'])
            after = {str(p.relative_to(package)):p.read_bytes() for p in package.rglob('*') if p.is_file()}
            self.assertEqual(before, after)

    def test_multiline_styles_retains_parser_field_and_counts(self):
        styles = 'Style: acid house, 124 BPM\nVocals: no vocals\nThemes: A minor, resonant motif\nInstruments: sub bass, dry drums\nMood: restrained tension'
        text = chunk(styles=styles)
        self.assertEqual(runtime.parse_chunk(text)['STYLES'], styles)
        self.assertEqual(runtime.validate_chunk(text)['counts']['STYLES'], runtime.utf16_length(styles))


if __name__ == '__main__':
    unittest.main()
