# Existing parser contract

One complete result has five fields in exact order: TRACK, LYRICS, STYLES, MOREOPTIONS, INFO. Each marker is uppercase NAME:-> on its own line, followed by a blank line and its value. Preserve separators/blank lines. TRACK is one nonempty title; INFO is readable multiline metadata. Return one fenced text block, with no extra top-level fields or prose outside the labeled metadata inside it.

Tags, production descriptions, Styles, Exclude and descriptive INFO values are English. Performed words and original title may use the requested language. A lyrics-only view uses a separate readable text block, never a partial parser chunk.

MOREOPTIONS has one line with seven keys in this exact order, then a separate nonempty Exclude line:

```text
Vocal Gender: none | Duration: Auto | Max Mode: Off | Weirdness: 50% | Style Influence: 75% | Variety: Off | Personalize: Off
Exclude: {context-specific unwanted styles}
```

| Key | Accepted legacy values / limitation |
|---|---|
| Vocal Gender | Male, Female, none; use none for duet/choir/instrumental with clear role descriptions; it does not set Instrumental toggle |
| Duration | Auto or Custom mm:ss; Auto preferred when exact-duration support is unknown; Custom is legacy syntax, not verified timing control |
| Max Mode | Off or On |
| Weirdness / Style Influence | Integer 0-100, optional percent sign |
| Variety | Off, Normal, High, Extra, Max; parser vocabulary, not proof of the current account interface |
| Personalize | Off; does not cancel unrelated account preferences |

50/75 are legacy examples, not current automatic presets. For unspecified new-composition settings use the Lyrics-detail corridors in [INTAKE_flow.md](INTAKE_flow.md#automatic-more-options-and-exclude-targets), selecting concrete values. Preserve explicit user settings/locks and unchanged source options; do not enforce recommendation ranges on imported chunks. If model is unspecified, v6-mini is a compatible legacy default and must be identified as a default, not a verified UI selection. Do not change a selected model during remix.

## INFO and counting

A new archived version needs exactly one Unique version ID (ID), matching JSON.id and the prompt filename suffix, plus Parent version (parent) under [PERSONAL_spec.md](PERSONAL_spec.md). Do not emit the redundant Version ID (version) in new outputs. Legacy version metadata remains accepted; when present it must match ID. A complete context-only output is also permitted when archival identity tools are unavailable; use the explicit metadata below instead of inventing an ID. Old incoming chunks without ID remain readable/importable with a warning; do not modify old records.

New outputs follow [CHUNK_tpl.md](CHUNK_tpl.md): VERSION AND STORAGE, COMPOSITION, CREATIVE DIRECTION, GENERATION AND VERIFICATION, then optional REVISION AND SOURCES and ADDITIONAL DETAILS. Each category has a standalone English heading; each parameter occupies its own Label (canonical_key): value line. Use blank lines between categories. The explanatory label must distinguish Suno generation model (model) from Writer model (gen_model), music freedom from text freedom, and ID from parent/source IDs. INFO lies outside the four Suno field payloads and has no length cap.

The helper reads canonical keys from INFO only. It accepts new labeled lines, simple key: value lines and legacy one-line semicolon/pipe entries. Do not rewrite old records for formatting. New finalization groups INFO, preserves meaningful custom parameters/notes, removes legacy version metadata and replaces ID/parent/storage with actual archive values. Exactly one model is required, using the retained v6/v6-wild/v6-mini vocabulary; this is metadata, not evidence of a current account selection. SunoFill reads the same canonical keys without restricting INFO labels/categories. Do not add special separators merely to satisfy a userscript.

Useful metadata: summary, lang, music_mode, text_mode, detail, risk, research, lyrics_chars, styles_chars, ID, parent, changes, translation, compromise, storage and opaque lyrics_source/music_source. version is a legacy import alias, not a new output row. gen_model is a known writer ID or unknown; gen_time is measured or ?. Never fabricate writer identity, time, source verification or saving. Semicolons/pipes inside a new labeled value are ordinary prose, not field delimiters. Never put real reference identities, identifying URLs, borrowed lyrics, private paths or hidden reasoning in INFO. Keep optional categories/parameters only when relevant. Checks still reject duplicate IDs/models, mismatching legacy versions and incorrect supplied length counts.

When actual UTC/randomness or counting is unavailable, omit ID/version or lyrics_chars/styles_chars respectively. Use Archive identity status (identity): unavailable and Field counting status (counting): unavailable for those capabilities, plus Storage status (storage): context-only when no persistent save occurred. An optional Conversation source label (context_ref): C1 identifies a complete chunk in this conversation only. Retain all five fields, one compatible model, real user settings and normal composition metadata. State that omitted counts mean the hard limits have not been mechanically verified; keep output compact and do not claim cap compliance. This is a complete limited output, not a fake saved version.

identity: verified requires one actual ID; an imported version value, if present, must match it. counting: verified requires both actual matching field counts. unavailable status forbids the corresponding claimed values. Local check still computes field lengths and enforces caps when it can run. Archiving replaces limited statuses with verified identity/counting and saved storage, assigns a fresh real ID/counts and preserves the first four fields and useful context_ref. These INFO keys do not change the private JSON/state schema. Other genuinely unavailable optional values should be omitted, not replaced with fabricated measurements.

Count field values, excluding markers/separating blanks, including internal cues/spaces/newlines. Normalize CRLF to LF. Use UTF-16 length to match browser JavaScript; astral characters such as emoji count as two. Caps are 5000 Lyrics and 1000 Styles, no minimum; user limits may be smaller. Rebuild overlong fields without cutting the finale. This is the agreed contract, not a guarantee of every future plan's limits.

INTAKE_flow supplies independent field ceilings/detail. Final generation must check both chosen ceilings and the hard caps after drafting/compression/finalization. The existing check/archive helper enforces hard caps and returns actual counts; the author also compares those counts with smaller chosen ceilings. It does not infer profiles, enforce slider recommendations or semantically select Exclude. No extra required INFO/top-level field is introduced; existing detail values and old chunks stay readable. Without actual counting use the explicit unavailable-counting contract above, never a fabricated pass.

SunoFill v3.12.0 is adapted to the current chunk: model/gen_model/gen_time are read only from the complete INFO field using canonical keys, including grouped labeled lines and legacy entries. Category headings are ignored; punctuation in labeled values stays opaque. Ambiguous duplicate metadata is not guessed. ID/parent and all INFO/STATE content remain outside Suno fields. Standalone markers delimit the payload, so inline marker text does not truncate lyrics. It supports native text fields and contenteditable Lyrics, sets supported controls, does not click Create and does not set Instrumental toggle. none/Auto and custom-duration handling can leave UI settings unchanged; inspect actual applied controls. Isolated synthetic browser tests do not prove the current live Suno DOM or Tampermonkey extension integration. Settings/details: [SUNO_TECH_lib.md](SUNO_TECH_lib.md).
