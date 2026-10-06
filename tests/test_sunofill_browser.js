// Full userscript on synthetic controls in isolated headless Chromium; no live Suno.
const fs = require('fs');
const path = require('path');
const assert = require('assert');
const root = path.resolve(__dirname, '..');
const temporary = path.join(root, 'work', 'sunofill_browser_tmp');
fs.mkdirSync(temporary, {recursive:true});
for (const name of ['TEMP','TMP','TMPDIR']) process.env[name] = temporary;
const {chromium} = require(process.env.SUNOFILL_NODE_MODULES ?
  path.join(process.env.SUNOFILL_NODE_MODULES, 'playwright') : 'playwright');
const source = fs.readFileSync(path.join(root, 'tools', 'suno-fill.user.js'), 'utf8');
const originalPath = path.join(root, 'work', 'sunofill_originals', 'tools', 'suno-fill.user.js');
const testedSource = process.argv.includes('--original') ? fs.readFileSync(originalPath, 'utf8') : source;
const reportArg = process.argv.indexOf('--report');
const reportPath = reportArg < 0 ? null : path.resolve(root, process.argv[reportArg+1]);
if (reportPath && (!reportPath.startsWith(path.join(root, 'work')+path.sep) || fs.existsSync(reportPath)))
  throw new Error('Choose a new report in work/.');

