# Suno tags: purpose, evidence and risk

Source check: 2026-10-03; targeted chord/drum review: 2026-10-04. This catalog is not a formal Suno grammar. OFFICIAL means recommended by Suno, not exact-performance assurance; LEGACY means inherited without a reproduced audio test; DESIGN means our practical adaptation. All risk levels are estimated, without measured failure rates or zero-risk claims. Vocalization and ignored/misinterpreted guidance are separate failures.

S01 in [SOURCES_lib.md](../references/SOURCES_lib.md) recommends [Intro], [Verse], [Verse 1], [Chorus], [Bridge]. S02 defines music terms without validating arbitrary syntax. Reading dates are not listening-test dates. Preserve user observations separately with model/conditions.

## Risk decisions

Low: familiar short sections. Medium: short functional/local descriptions, allowed by default. High: long, mixed or conflicting instructions. Unknown: insufficient construction-specific evidence. Maximum Lyrics detail under [INTAKE_flow.md](INTAKE_flow.md#independent-detail-choices) grants standing permission for high-risk tag use, including when the LLM selects maximum under explicit delegation or full freedom. Experimental syntax with unknown evidence may be used within that approved high-risk scope; its evidence remains unknown. Do not ask again solely for using that granted scope, require risky padding, or claim reliable execution. Maximum Styles, full field size and music mode free alone do not grant this permission. Explicit low-risk/safe-revision restrictions take priority.

Outside existing permission, if high/unknown syntax is materially necessary, explain the risk and a clearer alternative, then obtain agreement; otherwise rewrite directly. A requested musical effect alone does not approve unreliable syntax. Reuse scoped permission for the current composition. Actual INFO risk reflects constructions used, not merely the maximum detail label.

## Sections

| Construction | Purpose | Vocalization | Interpretation | Evidence |
|---|---|---|---|---|
| [Intro] | Opening/palette | low | low/medium | OFFICIAL S01 |
| [Verse], [Verse 1] | Main lyrical development | low | low/medium | OFFICIAL S01 |
| [Verse 2], [Verse 3] | Later verse | low | medium; number does not ensure variation | LEGACY/analogy |
| [Chorus] | Returning central statement | low | low/medium | OFFICIAL S01 |
| [Bridge] | Perspective contrast | low | medium | OFFICIAL S01 |
| [Outro] | Ending | low | medium; no exact length/stop | LEGACY |
| [Pre-Chorus], [Post-Chorus] | Preparation/echo | medium | medium | LEGACY |
| [Final Chorus], [Chorus 1], [Chorus 2] | Variant/final return | medium | medium; write the intended variation | LEGACY |
| [Build], [Build-Up] | Anticipation | medium | medium | LEGACY |
| [Drop] | Arrival/release | medium | medium; not necessarily dense | LEGACY |
| [Breakdown] | Reduced density | medium | medium | LEGACY |
| [Break], [Interlude] | Interruption/connection | medium | medium | LEGACY |
| [Instrumental], [Instrumental Break] | Voiceless passage | medium | medium; not a global mode replacement | LEGACY |
| [Solo], [Guitar Solo], [Piano Solo] | Foreground instrument | medium | medium | LEGACY |
| [Synth Solo], [Drum Solo], [Bass Solo], [Saxophone Solo] | Other solos | unknown | unknown | LEGACY, untested |
| [Hook], [Refrain] | Short recurring phrase | medium | medium; not always a separate section | LEGACY |
| [End], [Fade Out], [Fade In] | Entry/ending character | medium | medium/high | LEGACY |
| [Silence], [Big Finish], [Crescendo] | Rest/accent/growth | unknown | unknown | LEGACY, untested |

Plateau is a musical function, not a confirmed [Plateau] tag. Internal A-prime notation is not a required export header.

## Voice and local parts

| Construction | Function | Vocalization / interpretation | Evidence |
|---|---|---|---|
| [Male Vocal], [Female Vocal] | Following block's voice | medium / medium | LEGACY syntax; voice types OFFICIAL S06 |
| [Choir], [Duet], [Backing Vocals], [Harmonies] | Ensemble/layers | medium / medium | LEGACY |
| [Rap], [Spoken], [Whisper], [Falsetto], [Belted] | Delivery | medium / medium | LEGACY |
| [Humming], [Ad-Lib], [Shout], [Scream] | Vocal events | medium / medium | LEGACY; exclude from pure instrumentals |
| [Drums: TR-909 pulse, open hats] | Drum role | medium / medium | LEGACY + DESIGN |
| [Bass: offbeat analog notes] | Bass pattern | medium / medium | LEGACY + DESIGN |
| [Synth: bright motif returns] | Theme return | medium / medium | LEGACY + DESIGN |
| [Guitar: muted rhythm, then lead] | Role/articulation change | medium / medium | LEGACY + DESIGN |
| [Transition: snare roll, brief pause] | Transition | medium / medium | LEGACY + DESIGN |
| [Verse: intimate, sparse piano], [Verse - whispered] | Section modifiers | medium / medium | LEGACY; separate voice cue is clearer |

Prefer 1–2 musical actions per short cue; this is editorial guidance, not a proven eight-word limit. Styles holds global voice, gear/timbre, key/BPM. Lyrics marks local differences. Device names alone do not define the sound.

At every new section or handoff identify the lead before its lines. Consecutive male/female tags without separated blocks do not allocate lines. Duet means simultaneous leads; backing does not change the lead. [Backing Vocals: female, soft harmony] is an estimated medium-risk DESIGN modifier, not official control. See [VOCAL_lib.md](../references/VOCAL_lib.md).

## Rewrite problematic constructions

| Problem | Risk | Clearer alternative |
|---|---|---|
| Paragraph inside brackets | high vocalization/lost intent | Separate relevant events; move global details to Styles |
| Quoted hook inside a cue | high boundary ambiguity | Short voice cue, then performed words on their own lines |
| Parenthesized performance/FX instruction beside words | high vocalization | Bracketed delivery cue; parentheses only for intentionally performed backing |
| [Repeat x4] or repeat chorus instead of words | high vocalization | Write repeats fully or shorten form intentionally |
| [LOCK], [SYSTEM: ...] | unknown/high | Ordinary musical directions, no simulated system code |
| [Key Change], [Tempo Change], [Ritardando], [Accel] | unknown exact automation | Describe desired audible movement; agree needed risky syntax |
| [DO NOT SING THESE INSTRUCTIONS] | high | Remove meta-command; use consistent mode/voice/Exclude |
| Long gear/note/timecode/parameter chain | high | Retain meaningful events and audible sound characteristics |

Quotes do not guarantee singing, parentheses backing, or brackets silence. Do not delete all brackets/parentheses blindly: intentional responses may be performed content.

## Chord guidance

S02/S10 support musical description; M01 documents inline bracketed chords in ChordPro, not Suno. The reviewed official material did not confirm the following special syntax. User-provided examples are not USER-LISTENING evidence.

| Variant / placement | Vocalization | Interpretation | Decision |
|---|---|---|---|
| A minor, target progression Am - F - C - G in Styles | Outside performed words; no universal failure assurance | medium descriptive intent; exact progression unknown | Preferred ordinary DESIGN description |
| [Chords: Am - F - C - G] after section heading | unknown | high for exact execution | EXPERIMENTAL; requires risk agreement |
| [Chords: \|Am\|-\|F\|-\|C\|-\|G\|] | unknown | high; separators do not prove duration | EXPERIMENTAL; complexity does not improve reliability |
| [Am] original words [F] next words | high | high; syllable/beat alignment unconfirmed | EXPERIMENTAL; ChordPro support is not Suno support |

All ratings are estimated. Adding this capability to the library is not blanket permission to use risky notation in every song. The risk agreement above includes maximum-Lyrics permission. Without such permission, preserve the harmonic concept through Styles and local descriptions; disclose reduced precision. Preserve requested progressions unless adaptation is authorized. Use Latin chord names and compatible mode, extensions/inversions, theme and bass. Do not reuse this example progression automatically.

## Drum-description examples

Each proposed phrase expresses a musical event without confirmed special grammar. Short descriptive cues have estimated medium vocalization and medium/high interpretation risk, especially for exact bar alignment, solo or vocal removal. Clearer alternatives are DESIGN, not audio-proven safer commands.

| Proposed cue | Limits | Clearer event |
|---|---|---|
| [Catchy drum machine intro] | Catchy defines no pattern; drum-only not assured | [Intro], then [Drums: solo drum machine groove]; mark later entrances |
| [Four-on-the-floor beat drop] | No complete texture, bass or tempo change defined | [Drop], then [Drums: four-on-the-floor kick returns] |
| [80s gated snare fill] | Era/tail, not a particular machine/pattern | [Transition: brief gated snare fill]; global snare character in Styles |
| [Drum machine bridge] | Does not guarantee voice/lead withdrawal | [Bridge] with drum cue; separately define remaining parts and vocal rest |
| [Funky drum break] | Not simultaneously drum-only, bass-only and chopped breakbeat | [Break], then [Drums: syncopated groove]; assign bass separately if wanted |

Only Intro/Bridge in these alternatives have OFFICIAL S01 section evidence; other headers/modifiers remain LEGACY/DESIGN. Use only events relevant to the task.

## Views, safe revisions and evidence

For text/translation/highlight views, remove nonperformed chord/drum production cues while retaining line breaks and explicit voice ownership. Removing inline chords must not split an original line. Preserve actual backing/ad-libs and ordinary words resembling note names. Full Lyrics/full chunks retain musical cues unless revision is requested.

The helper recognizes a limited A–G chord vocabulary with sharps/flats, common extensions/slash bass, Chords/Chord Progression cues, and the five listed drum descriptions. It is a reading classifier, not a ChordPro engine, music expert or evidence of Suno support. Unknown/quoted cues need semantic review.

When Suno sings instructions or misses harmony/withdrawal, create a new safe revision of the selected chunk: move harmony/kit targets to Styles, remove inline notation, keep concise section/events, and preserve words/cast/important entrances. INFO records the compromise/risk. This changes the prompt, not already generated audio.

Vocal terms in [VOCAL_INSERTIONS_lib.md](../references/VOCAL_INSERTIONS_lib.md) do not become official control tags by inclusion. New records require construction, purpose, placement, separate risks, risk_basis, evidence_kind, source_url, checked_at and tested_model/conditions when available. One successful listening test does not prove universal low risk; parser success proves only parser acceptance.
