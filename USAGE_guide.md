# Using Vave Suno Composer

## Applying instructions in a chat

The skill needs accessible SKILL.md plus its relevant libraries, not an isolated entrypoint. Metadata declares name: vsuno-composer, matching the native folder name. Use [START_HERE_tpl.md](START_HERE_tpl.md) and [CONNECTION_flow.md](references/CONNECTION_flow.md).

If the environment actually reads local files, provide the complete vsuno-composer folder and a brief. If it supports only attachments, provide accessible task resources or the full TXT instructions. A written path or visible project name does not prove file access. Full TXT uses standalone FILE boundary markers for embedded addresses. These aid navigation, not selective retrieval: a full pasted/injected document consumes context as delivered. Use CONNECTION_flow's resource-selection guide when assembling a smaller task handoff; no token savings have been measured.

Prepare text exports locally, without starting a model. These commands work in Windows PowerShell 5.1; replace the illustrative path with the folder containing SKILL.md and vsuno.cmd:

```powershell
Set-Location 'C:\path\vsuno-composer'
.\vsuno.cmd prompt --starter --output '.\work\START_CHATGPT.txt'
.\vsuno.cmd prompt --full --output '.\work\Vave_Suno_Composer_full.txt'
```

Output folders are created as needed. Existing files are never overwritten. --output writes UTF-8 directly without shell-pipeline recoding. Default prompt outputs SKILL.md only; --starter outputs the short message; --full includes starter, SKILL, AGENTS, guide and all references with file addresses. The text handoff contains no personal archive or executable helpers; use helper commands only where scripts/interpreter are genuinely present.

ZIP creation is a separate optional action requiring an explicit user command and final checks. Save directly in the vsuno-composer root, never its parent, work or a temporary folder:

```powershell
.\vsuno.cmd bundle --output '.\Vave_Suno_Composer_ChatGPT.zip'
```

The archive's folder is vsuno-composer; packaging excludes personal/prompts/work/caches/unrelated root files. This documentation does not authorize creating an archive now.

File-based application does not register a native skill or plugin. If an application already exposes vsuno-composer, use its supported selection/invocation: $vsuno-composer in Codex, /vsuno-composer in Claude Code, or the host's actual activation method. CONNECTION_flow has the sourced host matrix. Codex discovery requires a supported skill directory or supported link with the complete resources. Installation/registration is separate; moving only SKILL.md can break its references.

Check actual reading, network, counting, writing and old-ID access in the current environment. Model names do not establish capabilities. Without persistent storage use supplied chunks/context; never promise cross-chat memory. A cloud workspace export is not a write to the user's Windows prompts folder.

An instruction-only chat can still return a complete five-field result. Omit unavailable IDs/counts, set identity/counting: unavailable as relevant and storage: context-only, optionally using context_ref: C1. Explain that unmeasured field caps remain unverified. Never put C1 in ID/version or claim a saved file. Local archive later assigns actual identity/counts and verified statuses under [PARSER_spec.md](references/PARSER_spec.md).

## First-request size and detail

[INTAKE_flow.md](references/INTAKE_flow.md) resolves Lyrics and Styles independently: three size ceilings plus an Own option, and four detail levels plus an Own option. Explicit compact/medium instructions let the LLM select suitable preferences for the covered fields; a one-field cue leaves only the other field's unresolved questions. Explicit delegation resolves missing choices autonomously; full-freedom test runs sample permitted profiles. Without a cue/delegation, missing field preferences and composition essentials are required questions in one message. Local edits/views inherit known choices rather than repeating intake.

Automatic new-composition Weirdness/Variety/Style Influence and Exclude targets follow Lyrics detail, preserving explicit controls/locks and unchanged revision settings. Maximum Lyrics permits high-risk tag use even if LLM-selected under delegation; maximum Styles alone does not. Exclude consists of meaningful adjacent unwanted styles, with flexible target counts and no random padding. Resolved preferences stay in the current composition/free state without archive migration or extra required chunk fields.

