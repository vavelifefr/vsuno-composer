"""Personal text exports contain exactly the final parser chunk."""
import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_chunk import chunk, runtime

ROOT = Path(__file__).resolve().parents[1]


class PromptExportTests(unittest.TestCase):
    def test_archive_exports_final_chunk_utf8_with_title_and_timestamp(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            item = runtime.archive_chunk(root, chunk(title='Тёплый ветер'))
            files = list((root/'prompts').glob('*.txt'))
            self.assertEqual(len(files), 1)
            self.assertEqual(files[0].name, 'Тёплый ветер_'+item['id']+'.txt')
            self.assertEqual(files[0].read_bytes(), item['chunk'].encode('utf-8'))
            self.assertFalse(runtime.validate_chunk(files[0].read_text(encoding='utf-8'))['errors'])

    def test_revisions_never_overwrite_export_even_with_same_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = runtime.archive_chunk(root, chunk())
            fixed_time = runtime.datetime.fromisoformat(first['created_at'])
            with patch.object(runtime, 'datetime', wraps=runtime.datetime) as clock:
                clock.now.return_value = fixed_time
                second = runtime.archive_chunk(root, chunk(), parent=first['id'])
            files = list((root/'prompts').glob('*.txt'))
            self.assertEqual(len(files), 2)
            self.assertEqual({p.read_text(encoding='utf-8') for p in files}, {first['chunk'], second['chunk']})

    def test_windows_unsafe_titles_stay_inside_prompts(self):
        for title in ['../Песня: <ветер>?*|', 'CON', 'LPT1.txt', 'a'*400]:
            with self.subTest(title=title), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                item = runtime.archive_chunk(root, chunk(title=title))
                files = list((root/'prompts').glob('*.txt'))
                self.assertEqual(len(files), 1)
                self.assertEqual(item['title'], title)
                self.assertNotRegex(files[0].name, r'[<>:"/\\|?*\x00-\x1f]')
                self.assertLess(len(files[0].name), 200)
                self.assertNotRegex(files[0].name.upper(), r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|_)')

    def test_verifier_does_not_read_personal_prompt_files(self):
        spec = importlib.util.spec_from_file_location('export_verifier', ROOT/'scripts/verify_files.py')
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        original = Path.read_bytes
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/'vsuno-composer'
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns('personal', 'prompts', 'work', '__pycache__', '.git'))
            (root/'prompts').mkdir()
            (root/'prompts'/'private.json').write_bytes(b'\xff')
            def guarded_read(path):
                if 'prompts' in path.relative_to(root).parts:
                    raise AssertionError('Private prompt contents must not be read')
                return original(path)
            with patch.object(verifier, 'ROOT', root), patch.object(Path, 'read_bytes', guarded_read):
                self.assertTrue(verifier.verify()['ok'])


if __name__ == '__main__':
    unittest.main()
