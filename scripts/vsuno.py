#!/usr/bin/env python3
"""Portable UTF-8 chunk checks, immutable local versions and optional Codex entry."""
import argparse
import copy
import html
import json
import re
import secrets
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEYS = ['TRACK', 'LYRICS', 'STYLES', 'MOREOPTIONS', 'INFO']
OPTION_KEYS = ['Vocal Gender', 'Duration', 'Max Mode', 'Weirdness', 'Style Influence', 'Variety', 'Personalize']


def bundle_skill(root, output):
    """Export shared UTF-8 resources; never install or include personal files."""
    root = Path(root).resolve()
    target = Path(output).resolve()
    if target.suffix.lower() != '.zip':
        raise ValueError('A bundle requires a .zip output file.')
    if target.exists():
        raise FileExistsError('Bundle already exists; choose another name. Overwriting is forbidden.')
    root_files = ('SKILL.md', 'AGENTS.md', 'START_HERE_tpl.md', 'USAGE_guide.md', 'README.md',
                  '.gitignore', 'vsuno.cmd', 'ORIGIN_AUDIT_spec.md', 'VALIDATION_spec.md')
    required = ('SKILL.md', 'AGENTS.md', 'START_HERE_tpl.md', 'USAGE_guide.md')
    for name in required:
        if not (root/name).is_file():
            raise ValueError('Incomplete bundle: missing '+name+'.')
    excluded = {'personal', 'prompts', 'work', '__pycache__', '.git'}
    candidates = [root/name for name in root_files if (root/name).is_file()]
    public_folders = {'references': {'.md'}, 'scripts': {'.py'}, 'tools': {'.js'},
                      'agents': {'.yaml'}, 'tests': {'.md', '.py', '.js', '.json'}}
    for folder, suffixes in public_folders.items():
        for path in (root/folder).rglob('*'):
            if path.is_file() and path.suffix in suffixes and not excluded.intersection(path.relative_to(root).parts):
                candidates.append(path)
    payload = []
    for path in sorted(candidates):
        resolved = path.resolve()
        if not resolved.is_relative_to(root) or excluded.intersection(resolved.relative_to(root).parts):
            raise ValueError('Public-file link resolves outside the permitted location.')
        data = path.read_bytes()
        data.decode('utf-8-sig')  # Preflight before creating the archive; preserve original bytes.
        payload.append(('vsuno-composer/'+path.relative_to(root).as_posix(), data))
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in payload:
            archive.writestr(name, data)
    return {'saved': True, 'archive': str(target), 'files': len(payload),
            'bytes': target.stat().st_size, 'installed': False}

def valid_version_id(value):
    if not isinstance(value, str):
        return False
    if re.fullmatch(r'[0-9a-f]{32}', value):
        return True  # Legacy records remain readable without migration.
    if not re.fullmatch(r'[a-z]{6}_[0-9]{8}T[0-9]{12}Z', value):
        return False
    try:
        datetime.strptime(value.split('_', 1)[1], '%Y%m%dT%H%M%S%fZ')
    except ValueError:
        return False
    return True


def render_lyrics_highlight(lyrics, title='Lyrics'):
    """Read-only HTML for an already extracted/translated structured lyric view."""
    rows = []
    for line in lyrics.split('\n'):
        stripped = line.strip()
        kind = 'gap' if not stripped else ('cue' if stripped.startswith('[') and stripped.endswith(']') else 'words')
        rows.append('<div class="line '+kind+'">'+html.escape(line)+'</div>')
    # JSON is the one canonical clipboard source, never text reconstructed from DOM.
    payload = json.dumps(lyrics, ensure_ascii=False).replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
    return '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>'''+html.escape(title)+''' — Lyrics</title>
<style>
:root { color-scheme: light dark; --bg:#FAFCFF; --words:#134A42; --cue:#596A7D; --button:#124E46; --button-text:#FFFFFF; }
@media (prefers-color-scheme:dark) { :root { --bg:#141A22; --words:#DDF4EE; --cue:#9DAAB9; --button:#79D6C9; --button-text:#142322; } }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--words); font:17px/1.65 "Segoe UI",Arial,sans-serif; }
main { max-width:860px; padding:28px 22px 48px; margin:auto; }
h1 { font-size:1.3rem; line-height:1.4; overflow-wrap:anywhere; }
.note, #copy-status, summary { color:var(--cue); font-size:.95rem; }
.line { white-space:pre-wrap; overflow-wrap:anywhere; }
.words { color:var(--words); font-weight:600; }
.cue { color:var(--cue); font: .95rem/1.6 Consolas,monospace; }
.gap { min-height:1.2em; }
button { background:var(--button); color:var(--button-text); border:0; border-radius:6px; padding:10px 16px; font:inherit; cursor:pointer; }
button:focus-visible, textarea:focus-visible { outline:3px solid var(--cue); outline-offset:3px; }
article { margin:24px 0; }
textarea { width:100%; min-height:220px; margin-top:12px; font:1rem/1.5 Consolas,monospace; }
</style>
</head>
<body><main>
<h1>'''+html.escape(title)+'''</h1>
<p class="note">Lyrics view: words emphasized, cues muted. This is not a parser chunk.</p>
<button id="copy-text" type="button">Copy text</button>
<p id="copy-status" role="status" aria-live="polite"></p>
<article aria-label="Lyrics and vocal annotations">
'''+('\n'.join(rows))+'''
</article>
<details id="copy-fallback"><summary>Plain text for manual copying</summary>
<textarea id="copy-plain" readonly aria-label="Plain text">'''+html.escape(lyrics)+'''</textarea></details>
<noscript><p>The button requires JavaScript. Open the plain text above and copy it manually.</p></noscript>
</main>
<script id="copy-source" type="application/json">'''+payload+'''</script>
<script>
const source = JSON.parse(document.getElementById('copy-source').textContent);
const plain = document.getElementById('copy-plain');
plain.value = source;
document.getElementById('copy-text').addEventListener('click', async () => {
  const status = document.getElementById('copy-status');
  try {
    if (!navigator.clipboard || !navigator.clipboard.writeText) throw new Error('Clipboard unavailable');
    await navigator.clipboard.writeText(source);
    status.textContent = 'Copied plain text with tags, without formatting.';
  } catch (_) {
    document.getElementById('copy-fallback').open = true;
    plain.focus();
    plain.select();
    status.textContent = 'Automatic copying is unavailable. Text is selected; press Ctrl+C or use Copy.';
  }
});
</script>
</body></html>
'''


