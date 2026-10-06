# Suno capabilities and project limits

Historical source check: 2026-10-03. Consult [SOURCES_lib.md](../references/SOURCES_lib.md) and [UPDATE_flow.md](../references/UPDATE_flow.md) before asserting current availability. Translation does not refresh evidence dates.

## Documented capabilities at that check

S03/S04 describe v6, v6-wild and v6-mini: v6/v6-wild for Pro/Premier and v6-mini for all users. v6 favors controllable general creation, wild experimentation, mini quick ideas. Availability may change. S04/S07 describe generation up to eight minutes and Extend; this is a ceiling, not a guaranteed requested duration.

Custom creation separates Lyrics and Styles and offers instrumental generation. S05 describes Weirdness (50 as the ordinary reference), Style Influence (loose to strong), and Audio Influence for uploaded audio. Do not add Audio Influence to the fixed parser contract or upload audio automatically. S06a describes excluding unwanted styles/instruments; exclusion is not absolute. S06 offers Male/Female vocal choices plus descriptive characteristics, without guaranteed per-line duet assignment.

## Exact local contract

Lyrics ≤5000 and Styles ≤1000 UTF-16 code units are the user's project acceptance limits, not a verified universal specification for every future plan/interface. There is no mandatory minimum. Independent size/detail choices and Lyrics-driven slider corridors in [INTAKE_flow.md](INTAKE_flow.md) are project recommendations; chosen smaller ceilings also apply. They do not guarantee execution of detailed tags. Final field counts are mandatory when actual counting is available; never pad to a ceiling or claim an unmeasured pass.

The seven MO values and Variety/Max flags belong to the existing parser. Preserve names/order and distinguish legacy labels from current UI capabilities. A parser pass does not prove live Suno integration. Details: [PARSER_spec.md](../references/PARSER_spec.md).

## Musical precision

Descriptions and tags are soft guidance, not MIDI, a score or exact automation. Gear names request timbre; BPM/key/chords/bar counts/entrance placement are targets until heard. Do not promise exact voices, duration, harmony or silent instructions without actual evidence.

Pure instrumental means no performed vocal material. Intentional humming, choir pads or wordless chops are vocal material and must be acknowledged consistently in Lyrics, Styles, Exclude and mode settings. Do not globally exclude voices to create one local instrumental passage.

Generating a prompt does not authorize account access, uploads, payment, publication or launching Suno/DAW. Capability limits must be explicit, with a limited model-knowledge fallback offered when research/storage is unavailable.

## Encoding

Write new text as UTF-8 without BOM with LF. Accept verified UTF-8 BOM and CRLF on import; never silently fall back to CP1251. Use explicit UTF-8 I/O in helpers. Preserve the userscript byte-for-byte unless separately authorized. The Windows launcher temporarily selects code page 65001 and restores the previous setting. Correct bytes cannot guarantee every old editor/font will render every language; use a Unicode-capable viewer. Do not replace real lyric letters with escaped Unicode sequences.
