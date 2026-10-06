# Personal research, versions and exact exports

Exclude personal/ and prompts/ from Git and distribution. Ignore rules do not untrack existing files; inspect the index before publication and never force-add personal data. Public files/tests must not contain user reference identities.

Paths below are relative to data_root. Default: the current skill root. Where instruction resources are read-only, use a separate writable root only after explicit authorization of that destination. archive/list/get support --data-root; use the same selected root for parent/donor reads and new writes. There is no migration, automatic location choice or fallback to the resource archive. Project maintenance remains in the project root. A cloud/session root does not imply lasting storage; disclose its actual persistence.

## Create records only when used

- personal/references/<id>.json: structured research, real identities/URLs allowed, no borrowed lyrics.
- personal/tracks/<ID>.json: immutable version with title/date/parent/full cleaned chunk/state. Legacy UUIDs remain readable; no migration.
- personal/feedback/<id>.json: explicitly reported listening observations for the selected version; not general statistics or lexical history.
- prompts/<title>_<ID>.txt: exact final UTF-8 parser chunk including INFO, no fences/commentary. Preserve Cyrillic titles; replace Windows-invalid characters, trim trailing dots/spaces, limit title stem to 100 characters, use Track for empty stems and Track_ for reserved names. Never overwrite; identical copies need no repeat write, differing content with one ID is a conflict. Do not change TRACK or rename old timestamp exports.

Do not seed fake personal records during installation. Without file access, records exist only in current context; disclose cross-chat loss. If writing is prohibited, save neither research nor chunks.

Archive writes JSON then exact text copy. On export failure, report the already saved ID and recover its copy from JSON without recomposing or overwriting. Read-only extraction/translation creates no archive; a requested new full translated chunk is a normal new version.

## Research record

```json
{
  "schema_version": 1,
  "id": "local-opaque-id",
  "scope": "recording | style | era-scene",
  "identities": {"artists": [], "tracks": [], "aliases": []},
  "style_keys": [],
  "summary": "neutral musical description",
  "claims": [{"topic": "rhythm | meter | tempo | bass | lead | drums | arrangement | voice | fx | era",
    "value": "description or null", "status": "confirmed | inferred | unknown",
    "source_urls": [], "checked_at": "YYYY-MM-DD", "basis": "specific supporting evidence"}],
  "sources": [{"url": "https://...", "kind": "official | primary | secondary | user-listening",
    "accessed_at": "YYYY-MM-DD"}],
  "limitations": [],
  "prompt_traits": {"rhythm": "", "instruments": [], "voice": "", "arrangement": "", "mood": ""}
}
```

Remove identities from prompt_traits. confirmed is not necessarily official; source kind/basis identifies support. Do not fill unknowns by guessing; a stylistic tempo range is inferred, not exact recording BPM.

## Version record and lookup

New archived outputs use six random lowercase Latin letters, underscore, actual UTC YYYYMMDDTHHMMSSffffffZ. The single INFO.ID, JSON.id and filename ID must match; retain Parent version (parent), omit the redundant Version ID (version). A legacy INFO.version, when present on import/read, must match the selected identity. Archive always assigns a new ID and records the selected parent. Reads do not change IDs. Without helper use actual clocks/randomness when available. If identity or counting tools are unavailable, return the complete context-only output under [PARSER_spec.md](PARSER_spec.md), omit unavailable IDs/counts and mark statuses honestly. C1/C2 conversation labels identify accessible full chunks, not retrievable archival records.

Final INFO is grouped multiline metadata with explanatory English labels and canonical keys under [CHUNK_tpl.md](CHUNK_tpl.md). Archive accepts legacy one-line and explicit limited input, groups the new version, preserves custom parameters/notes, removes legacy version metadata, replaces ID/parent/storage, marks identity/counting verified and writes actual field lengths. It does not change the first four fields. Old records remain byte-preserved; emit the exact new saved chunk so INFO in chat, JSON and prompts agrees. INFO is not a substitute for private state or evidence records.

Fields remain schema_version, id, created_at, parent, title, chunk, state. Store final parameters, bans, locks, brief musical map and opaque research IDs, not hidden reasoning. reference_identities may exist in personal state for checking, never in INFO. Different versions may share a title.

When field preferences are resolved under INTAKE_flow, retain each field's selected ceiling/detail, selection method and explicit/automatic setting origins as decisions in the existing free state or current conversation. INFO.detail may summarize both levels using its existing labeled row. This is not a new required archive schema; old states remain valid and no record is migrated or inferred from missing data. Revisions inherit known preferences while preserving locks and unchanged options.

For multiple donors, state.sources is [{role, id, mode}] with music/lyrics/structure/voice and verbatim/adapted/inspired. Parent is the base; sources identify extra donors. Keep the free state schema; read only selected versions/relevant research.

Archive inherits parent state then replaces only explicitly supplied keys. Empty bans/locks overwrite earlier values and require user authorization. Unpassed constraints/modes/identities remain. locks is a list of nonempty strings; TRACK/LYRICS/STYLES/MOREOPTIONS protect whole fields, not INFO. Semantic locks such as preserving a motif require LLM comparison. Resolve older incompatible lock representations explicitly; no automatic migration.

list reports malformed records by record ID to stderr and continues; get returns an error for the selected malformed record. Reads validate the chunk/limits/options and available state constraints, require TRACK to match title, compare present parent metadata and match embedded identities to the selected record. New-format IDs require ID; optional legacy version metadata must match it. Historical UUID cards may omit those fields or have version only; present values must still match. Neither command repairs/deletes records or echoes private content in validation errors. ID selects exactly; title may produce dated candidates; contextual lookup compares state. Never silently substitute latest or reconstruct a missing song.

Use python scripts/vsuno.py list --query "title", get <ID> --json, archive <chunk.txt> --parent <ID> --state <state.json>. Emit the exact saved get result, not the pre-archive input or edited metadata afterward. get accepts ID only, not paths/title. Ordinary personal writing does not authorize deletion, publication or moving another person's data. Donor rules: [REVISION_flow.md](../references/REVISION_flow.md).