def export_lyrics_highlight(text, output):
    target = Path(output).resolve()
    if target.suffix.lower() != '.html':
        raise ValueError('Highlighted viewing requires an .html output file.')
    if target.exists():
        raise FileExistsError('View file already exists; choose another name. Overwriting is forbidden.')
    fields = parse_chunk(text)
    lyrics = unwrap(lyrics_view(text))
    document = render_lyrics_highlight(lyrics, fields['TRACK'])
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(document)
    return {'saved': True, 'file': str(target), 'bytes': target.stat().st_size,
            'view': 'highlighted-lyrics', 'parser_chunk': False}

def read_utf8(path):
    return Path(path).read_text(encoding='utf-8-sig')

def normalize(text):
    return text.lstrip('\ufeff').replace('\r\n', '\n').replace('\r', '\n')

def utf16_length(text):
    return len(text.encode('utf-16-le')) // 2

def unwrap(text):
    lines = normalize(text).strip('\n').split('\n')
    if lines and re.fullmatch(r'```(?:text)?\s*', lines[0].strip()):
        if len(lines) < 2 or lines[-1].strip() != '```':
            raise ValueError('The text block is unclosed or not unique.')
        lines = lines[1:-1]
    if any(line.strip().startswith('```') for line in lines):
        raise ValueError('Provide one complete chunk without nested blocks.')
    return '\n'.join(lines).strip('\n')

def parse_chunk(text):
    lines = unwrap(text).split('\n')
    indices = [(i, line.strip()[:-3]) for i, line in enumerate(lines)
               if re.fullmatch(r'[A-Z]+:->', line.strip())]
    if [key for _, key in indices] != KEYS:
        raise ValueError('Exactly TRACK/LYRICS/STYLES/MOREOPTIONS/INFO are required in that order.')
    if indices[0][0] != 0:
        raise ValueError('No explanation may precede TRACK.')
    fields = {}
    for pos, (i, key) in enumerate(indices):
        if i + 1 >= len(lines) or lines[i + 1].strip():
            raise ValueError('A blank line is required after {}:->.'.format(key))
        end = indices[pos + 1][0] if pos + 1 < len(indices) else len(lines)
        body = lines[i + 2:end]
        while body and not body[-1].strip():
            body.pop()
        fields[key] = '\n'.join(body)
    return fields


# Human-readable labels retain canonical keys for exact local ID/source lookup.
# INFO is separate from Suno field content; do not impose the legacy clipboard
# regex on its presentation or scan Lyrics/Styles for metadata.
INFO_GROUPS = (
    ('VERSION AND STORAGE', (
        ('id', 'Unique version ID'), ('version', 'Version ID'),
        ('parent', 'Parent version'), ('storage', 'Storage status'),
        ('identity', 'Archive identity status'),
    )),
    ('COMPOSITION', (
        ('summary', 'Composition summary'), ('lang', 'Lyric language'),
    )),
    ('CREATIVE DIRECTION', (
        ('music_mode', 'Musical freedom'), ('text_mode', 'Lyric freedom'),
        ('detail', 'Prompt detail'),
    )),
    ('GENERATION AND VERIFICATION', (
        ('model', 'Suno generation model'), ('gen_model', 'Writer model'),
        ('gen_time', 'Preparation time'), ('risk', 'Tag risk'),
        ('research', 'Reference research'),
        ('lyrics_chars', 'Lyrics length in UTF-16 units'),
        ('styles_chars', 'Styles length in UTF-16 units'),
        ('counting', 'Field counting status'),
    )),
    ('REVISION AND SOURCES', (
        ('changes', 'Changes in this version'), ('translation', 'Translation mode'),
        ('compromise', 'Precision compromise'), ('lyrics_source', 'Lyrics donor'),
        ('music_source', 'Music donor'),
    )),
)
INFO_HEADINGS = {heading for heading, _ in INFO_GROUPS} | {'ADDITIONAL DETAILS'}


