"""English runtime messages preserve native user content and existing contracts."""
import unittest
from unittest.mock import patch

from test_chunk import runtime, chunk


class EnglishRuntimeTests(unittest.TestCase):
    def test_launcher_english_instructions_keep_user_brief_verbatim(self):
        brief = 'Русский запрос: строка\nEnglish words; $literal'
        with patch.object(runtime.shutil, 'which', return_value='C:/tools/codex.exe'):
            command = runtime.start_command(brief)
        self.assertEqual(command[1:4], ['--search', '--cd', str(runtime.ROOT)])
        instructions, supplied = command[-1].split('User request:\n', 1)
        self.assertEqual(supplied, brief)
        self.assertNotRegex(instructions, '[А-Яа-яЁё]')
        self.assertIn('$vsuno-composer', instructions)
        self.assertIn('references/FILES_spec.md', instructions)

    def test_validation_diagnostics_are_english_and_do_not_echo_private_values(self):
        result = runtime.validate_chunk(chunk('PrivateNeedle'), banned_words=['PrivateNeedle'])
        self.assertTrue(result['errors'])
        combined = ' '.join(result['errors'] + result['warnings'])
        self.assertNotRegex(combined, '[А-Яа-яЁё]')
        self.assertNotIn('PrivateNeedle', combined)

    def test_highlight_interface_english_with_native_words(self):
        # Interface language changes; native lyric bytes and escaping must survive.
        document = runtime.render_lyrics_highlight('[Verse]\n[Female Vocal]\nТихий <дом> & свет', 'Тихий дом')
        self.assertIn('Copy text', document)
        self.assertIn('Тихий &lt;дом&gt; &amp; свет', document)
        self.assertIn('Plain text', document)
        self.assertNotIn('Копировать текст', document)


if __name__ == '__main__':
    unittest.main()