function pageHTML(rich) {
  const options = (label, values) => '<div class="control"><span>'+label+'</span>'+values.map((value,i)=>
    '<button data-selected="'+(i===0)+'">'+value+'</button>').join('')+'</div>';
  const slider = (label,value,max) => '<div class="control"><span>'+label+'</span><div tabindex="0" role="slider" aria-label="'+label+
    '" aria-valuemin="0" aria-valuemax="'+max+'" aria-valuenow="'+value+'"></div></div>';
  return '<!doctype html><html><body><button role="tab" aria-selected="true">Advanced</button>'+
    '<button aria-expanded="true">More Options</button><button data-selected="true">v6-mini</button>'+
    (rich ? '<div id="lyrics" contenteditable="true" data-lexical-editor="true" style="white-space:pre-wrap">old lyrics</div>' :
      '<textarea id="lyrics" aria-label="Lyrics">old lyrics</textarea>')+
    '<div data-testid="create-form-styles-wrapper"><textarea id="styles">old styles</textarea></div>'+
    '<input id="title1" placeholder="Song Title"><input id="title2" placeholder="Song Title optional">'+
    '<input id="exclude" placeholder="Exclude styles" value="old exclusion">'+
    options('Vocal Gender',['Male','Female'])+options('Duration',['Auto','Custom 2:30'])+
    options('Max Mode',['On','Off'])+options('Personalize',['On','Off'])+
    slider('Weirdness',48,100)+slider('Style Influence',73,100)+slider('Variety',2,4)+
    '<button id="create">Create</button></body></html>';
}
const expected = {
  TRACK: 'Synthetic browser song',
  LYRICS: '[Verse]\nmodel: v6; gen_model: lyric-decoy\nInline INFO:-> stays in the lyrics\nA new road opens 😀',
  STYLES: 'Warm synth pulse\nDry drums, light bass',
  MOREOPTIONS: 'Vocal Gender: Female | Duration: Custom 2:30 | Max Mode: Off | Weirdness: 50% | Style Influence: 75% | Variety: Off | Personalize: Off\nExclude: ambient, trap'
};
const grouped = 'VERSION AND STORAGE\nUnique version ID (ID): abcdef_20261005T123456123456Z\nParent version (parent): bcdefg_20261005T113456123456Z\n\nCOMPOSITION\nComposition summary (summary): Preserve text; model: v6 is prose\n\nGENERATION AND VERIFICATION\nSuno generation model (model): v6-mini\nWriter model (gen_model): synthetic-writer\nPreparation time (gen_time): 1.25 s';
function chunk(info, fields=expected) {
  return ['TRACK','LYRICS','STYLES','MOREOPTIONS'].map(key=>key+':->\n\n'+fields[key]).join('\n\n')+
    '\n\nINFO:->\n\n'+info+'\n\nSTATE:->\n\nmodel: v6-wild; gen_model: state-decoy';
}
async function verifyCase(browser, item) {
  const context = await browser.newContext({serviceWorkers:'block'});
  const requests = [], errors = [], logs = [];
  try {
    const page = await context.newPage();
    await page.route('**/*', route => {
      requests.push(route.request().url());
      return route.request().url() === 'https://suno.com/create?synthetic-sunofill-test' ?
        route.fulfill({contentType:'text/html', body:pageHTML(item.rich)}) : route.abort();
    });
    page.on('pageerror', err=>errors.push(err.message));
    page.on('console', msg=>logs.push(msg.text()));
    await page.goto('https://suno.com/create?synthetic-sunofill-test');
    await page.evaluate(() => {
      window.__menus = {}; window.__reports = []; window.__createClicks = 0; window.__events = [];
      window.__alerts = [];
      window.alert = text=>window.__alerts.push(text);
      window.GM_registerMenuCommand = (name,fn)=>{ window.__menus[name] = fn; };
      Object.defineProperty(navigator, 'clipboard', {configurable:true,
        value:{readText:()=>Promise.resolve(window.__clipboard)}});
      const originalLog = console.log.bind(console);
      console.log = (...args) => {
        if (typeof args[0] === 'string' && args[0].startsWith('{')) {
          try { const report = JSON.parse(args[0]); if (report.kind === 'fill') window.__reports.push(report); } catch (_) {}
        }
        originalLog(...args);
      };
      document.getElementById('create').addEventListener('click',()=>window.__createClicks++);
      for (const el of document.querySelectorAll('input,textarea')) {
        el.addEventListener('input',()=>window.__events.push({id:el.id,kind:'input',value:el.value}));
        el.addEventListener('change',()=>window.__events.push({id:el.id,kind:'change',value:el.value}));
      }
      for (const button of document.querySelectorAll('.control button')) button.addEventListener('click',()=>{
        for (const sibling of button.parentElement.querySelectorAll('button')) sibling.setAttribute('data-selected','false');
        button.setAttribute('data-selected','true');
      });
      for (const slider of document.querySelectorAll('[role="slider"]')) slider.addEventListener('keydown',event=>{
        const delta = event.key === 'ArrowRight' ? 1 : event.key === 'ArrowLeft' ? -1 : 0;
        slider.setAttribute('aria-valuenow',String(Number(slider.getAttribute('aria-valuenow'))+delta));
      });
      const lyrics = document.getElementById('lyrics');
      if (!lyrics.isContentEditable) {
        // Simulate an already edited native textarea, where textContent no longer
        // replaces the live value. Filling must replace its actual value.
        lyrics.value = 'unsaved initial edits';
        lyrics.setSelectionRange(lyrics.value.length,lyrics.value.length);
      }
      if (lyrics.isContentEditable) lyrics.addEventListener('beforeinput',event=>{
        event.preventDefault(); lyrics.textContent = event.data;
        lyrics.dispatchEvent(new Event('input',{bubbles:true}));
      });
    });
    await page.addScriptTag({content:testedSource});
    const fills = item.repeat ? 2 : 1;
    for (let fill=1; fill<=fills; fill++) {
      await page.evaluate(text=>{window.__clipboard=text;window.__menus['Fill: paste from clipboard']();}, item.text);
      await page.waitForFunction(count=>window.__reports.length===count || window.__alerts.length>0, fill, {timeout:15000});
      const alerts = await page.evaluate(()=>window.__alerts);
      assert.deepStrictEqual(alerts,[],item.name+': fill must not abort');
      const observed = await page.evaluate(()=>({
        report:window.__reports.at(-1), alerts:window.__alerts, createClicks:window.__createClicks,
        lyrics:document.getElementById('lyrics').isContentEditable ? document.getElementById('lyrics').textContent : document.getElementById('lyrics').value,
        styles:document.getElementById('styles').value,
        titles:[document.getElementById('title1').value,document.getElementById('title2').value],
        exclude:document.getElementById('exclude').value, events:window.__events,
        controls:Array.from(document.querySelectorAll('.control')).map(row=>({label:row.querySelector('span').textContent,
          selected:row.querySelector('button[data-selected="true"]')?.textContent,
          slider:row.querySelector('[role="slider"]')?.getAttribute('aria-valuenow')}))
      }));
      assert.strictEqual(observed.lyrics,item.fields.LYRICS,item.name+': exact Lyrics replacement');
      assert.strictEqual(observed.styles,item.fields.STYLES,item.name+': exact Styles');
      assert.deepStrictEqual(observed.titles,[item.fields.TRACK,item.fields.TRACK]);
      assert.strictEqual(observed.exclude,item.exclude);
      assert.strictEqual(observed.report.after.fields.lyrics,item.fields.LYRICS.length);
      assert.strictEqual(observed.report.after.fields.styles,item.fields.STYLES.length);
      assert.strictEqual(observed.report.after.lyricsHead,item.fields.LYRICS.slice(0,40));
      assert.strictEqual(observed.report.after.lyricsTail,item.fields.LYRICS.slice(-40));
      assert.strictEqual(observed.report.after.lyricsHasDouble,false);
      assert.strictEqual(observed.report.model.block,'v6-mini','read grouped INFO model, ignore lyric/state decoys');
      assert.deepStrictEqual(observed.report.gen,{found:true,model:'synthetic-writer',time:'1.25 s'});
      assert.strictEqual(observed.createClicks,0);
      assert.deepStrictEqual(observed.alerts,[]);
      assert.strictEqual(observed.controls.find(c=>c.label==='Vocal Gender').selected,'Female');
      assert.strictEqual(observed.controls.find(c=>c.label==='Max Mode').selected,'Off');
      assert.strictEqual(observed.controls.find(c=>c.label==='Personalize').selected,'Off');
      assert.strictEqual(observed.controls.find(c=>c.label==='Weirdness').slider,'50');
      assert.strictEqual(observed.controls.find(c=>c.label==='Style Influence').slider,'75');
      assert.strictEqual(observed.controls.find(c=>c.label==='Variety').slider,'0');
      assert.ok(observed.report.moreOptionsApplied.every(control=>control.ok));
      for (const id of ['styles','title1','title2','exclude'])
        assert.ok(observed.events.some(event=>event.id===id && event.kind==='input'));
      if (!item.rich) for (const kind of ['input','change'])
        assert.ok(observed.events.some(event=>event.id==='lyrics' && event.kind===kind));
    }
    assert.deepStrictEqual(errors,[]);
    return {name:item.name,ok:true,fills,network_requests_intercepted:requests.length,
      lyrics_editor:item.rich?'contenteditable':'textarea',create_clicks:0};
  } finally { await context.close(); }
}
(async()=>{
  const browser = await chromium.launch({headless:true, executablePath:process.env.SUNOFILL_BROWSER_PATH,
    ...(process.env.SUNOFILL_BROWSER_PATH ? {} : {channel:'chrome'})});
  const results = [];
  try {
    const none = {...expected, MOREOPTIONS:expected.MOREOPTIONS.replace('ambient, trap','none')};
    const simple = {...expected, LYRICS:'[Verse]\nA new road opens'};
    const cases = [
      {name:'grouped-native-simple',rich:false,text:chunk(grouped,simple),fields:simple,exclude:'ambient, trap'},
      {name:'grouped-rich-metadata',rich:true,text:chunk(grouped,simple),fields:simple,exclude:'ambient, trap'},
      {name:'grouped-native',rich:false,text:chunk(grouped),fields:expected,exclude:'ambient, trap'},
      {name:'grouped-rich-repeated',rich:true,repeat:true,text:chunk(grouped),fields:expected,exclude:'ambient, trap'},
      {name:'old-grouped-dual-id',rich:true,text:chunk(grouped.replace('Parent version (parent):',
        'Version ID (version): abcdef_20261005T123456123456Z\nParent version (parent):')),fields:expected,exclude:'ambient, trap'},
      {name:'legacy-fences-crlf-clear-exclude',rich:false,text:'```text\r\n'+chunk(
        'summary: imported; model: v6-mini; gen_model: synthetic-writer; gen_time: 1.25 s',none).replace(/\n/g,'\r\n')+'\r\n```',fields:none,exclude:''}
    ];
    for (const item of cases) {
      try { results.push(await verifyCase(browser,item)); }
      catch (err) { results.push({name:item.name,ok:false,error:err.message}); }
    }
    const report = {ok:results.every(item=>item.ok),actual_userscript:true,original_script:process.argv.includes('--original'),
      browser:await browser.version(),headless:true,synthetic_dom:true,live_suno:false,tampermonkey_extension:false,
      user_browser_touched:false,results};
    if (reportPath) fs.writeFileSync(reportPath,JSON.stringify(report,null,2)+'\n',{encoding:'utf8',flag:'wx'});
    console.log(JSON.stringify(report,null,2));
    process.exitCode = report.ok ? 0 : 1;
  } finally { await browser.close(); }
})().catch(error=>{console.error(error);process.exitCode=1;});