def parse_info(info):
    """Read labeled lines and legacy key:value entries without losing duplicates.

    Labeled values are opaque: semicolons/pipes inside prose are preserved.
    Legacy separators split only before another key:value entry. Unknown data
    remains available for re-export; presentation headings are not parameters.
    """
    entries = []
    for line in normalize(info).splitlines():
        line = line.strip()
        if not line or line in INFO_HEADINGS:
            continue
        labeled = re.fullmatch(r'(.+?)\s+\(([A-Za-z][A-Za-z0-9_]*)\):\s*(.*)', line)
        if labeled:
            entries.append((labeled[2].casefold(), labeled[3], labeled[1]))
            continue
        for part in re.split(r'\s*[;|]\s*(?=[A-Za-z][A-Za-z0-9_]*\s*:)', line):
            plain = re.fullmatch(r'([A-Za-z][A-Za-z0-9_]*)\s*:\s*(.*)', part)
            if plain:
                entries.append((plain[1].casefold(), plain[2], None))
            else:
                entries.append(('notes', part, 'Additional note'))
    return entries


def info_values(info, key):
    return [value for name, value, _ in parse_info(info) if name == key.casefold()]


def format_info(entries):
    """Group known metadata; retain custom parameters and notes in the tail."""
    blocks, known = [], set()
    for heading, parameters in INFO_GROUPS:
        rows = []
        for key, label in parameters:
            known.add(key)
            rows.extend('{} ({}): {}'.format(label, 'ID' if key == 'id' else key, value)
                        for name, value, _ in entries if name == key)
        if rows:
            blocks.append(heading+'\n'+'\n'.join(rows))
    custom = ['{} ({}): {}'.format(label or key.replace('_', ' ').capitalize(), key, value)
              for key, value, label in entries if key not in known]
    if custom:
        blocks.append('ADDITIONAL DETAILS\n'+'\n'.join(custom))
    return '\n\n'.join(blocks)

def phrase_present(text, phrase):
    phrase = re.sub(r'\s+', ' ', str(phrase)).strip().casefold()
    haystack = re.sub(r'\s+', ' ', text).casefold()
    return bool(phrase and re.search(r'(?<!\w)' + re.escape(phrase) + r'(?!\w)', haystack))

SECTION_PATTERN = re.compile(
    r'^(?P<header>(?:(?:Final\s+)?(?:Intro|Verse|Pre[- ]?Chorus|Chorus|Post[- ]?Chorus|Bridge|'
    r'Hook|Refrain|Interlude|Breakdown|Break|Build(?:-Up)?|Drop|Outro|Solo|Instrumental(?:\s+Break)?|End)|'
    r'(?:Guitar|Piano|Synth|Drum|Bass|Saxophone)\s+Solo)(?:\s+\d+)?)'
    r'(?:\s*(?::|\||\s[-–]\s)\s*(?P<modifiers>.*))?$', re.I)

# Display vocabulary, not a claim of official Suno tag support.
VOCAL_CUE_PATTERN = re.compile(
    r'^(?:(?:Male|Female|Group|Gang|Unison)\s+)?'
    r'(?:Vocals?|Voice|Rap|Hook|Backing|Whisper(?:s|ing)?|Recitative|Spoken(?:\s+Word)?|'
    r'Humming|Choir|Falsetto|Chants?|Ad[- ]?libs?|Shouts?|Screams?|Shrieks?|'
    r'Breaths?|Sighs?|Grunts?|Groans?|Laughs?|Giggles?|Cr(?:y|ies)|Sobs?|Clicks?|Clucks?|'
    r'Harmonies|Harmony|Beatbox(?:ing)?|Producer\s+Tag|Glitch\s+Vocals?|Belted|Belting|Whispered|'
    r'Chest\s+Voice|Head\s+Voice|Breathy|Raspy|Growl|'
    r'Pitched\s+Vocals?|Formant[- ]shifted\s+Vocals?)\b', re.I)

def tag_owner(body):
    if re.match(r'^(?:Male|Female)\s+(?:Backing|Harmony)', body, re.I):
        return None
    if re.match(r'^(?:Duet|Unison)\b', body, re.I):
        return 'duet'
    match = re.match(r'^(Male|Female)\s+(?:Vocals?|Voice|Rap)\b', body, re.I)
    if match:
        return match.group(1).lower()
    if SECTION_PATTERN.fullmatch(body):
        # Combined section/voice tags are accepted for imported chunks.
        match = re.search(r'\b(male|female)\s+vocals?\b', body, re.I)
        if match:
            return match.group(1).lower()
    return None

PRODUCTION_CUE_PATTERN = re.compile(
    r'^(?:Synth|Lead|Bass|Drums?|Guitar|Piano|Keys|Strings|FX|Motif|Instrumental|Transition|'
    r'Pad|Arp|Melody|Percussion|Silence|Big Finish|Crescendo|Fade (?:In|Out))\b', re.I)
QUOTE_PATTERN = re.compile(r'["“]([^"”]+)["”]')
# Recognition for read-only word extraction, NOT a Suno control-language validator.
CHORD_SYMBOL_PATTERN = re.compile(
    r'[A-G](?:#|b)?(?:m(?:6|7|9|11|13)?|maj(?:7|9|11|13)|'
    r'6|7|9|11|13|dim7?|aug|sus[24]|add[29])?(?:/[A-G](?:#|b)?)?')
DRUM_DESCRIPTION_CUES = frozenset({
    'catchy drum machine intro', 'four-on-the-floor beat drop',
    '80s gated snare fill', 'drum machine bridge', 'funky drum break',
})


def is_harmony_cue(body):
    if CHORD_SYMBOL_PATTERN.fullmatch(body):
        return True
    match = re.fullmatch(r'(?:Chords?|Chord Progression):\s*(.+)', body, re.I)
    if not match:
        return False
    symbols = [part.strip() for part in re.split(r'[-|,→]+', match.group(1)) if part.strip()]
    return bool(symbols) and all(CHORD_SYMBOL_PATTERN.fullmatch(symbol) for symbol in symbols)


