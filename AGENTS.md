# Vave Suno Composer: change boundaries

Applies to agents using this folder. Policy: [FILES_spec.md](references/FILES_spec.md).

This folder is the sole project root. Keep project maintenance and changes inside it; use local references and do not depend on another checkout. Composition data defaults to this root. A separate data_root is allowed only when the user explicitly authorizes that destination; it holds personal/ and prompts/, not skill maintenance. Never auto-select, move data or fall back to a different archive.

- Song creation, remixing, chunk repair or feedback does not authorize changing the skill.
- Without explicit scoped authorization, do not edit SKILL, AGENTS, flows, contracts, templates, scripts, tools, tests, agents, launcher, configuration, library instructions or structure.
- Verified reference data may be added within existing library sections. Personal research/versions and final prompt copies follow PERSONAL_spec; real user reference identities belong only in personal records.
- Dictionary refresh authorizes data updates in its stated scope, not algorithm/parser changes. Present a concrete proposed core change and ask only if authorization is absent.
- A direct request to implement a feature authorizes its necessary targeted changes, not unrelated future changes.
- Use a new personal record or authorized report for task work. Preserve unrelated files, earlier versions and existing work.
- Final new/revised complete chunks also save to prompts/ when writing is permitted; exclude it from Git and distribution.
- New text is UTF-8. Preserve the original userscript byte-for-byte unless explicitly instructed to change it.
- Internal instructions are English; conversation may be Russian or English. Native-language examples/test data are intentional exceptions.
