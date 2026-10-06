# Intake, field preferences and independent modes

Build the brief from the first request and available selected source: task, instrumental/words/vocal sounds, style/era, references, subject/emotion, language, instruments/voices, structure/duration, music/text freedom, independent Lyrics/Styles size and detail, bans and locks. Record final decisions, not hidden reasoning.

Distinguish words, permitted vocal sounds and performers. Instrumental with requested wordless chops has no words but has a vocal layer. Resolve real contradictions such as no voices with a required choir.

## Resolve the first request before asking

Apply explicit field choices first, general prompt-size/detail cues second, and delegation only to the remaining choices. Preserve all explicit constraints.

| Input | Decision |
|---|---|
| Explicit sizes/detail/settings for both fields | Use them; no repeated questionnaire |
| General compact/short/medium prompt request | LLM chooses suitable size and detail for both fields from that direction; no size/detail questionnaire |
| Cue applies only to Styles or Lyrics | Resolve both preferences for that field; ask only unresolved preferences for the other field unless delegated |
| More detailed Styles, without another level | Interpret as expanded Styles detail; LLM selects a suitable Styles ceiling; unresolved Lyrics preferences still need answers |
| Choose the rest / explicit delegation | LLM selects missing preferences and other delegated essentials within constraints; do not ask them back |
| Full freedom for a test or exploration run | Randomly select permitted size/detail profiles independently for the two fields, retaining explicit constraints |
| Rich musical brief, but no size/detail cue or delegation | Ask required missing size/detail questions for both fields |
| Sparse brief without delegation | Ask missing composition essentials and field preferences together in one short round |
| Local edit / read-only extraction | Inherit the selected composition's known preferences; do not restart intake or invent new choices |

A general cue covers both fields unless its wording scopes it to one. An explicit size alone or detail alone lets the LLM select the companion preference for that same field. A compact size can have expanded detail; express useful decisions concisely. Generic detailed/more detailed means expanded; explicit maximum detail means maximum. A large amount of performed text is not maximum musical detail. Full size alone does not grant maximum-detail risk permission.

Music mode free is artistic freedom, not automatic delegation of every missing preference. A bare generate instruction containing only a genre does not resolve whether words are wanted. Explicit full delegation can cover those choices. If the user declines more input, offer to choose the missing decisions.

Ask only unresolved choices, in the user's language and in one message. Every question includes an Own option with free text, additional constraints or rejection of all offered choices. Wait for required answers before composing the full chunk; do not silently substitute medium detail. Do not use transient question cards.

For full-freedom sampling use an available random source where possible; otherwise choose varied profiles honestly without claiming verified random sampling. Random selection changes preferences, not explicit lyrics/locks or semantic Exclude selection. Keep the resolved preferences for this composition until the user changes them; no unsolicited global defaults. Preserve base options/Exclude during a words-only revision.

## Independent size choices

Offer these three ceilings plus an Own option separately for Lyrics and Styles. Count the complete field value in UTF-16 units, including cues, words, spaces and line breaks.

| Size | Lyrics ceiling | Styles ceiling |
|---|---:|---:|
| Compact | 1500 | 300 |
| Medium | 3000 | 650 |
| Full | 5000 | 1000 |
| Own option | User ceiling within the hard cap | User ceiling within the hard cap |

These are ceilings, not quotas; never pad to reach them. A custom instruction may also define form/line count, but it cannot bypass the character caps. Resolve an impossible combination of protected words, requested detail and size rather than silently truncating/replacing the words.

## Independent detail choices

Offer four levels plus an Own option separately for each field. Localize names and explanations in the user's language. Detail adds useful descriptions of the chosen composition, not compulsory extra sections, instruments, words or duration. Vocal descriptions apply to any requested vocal material, including wordless voices.

