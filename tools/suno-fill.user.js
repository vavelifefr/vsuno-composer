// ==UserScript==
// @name        SunoFill
// @namespace   vave-suno-multiprompts
// @version     3.12.0
// @description Fill Lyrics / Styles / Title / Exclude AND More Options on suno.com/create from a Vave Suno Composer chunk. Reads grouped or legacy INFO for diagnostics. NEVER clicks Create.
// @match       https://suno.com/create*
// @match       https://www.suno.com/create*
// @grant       GM_registerMenuCommand
// @run-at      document-idle
// ==/UserScript==

/*
 * SunoFill v3.12.0 — text fill + diagnostics for Vave Suno Composer chunks.
 *
 * WHAT IT DOES
 *   - Fill: reads the five-field chunk from the clipboard and writes the four text
 *     fields (Lyrics, Styles, Title — all matches, Exclude) AND applies the
 *     MOREOPTIONS 7-field line to the Suno controls: Vocal Gender, Duration,
 *     Max Mode and Personalize (toggles), Weirdness and Style Influence
 *     (numeric sliders), Variety (by name). Every control is read back and the
 *     result is reported. It first forces the Create panel to the Advanced tab.
 *   - Free-model awareness: detects the selected Suno model; when the free/mini
 *     model is active it logs a FREE-TIER notice and applies the safe style cap.
 *   - Diagnostics: one menu run produces a single copyable JSON report (fields,
 *     selectors, sliders, control rows, tabs, model, caps) so no extra
 *     copy-paste rounds are needed.
 *   - Gen stamp (read-only): reads gen_model / gen_time from grouped or legacy INFO
 *     (the ignored tail) and surfaces them in the report JSON only — they are never
 *     typed into any Suno field.
 *
 * WHAT IT DOES NOT DO
 *   - It NEVER clicks Create and never touches anything outside Lyrics / Styles /
 *     Title / Exclude / the seven More Options controls.
 *
 * Field kinds handled: native textarea/input (native value setter) AND the
 * Lexical Lyrics editor (one synthetic beforeinput, wait ~450ms, verify, else
 * synthetic paste, else insertHTML, else textContent — the wait is what keeps
 * the working path while avoiding a double insert).
 * Buffer policy: standalone TRACK:-> / INFO:-> lines delimit the payload slice.
 * INFO / STATE never reach the DOM. Suno model and writer/time are read from INFO
 * canonical keys only; labels/headings do not restrict the chunk presentation.
 */