WORDLESS_EVENT_PATTERN = re.compile(
    r'^(?:(?:Male|Female|Group|Gang|Unison)\s+)?(?:Vocal\s+)?'
    r'(?:Humming|Chops|Textures|Pads|Breaths?|Sighs?|Grunts?|Groans?|Laughs?|Giggles?|'
    r'Cr(?:y|ies)|Sobs?|Clicks?|Clucks?|Beatbox(?:ing)?|Shouts?|Screams?|Shrieks?)\b', re.I)

def lyric_events(line):
    """Keep inline words and cues in their original order."""
    start = 0
    for match in re.finditer(r'\[([^\]\n]+)\]', line):
        if line[start:match.start()].strip():
            yield False, line[start:match.start()].strip()
        yield True, match.group(1).strip()
        start = match.end()
    if line[start:].strip():
        yield False, line[start:].strip()

def vocal_assignment_errors(lyrics, styles):
    tagged = {tag_owner(body) for body in re.findall(r'\[([^\]\n]+)\]', lyrics)}
    # Limited English heuristic: ignore direct negation, not "not only ...".
    # Explicit lyric roles still take precedence over a conflicting Styles cue.
    positive_styles = re.sub(
        r'\b(?:no|not|without|exclude(?:d|s)?|excluding|avoid(?:ing)?)\s+(?:any\s+)?'
        r'(?:male|female)(?:\s+(?:or|and)\s+(?:male|female))?\b', '', styles, flags=re.I)
    multiple = (phrase_present(positive_styles, 'male') and phrase_present(positive_styles, 'female')) or {'male', 'female'} <= tagged or 'duet' in tagged
    if not multiple:
        return []
    errors, owner, pending = [], None, None
    for number, line in enumerate(lyrics.splitlines(), 1):
        for is_tag, body in lyric_events(line):
            if not is_tag:
                if not owner:
                    errors.append('LYRICS: line {} lacks an assigned performer in a changing-voice composition.'.format(number))
                pending = None
                continue
            if SECTION_PATTERN.fullmatch(body):
                owner, pending = None, None
            singer = tag_owner(body)
            if singer:
                if pending and pending != singer:
                    errors.append('LYRICS: line {} has adjacent solo tags that do not allocate words; use separate blocks or Duet.'.format(number))
                owner, pending = singer, singer
            vocal_event = WORDLESS_EVENT_PATTERN.match(body) or (
                VOCAL_CUE_PATTERN.match(body) and re.search(r'\b(?:wordless|nonverbal)\b', body, re.I)) or (
                QUOTE_PATTERN.search(body) and (VOCAL_CUE_PATTERN.match(body) or singer or SECTION_PATTERN.fullmatch(body)))
            if vocal_event:
                # A nonverbal performance also separates two assigned sources.
                backing_source = re.search(r'\b(?:male|female)\b', body, re.I) if re.search(r'\b(?:backing|harmon)', body, re.I) else None
                if not owner and not backing_source:
                    errors.append('LYRICS: line {} lacks the source of a vocal event.'.format(number))
                pending = None
    return errors

def section_vocal_cue(body, section):
    modifiers = QUOTE_PATTERN.sub('', section.group('modifiers') or '').strip(' ,;:')
    # Remove instrument clauses, but retain the imported vocal delivery.
    clauses = [part.strip() for part in re.split('[,;|]', modifiers) if part.strip()]
    voice_pattern = r'\b(?:whisper\w*|belt\w*|rap|recitative|spoken|falsetto|breathy|raspy|vocal\w*)\b'
    instrument_pattern = r'\b(?:piano|synth|guitar|drums?|bass|strings|pads?|FX|motif|arpeggio)\b'
    if any(re.search(instrument_pattern, part, re.I) and re.search(voice_pattern, part, re.I) for part in clauses):
        raise ValueError('Voice and instruments share one instruction; semantic review must preserve delivery.')
    clauses = [part for part in clauses if not re.search(instrument_pattern, part, re.I)]
    singer = tag_owner(body)
    if singer:
        delivery = re.sub(r'\b(?:male|female)\s+vocals?\b', '', ', '.join(clauses), flags=re.I).strip(' ,;:')
        return '{} Vocal{}'.format(singer.title(), ': '+delivery if delivery else '')
    if clauses and any(re.search(voice_pattern, part, re.I) for part in clauses):
        return 'Vocal: '+', '.join(clauses)
    if clauses:
        raise ValueError('Ambiguous section modifier; semantic review is required before extraction.')
    return None

