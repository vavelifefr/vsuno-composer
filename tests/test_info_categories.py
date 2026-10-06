"""Readable INFO metadata, legacy imports and lossless private finalization."""
import tempfile
import unittest
from pathlib import Path

from test_chunk import chunk, runtime


def with_info(info, source=None):
    return (source or chunk()).split('INFO:->', 1)[0] + 'INFO:->\n\n' + info


def grouped_info():
    return ('COMPOSITION\n'
            'Composition summary (summary): A quiet pulse; space | contrast\n'
            'Lyric language (lang): none\n\n'
            'CREATIVE DIRECTION\n'
            'Musical freedom (music_mode): strict\n'
            'Lyric freedom (text_mode): na\n'
            'Prompt detail (detail): medium\n\n'
            'GENERATION AND VERIFICATION\n'
            'Suno generation model (model): v6-mini\n'
            'Writer model (gen_model): unknown\n'
            'Preparation time (gen_time): ?')


class InfoCategoryTests(unittest.TestCase):
    def test_readable_categories_and_labels_are_valid(self):
        self.assertEqual(runtime.validate_chunk(with_info(grouped_info()))['errors'], [])

    def test_values_preserve_punctuation_and_do_not_invent_metadata(self):
        info = grouped_info().replace('A quiet pulse; space | contrast', 'Describe model: freely; model: is prose | not a setting')
        self.assertEqual(runtime.info_values(info, 'model'), ['v6-mini'])
        self.assertEqual(runtime.info_values(info, 'summary'), ['Describe model: freely; model: is prose | not a setting'])

    def test_legacy_delimiters_and_new_simple_lines_remain_readable(self):
        for info in ('model: v6-mini; summary: legacy | lang: none',
                     'model: v6-mini\nsummary: imported\nlang: none'):
            self.assertEqual(runtime.validate_chunk(with_info(info))['errors'], [])
            self.assertEqual(runtime.info_values(info, 'model'), ['v6-mini'])

    def test_archive_groups_info_preserves_fields_state_and_utf8_export(self):
        source = with_info(grouped_info(), chunk(title='Quiet Return', lyrics='[Intro]\n[Instrumental: soft motif]'))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = {'music_mode': 'strict', 'locks': ['STYLES']}
            saved = runtime.archive_chunk(root, source, state=state)
            before, after = runtime.parse_chunk(source), runtime.parse_chunk(saved['chunk'])
            for key in runtime.KEYS[:-1]:
                self.assertEqual(after[key], before[key])
            self.assertEqual(saved['state'], state)
            for heading in ('VERSION AND STORAGE', 'COMPOSITION', 'CREATIVE DIRECTION', 'GENERATION AND VERIFICATION'):
                self.assertIn(heading, after['INFO'])
            for key, expected in [('ID', saved['id']), ('parent', 'none'), ('storage', 'saved')]:
                self.assertEqual(runtime.info_values(after['INFO'], key), [expected])
            self.assertEqual(runtime.info_values(after['INFO'], 'version'), [])
            self.assertEqual(runtime.info_values(after['INFO'], 'summary'), ['A quiet pulse; space | contrast'])
            for key, field in [('lyrics_chars', 'LYRICS'), ('styles_chars', 'STYLES')]:
                self.assertEqual(runtime.info_values(after['INFO'], key), [str(runtime.utf16_length(before[field]))])
            exported = root/'prompts'/('Quiet Return_'+saved['id']+'.txt')
            self.assertEqual(exported.read_bytes(), saved['chunk'].encode('utf-8'))
            self.assertEqual(runtime.get_track(root, saved['id']), saved)

    def test_repeated_archive_keeps_unknown_metadata_and_provenance(self):
        info = grouped_info() + '\n\nREVISION AND SOURCES\nTranslation mode (translation): singable\nLyrics donor (lyrics_source): opaque-source\nCustom accent (custom_accent): sparse; rhythmic | delayed\nKeep this note intact.'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            parent = runtime.archive_chunk(root, with_info(info))
            original = parent['chunk']
            child = runtime.archive_chunk(root, original, parent=parent['id'])
            tail = runtime.parse_chunk(child['chunk'])['INFO']
            self.assertEqual(runtime.info_values(tail, 'parent'), [parent['id']])
            self.assertEqual(runtime.info_values(tail, 'custom_accent'), ['sparse; rhythmic | delayed'])
            self.assertEqual(runtime.info_values(tail, 'translation'), ['singable'])
            self.assertEqual(runtime.info_values(tail, 'lyrics_source'), ['opaque-source'])
            self.assertEqual(tail.count('Keep this note intact.'), 1)
            self.assertEqual(runtime.get_track(root, parent['id'])['chunk'], original)

    def test_labeled_duplicates_and_bad_counts_are_rejected(self):
        version_id = 'abcdef_20261005T123456123456Z'
        suffixes = [
            '\nUnique version ID (ID): '+version_id+'\nUnique version ID (ID): '+version_id,
            '\nUnique version ID (ID): '+version_id+'\nVersion ID (version): '+'a'*32,
            '\nSuno generation model (model): v6',
            '\nLyrics length in UTF-16 units (lyrics_chars): 1',
            '\nStyles length in UTF-16 units (styles_chars): invalid',
        ]
        for suffix in suffixes:
            with self.subTest(suffix=suffix):
                self.assertTrue(runtime.validate_chunk(with_info(grouped_info()+suffix))['errors'])

    def test_private_identities_are_still_rejected_in_info(self):
        result = runtime.validate_chunk(with_info(grouped_info()+'\nAdditional note (notes): Private Reference'), forbidden=['Private Reference'])
        self.assertTrue(result['errors'])
        self.assertNotIn('Private Reference', str(result['errors']))


if __name__ == '__main__':
    unittest.main()
