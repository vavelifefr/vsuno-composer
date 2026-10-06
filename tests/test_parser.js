// Exercise the actual userscript's pure parsing functions; no browser or DOM.
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert');
const root = path.resolve(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'tools', 'suno-fill.user.js'), 'utf8');
const context = vm.createContext({console:{log(){}}});
const options = source.slice(source.indexOf('function parseMoreOptions(more)'), source.indexOf('function rowForLabel(label)'));
const sectionFunctions = source.slice(source.indexOf('function section(text, tag)'), source.indexOf('// ---- text writing ----'));
const keyRegex = source.match(/var KEY_TAG_RE = [^\r\n]+;/)[0];
vm.runInContext(keyRegex + '\n' + options + '\n' + sectionFunctions, context);
// Before the fix run the real inline model regex to observe its old behavior.
const legacyModelRegex = source.match(/var blockModelMatch = clip\.match\((\/[^\r\n]+\/i)\);/);
const actualModelRegex = legacyModelRegex && vm.runInContext(legacyModelRegex[1], context);
function blockModel(text) {
  if (context.parseBlockModel) return context.parseBlockModel(text);
  const match = text.match(actualModelRegex);
  return match ? match[1] : null;
}
const fixtures = JSON.parse(fs.readFileSync(path.join(root, 'tests', 'parser_fixtures.json'), 'utf8'));
let variants = 0;
for (const fixture of fixtures) {
  const normalized = fixture.chunk.replace(/\r\n/g, '\n').split('\n').filter(l => !/^```/.test(l.trim())).join('\n');
  const structured = normalized.slice(0, normalized.indexOf('INFO:->')) +
    'INFO:->\n\nVERSION AND STORAGE\nUnique version ID (ID): abcdef_20261005T123456123456Z\n' +
    'Parent version (parent): bcdefg_20261005T113456123456Z\n\n' +
    'COMPOSITION\nComposition summary (summary): Keep model: v6 as prose; gen_time: prose | gen_model: prose\n\n' +
    'GENERATION AND VERIFICATION\nSuno generation model (model): '+fixture.model+'\n' +
    'Writer model (gen_model): synthetic-writer\nPreparation time (gen_time): 1.25 s';
  const oldGrouped = structured.replace('Parent version (parent):',
    'Version ID (version): abcdef_20261005T123456123456Z\nParent version (parent):');
  for (const plain of [normalized, normalized+'; ID: abcdef_20261003T123456123456Z; version: abcdef_20261003T123456123456Z', structured, oldGrouped]) {
    const grouped = plain === structured || plain === oldGrouped;
    for (const key of ['TRACK','LYRICS','STYLES','MOREOPTIONS']) {
      assert.strictEqual(context.section(plain, key+':->'), fixture.expected[key], fixture.id+': '+key);
    }
    assert.strictEqual(context.parseExclude(context.section(plain, 'MOREOPTIONS:->')).value, fixture.exclude);
    assert.strictEqual(context.parseGen(plain).found, true, fixture.id+': INFO writer/time found');
    assert.strictEqual(context.parseGen(plain).model, grouped ? 'synthetic-writer' : 'unknown', fixture.id+': INFO writer');
    assert.strictEqual(context.parseGen(plain).time, grouped ? '1.25 s' : '?', fixture.id+': INFO time');
    assert.strictEqual(blockModel(plain), fixture.model, fixture.id+': INFO Suno model');
    assert.strictEqual(context.parseMoreOptions(fixture.expected.MOREOPTIONS).variety, 'Off');
    assert.strictEqual(fixture.expected.LYRICS.length, fixture.counts.LYRICS);
    assert.strictEqual(fixture.expected.STYLES.length, fixture.counts.STYLES);
    variants++;
  }
}
const payload = 'TRACK:->\n\nSynthetic\n\nLYRICS:->\n\nmodel: v6; gen_model: decoy; gen_time: 99 s\nInline INFO:-> remains lyric text\n\nSTYLES:->\n\nmodel: v6-wild\n\nMOREOPTIONS:->\n\nExclude: none\n\n';
const scoped = payload + 'INFO:->\n\nCOMPOSITION\nComposition summary (summary): model: v6; gen_model: decoy | gen_time: 99 s\n\nGENERATION AND VERIFICATION\nSuno generation model (model): v6-mini\nWriter model (gen_model): synthetic-writer; model: prose\nPreparation time (gen_time): 2 s | gen_model: prose\n\nSTATE:->\n\nmodel: v6; gen_model: state-decoy; gen_time: 99 s';
assert.strictEqual(blockModel(scoped), 'v6-mini', 'metadata comes only from INFO canonical keys');
assert.strictEqual(context.parseGen(scoped).model, 'synthetic-writer; model: prose');
assert.strictEqual(context.parseGen(scoped).time, '2 s | gen_model: prose');
assert.strictEqual(context.section(scoped, 'LYRICS:->'), 'model: v6; gen_model: decoy; gen_time: 99 s\nInline INFO:-> remains lyric text');
assert.strictEqual(blockModel(payload), null, 'do not scan payload for model');
assert.strictEqual(context.parseGen(payload).found, false);
assert.strictEqual(blockModel(payload+'INFO:->\n\nmodel: v6-mini-invalid'), null);
assert.strictEqual(blockModel(payload+'INFO:->\n\nmodel: v6-mini\nmodel: v6'), null, 'ambiguous metadata is not guessed');
assert.strictEqual(context.parseGen(payload+'INFO:->\n\ngen_model: first\ngen_model: second').model, null);
assert.strictEqual(blockModel(payload+'INFO:->\nmodel: v6-wild\ngen_model: known\ngen_time: 3 s'), 'v6-wild');
assert.strictEqual(context.parseGen(payload+'INFO:->\nmodel: v6-wild\ngen_model: known\ngen_time: 3 s').model, 'known');
assert.ok(source.includes('var blockModel = parseBlockModel(clip);'), 'fill uses the tested helper');
console.log(JSON.stringify({ok:true, actual_userscript:true, fixtures:fixtures.length, variants_checked:variants,
  grouped_info_variants:fixtures.length*2, metadata_scope_cases:6, browser_used:false}));