The LLM applies this instruction policy; the CLI does not conduct the questionnaire or generate defaults automatically. Existing check/archive validates syntax/hard caps and reports actual UTF-16 counts. Final authorship must also compare them against the smaller chosen ceilings, preserve words/endings during compression and recount. Passing mechanics does not verify model choice quality or live Suno performance.

Every detail level retains brief main-theme identity and its allowed initial presentation under [MAIN_THEME_lib.md](references/MAIN_THEME_lib.md#default-recurrence-at-every-detail-level) when the user permits a theme. Ordinarily, add at least two later recognizable returns when the user permits recurrence. The LLM selects suitable key sections/transitions; Intro is optional. Basic uses short core descriptions, fuller detail adds development. Genuinely very short forms may have fewer returns without artificial extension; a compact prompt alone is not that exception. Explicit user prohibitions and locks take priority: do not impose a rejected theme or returns the user disallows. Retain compatible placements during compression and review the final map before counting. Instrumental, vocal and rhythmic themes are valid; audio recurrence remains unverified by the parser. Existing words-only/read-only source-preservation boundaries remain.

## Windows console

Work from your verified project root:

```powershell
Set-Location 'C:\path\vsuno-composer'
.\vsuno.cmd --help
.\vsuno.cmd start --dry-run 'Compose instrumental acid house, strict music, compact detail'
.\vsuno.cmd 'Compose instrumental acid house, strict music, compact detail'
```

CMD from this folder accepts vsuno; PowerShell requires .\vsuno.cmd unless a separate PATH setup exists. The launcher uses Python 3.9+ and an existing Codex CLI with its configured model/account. Default/start opens that CLI session, not an arbitrary GPT chat or provider. It can consume normal account allowance; exit through CLI controls. A dry run prints argv without invoking a model.

prompt, check, archive, list, get and text are local helpers. bundle is also local but requires the separate packaging instruction. No helper installs software or changes PATH/settings. Other LLMs use the same accessible English instruction set.

## Checking and selecting versions

Illustrative input paths, not existing user files:

```powershell
.\vsuno.cmd check 'C:\path\chunk.txt'
.\vsuno.cmd archive 'C:\path\chunk.txt' --state 'C:\path\state.json'
.\vsuno.cmd list --query 'song title'
.\vsuno.cmd get 'EXACT_ID_FROM_LIST'
.\vsuno.cmd text 'C:\path\chunk.txt'
.\vsuno.cmd text 'C:\path\chunk.txt' --plain
.\vsuno.cmd text 'C:\path\chunk.txt' --highlight --output 'C:\path\lyrics.html'
```

check returns 0 for its mechanical conditions, 1 for violations, 2 for input/argument failures. state may supply reference_identities and banned_words; errors never print those names/words. Semantic English, originality, rhyme, exclusions and actual musical performance remain separate checks.

archive creates an immutable version, groups INFO by category with explanatory English labels, adds actual ID/parent/storage/counts and saves the exact final chunk. Export get's finalized chunk rather than the pre-archive file. Use --parent ID for revisions; same-title candidates require exact selection. IDs are six random Latin letters plus UTC timestamp; the single INFO.ID, JSON.id and filename ID agree. New chunks omit the redundant Version ID (version) row and retain Parent version (parent). New prompt copies are prompts/<sanitized-title>_<ID>.txt. Old duplicate ID/version metadata, UUID versions and one-line INFO stay readable without migration. The new INFO layout is defined in [CHUNK_tpl.md](references/CHUNK_tpl.md); custom metadata remains available while the first four fields are preserved.

Parent state is inherited with explicit keys overriding corresponding decisions. Field locks persist until the user changes them. Invalid list cards are skipped with a notice; get reports invalid records without repair/deletion. Full contract: [PERSONAL_spec.md](references/PERSONAL_spec.md).

Reads check the chunk itself, selected identity, title/parent metadata and available state constraints; old UUID cards with absent ID/version or version only remain supported. Invalid record diagnostics do not echo its private title/words. Reading does not rewrite or migrate records.

Resource root and data root are independent only when explicitly requested. By default personal/ and prompts/ stay in this project. archive/list/get accept --data-root for an authorized writable location; parent lookup uses that same root, with no fallback. Illustrative commands after destination authorization:

```powershell
.\vsuno.cmd archive 'C:\path\chunk.txt' --data-root 'C:\authorized\music-data'
.\vsuno.cmd list --data-root 'C:\authorized\music-data'
.\vsuno.cmd get 'EXACT_ID_FROM_LIST' --json --data-root 'C:\authorized\music-data'
```

This does not relocate existing records or install the skill. On session-only cloud storage, keep persistence limitations explicit. An arbitrary packaging tool must also exclude the separately located personal data.

Revisions reread explicitly selected donors: words from ID A, everything else from ID B retains B's musical cues/Styles/options/title, with provenance recorded. Full Lyrics from A also transfers A's section/music cues; it differs from words-only transfer. User text stays verbatim unless adaptation is requested. Default translation is literary with rhyme; explicit literal translation prioritizes accurate meaning. See [REVISION_flow.md](references/REVISION_flow.md).

Without archive/helper access, complete original chunks in messages or attachments are valid revision sources. Select them explicitly as C1/C2, reread their full text and use only supplied state; request a missing source instead of asking for an unavailable Windows path. Conversation labels are source provenance, not archive parent IDs.

## Text and highlight views

Only lyrics normally means one copyable text block with Suno section tags, line breaks and English singer/delivery annotations. Explicit plain text removes tags. Both preserve performed words, do not alter the source or create an ID/archive. Unknown legacy cues/quotes/roles require semantic review rather than partial silent extraction.

Highlight lyrics selects a separate readable view: mint words and muted gray-blue cues on dark backgrounds, dark-green words on light backgrounds. HTML copy copies plain minimally marked text without HTML/parser fields; manual-copy fallback is provided. Without supported HTML rendering, Markdown uses inline-code cues and bold words without promising exact colors/plain clipboard output. Ordinary chunks remain plain parser-compatible text. Details: [LYRICS_VIEW_tpl.md](references/LYRICS_VIEW_tpl.md).

text --highlight --output creates a standalone HTML file only; it does not translate, invoke a model or open a browser. --plain/--highlight are exclusive. Existing HTML is not overwritten.

## Protected files, encoding and limits

Ordinary song/remix work or reference refresh does not authorize changes to core/flows/specs/templates/code/parser. Supported dictionary enrichment is scoped separately: [FILES_spec.md](references/FILES_spec.md). These are agent instructions, not OS access controls.

New files use explicit UTF-8 without BOM/LF; input accepts UTF-8 BOM/CRLF, no ANSI guessing. Native multilingual text remains native. Use Unicode-capable editors/fonts.

The helper checks fields, limits, supplied avoid-lists, metadata and some role cases. Its direct English negation heuristic prevents no female vocals from creating a duet; complex negatives/same-gender casts still need semantic review. [LYRIC_REVIEW_lib.md](references/LYRIC_REVIEW_lib.md) defines artistic/content review. Audio is required to judge actual motif fit, breathing and performance.

With the complete project folder, use SunoFill v3.12.0 from tools/suno-fill.user.js for the current chunk; the full instruction TXT does not contain executable code. Update the userscript in Tampermonkey manually, then copy the complete chunk and invoke Fill on the Create page. It fills Lyrics/Styles/Title/Exclude and applies More Options, including sliders. Manually verify settings/model/instrumental toggle and skipped values. none does not reset gender or set instrumental mode; custom duration is not assured. Skill operation does not install/run the userscript.

Grouped INFO and legacy one-line metadata are supported by the payload parser and model/writer/time diagnostics. Metadata is read from INFO canonical keys only, never from lyrics or descriptive prose. Version identity and parent are not typed into Suno. Browser tests use isolated synthetic controls; actual Tampermonkey/live Suno integration still needs a separately authorized check.

## Public-file verification

```powershell
python -X utf8 -B scripts/verify_files.py
node tests/test_parser.js
```

The verifier is read-only and needs no private folders or original author checkout. Optional --source-hashes accepts an explicitly supplied developer manifest; only --prepare-fixtures regenerates test fixtures. Review actual publish/package membership: .gitignore neither removes already tracked data nor controls arbitrary packagers. Mechanical checks, historical results and live integrations must be distinguished.
