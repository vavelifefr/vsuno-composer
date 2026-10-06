# Complete-result template

Replace all placeholders; this is not a preset song. Resolve independent field size/detail under [INTAKE_flow.md](INTAKE_flow.md). English descriptions, selected-language performed words. When the user permits a main theme, every level keeps its brief identity in Styles and its allowed initial presentation in Lyrics under [MAIN_THEME_lib.md](MAIN_THEME_lib.md#default-recurrence-at-every-detail-level); add later returns when the user permits recurrence. Fuller detail elaborates development. Retain essential changing vocal ownership. Merge theme identity into an existing basic Styles category; omit other optional rows outside the chosen profile. Return the filled content in one text code block:

```text
TRACK:->

{Original title}

LYRICS:->

{Section headers, short music events and original performed lines if wanted}

STYLES:->

Genre: {Principal genre and purposeful blend}
Style: {Era, tempo/groove, key/mode if tonal, sound character}
Vocals: {Cast, roles, delivery, diction and natural phrasing, or absence of voices}
Main theme: {Carrier/timbre, contour/rhythm, register/articulation and intensity; omit if the user rejects a main theme}
Secondary theme: {Carrier/performance and relationship to the main motif, only if needed}
Instruments: {Other important parts and functions}
Bass: {Timbre/pattern, selected layers and interaction with theme/groove}
Mood: {Emotional character and trajectory}

MOREOPTIONS:->

Vocal Gender: {Male/Female/none} | Duration: {Auto/Custom mm:ss} | Max Mode: {Off/On} | Weirdness: {0-100}% | Style Influence: {0-100}% | Variety: {Off/Normal/High/Extra/Max} | Personalize: Off
Exclude: {Nonempty context-specific unwanted styles compatible with the desired sound}

INFO:->

VERSION AND STORAGE
Unique version ID (ID): {Random letters_actual UTC timestamp}
Parent version (parent): {Base version ID or none}
Storage status (storage): {saved/context-only/unavailable}
Archive identity status (identity): {verified/unavailable}

COMPOSITION
Composition summary (summary): {Neutral description of the resulting composition}
Lyric language (lang): {ru/en/mixed/none or another requested language}

CREATIVE DIRECTION
Musical freedom (music_mode): {strict/balanced/free}
Lyric freedom (text_mode): {strict/balanced/free/na}
Prompt detail (detail): {Resolved Lyrics and Styles levels, or custom detail}

GENERATION AND VERIFICATION
Suno generation model (model): {v6/v6-wild/v6-mini}
Writer model (gen_model): {Known writer ID or unknown}
Preparation time (gen_time): {Measured time or ?}
Tag risk (risk): {medium/low/high-approved}
Reference research (research): {verified/partial/limited/not-needed}
Lyrics length in UTF-16 units (lyrics_chars): {Actual count}
Styles length in UTF-16 units (styles_chars): {Actual count}
Field counting status (counting): {verified/unavailable}
```

Styles categories are separate lines in one field. Omit the main-theme category if the user rejects a main theme; also omit nonexistent secondary-theme/bass categories. Merge categories for a short prompt. Use concrete audible choices, not adjective chains. All headers/newlines count toward 1000. Pure instrumental excludes all voice sounds; requested wordless layers assign sources without contradictory no vocals.

At every detail level, place the main theme's allowed initial presentation and, when the user permits recurrence, ordinarily at least two recognizable later returns across key parts. Repeat a short core description at each planned placement, not the entire Styles card; basic Lyrics retains these alongside sections/text/essential role cues. Locations are flexible and Intro optional; genuinely very short forms may use fewer returns without extension. Explicit user prohibitions and locks take priority: do not impose a rejected theme or returns the user disallows. Preserve compatible placements after compression, then check final fields against chosen ceilings and hard caps (Lyrics 5000; Styles 1000). Use actual integer settings from the Lyrics-detail corridors, preserving explicit controls, and meaningful adjacent Exclude entries. A new revision needs one new Unique version ID (ID) plus parent/changes; never also emit Version ID (version). Safe revision records compromise. A lyrics-only request follows [REVISION_flow.md](REVISION_flow.md), not this parser template.

INFO uses the readable categories above, one labeled parameter per line and one blank line between categories. The English label explains the parameter; the canonical key in parentheses supports exact local lookup. Do not compress new INFO into a semicolon-separated line. INFO has no length cap and does not consume Lyrics/Styles limits. Keep it factual and omit empty optional categories, placeholders and unavailable optional details.

For a complete instruction-only result without actual identity/counting tools, omit ID/version and unavailable length rows; retain the five fields. Set storage: context-only and the affected identity/counting status to unavailable. Optionally add Conversation source label (context_ref): C1 in ADDITIONAL DETAILS, never in ID/version. If a parent/source ID is unknown, omit it rather than claiming none or inventing one. Explain unverified limits under [PARSER_spec.md](PARSER_spec.md). Available measurements may be reported accurately; archive assigns verified identity/counts when saving becomes possible.

When applicable, add REVISION AND SOURCES with Changes in this version (changes), Translation mode (translation): singable/literal, Precision compromise (compromise), Lyrics donor (lyrics_source) and Music donor (music_source). Donor values are actual opaque archive IDs or explicitly prefixed conversation labels such as context:C1; do not confuse the latter with archive lookup IDs. Put useful custom parameters/notes in ADDITIONAL DETAILS with the same Label (key): value syntax. Never include real reference identities/identifying URLs, private paths or hidden reasoning. Preserve meaningful custom data when revising; replace only metadata that actually changes.
