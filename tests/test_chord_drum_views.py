"""Experimental music cues remain production data when viewing words."""
import unittest

from test_chunk import runtime, chunk


class ChordDrumViewTests(unittest.TestCase):
    def test_section_progression_is_removed_without_losing_voice_or_words(self):
        lyrics = '[Verse 1]\n[Chords: |Am|-|F|-|C|-|G|]\n[Male Vocal: calm singing]\nI kept your letter.\n[Chorus]\n[Female Vocal: soft singing]\nYou made it better.'
        source = chunk(lyrics)
        expected = '[Verse 1]\n\n[Male Vocal: calm singing]\nI kept your letter.\n\n[Chorus]\n[Female Vocal: soft singing]\nYou made it better.'
        self.assertEqual(runtime.unwrap(runtime.lyrics_view(source)), expected)
        self.assertEqual(runtime.parse_chunk(source)['LYRICS'], lyrics)

    def test_inline_chords_do_not_fragment_original_lyric_lines(self):
        source = chunk('[Verse]\n[Male Vocal: rapid recitative]\n[Am]I kept the note; [F]you kept the coat.\n[C]Stay[G] here.')
        self.assertEqual(runtime.unwrap(runtime.lyrics_view(source)), '[Verse]\n[Male Vocal: rapid recitative]\nI kept the note; you kept the coat.\nStay here.')
        self.assertEqual(runtime.unwrap(runtime.lyrics_view(source, plain=True)), 'I kept the note; you kept the coat.\nStay here.')

    def test_common_extensions_accidentals_and_slash_chords(self):
        source = chunk('[Verse]\n[Chord Progression: F#m7, Bbmaj7, C/G, E7]\n[F#m7]Still [Bbmaj7]here, [C/G]with [E7]you.')
        self.assertEqual(runtime.unwrap(runtime.lyrics_view(source)), '[Verse]\n\nStill here, with you.')

    def test_known_drum_descriptions_are_not_performed_words(self):
        source = chunk('[Intro]\n[Catchy drum machine intro]\n[Verse]\n[Male Vocal: calm singing]\nI kept the note.\n[80s gated snare fill]\n[Drop]\n[Four-on-the-floor beat drop]\n[Female Vocal: soft singing]\nYou kept the coat.\n[Bridge]\n[Drum machine bridge]\n[Funky drum break]\n[Verse 2]\n[Male Vocal: calm singing]\nWe chose a road.')
        view = runtime.unwrap(runtime.lyrics_view(source))
        for cue in ['Catchy drum machine intro', '80s gated snare fill', 'Four-on-the-floor beat drop', 'Drum machine bridge', 'Funky drum break']:
            self.assertNotIn(cue, view)
        for value in ['[Intro]', '[Bridge]', '[Verse 2]', '[Male Vocal: calm singing]', '[Female Vocal: soft singing]', 'I kept the note.', 'You kept the coat.', 'We chose a road.']:
            self.assertIn(value, view)

    def test_chord_like_unknown_or_quoted_cues_are_not_silently_dropped(self):
        for cue in ['[Ambience]', '[Chords: Am - Frog]', '[Chords: "words to sing"]', '[Coda: "Stay here"]']:
            with self.subTest(cue=cue), self.assertRaises(ValueError):
                runtime.lyrics_view(chunk('[Verse]\n'+cue+'\nKeep the words.'))

    def test_words_that_look_like_chord_names_and_backing_survive(self):
        source = chunk('[Verse]\nA major change; C is a letter.\n(Am) Keep the reply.\n[Ad-libs: "Stay"]')
        view = runtime.unwrap(runtime.lyrics_view(source, plain=True))
        self.assertEqual(view, 'A major change; C is a letter.\n(Am) Keep the reply.\nStay')


if __name__ == '__main__':
    unittest.main()
