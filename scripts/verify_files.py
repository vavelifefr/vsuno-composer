"""Validate actual artifacts and prepare fixtures, without Suno or another LLM."""
import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARSER_SHA256 = 'B753AF605620C8E2FF1F6925AA0E3F5A0771E294241CF7F7ADF6C30F941DE34F'

def metadata_errors(entry, directory_name):
    """Check this skill's restricted frontmatter and native containing directory."""
    errors = []
    match = re.match(r'^---\nname: ([a-z0-9-]+)\ndescription: ([^\n]+)\n---\n', entry)
    if not match:
        return ['Frontmatter does not match the deliberately simple two-scalar format.']
    name, description = match.groups()
    if len(name) > 64 or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name):
        errors.append('Invalid native skill name.')
    if name != directory_name:
        errors.append('Skill name must match its containing directory.')
    if not description.strip() or len(description) > 1024:
        errors.append('Invalid skill description length.')
    if ':' in description or any(c in description for c in '<>'):
        errors.append('Ambiguous unquoted YAML description.')
    return errors


def verify(source_hashes=None):
    errors = []
    files = [p for p in ROOT.rglob('*') if p.is_file() and not any(part in ('personal','prompts','work','__pycache__') for part in p.relative_to(ROOT).parts)]
    for path in files:
        if path.suffix in ('.md','.py','.js','.cmd','.json','.yaml') or path.name == '.gitignore':
            try:
                text = path.read_bytes().decode('utf-8-sig')
            except UnicodeError:
                errors.append('Not UTF-8: ' + str(path))
                continue
            if path.name != 'suno-fill.user.js' and path.read_bytes().startswith(b'\xef\xbb\xbf'):
                errors.append('New file unexpectedly has BOM: '+str(path))
            if '\ufffd' in text:
                errors.append('Replacement character: '+str(path))
            if path.suffix == '.md':
                for label, target in re.findall(r'\[([^\]\n]+)\]\(([^)]+)\)', text):
                    if target.startswith(('https://','http://','#')):
                        continue
                    destination = (path.parent / target.split('#')[0]).resolve()
                    if not destination.exists():
                        errors.append('Broken local link '+str(path)+': '+target)
    entry = (ROOT/'SKILL.md').read_text(encoding='utf-8')
    errors.extend(metadata_errors(entry, ROOT.name))
    match = re.match(r'^---\nname: ([a-z0-9-]+)\n', entry)
    if '[TODO:' in entry:
        errors.append('Unfinished scaffold.')
    ui = (ROOT/'agents'/'openai.yaml').read_text(encoding='utf-8').splitlines()
    if ui[0] != 'interface:':
        errors.append('Bad UI metadata root.')
    else:
        values = {}
        for line in ui[1:]:
            m = re.fullmatch(r'  ([a-z_]+): (".*")', line)
            if not m:
                errors.append('Bad UI metadata scalar.')
                continue
            values[m.group(1)] = json.loads(m.group(2))
        if values.get('display_name') != 'Vave Suno Composer' or not 25 <= len(values.get('short_description','')) <= 64:
            errors.append('Bad UI name or description length.')
        if not match or not re.search(r'\$' + re.escape(match.group(1)) + r'(?![a-z0-9-])', values.get('default_prompt','')):
            errors.append('Default prompt missing invocation.')
    refs = sorted((ROOT/'references').glob('*.md'))
    for path in refs:
        if not re.search(r'_(lib|flow|spec|tpl)\.md$', path.name):
            errors.append('Unclassified reference filename: '+path.name)
    # Traverse entry references rather than requiring every library on every request.
    reached, queue = set(), [ROOT/'SKILL.md']
    while queue:
        path = queue.pop()
        if path in reached: continue
        reached.add(path)
        text = path.read_text(encoding='utf-8-sig')
        for target in re.findall(r'\[[^\]\n]+\]\(([^)]+\.md(?:#[^)]*)?)\)', text):
            if target.startswith(('http://','https://')): continue
            dest = (path.parent / target.split('#')[0]).resolve()
            if dest.exists() and dest.is_relative_to(ROOT) and dest not in reached:
                queue.append(dest)
    for path in refs:
        if path.resolve() not in reached:
            errors.append('Unreachable reference: '+path.name)
    source_rows = None
    if source_hashes is not None:
        try:
            source_rows = json.loads(Path(source_hashes).read_text(encoding='utf-8-sig'))
            for row in source_rows:
                if hashlib.sha256(Path(row['path']).read_bytes()).hexdigest().upper() != row['hash']:
                    errors.append('Source changed: '+row['path'])
        except (OSError, UnicodeError, ValueError, KeyError, TypeError) as exc:
            errors.append('Source audit unavailable: '+str(exc))
    if hashlib.sha256((ROOT/'tools'/'suno-fill.user.js').read_bytes()).hexdigest().upper() != PARSER_SHA256:
        errors.append('Userscript differs from the audited v3.12.0 artifact.')
    if not all(value in (ROOT/'.gitignore').read_text(encoding='utf-8') for value in ('/personal/', '/prompts/')):
        errors.append('Private data not excluded.')
    # A used skill legitimately contains personal records. Never read/delete them
    # or treat their existence as an artifact failure; packaging must omit them.
    private_present = (ROOT/'personal').exists() and any(p.is_file() for p in (ROOT/'personal').rglob('*'))
    return {'ok':not errors,'errors':errors,'text_files':len(files),'reference_files':len(refs),
            'libraries':len(list((ROOT/'references').glob('*_lib.md'))),
            'source_files_unchanged':len(source_rows) if source_rows is not None and not errors else None,
            'source_audit':'not-requested' if source_hashes is None else ('failed' if errors else 'verified'),
            'parser_sha256':PARSER_SHA256,
            'yaml_check':'restricted concrete scalar format; not general PyYAML',
            'live_model_or_suno_test':False, 'personal_data_present':private_present,
            'packaging_note':'Exclude personal/, prompts/ and work/ from shared archives; this check does not publish files.'}