def lyrics_view(text, plain=False):
    """Read-only display: keep form/voice cues; omit production directions."""
    lyrics = parse_chunk(text)['LYRICS']
    rendered, has_words = [], False
    for line in lyrics.splitlines():
        # Remove only recognized music annotations; keep the original lyric line
        # together even when chord markers occur inside words or between phrases.
        line = re.sub(r'\[([^\]\n]+)\]',
                      lambda match: '' if is_harmony_cue(match.group(1).strip()) else match.group(0), line)
        for is_tag, body in lyric_events(line):
            if not is_tag:
                rendered.append(body)
                has_words = True
                continue
            section = SECTION_PATTERN.fullmatch(body)
            singer = tag_owner(body)
            quoted = QUOTE_PATTERN.findall(body)
            vocal = bool(VOCAL_CUE_PATTERN.match(body))
            instrument = bool(PRODUCTION_CUE_PATTERN.match(body)) or body.casefold() in DRUM_DESCRIPTION_CUES
            if quoted and instrument and not (section or vocal or singer):
                raise ValueError('Ambiguous quotation in an instrumental cue; review meaning before extraction.')
            if section:
                if rendered and rendered[-1]:
                    rendered.append('')
                cue = section_vocal_cue(body, section)
                if not plain:
                    rendered.append('[' + section.group('header') + ']')
                    if cue:
                        rendered.append('[' + cue + ']')
            elif vocal or singer:
                if not plain:
                    if quoted:
                        cue = QUOTE_PATTERN.sub('', body)
                        cue = re.sub(r':\s*[,;]\s*', ': ', cue).strip(' ,;:')
                        rendered.append('[' + cue + ']')
                    else:
                        rendered.append('[' + body + ']')
            elif not instrument:
                raise ValueError('Unknown construction requires semantic review before extraction; no partial text is returned.')
            if quoted and (vocal or singer or section):
                rendered.extend(quoted)
                has_words = True
            # Instrument/FX tags are intentionally absent from this view.
        if not line.strip() and rendered and rendered[-1]:
            rendered.append('')
    content = '\n'.join(rendered).strip()
    if not has_words:
        raise ValueError('No performed words; request the musical structure for an instrumental.')
    return '```text\n' + content + '\n```'

def validate_chunk(text, forbidden=None, banned_words=None):
    errors, warnings, counts = [], [], {}
    for label, values in [('reference_identities', forbidden), ('banned_words', banned_words)]:
        if values is not None and (not isinstance(values, list) or not all(isinstance(v, str) and v.strip() for v in values)):
            errors.append(label + ': requires a list of nonempty strings.')
    if errors:
        return {'ok': False, 'errors': errors, 'warnings': warnings, 'counts': counts}
    try:
        fields = parse_chunk(text)
    except (ValueError, UnicodeError) as exc:
        return {'ok': False, 'errors': [str(exc)], 'warnings': warnings, 'counts': counts}
    for key, cap in [('LYRICS', 5000), ('STYLES', 1000)]:
        try:
            counts[key] = utf16_length(fields[key])
        except UnicodeError:
            errors.append(key + ': invalid Unicode.')
            continue
        if counts[key] > cap:
            errors.append('{}: {} > {} UTF-16 code units.'.format(key, counts[key], cap))
    if not fields['TRACK'].strip() or '\n' in fields['TRACK']:
        errors.append('TRACK must contain one nonempty title.')
    if not fields['LYRICS'].strip() or not fields['STYLES'].strip():
        errors.append('LYRICS and STYLES must be nonempty; there is no minimum length.')
    more = fields['MOREOPTIONS'].split('\n')
    if len(more) != 2 or not re.fullmatch(r'Exclude:\s*[^\n]*', more[-1]):
        errors.append('MOREOPTIONS requires one line of seven settings, then a separate Exclude: line.')
    else:
        exclusions = [part.strip() for part in more[-1].split(':', 1)[1].split(',')]
        if any(not re.search(r'[^\W\d_]', part, re.UNICODE) or part.casefold() in ('none', 'null', 'n/a', 'нет') for part in exclusions):
            errors.append('Exclude requires nonempty style values without empty elements or none.')
    errors.extend(vocal_assignment_errors(fields['LYRICS'], fields['STYLES']))
    if more:
        parts = [part.strip() for part in more[0].split('|')]
        pairs = [re.fullmatch(r'([^:]+):\s*(.*)', part) for part in parts]
        if len(pairs) != 7 or not all(pairs) or [p.group(1).strip() for p in pairs if p] != OPTION_KEYS:
            errors.append('MOREOPTIONS has invalid keys or order for the seven settings.')
        else:
            options = {p.group(1).strip(): p.group(2).strip() for p in pairs}
            accepted = {
                'Vocal Gender': r'(?:Male|Female|none)',
                'Duration': r'(?:Auto|Custom \d+:[0-5]\d)',
                'Max Mode': r'(?:Off|On)',
                'Weirdness': r'(?:100|[1-9]?\d)%?',
                'Style Influence': r'(?:100|[1-9]?\d)%?',
                'Variety': r'(?:Off|Normal|High|Extra|Max)',
                'Personalize': r'Off',
            }
            for key, pattern in accepted.items():
                if not re.fullmatch(pattern, options[key]):
                    errors.append(key + ': invalid value.')
            if options['Duration'] != 'Auto':
                warnings.append('Custom Duration: the original userscript does not guarantee setting the time.')
            if options['Vocal Gender'] == 'none':
                warnings.append('none does not reset Vocal Gender or set the Instrumental toggle.')
    info = fields['INFO']
    if not info.strip():
        errors.append('INFO must contain nonempty metadata.')
    ids = info_values(info, 'ID')
    versions = info_values(info, 'version')
    if ids and (len(ids) != 1 or not valid_version_id(ids[0])):
        errors.append('INFO requires one valid version ID.')
    if versions and (len(versions) != 1 or not valid_version_id(versions[0])):
        errors.append('INFO requires one valid version value.')
    if ids and versions and versions != ids:
        errors.append('INFO: ID and version must match.')
    if not ids:
        warnings.append('Imported chunk lacks ID; assign an ID when finalizing a new full version.')
    if info_values(info, 'storage') == ['context-only']:
        warnings.append('context-only: this output is not a saved archival version; retain its complete source in this conversation.')
    for key in ('identity', 'counting'):
        status = info_values(info, key)
        if status and (len(status) != 1 or status[0] not in ('verified', 'unavailable')):
            errors.append(key + ': requires one verified or unavailable status.')
        if key == 'identity':
            if status == ['unavailable'] and (ids or versions):
                errors.append('Unavailable identity must omit archival ID and version.')
            if status == ['verified'] and not ids:
                errors.append('Verified identity requires ID.')
        else:
            declared_counts = [info_values(info, name) for name in ('lyrics_chars', 'styles_chars')]
            if status == ['unavailable'] and any(declared_counts):
                errors.append('Unavailable counting must omit declared field lengths.')
            if status == ['verified'] and not all(declared_counts):
                errors.append('Verified counting requires both declared field lengths.')
    models = info_values(info, 'model')
    if len(models) != 1:
        errors.append('INFO must contain exactly one model parameter.')
    elif models[0] not in ('v6', 'v6-wild', 'v6-mini'):
        errors.append('INFO requires a compatible model: v6/v6-wild/v6-mini.')
    for key, count_key in [('lyrics_chars', 'LYRICS'), ('styles_chars', 'STYLES')]:
        declared = info_values(info, key)
        if declared and (len(declared) != 1 or not re.fullmatch(r'\d+', declared[0])):
            errors.append(key + ': requires one nonnegative integer count.')
        elif declared and count_key in counts and int(declared[0]) != counts[count_key]:
            errors.append(key + ': count does not match the field.')
    for phrase in forbidden or []:
        if phrase_present(unwrap(text), phrase):
            # Deliberately do not echo a private reference identity into reports.
            errors.append('A forbidden reference identity was found in the chunk.')
    for phrase in banned_words or []:
        if phrase_present(fields['LYRICS'], phrase):
            errors.append('LYRICS contains an expression from the user avoid-list.')
    if not forbidden:
        warnings.append('No identity list supplied; reference names were not checked mechanically.')
    warnings.append('Rhyme, lyric originality and Suno performance require separate review.')
    return {'ok': not errors, 'errors': errors, 'warnings': warnings, 'counts': counts}

