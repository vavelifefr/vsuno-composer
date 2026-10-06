"""Portable handoffs preserve instructions and exclude personal data."""
import contextlib
import hashlib
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from test_chunk import runtime


class ConnectionExportTests(unittest.TestCase):
    def make_source(self, folder, starter=True):
        root = Path(folder)/'source'
        files = {
            'SKILL.md': '---\nname: vsuno-composer\ndescription: Compose music.\n---\nCompact core\n',
            'AGENTS.md': 'Protect the skill.\n',
            'USAGE_guide.md': 'Use the supplied files.\n',
            'README.md': 'Public project overview.\n',
            '.gitignore': '/personal/\n/prompts/\n/work/\n',
            'vsuno.cmd': '@echo off\n',
            'references/PARSER_spec.md': 'Five output fields.\n',
            'references/TEST_lib.md': 'PUBLIC_LIBRARY_TOKEN\n',
            'scripts/vsuno.py': 'print("public helper")\n',
            'agents/openai.yaml': 'interface:\n  display_name: "Vave Suno Composer"\n',
            'tools/suno-fill.user.js': '// public parser\n',
        }
        if starter:
            files['START_HERE_tpl.md'] = 'STARTER_TOKEN: apply SKILL.md and references on demand.\n'
        for name, text in files.items():
            path = root/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding='utf-8', newline='\n')
        # Invalid private data must never be decoded or copied.
        for name in ['personal/references/private.json', 'prompts/private.txt',
                     'work/private.md', 'scripts/__pycache__/private.py',
                     '.env', 'unrelated_private.md']:
            path = root/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'PRIVATE_TOKEN\xff')
        return root, files

    def run_cli(self, root, args):
        out, err = io.StringIO(), io.StringIO()
        with patch.object(runtime, 'ROOT', root), \
             patch.object(runtime, 'start_command', side_effect=AssertionError('Handoff must not start an LLM')), \
             contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = runtime.main(args)
            except SystemExit as exc:
                code = exc.code
        return code, out.getvalue(), err.getvalue()

    def test_starter_is_a_small_independent_handoff(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, files = self.make_source(tmp)
            code, out, err = self.run_cli(root, ['prompt', '--starter'])
            self.assertEqual(code, 0, err)
            self.assertEqual(out.rstrip('\n'), files['START_HERE_tpl.md'].rstrip('\n'))
            self.assertNotIn('PUBLIC_LIBRARY_TOKEN', out)

    def test_default_prompt_keeps_existing_entrypoint_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, files = self.make_source(tmp)
            code, out, err = self.run_cli(root, ['prompt'])
            self.assertEqual(code, 0, err)
            self.assertEqual(out.rstrip('\n'), files['SKILL.md'].rstrip('\n'))

    def test_full_handoff_has_starter_and_addressable_embedded_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, files = self.make_source(tmp)
            code, out, err = self.run_cli(root, ['prompt', '--full'])
            self.assertEqual(code, 0, err)
            self.assertTrue(out.startswith('--- FILE: START_HERE_tpl.md ---\n' + files['START_HERE_tpl.md']))
            self.assertIn('--- FILE: SKILL.md ---', out)
            self.assertIn('--- FILE: AGENTS.md ---', out)
            self.assertIn('--- FILE: USAGE_guide.md ---', out)
            self.assertIn('--- FILE: references/TEST_lib.md ---', out)
            self.assertIn('PUBLIC_LIBRARY_TOKEN', out)
            self.assertNotIn('PRIVATE_TOKEN', out)
            # Resolve embedded file addresses and recover their actual content.
            sections = {}
            for part in out.split('--- FILE: ')[1:]:
                name, body = part.split(' ---\n', 1)
                self.assertNotIn(name, sections)
                sections[name] = body.rstrip('\n')
            expected = {'START_HERE_tpl.md', 'SKILL.md', 'AGENTS.md', 'USAGE_guide.md'}
            expected.update(name for name in files if name.startswith('references/'))
            self.assertEqual(set(sections), expected)
            for name in expected:
                self.assertEqual(sections[name], files[name].rstrip('\n'))

    def test_starter_and_full_are_mutually_exclusive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, _ = self.make_source(tmp)
            code, _, _ = self.run_cli(root, ['prompt', '--full', '--starter'])
            self.assertEqual(code, 2)

    def test_starter_file_export_is_utf8_without_shell_recoding(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, files = self.make_source(tmp)
            starter = 'Применяй Vave Suno Composer.\nRead SKILL.md.\n'
            (root/'START_HERE_tpl.md').write_text(starter, encoding='utf-8', newline='\n')
            target = Path(tmp)/'export'/'START_CHATGPT.txt'
            code, out, err = self.run_cli(root, ['prompt', '--starter', '--output', str(target)])
            self.assertEqual(code, 0, err)
            self.assertTrue(json.loads(out)['saved'])
            self.assertEqual(target.read_bytes(), starter.encode('utf-8'))

    def test_instruction_export_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, _ = self.make_source(tmp)
            target = Path(tmp)/'instructions.txt'
            target.write_bytes(b'KEEP_EXISTING')
            code, out, err = self.run_cli(root, ['prompt', '--full', '--output', str(target)])
            self.assertEqual(code, 2)
            self.assertEqual(target.read_bytes(), b'KEEP_EXISTING')
            self.assertFalse(out)

    def test_bundle_contains_exact_public_files_without_reading_private_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, files = self.make_source(tmp)
            target = Path(tmp)/'handoff.zip'
            public = {root/name for name in files}
            original_read = Path.read_bytes
            def guarded_read(path):
                if path.is_relative_to(root) and path not in public:
                    raise AssertionError('Unexpected private file read: '+str(path))
                return original_read(path)
            before = {name: hashlib.sha256((root/name).read_bytes()).hexdigest() for name in files}
            with patch.object(Path, 'read_bytes', guarded_read):
                result = runtime.bundle_skill(root, target)
            self.assertFalse(result['installed'])
            self.assertTrue(result['saved'])
            self.assertEqual(result['files'], len(files))
            with zipfile.ZipFile(target) as archive:
                self.assertEqual(set(archive.namelist()), {'vsuno-composer/'+name for name in files})
                for name, content in files.items():
                    self.assertEqual(archive.read('vsuno-composer/'+name), content.encode('utf-8'))
            self.assertEqual(before, {name: hashlib.sha256((root/name).read_bytes()).hexdigest() for name in files})

    def test_bundle_cli_exports_without_starting_or_installing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, files = self.make_source(tmp)
            target = Path(tmp)/'handoff.zip'
            code, out, err = self.run_cli(root, ['bundle', '--output', str(target)])
            self.assertEqual(code, 0, err)
            result = json.loads(out)
            self.assertTrue(result['saved'])
            self.assertFalse(result['installed'])
            self.assertEqual(result['files'], len(files))
            self.assertTrue(target.is_file())

    def test_bundle_refuses_to_overwrite_existing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, _ = self.make_source(tmp)
            target = Path(tmp)/'handoff.zip'
            target.write_bytes(b'KEEP_EXISTING')
            with self.assertRaises((ValueError, FileExistsError)):
                runtime.bundle_skill(root, target)
            self.assertEqual(target.read_bytes(), b'KEEP_EXISTING')

    def test_missing_starter_does_not_create_incomplete_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, _ = self.make_source(tmp, starter=False)
            target = Path(tmp)/'handoff.zip'
            with self.assertRaises((ValueError, FileNotFoundError)):
                runtime.bundle_skill(root, target)
            self.assertFalse(target.exists())

    def test_invalid_utf8_public_reference_does_not_create_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, _ = self.make_source(tmp)
            (root/'references'/'BAD_lib.md').write_bytes(b'\xff')
            target = Path(tmp)/'handoff.zip'
            with self.assertRaises(UnicodeError):
                runtime.bundle_skill(root, target)
            self.assertFalse(target.exists())


if __name__ == '__main__':
    unittest.main()