def prepare_fixtures():
    spec = importlib.util.spec_from_file_location('runtime', ROOT/'scripts'/'vsuno.py')
    runtime = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runtime)
    testspec = importlib.util.spec_from_file_location('fixture_builder', ROOT/'tests'/'test_chunk.py')
    builder = importlib.util.module_from_spec(testspec)
    testspec.loader.exec_module(builder)
    inputs = [
        ('short-instrumental', builder.chunk()),
        ('cyrillic', builder.chunk('[Verse]\nЯ оставил ключи у двери\nТы вернёшься — тогда забери',title='Новый адрес')),
        ('bilingual', builder.chunk('[Verse]\nНовый день изменил разговор\nЯ закрыл за собой коридор\n[Bridge]\nI put the folded coat away\nAnd chose a different road today',title='Поворот')),
        ('boundaries', builder.chunk('a'*5000,'b'*1000)),
        ('emoji', builder.chunk('[Intro]\n😀'*25)),
        ('fence-crlf', '```text\r\n'+builder.chunk().replace('\n','\r\n')+'\r\n```'),
        ('negative-styles', builder.chunk().replace('Exclude: ambient','Exclude: hardstyle, trap')),
        ('explicit-duet', builder.chunk('[Verse]\n[Male Vocal: rapid rap delivery]\nНовый поворот\n[Chorus]\n[Female Vocal: whispering]\nНас дорога ждёт','Male rap verses, female whispered chorus')),
        ('vocal-insertions', builder.chunk('[Intro]\n[Male Vocal: calm spoken word]\nПовернись, я здесь\n[Verse]\n[Female Vocal: soft singing]\nЯ вернусь домой\n[Ad-libs: whispered response]\nЯ вернусь\n[Chorus]\n[Duet]\nНаши голоса','Male spoken intro, female lead and ad-libs, shared final refrain')),
        ('multiline-styles', builder.chunk(styles='Genre: acid house\nStyle: 124 BPM, A minor\nVocals: instrumental, no vocal sounds\nMain theme: short resonant motif\nInstruments: dry drums\nBass: sub foundation\nMood: restrained tension')),
    ]
    fixtures = []
    for key, text in inputs:
        result = runtime.validate_chunk(text)
        if result['errors']: raise ValueError(key+': '+str(result['errors']))
        fields = runtime.parse_chunk(text)
        fixtures.append({'id':key,'chunk':text,'expected':{k:fields[k] for k in runtime.KEYS[:-1]},
                         'model':'v6-mini','exclude':fields['MOREOPTIONS'].split('\n')[1].split(':',1)[1].strip(),
                         'counts':result['counts']})
    (ROOT/'tests'/'parser_fixtures.json').write_text(json.dumps(fixtures,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return len(fixtures)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Read-only portable skill checks; optional developer source audit.')
    parser.add_argument('--source-hashes', help='Optional local manifest for the original source audit.')
    parser.add_argument('--prepare-fixtures', action='store_true', help='Explicitly regenerate tests/parser_fixtures.json.')
    args = parser.parse_args()
    if args.prepare_fixtures:
        prepare_fixtures()
    report = verify(args.source_hashes)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(0 if report['ok'] else 1)