def tracks_dir(root):
    root = Path(root).resolve()
    target = root / 'personal' / 'tracks'
    if not target.resolve().is_relative_to(root):
        raise ValueError('Personal folder resolves outside the selected data root.')
    return target

def list_tracks(root, query=''):
    folder = tracks_dir(root)
    if not folder.exists():
        return []
    rows = []
    for path in sorted(folder.glob('*.json')):
        try:
            item = json.loads(read_utf8(path))
            validate_track_record(item, path.stem)
        except (OSError, UnicodeError, ValueError):
            label = path.stem if valid_version_id(path.stem) else '(unrecognized ID)'
            print('vsuno: skipped an invalid archive record '+label, file=sys.stderr)
            continue
        if query.casefold() in item.get('title', '').casefold():
            rows.append({'id': item['id'], 'title': item['title'], 'created_at': item['created_at'], 'parent': item.get('parent')})
    return sorted(rows, key=lambda row: (row['created_at'], row['id']))

def validate_track_record(item, version_id):
    if not isinstance(item, dict) or item.get('id') != version_id or not valid_version_id(version_id):
        raise ValueError('Invalid version card: an object with matching ID is required.')
    if any(not isinstance(item.get(key), str) or not item[key].strip() for key in ('title', 'created_at', 'chunk')):
        raise ValueError('Invalid version card: title/created_at/chunk must be nonempty strings.')
    try:
        datetime.fromisoformat(item['created_at'].replace('Z', '+00:00'))
    except ValueError:
        raise ValueError('Invalid version date.') from None
    if not isinstance(item.get('state', {}), dict):
        raise ValueError('Invalid version card: state must be an object.')
    parent = item.get('parent')
    if parent is not None and not valid_version_id(parent):
        raise ValueError('Invalid version card: parent must be a valid ID or null.')
    state = item.get('state', {})
    checked = validate_chunk(item['chunk'], state.get('reference_identities'), state.get('banned_words'))
    if checked['errors']:
        # Do not expose private title, words, identities or chunk content.
        raise ValueError('Invalid version card: chunk fails local validation.')
    fields = parse_chunk(item['chunk'])
    if fields['TRACK'] != item['title']:
        raise ValueError('Invalid version card: title does not match TRACK.')
    info = fields['INFO']
    ids, versions = info_values(info, 'ID'), info_values(info, 'version')
    if re.fullmatch(r'[0-9a-f]{32}', version_id):
        # Historical UUID cards may omit ID/version; present values must agree.
        if (ids and ids != [version_id]) or (versions and versions != [version_id]):
            raise ValueError('Invalid version card: embedded identity does not match the selected ID.')
    elif ids != [version_id] or (versions and versions != [version_id]):
        raise ValueError('Invalid version card: embedded identity must match the selected ID.')
    parents = info_values(info, 'parent')
    if parents and parents != [parent or 'none']:
        raise ValueError('Invalid version card: embedded parent does not match the record.')

def get_track(root, version_id):
    if not valid_version_id(version_id):
        raise ValueError('Provide the exact version ID from list, not a title or path.')
    path = tracks_dir(root) / (version_id + '.json')
    if not path.exists():
        raise ValueError('Version not found.')
    item = json.loads(read_utf8(path))
    validate_track_record(item, version_id)
    return item