(function () {
  'use strict';

  var VERSION = '3.12.0';
  var CREATE_RE = /^https:\/\/(www\.)?suno\.com\/create/;
  var KEY_TAG_RE = /^[A-Z]+:->$/;
  var FREE_MODEL_RE = /mini/i;          // free-tier model family
  var FREE_STYLE_CAP = 1000;            // working style cap; trim only if exceeded
  var CONTROL_LABELS = ['Vocal Gender', 'Duration', 'Max Mode', 'Weirdness', 'Style Influence', 'Variety', 'Personalize'];
  var FILL_LOG = [];
  var SETTLE_MS = 700;
  var RICH_SETTLE_MS = 450;
  var SLIDER_STEP_MS = 45;

  function onCreatePage() {
    return CREATE_RE.test(location.href);
  }

  function norm(s) { return (s || '').trim().toLowerCase(); }

  function labelOf(el) {
    var parts = [
      el.getAttribute ? el.getAttribute('aria-label') : null,
      el.getAttribute ? el.getAttribute('placeholder') : null,
      el.getAttribute ? el.getAttribute('data-placeholder') : null,
      el.getAttribute ? el.getAttribute('title') : null,
      el.id || null,
      el.name || null,
      (el.getAttribute && el.getAttribute('role')) || null
    ];
    return parts.filter(Boolean).join(' ').toLowerCase();
  }

  function findTextareas() { return Array.prototype.slice.call(document.querySelectorAll('textarea')); }
  function findInputs() { return Array.prototype.slice.call(document.querySelectorAll('input[type="text"], input:not([type]), input[type="search"]')); }
  function findEditables() { return Array.prototype.slice.call(document.querySelectorAll('[contenteditable="true"]')); }

  function pick(re, list, skipRes) {
    for (var i = 0; i < list.length; i++) {
      var s = labelOf(list[i]);
      if (re.test(s) && !(skipRes && skipRes.test(s))) return list[i];
    }
    return null;
  }

  function bySectionHeading(word) {
    var els = document.querySelectorAll('span, div, label, h1, h2, h3, h4, p, summary');
    var head = null;
    for (var i = 0; i < els.length; i++) {
      var t = (els[i].textContent || '').trim().toLowerCase();
      if (t === word && els[i].children.length === 0) { head = els[i]; break; }
    }
    if (!head) return null;
    var node = head.parentElement;
    for (var depth = 0; depth < 4 && node; depth++) {
      var ed = node.querySelector('textarea, [contenteditable="true"]');
      if (ed) return ed;
      node = node.parentElement;
    }
    return null;
  }

  var SEL = {
    lyrics: '[data-lexical-editor="true"], [aria-label="Lyrics editor"], .lyrics-editor-content',
    styles: '[data-testid="create-form-styles-wrapper"] textarea',
    exclude: 'input[placeholder="Exclude styles"]',
    title: 'input[placeholder^="Song Title"]'
  };

  function locateFields() {
    var areas = findTextareas();
    var inputs = findInputs();
    var rich = findEditables();
    var lyricsExact = document.querySelector(SEL.lyrics);
    var lyrics = lyricsExact || pick(/lyrics/, areas) || pick(/lyrics/, rich) || bySectionHeading('lyrics');
    var stylesExact = document.querySelector(SEL.styles);
    var styles = stylesExact || pick(/style/, areas.concat(rich), /exclude/) || bySectionHeading('style') || bySectionHeading('styles');
    var excludeExact = document.querySelector(SEL.exclude);
    var exclude = excludeExact || pick(/exclude/, inputs.concat(areas, rich));
    var titleAll = Array.prototype.slice.call(document.querySelectorAll(SEL.title));
    var titles = titleAll.length ? titleAll : (function () { var t = pick(/title/, inputs); return t ? [t] : []; })();
    return { lyrics: lyrics, styles: styles, titles: titles, exclude: exclude, exact: { lyrics: !!lyricsExact, styles: !!stylesExact, exclude: !!excludeExact, title: titleAll.length } };
  }

  // ---- Advanced tab ----

  function activeTab() {
    var tabs = document.querySelectorAll('[role="tab"]');
    for (var i = 0; i < tabs.length; i++) {
      var t = tabs[i];
      var cls = ' ' + (t.className || '') + ' ';
      if (cls.indexOf(' active ') >= 0 || t.getAttribute('aria-selected') === 'true' || t.getAttribute('data-state') === 'active') {
        return (t.textContent || '').trim();
      }
    }
    return null;
  }

  function isAdvancedActive() {
    var tabs = document.querySelectorAll('[role="tab"]');
    for (var i = 0; i < tabs.length; i++) {
      if (norm(tabs[i].textContent) === 'advanced') {
        var cls = ' ' + (tabs[i].className || '') + ' ';
        return cls.indexOf(' active ') >= 0 || tabs[i].getAttribute('aria-selected') === 'true' || tabs[i].getAttribute('data-state') === 'active';
      }
    }
    return null; // tab not found — cannot tell
  }

  function ensureAdvanced() {
    return new Promise(function (resolve) {
      if (isAdvancedActive() !== false) { resolve(isAdvancedActive()); return; }
      var tabs = document.querySelectorAll('[role="tab"]');
      for (var i = 0; i < tabs.length; i++) {
        if (norm(tabs[i].textContent) === 'advanced') { tabs[i].click(); break; }
      }
      window.setTimeout(function () { resolve(isAdvancedActive()); }, 500);
    });
  }

  // "More Options" holds the sliders. While it is collapsed the Lyrics/Lexical editor has no
  // layout, so Range/selection cannot be built and inserts misbehave (append, lagging counter).
  // Expand it first — this does not change any value.
  function moreOptionsToggle() {
    var els = document.querySelectorAll('button, [role="button"], summary, [aria-expanded]');
    for (var i = 0; i < els.length; i++) {
      var t = (els[i].textContent || '').replace(/\s+/g, ' ').trim();
      if (t.length < 40 && /more\s*option/i.test(t)) return els[i];
    }
    return null;
  }
  function slidersVisible() {
    var list = document.querySelectorAll('div[role="slider"][aria-label]');
    for (var i = 0; i < list.length; i++) { if (list[i].offsetParent !== null) return true; }
    return false;
  }
  function ensureMoreOptions() {
    return new Promise(function (resolve) {
      var toggle = moreOptionsToggle();
      if (!toggle) { resolve({ found: false }); return; }
      if (slidersVisible() || toggle.getAttribute('aria-expanded') === 'true') { resolve({ found: true, wasCollapsed: false, expanded: true }); return; }
      try { toggle.click(); } catch (e) {}
      window.setTimeout(function () {
        resolve({ found: true, wasCollapsed: true, expanded: slidersVisible() || toggle.getAttribute('aria-expanded') === 'true' });
      }, 400);
    });
  }

  // ---- More Options automation (Vocal Gender / Duration / Max Mode / Weirdness / Style Influence / Variety / Personalize) ----
  // Click toggles and drive sliders from the MOREOPTIONS line, always read back. Create is never clicked.

  function parseMoreOptions(more) {
    var out = {};
    if (!more) return out;
    var line = String(more).split('\n').map(function (l) { return l.trim(); }).filter(function (l) { return l !== ''; })[0] || '';
    line.split('|').forEach(function (p) {
      var m = p.match(/^\s*([^:]+?)\s*:\s*(.*)$/);
      if (!m) return;
      var k = m[1].trim().toLowerCase(), v = m[2].trim();
      if (k === 'vocal gender') out.vocalGender = v;
      else if (k === 'duration') out.duration = v;
      else if (k === 'max mode') out.maxMode = v;
      else if (k === 'weirdness') out.weirdness = parseInt(v, 10);
      else if (k === 'style influence') out.styleInfluence = parseInt(v, 10);
      else if (k === 'variety') out.variety = v;
      else if (k === 'personalize') out.personalize = v;
    });
    return out;
  }

  function rowForLabel(label) {
    var nodes = document.querySelectorAll('div, span, p, label, h2, h3, h4');
    var want = label.toLowerCase();
    for (var i = 0; i < nodes.length; i++) {
      if (nodes[i].children.length !== 0) continue;
      if ((nodes[i].textContent || '').trim().toLowerCase() !== want) continue;
      var p = nodes[i];
      for (var up = 0; up < 5 && p; up++) {
        p = p.parentElement;
        if (p && p.querySelectorAll('button, [role="button"], [role="slider"]').length) return p;
      }
    }
    return null;
  }
  function rowButtons(row) {
    if (!row) return [];
    return Array.prototype.slice.call(row.querySelectorAll('button, [role="button"]'))
      .filter(function (b) { return (b.textContent || '').trim().length > 0 && (b.textContent || '').trim().length < 24; });
  }
  function controlRow(label) {
    var row = rowForLabel(label);
    var out = { label: label, row: !!row, buttons: [], slider: null };
    rowButtons(row).forEach(function (b) { out.buttons.push({ text: (b.textContent || '').trim(), state: selectedState(b) }); });
    var sl = document.querySelector('[role="slider"][aria-label="' + label + '"]');
    if (sl) out.slider = { min: sl.getAttribute('aria-valuemin'), max: sl.getAttribute('aria-valuemax'), now: sl.getAttribute('aria-valuenow'), text: sl.getAttribute('aria-valuetext') };
    return out;
  }
  function clickOption(label, value) {
    var row = rowForLabel(label);
    if (!row) return { label: label, ok: false, reason: 'row not found', target: value };
    var btns = rowButtons(row);
    var target = null;
    for (var i = 0; i < btns.length; i++) if ((btns[i].textContent || '').trim().toLowerCase() === String(value).toLowerCase()) { target = btns[i]; break; }
    if (!target) return { label: label, ok: false, reason: 'option not found', target: value, options: btns.map(function (b) { return (b.textContent || '').trim(); }) };
    var before = selectedState(target);
    if (before === 'selected') return { label: label, ok: true, changed: false, value: value };
    try { target.click(); } catch (e) {}
    return { label: label, ok: true, changed: true, value: value, before: before };
  }
  function sliderNow(sl) { return parseInt(sl.getAttribute('aria-valuenow'), 10); }
  function pressSlider(sl, key, code) {
    try {
      sl.dispatchEvent(new KeyboardEvent('keydown', { key: key, keyCode: code, which: code, bubbles: true }));
      sl.dispatchEvent(new KeyboardEvent('keyup', { key: key, keyCode: code, which: code, bubbles: true }));
    } catch (e) {}
  }
  function sleep(ms) { return new Promise(function (r) { window.setTimeout(r, ms); }); }
  function setNumericSlider(label, goal) {
    var sl = document.querySelector('[role="slider"][aria-label="' + label + '"]');
    if (!sl) return Promise.resolve({ label: label, ok: false, reason: 'slider not found', target: goal });
    var min = parseInt(sl.getAttribute('aria-valuemin'), 10), max = parseInt(sl.getAttribute('aria-valuemax'), 10);
    goal = Math.max(min, Math.min(max, goal));
    try { sl.focus(); } catch (e) {}
    var stall = 0;
    return (function step(i) {
      var now = sliderNow(sl);
      if (now === goal) return Promise.resolve({ label: label, ok: true, target: goal, got: now });
      if (i > 260) return Promise.resolve({ label: label, ok: false, reason: 'gave up', target: goal, got: now });
      pressSlider(sl, now < goal ? 'ArrowRight' : 'ArrowLeft', now < goal ? 39 : 37);
      return sleep(SLIDER_STEP_MS).then(function () {
        var after = sliderNow(sl);
        if (after === now) { stall++; if (stall >= 3) return { label: label, ok: false, reason: 'no movement on synthetic keys', target: goal, got: after }; }
        else stall = 0;
        return step(i + 1);
      });
    })(0);
  }
  function setVariety(name) {
    // Live-UI mapping observed 2026-09-13: 0=Off, 1=Normal, 2=High, 3=Extra, 4=Max.
    var map = { off: 0, normal: 1, high: 2, extra: 3, max: 4 };
    var key = String(name).trim().toLowerCase();
    if (!(key in map)) return Promise.resolve({ label: 'Variety', ok: false, reason: 'unknown Variety label', target: name, known: Object.keys(map) });
    return setNumericSlider('Variety', map[key]).then(function (r) { r.variety = name; return r; });
  }
  function setPersonalize(value) {
    var row = rowForLabel('Personalize');
    if (!row) return Promise.resolve({ label: 'Personalize', ok: false, reason: 'row not found', target: value });
    var btns = Array.prototype.slice.call(row.querySelectorAll('button, [role="button"]')).filter(function (b) { return (b.textContent || '').trim().length > 0; });
    for (var i = 0; i < btns.length; i++) {
      if ((btns[i].textContent || '').trim().toLowerCase() === String(value).toLowerCase()) {
        if (selectedState(btns[i]) === 'selected') return Promise.resolve({ label: 'Personalize', ok: true, changed: false, value: value });
        try { btns[i].click(); } catch (e) {}
        return Promise.resolve({ label: 'Personalize', ok: true, changed: true, value: value });
      }
    }
    if (btns.length === 1) {
      var pressed = btns[0].getAttribute('aria-pressed');
      if (pressed === 'true' || pressed === 'false') {
        if ((pressed === 'true') !== /^on$/i.test(value)) { try { btns[0].click(); } catch (e) {} }
        return sleep(120).then(function () { return { label: 'Personalize', ok: true, via: 'aria-pressed toggle', value: value, before: pressed }; });
      }
      return Promise.resolve({ label: 'Personalize', ok: false, warn: true, reason: 'single button without aria-pressed; leaving as-is', target: value, options: btns.map(function (b) { return (b.textContent || '').trim(); }) });
    }
    return Promise.resolve({ label: 'Personalize', ok: false, reason: 'option not found', target: value, options: btns.map(function (b) { return (b.textContent || '').trim(); }) });
  }
  function applyMoreOptions(o) {
    var jobs = [];
    if (o.vocalGender && !/^none$/i.test(o.vocalGender)) jobs.push(function () { return Promise.resolve(clickOption('Vocal Gender', o.vocalGender)); });
    if (o.duration && !/^auto$/i.test(o.duration)) jobs.push(function () { return Promise.resolve(clickOption('Duration', o.duration)); });
    if (o.maxMode) jobs.push(function () { return Promise.resolve(clickOption('Max Mode', o.maxMode)); });
    if (o.personalize) jobs.push(function () { return setPersonalize(o.personalize); });
    if (typeof o.weirdness === 'number' && !isNaN(o.weirdness)) jobs.push(function () { return setNumericSlider('Weirdness', o.weirdness); });
    if (typeof o.styleInfluence === 'number' && !isNaN(o.styleInfluence)) jobs.push(function () { return setNumericSlider('Style Influence', o.styleInfluence); });
    if (o.variety) jobs.push(function () { return setVariety(o.variety); });
    var res = [];
    return jobs.reduce(function (p, job) {
      return p.then(function () { return job(); }).then(function (r) { res.push(r); });
    }, Promise.resolve()).then(function () { return res; });
  }

  // ---- model detection (read-only) ----

  function selectedState(el) {
    var ds = el.getAttribute && el.getAttribute('data-selected');
    if (ds === 'true') return 'selected';
    if (ds === 'false') return 'off';
    var st = el.getAttribute && el.getAttribute('data-state');
    if (st === 'on' || st === 'active') return 'selected';
    if (st === 'off') return 'off';
    if (el.getAttribute && el.getAttribute('aria-checked') === 'true') return 'selected';
    if (el.getAttribute && el.getAttribute('aria-pressed') === 'true') return 'selected';
    if (el.getAttribute && el.getAttribute('aria-selected') === 'true') return 'selected';
    var cls = ' ' + (el.className || '') + ' ';
    if (cls.indexOf(' active ') >= 0 || cls.indexOf(' selected ') >= 0) return 'selected';
    return 'unknown';
  }

  function findModel() {
    var out = { selected: null, options: [] };
    var els = document.querySelectorAll('button, [role="tab"], [role="radio"], [role="option"], [data-selected]');
    for (var i = 0; i < els.length; i++) {
      var t = (els[i].textContent || '').trim();
      if (/^v6(-mini|-wild)?$/i.test(t) || /^v6/i.test(t)) {
        if (out.options.indexOf(t) < 0) out.options.push(t);
        if (selectedState(els[i]) === 'selected' && !out.selected) out.selected = t;
      }
    }
    if (!out.selected && out.options.length) out.selected = out.options[0];
    return out;
  }

  // ---- parser block ----

  function section(text, tag) {
    var lines = text.split(/\r?\n/);
    var idx = -1;
    for (var i = 0; i < lines.length; i++) { if (lines[i].trim() === tag) { idx = i; break; } }
    if (idx < 0) return null;
    var j = idx + 1;
    if (j >= lines.length || lines[j].trim() !== '') return null;
    j++;
    var out = [];
    while (j < lines.length && !KEY_TAG_RE.test(lines[j].trim())) { out.push(lines[j]); j++; }
    while (out.length && out[out.length - 1].trim() === '') out.pop();
    return out.join('\n');
  }

  function sectionLoose(text, tag) {
    var lines = text.split(/\r?\n/);
    var idx = -1;
    for (var i = 0; i < lines.length; i++) { if (lines[i].trim() === tag) { idx = i; break; } }
    if (idx < 0) return null;
    var j = idx + 1;
    while (j < lines.length && lines[j].trim() === '') j++;
    if (j >= lines.length || KEY_TAG_RE.test(lines[j].trim())) return null;
    var out = [];
    while (j < lines.length && !KEY_TAG_RE.test(lines[j].trim())) { out.push(lines[j]); j++; }
    while (out.length && out[out.length - 1].trim() === '') out.pop();
    return out.length ? out.join('\n') : null;
  }

  function foundTags(text) {
    var tags = [];
    var lines = text.split(/\r?\n/);
    for (var i = 0; i < lines.length; i++) {
      var t = lines[i].trim();
      if (KEY_TAG_RE.test(t) && tags.indexOf(t) < 0) tags.push(t);
    }
    return tags;
  }

  function parseExclude(moreOptions) {
    if (moreOptions == null) return { found: false, value: '' };
    var lines = moreOptions.split(/\r?\n/);
    for (var i = 0; i < lines.length; i++) {
      var m = lines[i].match(/^\s*Exclude\s*:\s*(.*)$/i);
      if (m) return { found: true, value: m[1].trim() };
    }
    var g = moreOptions.match(/Exclude\s*:\s*([^\r\n]*)/i);
    if (g) {
      console.log('SunoFill HEALED: Exclude recovered from a merged 7-field line — re-split the source block (Personalize value must end its own line, Exclude opens the next)');
      return { found: true, value: g[1].trim() };
    }
    return { found: false, value: '' };
  }

  function payloadSlice(text) {
    var lines = text.split(/\r?\n/), start = -1, end = lines.length;
    for (var i = 0; i < lines.length; i++) {
      var tag = lines[i].trim();
      if (start < 0 && tag === 'TRACK:->') start = i;
      else if (start >= 0 && tag === 'INFO:->') { end = i; break; }
    }
    return start >= 0 ? lines.slice(start, end).join('\n') : text;
  }

  // Read canonical keys only inside INFO. Labeled values are opaque; punctuation
  // inside prose cannot introduce extra keys. Retain duplicates for ambiguity checks.
  function infoValues(text, key) {
    var info = sectionLoose(text, 'INFO:->'), values = [];
    if (info == null) return values;
    info.split(/\r?\n/).forEach(function (line) {
      line = line.trim();
      var labeled = line.match(/^(.+?)\s+\(([A-Za-z][A-Za-z0-9_]*)\):\s*(.*)$/);
      if (labeled) {
        if (labeled[2].toLowerCase() === key.toLowerCase()) values.push(labeled[3]);
        return;
      }
      line.split(/\s*[;|]\s*(?=[A-Za-z][A-Za-z0-9_]*\s*:)/).forEach(function (part) {
        var plain = part.match(/^([A-Za-z][A-Za-z0-9_]*)\s*:\s*(.*)$/);
        if (plain && plain[1].toLowerCase() === key.toLowerCase()) values.push(plain[2]);
      });
    });
    return values;
  }

  function parseBlockModel(text) {
    var values = infoValues(text, 'model');
    return values.length === 1 && /^v6(?:-wild|-mini)?$/i.test(values[0]) ? values[0].toLowerCase() : null;
  }

  // Read the full INFO tail before slicing. Writer/time remain report-only.
  function parseGen(text) {
    var out = { found: false, model: null, time: null };
    if (!text) return out;
    var models = infoValues(text, 'gen_model'), times = infoValues(text, 'gen_time');
    if (models.length === 1 && models[0]) out.model = models[0];
    if (times.length === 1 && times[0]) out.time = times[0];
    out.found = out.model != null || out.time != null;
    return out;
  }

  // ---- text writing ----

  function escHtml(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  // Replace (not append) in a contenteditable: focus + select all its contents.
  function selectAllEditable(el) {
    try {
      el.focus();
      var sel = window.getSelection();
      var range = document.createRange();
      range.selectNodeContents(el);
      sel.removeAllRanges();
      sel.addRange(range);
    } catch (e) {}
  }

  // Lexical applies edits asynchronously: dispatch ONE synthetic event, WAIT, verify, and only then
  // try the next method. Firing the next attempt without waiting is what produced the double insert.
  function richState(el, text) {
    var lt = el.innerText || el.textContent || '';
    var want = text.replace(/\s+/g, '').length;
    var got = lt.replace(/\s+/g, '').length;
    var lines = text.split('\n').map(function (l) { return l.replace(/\s+/g, ''); }).filter(function (l) { return l !== ''; });
    var head = lines.length ? lines[0].slice(0, 20) : '';
    var tail = lines.length ? lines[lines.length - 1].slice(-20) : '';
    var flat = lt.replace(/\s+/g, '');
    return { got: got, want: want, ok: (head === '' || flat.indexOf(head) >= 0) && (tail === '' || flat.indexOf(tail) >= 0) && got >= want * 0.9 && got <= want * 1.15 };
  }
  function dispatchBeforeInput(el, text) {
    var evt = null;
    try { evt = new InputEvent('beforeinput', { inputType: 'insertText', data: text, bubbles: true, cancelable: true }); } catch (e) { return false; }
    if (!evt) return false;
    selectAllEditable(el);
    try { el.dispatchEvent(evt); } catch (e) { return false; }
    return true;
  }
  function dispatchPaste(el, text) {
    var dt = null;
    try { dt = new DataTransfer(); } catch (e) { return false; }
    if (!dt) return false;
    try { dt.setData('text/plain', text); } catch (e) { return false; }
    var evt = null;
    try { evt = new ClipboardEvent('paste', { bubbles: true, cancelable: true, clipboardData: dt }); } catch (e) { return false; }
    if (!evt || !evt.clipboardData) return false;
    selectAllEditable(el);
    try { el.dispatchEvent(evt); } catch (e) { return false; }
    return true;
  }
  function dispatchInsertHtml(el, text) {
    selectAllEditable(el);
    try {
      if (typeof document.execCommand !== 'function') return false;
      var html = text.split('\n').map(function (ln) { return ln === '' ? '<div><br></div>' : '<div>' + escHtml(ln) + '</div>'; }).join('');
      return document.execCommand('insertHTML', false, html);
    } catch (e) { return false; }
  }
  function fillContentEditable(el, text, name) {
    return new Promise(function (resolve) {
      if (!el) { console.log('SunoFill skip (field not found): ' + name); resolve('skip'); return; }
      if (el instanceof HTMLTextAreaElement || el instanceof HTMLInputElement) {
        setNative(el, text, name);
        resolve('native');
        return;
      }
      var methods = [
        { method: 'beforeinput', run: function () { return dispatchBeforeInput(el, text); } },
        { method: 'paste', run: function () { return dispatchPaste(el, text); } },
        { method: 'insertHTML', run: function () { return dispatchInsertHtml(el, text); } }
      ];
      var i = 0;
      function attempt() {
        if (i >= methods.length) {
          el.textContent = text;
          el.dispatchEvent(new Event('input', { bubbles: true }));
          FILL_LOG.push({ name: name, method: 'textContent', chars: text.length });
          console.log('SunoFill filled (textContent — DOM only, may not stick): ' + name + ' (' + text.length + ' chars)');
          resolve('textContent');
          return;
        }
        var m = methods[i++];
        var fired = false;
        try { fired = m.run(); } catch (e) { fired = false; }
        window.setTimeout(function () {
          var st = richState(el, text);
          if (fired && st.ok) {
            FILL_LOG.push({ name: name, method: m.method, chars: text.length });
            console.log('SunoFill filled (' + m.method + ', settled): ' + name + ' (' + text.length + ' chars, got ' + st.got + ')');
            resolve(m.method);
            return;
          }
          console.log('SunoFill: ' + m.method + ' did not settle (got ' + st.got + '/' + st.want + '), trying next');
          attempt();
        }, RICH_SETTLE_MS);
      }
      attempt();
    });
  }

  function setNative(el, text, name) {
    if (!el) { console.log('SunoFill skip (field not found): ' + name); return false; }
    var proto = (el instanceof HTMLTextAreaElement) ? window.HTMLTextAreaElement.prototype : window.HTMLInputElement.prototype;
    var desc = Object.getOwnPropertyDescriptor(proto, 'value');
    if (!desc || typeof desc.set !== 'function') { console.error('SunoFill skip (no native setter): ' + name); return false; }
    desc.set.call(el, text);
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
    FILL_LOG.push({ name: name, method: 'native', chars: text.length });
    console.log('SunoFill filled: ' + name + ' (' + text.length + ' chars)');
    return true;
  }

  // ---- fill ----

  function runFill() {
    if (!onCreatePage()) { console.error('SunoFill: not on suno.com/create — abort, DOM untouched'); alert('SunoFill: open suno.com/create'); return; }
    if (!navigator.clipboard || typeof navigator.clipboard.readText !== 'function') { console.error('SunoFill: clipboard.readText unavailable — abort'); alert('SunoFill: clipboard access unavailable'); return; }

    ensureAdvanced().then(function (adv) {
      console.log('SunoFill: Advanced tab active = ' + adv);
      ensureMoreOptions().then(function (mo) {
      if (mo.found && mo.wasCollapsed) console.log('SunoFill: More Options was collapsed — expanded it (editor/sliders now have layout): expanded=' + mo.expanded);
      else console.log('SunoFill: More Options ' + (mo.found ? (mo.expanded ? 'already open' : 'toggle found but still collapsed') : 'toggle not found'));
      var f = locateFields();
      if (!f.lyrics) { console.error('SunoFill: Lyrics field not found — abort, DOM untouched'); alert('SunoFill: no Lyrics field — open Advanced and press again'); return; }
      navigator.clipboard.readText().then(function (clip) {
        FILL_LOG.length = 0;
        clip = clip.split(/\r?\n/).filter(function (l) { return !/^```/.test(l.trim()); }).join('\n');
        var blockModel = parseBlockModel(clip);
        var gen = parseGen(clip);
        if (gen.found) console.log('SunoFill gen stamp (read-only, tail): ' + (gen.model || '?') + ' · ' + (gen.time || '?'));
        else console.log('SunoFill gen stamp: none in INFO (tail)');
        clip = payloadSlice(clip);
        console.log('SunoFill: standalone markers delimit [TRACK:-> .. INFO:->), tail ignored');
        var lyrics = section(clip, 'LYRICS:->');
        var styles = section(clip, 'STYLES:->');
        var track = section(clip, 'TRACK:->');
        var more = section(clip, 'MOREOPTIONS:->');
        if (lyrics == null || styles == null || track == null || more == null) {
          if (lyrics == null) lyrics = sectionLoose(clip, 'LYRICS:->');
          if (styles == null) styles = sectionLoose(clip, 'STYLES:->');
          if (track == null) track = sectionLoose(clip, 'TRACK:->');
          if (more == null) more = sectionLoose(clip, 'MOREOPTIONS:->');
        }
        if (lyrics == null || styles == null || track == null || more == null) {
          var have = foundTags(clip);
          var need = ['TRACK:->', 'LYRICS:->', 'STYLES:->', 'MOREOPTIONS:->'];
          var missing = need.filter(function (t) { return have.indexOf(t) < 0; });
          console.error('SunoFill: clipboard is not a parser block. found: [' + have.join(', ') + '] missing: [' + missing.join(', ') + '] — abort, DOM untouched');
          alert('SunoFill: no parser block in clipboard (missing: ' + missing.join(', ') + '). Copy the whole block from TRACK:-> to the end.');
          return;
        }

        var uiModel = findModel();
        console.log('SunoFill model: block=' + (blockModel || '?') + ' ui=' + (uiModel.selected || '?'));
        if (blockModel && uiModel.selected && norm(blockModel) !== norm(uiModel.selected)) {
          console.error('SunoFill MODEL MISMATCH: the block says "' + blockModel + '" but the UI model chip shows "' + uiModel.selected + '" — switch the model in Suno or re-run the skill; caps/limits follow the selected model');
        }
        var free = !!(blockModel && FREE_MODEL_RE.test(blockModel)) || !!(uiModel.selected && FREE_MODEL_RE.test(uiModel.selected));
        if (free) console.log('SunoFill FREE-TIER: v6-mini/free — non-commercial, public by default, no stems/Studio; the seven More Options controls from the block are still applied, only Pro-only features are left untouched.');
        if (free && styles.length > FREE_STYLE_CAP) {
          styles = styles.slice(0, FREE_STYLE_CAP).replace(/,[^,]*$/, '');
          console.log('SunoFill FREE-TIER: trimmed Styles to ' + styles.length + ' chars (cap ' + FREE_STYLE_CAP + ')');
        }

        var ex = parseExclude(more);
        var exText = '';
        if (!ex.found) console.log('SunoFill ignored: no Exclude: line in MOREOPTIONS, Exclude field left as-is');
        else if (/^none$/i.test(ex.value) || ex.value === '') console.log('SunoFill: Exclude: none → Exclude field cleared (nothing typed)');
        else exText = ex.value;

        var moOpts = parseMoreOptions(more);
        console.log('SunoFill More Options target: ' + JSON.stringify(moOpts));
        var before = { counters: counterSnapshot(), fields: fieldLengths(f), controls: CONTROL_LABELS.map(controlRow) };
        fillContentEditable(f.lyrics, lyrics, 'Lyrics').then(function () {
        setNative(f.styles, styles, 'Styles');
        var titleText = track.trim();
        if (!f.titles.length) console.log('SunoFill skip (field not found): Title');
        else {
          f.titles.forEach(function (el, i) { setNative(el, titleText, 'Title[' + i + ']'); });
          var titleVals = f.titles.map(function (el) { return el.value; });
          if (titleVals.every(function (v) { return v === titleText; })) console.log('SunoFill verified: all ' + titleVals.length + ' Title field(s) equal');
          else console.error('SunoFill MISMATCH: Title fields differ after fill — check visually before Create: [' + titleVals.join(' | ') + ']');
        }
        if (ex.found && exText !== '') setNative(f.exclude, exText, 'Exclude');
        else if (ex.found && f.exclude) setNative(f.exclude, '', 'Exclude (cleared)');
        else if (!ex.found) console.log('SunoFill skip: Exclude field untouched (no Exclude: line)');
        applyMoreOptions(moOpts).then(function (moApplied) {
        moApplied.forEach(function (r) { console.log('SunoFill control ' + ((r.ok || r.warn) ? 'OK' : 'FAIL') + ': ' + JSON.stringify(r)); });
        var afterImmediate = { counters: counterSnapshot(), fields: fieldLengths(f), controls: CONTROL_LABELS.map(controlRow) };
        window.setTimeout(function () {
          var lt = f.lyrics ? (f.lyrics.value != null ? f.lyrics.value : (f.lyrics.innerText || f.lyrics.textContent || '')) : '';
          var probe = lyrics.slice(0, 24);
          var firstAt = probe ? lt.indexOf(probe) : -1;
          emitReport({
            userscript: VERSION,
            kind: 'fill',
            url: location.href,
            advanced: adv,
            moreOptions: mo,
            note: 'after/counters are sampled ' + SETTLE_MS + 'ms after the write (Lexical + UI counters settle asynchronously). Compare after.fields.lyrics vs expected.lyricsChars; lyricsHasDouble=true means the editor appended instead of replacing.',
            exactSelectors: f.exact,
            model: { block: blockModel, ui: uiModel.selected },
            gen: gen,
            paths: FILL_LOG,
            expected: { lyricsChars: lyrics.length, stylesChars: styles.length, title: titleText, exclude: exText },
            moreOptionsTarget: moOpts,
            moreOptionsApplied: moApplied,
            controls: CONTROL_LABELS.map(controlRow),
            before: before,
            afterImmediate: afterImmediate,
            after: {
              counters: counterSnapshot(),
              fields: fieldLengths(f),
              lyricsHead: lt.slice(0, 40),
              lyricsTail: lt.slice(-40),
              lyricsHasDouble: firstAt >= 0 && lt.indexOf(probe, firstAt + probe.length) >= 0
            }
          }, 'fill');
          console.log('SunoFill done: check the text with your eyes and confirm the More Options controls, then press Create yourself. Create was NOT clicked.');
        }, SETTLE_MS);
        });
        });
      }, function (err) { console.error('SunoFill: clipboard read failed — abort', err); alert('SunoFill: could not read the clipboard'); });
      });
    });
  }

  // ---- diagnostics (read-only; one copyable report) ----

  function fieldLen(el) {
    if (!el) return null;
    return (el.value != null ? el.value.length : (el.innerText || el.textContent || '').length);
  }
  function fieldLengths(f) {
    return {
      lyrics: fieldLen(f.lyrics),
      styles: fieldLen(f.styles),
      titles: (f.titles || []).map(fieldLen),
      exclude: fieldLen(f.exclude)
    };
  }
  function counterSnapshot() {
    var out = [];
    var cand = document.querySelectorAll('span, div, p, small, output');
    for (var q = 0; q < cand.length && out.length < 20; q++) {
      if (cand[q].children.length !== 0) continue;
      var ct = (cand[q].textContent || '').trim();
      if (/^\d{1,5}\s*\/\s*\d{1,5}$/.test(ct)) out.push(ct.replace(/\s+/g, ''));
    }
    return out;
  }
  function emitReport(obj, tag) {
    console.log('SunoFill ' + (tag || 'report') + ' v' + VERSION + ' — copy everything between the BEGIN/END lines in ONE paste:');
    console.log('----- BEGIN SunoFill ' + (tag || 'report') + ' -----');
    console.log(JSON.stringify(obj, null, 2));
    console.log('----- END SunoFill ' + (tag || 'report') + ' -----');
  }

  function buildDiag() {
    var f = locateFields();
    function field(name, el) {
      if (!el) return { found: false };
      var o = { found: true, tag: el.tagName, label: labelOf(el), length: (el.value != null ? el.value.length : (el.innerText || '').length) };
      try { if ('maxLength' in el) o.maxLength = el.maxLength; } catch (e) {}
      return o;
    }
    var sliders = [];
    var slEls = document.querySelectorAll('[role="slider"], input[type="range"]');
    for (var i = 0; i < slEls.length; i++) {
      var s = slEls[i];
      sliders.push({
        label: s.getAttribute('aria-label'),
        min: s.getAttribute('aria-valuemin'), max: s.getAttribute('aria-valuemax'),
        now: s.getAttribute('aria-valuenow'), text: s.getAttribute('aria-valuetext'),
        disabled: s.getAttribute('aria-disabled'), ticks: s.querySelectorAll('[data-tick-value]').length,
        visible: s.offsetParent !== null,
        html: s.outerHTML.slice(0, 220)
      });
    }
    var tabs = [];
    var tabEls = document.querySelectorAll('[role="tab"]');
    for (var t = 0; t < tabEls.length; t++) tabs.push({ text: (tabEls[t].textContent || '').trim(), state: selectedState(tabEls[t]) });
    var marked = [];
    var markEls = document.querySelectorAll('[data-selected],[data-state],[aria-checked],[aria-pressed]');
    for (var m = 0; m < markEls.length && marked.length < 60; m++) {
      var txt = (markEls[m].textContent || '').trim();
      if (txt) marked.push({ text: txt.slice(0, 32), state: selectedState(markEls[m]) });
    }
    var counters = counterSnapshot();
    var moProbe = [];
    var moEls = document.querySelectorAll('button, [role="button"], summary, [aria-expanded]');
    for (var mp = 0; mp < moEls.length && moProbe.length < 8; mp++) {
      var mt = (moEls[mp].textContent || '').replace(/\s+/g, ' ').trim();
      if (mt.length < 60 && /more\s*option/i.test(mt)) moProbe.push({ tag: moEls[mp].tagName, role: moEls[mp].getAttribute('role'), ariaExpanded: moEls[mp].getAttribute('aria-expanded'), visible: moEls[mp].offsetParent !== null, text: mt });
    }
    return {
      userscript: VERSION,
      url: location.href,
      onCreatePage: onCreatePage(),
      activeTab: activeTab(),
      advancedActive: isAdvancedActive(),
      exactSelectors: f.exact,
      fields: {
        lyrics: field('lyrics', f.lyrics),
        styles: field('styles', f.styles),
        titles: (f.titles || []).map(function (el) { return field('title', el); }),
        exclude: field('exclude', f.exclude)
      },
      sliders: sliders,
      tabs: tabs,
      model: findModel(),
      markedButtons: marked,
      moreOptionsToggle: !!moreOptionsToggle(),
      slidersVisible: slidersVisible(),
      moreOptionsProbe: moProbe,
      controlRows: CONTROL_LABELS.map(controlRow),
      textCounters: counters,
      counts: { buttons: document.querySelectorAll('button').length, textareas: document.querySelectorAll('textarea').length, contenteditables: findEditables().length }
    };
  }

  function diagReport() {
    emitReport(buildDiag(), 'diag');
    console.log('SunoFill diag done: nothing was written, nothing clicked.');
  }

  if (typeof GM_registerMenuCommand === 'function') {
    GM_registerMenuCommand('Fill: diagnostics (read-only)', function () { diagReport(); });
    GM_registerMenuCommand('Fill: paste from clipboard', function () { runFill(); });
  }

  // Own floating button (not a Suno button). Shown only on /create (SPA-aware).
  // Shifted 50px further left so it does not cover the panel controls.
  var btn = null;
  function syncButton() {
    if (onCreatePage()) {
      if (!btn) {
        btn = document.createElement('button');
        btn.type = 'button';
        btn.textContent = 'Fill';
        btn.title = 'Fill Lyrics/Styles/Title/Exclude and More Options from the clipboard. Forces Advanced. Never clicks Create.';
        btn.style.cssText = 'position:fixed;left:16px;top:50%;transform:translateY(-50%);z-index:2147483647;padding:8px 14px;cursor:pointer;';
        btn.addEventListener('click', function () { runFill(); });
        document.documentElement.appendChild(btn);
      }
      btn.style.display = '';
    } else if (btn) {
      btn.style.display = 'none';
    }
  }
  syncButton();
  window.setInterval(syncButton, 2000);
})();
