"""Highlighted reading keeps a distinct, exact plain-text copy source."""
import contextlib
import io
import json
import shutil
import subprocess
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch

from test_chunk import runtime, chunk


class PageReader(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.scripts = {}
        self.rows = []
        self.script = None
        self.row = None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'script':
            self.script = attrs.get('id', 'behavior')
            self.scripts[self.script] = ''
        if tag == 'div' and 'line' in attrs.get('class', '').split():
            self.row = [attrs['class'], '']

    def handle_data(self, data):
        if self.script is not None:
            self.scripts[self.script] += data
        if self.row is not None:
            self.row[1] += data

    def handle_endtag(self, tag):
        if tag == 'script':
            self.script = None
        if tag == 'div' and self.row is not None:
            self.rows.append(self.row)
            self.row = None


class HighlightTests(unittest.TestCase):
    def test_unicode_words_cues_blanks_and_punctuation_are_preserved(self):
        words = '[Verse 1]\n[Female Vocal: whispering]\n  Ты рядом — ёлки, дождь.\n\n[Chorus]\n(Mm) Don\'t change me & you. 😀'
        page = PageReader(runtime.render_lyrics_highlight(words, 'Тихий разговор'))
        self.assertEqual(json.loads(page.scripts['copy-source']), words)
        self.assertEqual('\n'.join(row[1] for row in page.rows), words)
        self.assertEqual(page.rows[0][0], 'line cue')
        self.assertEqual(page.rows[2][0], 'line words')
        self.assertEqual(page.rows[3][0], 'line gap')
        self.assertEqual(page.rows[-1][0], 'line words')

    def test_user_text_cannot_close_script_or_create_active_html(self):
        words = '[Verse]\n</script><img src=x onerror=alert(1)> & "hello"\n\u2028\u2029'
        html = runtime.render_lyrics_highlight(words, '<script>bad title</script>')
        page = PageReader(html)
        self.assertEqual(json.loads(page.scripts['copy-source']), words)
        self.assertEqual(len(page.scripts), 2)
        self.assertNotIn('<img', html)
        self.assertNotIn('<script>bad title', html)
        self.assertEqual('\n'.join(row[1] for row in page.rows), words)

    def run_cli(self, args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = runtime.main(args)
            except SystemExit as exc:
                code = exc.code
        return code, out.getvalue(), err.getvalue()

    def test_cli_exports_reading_view_without_rewriting_song_or_archiving(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root/'song.txt'
            data = chunk('[Verse]\n[Male Vocal: rapid recitative]\nI kept the key.\n[Lead: muted synth]\n[Chorus]\n[Female Vocal: soft singing]\nYou stayed with me.', title='Two replies')
            source.write_text(data, encoding='utf-8')
            target = root/'reading'/'song.html'
            before = source.read_bytes()
            with patch.object(runtime, 'archive_chunk', side_effect=AssertionError('Reading must not archive')):
                code, out, err = self.run_cli(['text', str(source), '--highlight', '--output', str(target)])
            self.assertEqual(code, 0, err)
            self.assertTrue(json.loads(out)['saved'])
            self.assertEqual(source.read_bytes(), before)
            copied = json.loads(PageReader(target.read_text(encoding='utf-8')).scripts['copy-source'])
            self.assertEqual(copied, runtime.unwrap(runtime.lyrics_view(data)))
            self.assertNotIn('[Lead:', copied)
            self.assertNotIn('TRACK:->', copied)
            self.assertFalse((root/'personal').exists())
            self.assertFalse((root/'prompts').exists())
            self.assertFalse(target.read_bytes().startswith(b'\xef\xbb\xbf'))

    def test_cli_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)/'song.txt'
            source.write_text(chunk('[Verse]\nKeep these words.'), encoding='utf-8')
            target = Path(tmp)/'song.html'
            target.write_bytes(b'KEEP_EXISTING')
            code, out, _ = self.run_cli(['text', str(source), '--highlight', '--output', str(target)])
            self.assertEqual(code, 2)
            self.assertFalse(out)
            self.assertEqual(target.read_bytes(), b'KEEP_EXISTING')

    def test_highlight_requires_html_output(self):
        code, _, err = self.run_cli(['text', 'missing.txt', '--highlight'])
        self.assertEqual(code, 2)
        self.assertIn('--output', err)

    def test_plain_and_highlight_are_mutually_exclusive(self):
        code, _, _ = self.run_cli(['text', 'missing.txt', '--plain', '--highlight'])
        self.assertEqual(code, 2)

    def test_plain_or_default_output_does_not_silently_become_html(self):
        code, _, _ = self.run_cli(['text', 'missing.txt', '--output', 'unrequested.html'])
        self.assertEqual(code, 2)

    def test_non_html_output_is_rejected_without_file_creation(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)/'song.txt'
            source.write_text(chunk('[Verse]\nKeep these words.'), encoding='utf-8')
            target = Path(tmp)/'song.txt.bak'
            code, _, _ = self.run_cli(['text', str(source), '--highlight', '--output', str(target)])
            self.assertEqual(code, 2)
            self.assertFalse(target.exists())

    def test_real_javascript_copies_plain_source_and_handles_clipboard_restrictions(self):
        node = shutil.which('node')
        if not node:
            self.skipTest('Node unavailable for isolated clipboard checks')
        words = '[Verse]\n[Male Vocal: soft singing]\nMe & you — ё.\n\n[Chorus]\n(Mm) Stay.'
        page = PageReader(runtime.render_lyrics_highlight(words))
        harness = r'''
const vm = require('node:vm');
const assert = require('node:assert/strict');
const input = JSON.parse(require('node:fs').readFileSync(0, 'utf8'));
(async () => {
  for (const mode of ['ok', 'denied', 'absent']) {
    let copied;
    const elements = {};
    for (const id of ['copy-source','copy-text','copy-status','copy-fallback','copy-plain']) {
      elements[id] = {textContent:'',value:'',open:false,selected:false,
        addEventListener(event, fn) { this.handler = fn; }, focus() {},
        select() { this.selected = true; }};
    }
    elements['copy-source'].textContent = input.payload;
    const navigator = mode === 'absent' ? {} : {clipboard:{async writeText(value) {
      if (mode === 'denied') throw new Error('denied'); copied = value;
    }}};
    vm.runInNewContext(input.behavior, {document:{getElementById:id=>elements[id]},navigator});
    await elements['copy-text'].handler();
    assert.equal(elements['copy-plain'].value, input.words);
    if (mode === 'ok') assert.equal(copied,input.words);
    else { assert.equal(copied,undefined); assert.equal(elements['copy-fallback'].open,true);
      assert.equal(elements['copy-plain'].selected,true);
      assert.equal(elements['copy-status'].textContent.includes('Ctrl+C'),true); }
  }
})().catch(e=>{console.error(e);process.exitCode=1;});
'''
        result = subprocess.run([node, '-e', harness], input=json.dumps({'payload': page.scripts['copy-source'], 'behavior': page.scripts['behavior'], 'words': words}), capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