def export_prompt(root, item):
    """Write a private, copy-ready mirror; never replace an existing export."""
    root = Path(root).resolve()
    folder = (root/'prompts').resolve()
    if not folder.is_relative_to(root):
        raise ValueError('prompts resolves outside the selected data root.')
    title = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', item['title']).strip(' .')[:100].rstrip(' .')
    if not title:
        title = 'Track'
    if re.match(r'^(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)', title, re.I):
        title = 'Track_' + title
    if not valid_version_id(item['id']):
        raise ValueError('Invalid ID for text export.')
    folder.mkdir(parents=True, exist_ok=True)
    path = folder/(title+'_'+item['id']+'.txt')
    try:
        stream = path.open('x', encoding='utf-8', newline='\n')
    except FileExistsError:
        if path.read_bytes() == item['chunk'].encode('utf-8'):
            return path  # An exact existing mirror needs no rewrite.
        raise ValueError('This ID file exists with different content; overwriting is forbidden.') from None
    with stream:
        stream.write(item['chunk'])
    if path.read_bytes() != item['chunk'].encode('utf-8'):
        raise ValueError('Text export verification failed.')
    return path


def archive_chunk(root, text, parent=None, state=None):
    if state is not None and not isinstance(state, dict):
        raise ValueError('state must be a JSON object.')
    parent_item = get_track(root, parent) if parent else None
    effective_state = copy.deepcopy(parent_item.get('state', {}) if parent_item else {})
    effective_state.update(copy.deepcopy(state or {}))
    state = effective_state
    locks = state.get('locks', [])
    if not isinstance(locks, list) or not all(isinstance(value, str) and value.strip() for value in locks):
        raise ValueError('state.locks must be a list of nonempty strings.')
    checked = validate_chunk(text, state.get('reference_identities', []), state.get('banned_words', []))
    if checked['errors']:
        raise ValueError('Chunk not saved: ' + ' '.join(checked['errors']))
    fields = parse_chunk(text)
    if parent_item:
        original_fields = parse_chunk(parent_item['chunk'])
        for locked in locks:
            key = locked.upper()
            if key in KEYS[:-1] and fields[key] != original_fields[key]:
                raise ValueError('Chunk not saved: protected field changed: '+key+'. Change locks only at the user request.')
    created_at = datetime.now(timezone.utc)
    version_id = ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6))+'_'+created_at.strftime('%Y%m%dT%H%M%S%fZ')
    owned = {'id', 'version', 'parent', 'storage', 'identity', 'counting', 'lyrics_chars', 'styles_chars'}
    metadata = [entry for entry in parse_info(fields['INFO']) if entry[0] not in owned]
    metadata.extend((key, value, None) for key, value in (
        ('id', version_id), ('parent', parent or 'none'),
        ('storage', 'saved'), ('lyrics_chars', str(checked['counts']['LYRICS'])),
        ('styles_chars', str(checked['counts']['STYLES'])),
        ('identity', 'verified'), ('counting', 'verified'),
    ))
    fields['INFO'] = format_info(metadata)
    saved_chunk = '\n\n'.join(key + ':->\n\n' + fields[key] for key in KEYS)
    checked_saved = validate_chunk(saved_chunk, state.get('reference_identities', []), state.get('banned_words', []))
    if checked_saved['errors']:
        raise ValueError('Archive metadata invalidates the chunk: '+' '.join(checked_saved['errors']))
    item = {'schema_version': 1, 'id': version_id,
            'created_at': created_at.isoformat(),
            'parent': parent, 'title': fields['TRACK'], 'chunk': saved_chunk, 'state': state}
    folder = tracks_dir(root)
    folder.mkdir(parents=True, exist_ok=True)
    # Exclusive creation: a revision never overwrites another version.
    path = folder / (item['id'] + '.json')
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(item, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    if json.loads(read_utf8(path)) != item:
        raise ValueError('Saved version verification failed.')
    try:
        export_prompt(root, item)
    except (OSError, UnicodeError, ValueError) as exc:
        raise ValueError('Version '+item['id']+' saved in personal/tracks, but prompts export failed: '+str(exc)) from exc
    return item

def start_command(brief=''):
    executable = shutil.which('codex.exe') or shutil.which('codex')
    if not executable:
        raise ValueError('Codex CLI not found. For another LLM provide SKILL.md and references; prompt --full prints instructions. No installation is performed.')
    if sys.platform == 'win32' and Path(executable).suffix.lower() in ('.cmd', '.bat'):
        raise ValueError('codex.exe is required to pass text safely without an additional shell.')
    prompt = ('Use $vsuno-composer (Vave Suno Composer) from SKILL.md in the current root. Read SKILL.md and only relevant linked resources. '
              'Follow the user request within the skill. Apply AGENTS.md and references/FILES_spec.md: '
              'protected files are read-only without explicit scoped edit permission; supported dictionary and personal-data enrichment is allowed. '
              'A library refresh does not authorize core, flow, contract, template, code or parser changes. '
              'Respond in the user language (Russian or English); keep instructions/cues English and lyrics in the requested language. Do not control Suno or generate audio. User request:\n' +
              (brief or 'Start by identifying the composition through the skill intake rules.'))
    return [executable, '--search', '--cd', str(ROOT), prompt]

def main(argv=None):
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors='strict')
    argv = list(sys.argv[1:] if argv is None else argv)
    known = {'start', 'prompt', 'bundle', 'check', 'archive', 'list', 'get', 'text', '-h', '--help'}
    if not argv or argv[0] not in known:
        argv.insert(0, 'start')
    parser = argparse.ArgumentParser(description='Vave Suno Composer (vsuno-composer): local launching and chunk checks.')
    sub = parser.add_subparsers(dest='action', required=True)
    start = sub.add_parser('start', help='Start an interactive session of the existing Codex CLI.')
    start.add_argument('--dry-run', action='store_true', help='Show argv without starting a model.')
    start.add_argument('brief', nargs='*')
    prompt = sub.add_parser('prompt', help='Output UTF-8 instructions for another LLM.')
    prompt_modes = prompt.add_mutually_exclusive_group()
    prompt_modes.add_argument('--full', action='store_true', help='Core and addressable sections of all reference libraries.')
    prompt_modes.add_argument('--starter', action='store_true', help='Short application instructions without installation.')
    prompt.add_argument('--output', help='Save instructions directly to a new UTF-8 file without overwriting.')
    bundle = sub.add_parser('bundle', help='Create a public chat ZIP without private data or installation.')
    bundle.add_argument('--output', required=True, help='New .zip file; existing files are not overwritten.')
    check = sub.add_parser('check', help='Check a chunk file without Suno.')
    check.add_argument('file')
    check.add_argument('--state', help='JSON with reference_identities and banned_words.')
    archive = sub.add_parser('archive', help='Save a new immutable personal version.')
    archive.add_argument('file')
    archive.add_argument('--parent')
    archive.add_argument('--state')
    listing = sub.add_parser('list', help='Find versions by title.')
    listing.add_argument('--query', default='')
    get = sub.add_parser('get', help='Read an exact version.')
    get.add_argument('id')
    get.add_argument('--json', action='store_true')
    for action in (archive, listing, get):
        action.add_argument('--data-root', help='Explicit authorized personal-data folder; defaults to the skill root, with no fallback or migration.')
    view = sub.add_parser('text', help='Show lyrics with sections and vocal annotations, without parser fields.')
    view.add_argument('file')
    view_modes = view.add_mutually_exclusive_group()
    view_modes.add_argument('--plain', action='store_true', help='Explicitly remove tags, retaining performed words.')
    view_modes.add_argument('--highlight', action='store_true', help='Separate colored HTML view; source stays unchanged.')
    view.add_argument('--output', help='New .html file for --highlight; existing files are not overwritten.')
    args = parser.parse_args(argv)
    try:
        data_root = Path(args.data_root).resolve() if getattr(args, 'data_root', None) else ROOT
        if args.action == 'start':
            command = start_command(' '.join(args.brief))
            if args.dry_run:
                print(json.dumps({'argv': command, 'started': False}, ensure_ascii=False, indent=2))
                return 0
            return subprocess.call(command, shell=False)
        if args.action == 'prompt':
            if args.starter:
                instructions = read_utf8(ROOT / 'START_HERE_tpl.md')
            else:
                parts = []
                if args.full:
                    parts.extend(['--- FILE: START_HERE_tpl.md ---\n', read_utf8(ROOT / 'START_HERE_tpl.md'), '\n--- FILE: SKILL.md ---\n'])
                parts.append(read_utf8(ROOT / 'SKILL.md'))
                if args.full:
                    for name in ('AGENTS.md', 'USAGE_guide.md'):
                        parts.extend(['\n\n--- FILE: ' + name + ' ---\n', read_utf8(ROOT / name)])
                    for path in sorted((ROOT / 'references').glob('*.md')):
                        parts.extend(['\n\n--- FILE: references/' + path.name + ' ---\n', read_utf8(path)])
                instructions = ''.join(parts)
            if args.output:
                target = Path(args.output).resolve()
                if target.exists():
                    raise FileExistsError('Instruction file already exists; choose another name. Overwriting is forbidden.')
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open('x', encoding='utf-8', newline='\n') as stream:
                    stream.write(instructions)
                if target.read_bytes() != instructions.encode('utf-8'):
                    raise ValueError('Saved UTF-8 instruction verification failed.')
                print(json.dumps({'saved': True, 'file': str(target), 'bytes': target.stat().st_size},
                                 ensure_ascii=False, indent=2))
            else:
                print(instructions)
            return 0
        if args.action == 'bundle':
            print(json.dumps(bundle_skill(ROOT, args.output), ensure_ascii=False, indent=2))
            return 0
        if args.action in ('check', 'archive'):
            state = json.loads(read_utf8(args.state)) if args.state else {}
            if not isinstance(state, dict):
                raise ValueError('state must be a JSON object.')
            text = read_utf8(args.file)
            if args.action == 'check':
                result = validate_chunk(text, state.get('reference_identities', []), state.get('banned_words', []))
            else:
                item = archive_chunk(data_root, text, args.parent, state)
                result = {'saved': True, 'id': item['id'], 'parent': item['parent'], 'title': item['title']}
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if args.action == 'archive' or result['ok'] else 1
        if args.action == 'list':
            print(json.dumps(list_tracks(data_root, args.query), ensure_ascii=False, indent=2))
        if args.action == 'text':
            if args.highlight:
                if not args.output:
                    raise ValueError('For --highlight specify --output <new-file.html>.')
                print(json.dumps(export_lyrics_highlight(read_utf8(args.file), args.output), ensure_ascii=False, indent=2))
            else:
                if args.output:
                    raise ValueError('--output in text is supported only with --highlight.')
                print(lyrics_view(read_utf8(args.file), plain=args.plain))
        if args.action == 'get':
            item = get_track(data_root, args.id)
            print(json.dumps(item, ensure_ascii=False, indent=2) if args.json else item['chunk'])
        return 0
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print('vsuno: ' + str(exc), file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
