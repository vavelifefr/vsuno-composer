"""Library/display and voice-ownership regressions found in the release audit."""
import unittest

from test_chunk import chunk, runtime


class ReleaseRegressions(unittest.TestCase):
    def test_keys_cue_removed_without_losing_words_in_both_views(self):
        source = chunk('[Verse]\n[Keys: sustained chord]\n[Male Vocal: gentle]\nKeep a place for me.')
        for plain in (False, True):
            with self.subTest(plain=plain):
                result = runtime.lyrics_view(source, plain=plain)
                self.assertIn('Keep a place for me.', result)
                self.assertNotIn('sustained chord', result)
                self.assertEqual('[Male Vocal: gentle]' in result, not plain)

    def test_build_up_section_keeps_delivery_and_words(self):
        source = chunk('[Build-Up 2: male vocals, whispering]\nKeep a place for me.')
        result = runtime.lyrics_view(source)
        self.assertIn('[Build-Up 2]', result)
        self.assertIn('Male Vocal', result)
        self.assertIn('whispering', result)
        self.assertIn('Keep a place for me.', result)
        plain = runtime.lyrics_view(source, plain=True)
        self.assertIn('Keep a place for me.', plain)
        self.assertNotIn('[Build-Up', plain)

    def test_build_up_resets_owner_in_actual_duet(self):
        source = '[Verse]\n[Male Vocal]\nFirst phrase\n[Build-Up]\nUnassigned phrase'
        self.assertTrue(runtime.vocal_assignment_errors(source, 'Male and female vocals'))

    def test_negated_voice_does_not_turn_solo_into_duet(self):
        source = '[Verse]\nKeep a place for me.'
        for styles in ('Male lead vocals, no female vocals',
                       'Female lead vocals, without male vocals',
                       'Male lead vocals; exclude female backing vocals',
                       'Instrumental, no male or female vocals'):
            with self.subTest(styles=styles):
                self.assertEqual(runtime.vocal_assignment_errors(source, styles), [])

    def test_positive_roles_still_require_owners_despite_other_negation(self):
        source = '[Verse]\nKeep a place for me.'
        for styles in ('Male and female vocals',
                       'Not only male but also female vocals',
                       'Male lead, female response; no female choir'):
            with self.subTest(styles=styles):
                self.assertTrue(runtime.vocal_assignment_errors(source, styles))

    def test_lyric_roles_override_negated_style_description(self):
        source = '[Verse]\n[Male Vocal]\nFirst phrase\n[Female Vocal]\nSecond phrase\n[Chorus]\nUnassigned phrase'
        self.assertTrue(runtime.vocal_assignment_errors(source, 'Male vocals, no female vocals'))

    def test_quoted_keys_cue_still_requires_review(self):
        with self.assertRaises(ValueError):
            runtime.lyrics_view(chunk('[Verse]\n[Keys: "possible sample"]\nKeep a place for me.'))


if __name__ == '__main__':
    unittest.main()