Where the user permits a main theme, every level retains its identity and allowed initial presentation under [MAIN_THEME_lib.md](MAIN_THEME_lib.md#default-recurrence-at-every-detail-level). Ordinarily include at least two later returns across key parts when the user permits recurrence. Basic means concise descriptions, not omission of permitted appearances. The LLM chooses locations; Intro is optional. Only genuinely very short musical forms may use fewer returns without extension; compact field size alone is not that exception. Explicit user prohibitions and locks take priority over this default.

### Lyrics

| Level | Questionnaire explanation |
|---|---|
| Basic | Core section structure and performed text if present; essential singer/role cues and, when a theme is permitted, short recognizable presentation/return cues |
| Medium | Structure and principal transitions; where/how a permitted main theme enters or returns; short vocal delivery cues if vocals are present |
| Expanded | Key musical/vocal events and accents by section: entries, pauses, withdrawals, density changes and relationships; medium estimated tag risk |
| Maximum | Detailed within-section development, instrumental actions, motif/bass relationships, transitions, vocal delivery changes and other useful specifics; high-risk tag use permitted |
| Own option | User-selected structure, detail and restrictions |

Prefer concise meaningful cues at every level. Maximum permits useful high-risk constructs; it does not require risky padding. Its risk permission also applies when the LLM selects maximum under explicit delegation or full freedom. Respect an explicit lower-risk restriction or safer-revision request.

### Styles

Word ranges below guide the amount of useful description; they are not mandatory minima. Omit absent/irrelevant categories and do not expand a genre name just to fill a range. Era belongs with Style when useful. Essential user choices and voice assignments remain represented even in compact output.

When the user permits a main theme, keep a brief carrier/recognizable-core description at every level. Basic Styles may merge theme identity into an existing category instead of adding a full theme card. Higher detail elaborates the identity and its relationships; it does not change whether later returns are permitted or required by the default.

| Level | Questionnaire explanation / word guidance |
|---|---|
| Basic | Genre 3-5; Style 3-5; delivery/mood 3-7 |
| Medium | Genre 5-10; Style 5-10; Vocals 7-12 if present; Main theme 5-15; delivery/mood 5-10 |
| Expanded | Genre 5-15; Style 5-15; Vocals 5-20 if present; Main theme 5-15; key Instruments 7-15; delivery/mood 5-15 |
| Maximum | Genre 5-15; Style 5-15; Vocals 5-25 if present; Main theme 5-15; Secondary theme 5-20 if designed; bass/arrangement 5-20; key Instruments 7-15; delivery/mood 5-15 |
| Own option | User-selected categories, density and restrictions |

Maximum Styles does not require inventing a secondary theme or extra bass layers, and does not itself grant high-risk Lyrics-tag permission. Keep the existing multiline Styles presentation under CHUNK_tpl; compress by meaning to fit the selected ceiling.

## Automatic More Options and Exclude targets

Use Lyrics detail only, regardless of Styles detail or field length. Pick concrete integer percentages inside the corridors; output actual values, never a range, in MOREOPTIONS. Preserve explicit user values, locks and unchanged source options. Apply defaults only to unspecified settings for a new composition/redesign. Other controls retain their existing rules.

| Lyrics detail | Weirdness | Variety | Style Influence | Adjacent anti-style target |
|---|---|---|---|---|
| Basic | 55-65; reference 60 | Normal | 45-55 | 3-4 |
| Medium | 50-55 | Normal | 55-65 | 4-5 |
| Expanded | 40-50 | Off | 65-70 | 5-7 |
| Maximum | 35-40; reference 40 | Off | 70-80; reference 75 | 5-10 |

These are the user's project recommendations, not official presets or guaranteed obedience. Style Influence acts on Styles; these values do not certify exact Lyrics-tag execution. LLM-selected maximum has the same high-risk permission as a human selection. For a custom detail description, use the closest functional level for defaults unless settings/risk are explicitly specified; mere length does not imply high-risk permission.

Exclude targets are flexible ranges, not forced counts. Select meaningful adjacent unwanted styles under NEGATIVE_STYLES_lib; never fill a count with unrelated directions. If fewer valid exclusions exist, retain the meaningful set and briefly explain the smaller count outside the chunk. Exclude remains nonempty under PARSER_spec.

## Music and text freedom

| Mode | Music | Words |
|---|---|---|
| strict | Genre convention or clear roles in a blend; characteristic groove/timbres/form | Direct subject development, appropriate idiom and coherent form |
| balanced | Recognizable framework with purposeful distinctive choices | Concrete detail, fresh perspective, moderate imagery |
| free | Inventive form, transitions and accents within the brief | Bold perspective and structural/rhyme choices within the subject |

Strict does not mean cliched or poorly rhymed; free does not permit incoherence or wrong stress. Modes do not impose fixed sliders; automatic recommendations use Lyrics detail. Propose balanced modes when absent and not delegated; text mode is not applicable to a piece without performed words.

## Brief, continuity and final limits

Summarize style/era, groove/theme, voices, development, modes, each field's size/detail and chosen options briefly. Existing explicit generation/delegation authorizes completion once required answers are available; do not add a second routine approval. Save resolved preferences, selection method and explicit/automatic setting origins as final decisions in the existing free private state when saving is available, or retain them in the current conversation. Do not create a new archive schema or migrate old states. INFO's existing detail value may summarize both field levels; no extra top-level chunk field is needed.

After drafting and after any compression/finalization, measure both final field values. Require each to fit its selected ceiling and the hard caps (Lyrics 5000; Styles 1000) under PARSER_spec. Word ranges and profile selection never replace this check. Rework optional descriptions first, preserve protected words and endings, then measure again. Without actual counting tools use the contract's explicit unavailable-counting result and never claim mechanically verified limits.

Resources: [COMPOSE_flow.md](COMPOSE_flow.md), [NEGATIVE_STYLES_lib.md](NEGATIVE_STYLES_lib.md), [SUNO_TAGS_lib.md](SUNO_TAGS_lib.md), [PARSER_spec.md](PARSER_spec.md), [CHUNK_tpl.md](CHUNK_tpl.md), [PERSONAL_spec.md](PERSONAL_spec.md).
