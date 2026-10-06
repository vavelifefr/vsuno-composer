"""Checks of observable chunk compatibility, caps and private revision storage."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('vsuno_runtime', ROOT / 'scripts' / 'vsuno.py')
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)

def chunk(lyrics='[Intro]\n[Instrumental]', styles='Acid house, 124 BPM, resonant TB-303 bass', title='Test composition'):
    return ('TRACK:->\n\n' + title + '\n\nLYRICS:->\n\n' + lyrics +
            '\n\nSTYLES:->\n\n' + styles + '\n\nMOREOPTIONS:->\n\n' +
            'Vocal Gender: none | Duration: Auto | Max Mode: Off | Weirdness: 40% | Style Influence: 80% | Variety: Off | Personalize: Off\n' +
            'Exclude: ambient\n\nINFO:->\n\nsummary: fixture; model: v6-mini; lang: none; gen_model: unknown; gen_time: ?')

class ChunkTests(unittest.TestCase):
    def test_short_instrumental_valid_no_minimum(self):
        self.assertEqual(runtime.validate_chunk(chunk())['errors'], [])

    def test_caps_inclusive(self):
        self.assertFalse(runtime.validate_chunk(chunk('a'*5000, 'b'*1000))['errors'])
        self.assertTrue(runtime.validate_chunk(chunk('a'*5001))['errors'])
        self.assertTrue(runtime.validate_chunk(chunk(styles='b'*1001))['errors'])

    def test_utf16_matches_browser_length(self):
        result = runtime.validate_chunk(chunk('😀'*2501))
        self.assertEqual(result['counts']['LYRICS'], 5002)
        self.assertTrue(result['errors'])

    def test_fences_and_crlf_supported(self):
        self.assertFalse(runtime.validate_chunk('```text\r\n'+chunk().replace('\n','\r\n')+'\r\n```')['errors'])

    def test_missing_duplicate_reordered_or_unknown_markers_rejected(self):
        for bad in [chunk().replace('INFO:->', 'STATE:->'), chunk()+'\nTRACK:->\n\nOther',
                    chunk().replace('LYRICS:->','TEMP:->'), chunk().replace('TRACK:->','STYLES:->',1)]:
            with self.subTest(bad=bad[-60:]): self.assertTrue(runtime.validate_chunk(bad)['errors'])

    def test_field_blank_lines_required_and_multiline_info_allowed(self):
        self.assertTrue(runtime.validate_chunk(chunk().replace('LYRICS:->\n\n','LYRICS:->\n'))['errors'])
        self.assertFalse(runtime.validate_chunk(chunk()+'\nextra: text')['errors'])

    def test_options_are_complete_and_valid(self):
        for bad in [chunk().replace('40%','101%'),chunk().replace('Variety: Off','Variety: Unusual'),
                    chunk().replace('Exclude: ambient',''),chunk().replace('model: v6-mini','model: v7'),
                    chunk().replace('Personalize: Off','Personalize: On')]:
            self.assertTrue(runtime.validate_chunk(bad)['errors'])

    def test_exclude_must_be_nonempty_and_not_none(self):
        for value in ['', 'none']:
            self.assertTrue(runtime.validate_chunk(chunk().replace('Exclude: ambient','Exclude: '+value))['errors'])

    def test_duet_needs_owner_in_every_vocal_section(self):
        styles = 'Male rap verses, female melodic chorus, shared final duet'
        self.assertTrue(runtime.validate_chunk(chunk('[Verse]\nA line\n[Chorus]\nAnother line',styles))['errors'])
        self.assertFalse(runtime.validate_chunk(chunk('[Verse]\n[Male Vocal]\nA line\n[Chorus]\n[Female Vocal]\nAnother line\n[Chorus]\n[Duet]\nBoth sing',styles))['errors'])

    def test_section_change_does_not_inherit_singer_in_duet(self):
        text = '[Verse]\n[Male Vocal]\nA line\n[Chorus]\nUnassigned line\n[Bridge]\n[Female Vocal]\nReply'
        self.assertTrue(runtime.validate_chunk(chunk(text,'Male and female duet'))['errors'])

    def test_line_switches_allowed_but_stacked_solo_tags_ambiguous(self):
        good = '[Verse]\n[Male Vocal]\nFirst line\n[Female Vocal]\nReply line'
        bad = '[Verse]\n[Male Vocal]\n[Female Vocal]\nWho sings this line?'
        self.assertFalse(runtime.validate_chunk(chunk(good,'Male and female duet'))['errors'])
        self.assertTrue(runtime.validate_chunk(chunk(bad,'Male and female duet'))['errors'])

    def test_instrumental_interlude_not_assigned_to_singer(self):
        text = '[Intro]\n[Instrumental]\n[Drums: steady pulse]\n[Verse]\n[Male Vocal]\nFirst line\n[Interlude]\n[Synth: rising motif]\n[Chorus]\n[Female Vocal]\nReply line'
        self.assertFalse(runtime.validate_chunk(chunk(text,'Male and female duet'))['errors'])

    def test_lyrics_view_default_keeps_sections_and_vocal_features(self):
        text = '[Intro]\n[Instrumental]\n[Synth: short motif]\n[Verse 1]\n[Male Vocal: rapid recitative]\nПервая строка\nВторая строка\n[Chorus]\n[Female Vocal: whispering]\nОтветная строка'
        result = runtime.lyrics_view(chunk(text,'Male rap verses, female whispered chorus'))
        self.assertTrue(result.startswith('```text\n'))
        self.assertIn('[Verse 1]\n[Male Vocal: rapid recitative]\nПервая строка\nВторая строка',result)
        self.assertIn('[Female Vocal: whispering]',result)
        self.assertNotIn('[Synth:',result)
        self.assertNotIn('LYRICS:->',result)

    def test_plain_lyrics_view_only_on_explicit_request(self):
        text = '[Verse]\n[Male Vocal]\nПервая строка\n[Chorus]\n[Female Vocal]\nОтвет'
        result = runtime.lyrics_view(chunk(text,'Male and female duet'),plain=True)
        self.assertNotIn('[Verse]',result)
        self.assertIn('Первая строка',result)
        self.assertIn('Ответ',result)

    def test_lyrics_view_does_not_drop_legacy_quoted_hook(self):
        result = runtime.lyrics_view(chunk('[Chorus]\n[Female Vocal Hook: "Наш ответ"]','Female melodic lead'))
        self.assertIn('Наш ответ',result)
        self.assertNotIn('Hook: "',result)

    def test_lyrics_view_quoted_hook_retains_delivery_and_section_hook_words(self):
        result = runtime.lyrics_view(chunk('[Chorus]\n[Female Vocal Hook: "Наш ответ", whispering]','Female lead'))
        self.assertIn('whispering',result)
        self.assertIn('Наш ответ',result)
        self.assertIn('Наш ответ',runtime.lyrics_view(chunk('[Hook: "Наш ответ"]')))

    def test_text_cli_preserves_utf8_and_returns_single_copyable_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'песня.txt'
            path.write_text(chunk('[Verse]\n[Female Vocal: whispering]\nЯ вернусь домой'),encoding='utf-8')
            result = subprocess.run([sys.executable,str(ROOT/'scripts'/'vsuno.py'),'text',str(path)],capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr.decode('utf-8'))
            self.assertEqual(runtime.normalize(result.stdout.decode('utf-8')).strip(),'```text\n[Verse]\n[Female Vocal: whispering]\nЯ вернусь домой\n```')

    def test_lyrics_view_instrumental_has_no_song_words(self):
        with self.assertRaises(ValueError):
            runtime.lyrics_view(chunk())

    def test_lyrics_view_ambiguous_quoted_words_are_not_silently_lost(self):
        with self.assertRaises(ValueError):
            runtime.lyrics_view(chunk('[Chorus]\n[Special: "Наш ответ"]'))

    def test_lyrics_view_instrument_hook_is_not_a_vocal_cue(self):
        result = runtime.lyrics_view(chunk('[Verse]\n[Male Vocal]\nNew words\n[Lead Hook: plucked synth]','Male lead'))
        self.assertNotIn('[Lead Hook:',result)

    def test_lyrics_view_keeps_vocal_insertions_with_song_words(self):
        cues = ['Ad-libs: brief response', 'Vocal Chops: short rhythmic answer',
                'Spoken Word: quiet delivery', 'Gang Vocals: rough group refrain',
                'Breaths: short inhale', 'Sighs: restrained exhale',
                'Laughs: brief soft laugh', 'Cries: restrained sob',
                'Clicks: tongue percussion', 'Unison Chants: short group accent']
        source = '[Verse]\n[Male Vocal]\nНовые слова\n' + '\n'.join('['+cue+']' for cue in cues)
        viewed = runtime.lyrics_view(chunk(source,'Male lead'))
        for cue in cues:
            with self.subTest(cue=cue): self.assertIn('['+cue+']',viewed)
        plain = runtime.lyrics_view(chunk(source,'Male lead'),plain=True)
        self.assertIn('Новые слова',plain)
        self.assertNotIn('[',plain)

    def test_legacy_quoted_adlib_words_are_preserved(self):
        viewed = runtime.lyrics_view(chunk('[Verse]\n[Male Vocal]\nНовые слова\n[Ad-libs: "Вернусь", whispered]'))
        self.assertIn('Вернусь',viewed)
        self.assertIn('whispered',viewed)

    def test_model_not_confused_with_generation_model(self):
        self.assertTrue(runtime.validate_chunk(chunk().replace('model: v6-mini;','gen_model: v6-mini;',1))['errors'])
        self.assertTrue(runtime.validate_chunk(chunk()+'; model: v6')['errors'])

    def test_model_first_in_info_is_valid_metadata(self):
        self.assertFalse(runtime.validate_chunk(chunk().replace('summary: fixture; ',''))['errors'])

    def test_identity_lists_are_not_strings(self):
        self.assertTrue(runtime.validate_chunk(chunk(), forbidden='some text')['errors'])

    def test_declared_counts_must_match(self):
        self.assertTrue(runtime.validate_chunk(chunk()+'; lyrics_chars: 1')['errors'])

    def test_launcher_passes_brief_as_data(self):
        with patch.object(runtime.shutil, 'which', return_value='codex.exe'):
            text = 'Тема "дом" & $HOME; не команда'
            command = runtime.start_command(text)
            self.assertEqual(command[-1].split('User request:\n')[1], text)
            self.assertEqual(command[1:3], ['--search','--cd'])

    def test_archived_utf8_cyrillic_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            title = 'Возвращение домой'
            item = runtime.archive_chunk(Path(tmp), chunk('[Verse]\nЭто новый текст', title=title))
            self.assertEqual(runtime.get_track(Path(tmp), item['id'])['title'], title)
            path = Path(tmp) / 'personal' / 'tracks' / (item['id']+'.json')
            self.assertIn(title, path.read_bytes().decode('utf-8'))
            self.assertFalse(path.read_bytes().startswith(b'\xef\xbb\xbf'))

    def test_cli_reads_utf8_bom_and_returns_correct_failure_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'входной чанк.txt'
            path.write_bytes(('\ufeff'+chunk('[Verse]\nРусский текст').replace('\n','\r\n')).encode('utf-8'))
            result = subprocess.run([sys.executable,str(ROOT/'scripts'/'vsuno.py'),'check',str(path)],capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr.decode('utf-8'))
            self.assertTrue(json.loads(result.stdout.decode('utf-8'))['ok'])
            path.write_text(chunk('a'*5001),encoding='utf-8')
            failed = subprocess.run([sys.executable,str(ROOT/'scripts'/'vsuno.py'),'check',str(path)],capture_output=True)
            self.assertEqual(failed.returncode,1)

    def test_cli_rejects_ansi_instead_of_guessing(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'input.txt'
            path.write_bytes(chunk('[Verse]\nРусский текст').encode('cp1251'))
            result = subprocess.run([sys.executable,str(ROOT/'scripts'/'vsuno.py'),'check',str(path)],capture_output=True)
            self.assertEqual(result.returncode,2)
            self.assertIn('utf-8',result.stderr.decode('utf-8'))

    def test_reference_identity_checked_including_info(self):
        for suffix in ['', '; source: Fixture Performer']:
            text = chunk(title='Fixture Performer' if not suffix else 'Test composition')+suffix
            self.assertTrue(runtime.validate_chunk(text, forbidden=['fixture performer'])['errors'])
        self.assertFalse(runtime.validate_chunk(chunk(styles='Roland TR-909 drums'), forbidden=['Fixture Performer'])['errors'])

    def test_requested_word_exclusions_boundaries(self):
        self.assertTrue(runtime.validate_chunk(chunk('Запретное слово'), banned_words=['слово'])['errors'])
        self.assertFalse(runtime.validate_chunk(chunk('Словообразование'), banned_words=['слово'])['errors'])

    def test_archive_parent_and_revisions_are_immutable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            a = runtime.archive_chunk(root, chunk(), state={'music_mode':'strict'})
            b = runtime.archive_chunk(root, chunk(lyrics='[Verse]\nNew subject'), parent=a['id'])
            saved_a = runtime.get_track(root, a['id'])['chunk']
            for key in ['TRACK','LYRICS','STYLES','MOREOPTIONS']:
                self.assertEqual(runtime.parse_chunk(saved_a)[key], runtime.parse_chunk(chunk())[key])
            self.assertEqual(runtime.get_track(root, a['id'])['chunk'], saved_a)
            self.assertEqual(runtime.get_track(root, b['id'])['parent'], a['id'])
            self.assertEqual(len(runtime.list_tracks(root, 'Test composition')), 2)
            with self.assertRaises(ValueError): runtime.get_track(root, 'Test composition')
            with self.assertRaises(ValueError): runtime.archive_chunk(root, chunk(), parent='../missing')

    def test_archive_id_matches_emitted_info(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = runtime.archive_chunk(Path(tmp), chunk())
            second = runtime.archive_chunk(Path(tmp), chunk(), parent=first['id'])
            info = runtime.parse_chunk(second['chunk'])['INFO']
            self.assertEqual(runtime.info_values(info, 'version'), [])
            self.assertEqual(runtime.info_values(info, 'parent'), [first['id']])
            self.assertEqual(runtime.info_values(info, 'storage'), ['saved'])

    def test_archive_rejects_invalid_and_path_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): runtime.archive_chunk(Path(tmp), chunk('a'*5001))
            with self.assertRaises(ValueError): runtime.get_track(Path(tmp), '../../outside')

if __name__ == '__main__': unittest.main()
