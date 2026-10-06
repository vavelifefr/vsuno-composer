# Main musical theme

The lyrical subject and main musical theme are different. The theme is a recognizable musical idea carried by a voice, synth, guitar, piano, bass, ostinato or defined interaction. Not every foreground part or pad is a theme. Match exported description to the independent field levels in [INTAKE_flow.md](INTAKE_flow.md#independent-detail-choices); a basic profile needs no full theme card or extra category.

## Default recurrence at every detail level

For an ordinary composition, plan one initial presentation and at least two subsequent recognizable returns of the main theme, distributed across later key parts. If the user explicitly rejects a main theme, do not impose one. If the user permits a theme but prohibits its recurrence, keep only a single presentation if the request allows it and omit later returns. The LLM chooses suitable choruses, transitions, instrumental gaps, post-bridge passages or the final section within the existing form. Do not cluster allowed appearances at the opening. Intro is optional; the first presentation may occur in another section. Forms without choruses use their own key parts rather than adding a Chorus.

This default applies to basic, medium, expanded, maximum and custom detail. Whenever the user permits a main theme, Styles retains a brief identity: carrier plus a distinguishing rhythmic/melodic gesture; basic Styles can merge this into an existing category. Lyrics explicitly places the initial presentation and any permitted later returns, repeating a concise description of the recognizable core at each chosen location. A bare main theme returns reference is insufficient. Higher detail adds performance, development and relationships; it does not determine whether the returns exist.

The theme may be instrumental, vocal or rhythmic. A vocal theme uses its assigned voice and performed material, with words outside instruction brackets. Variations may change intensity, register, texture or carrier while preserving the recognizable core; unrelated contrast is not a return. A continuously repeated motif can be reaffirmed in later key parts without forced stops. Do not impose instrumental lead doubling on a vocal theme or mask dense words.

A genuinely very short form may use fewer returns while retaining recognition; do not lengthen it or invent sections just to reach the count. Compact prompt size or basic detail alone does not make the composition a short-form exception. Explicit user form, prohibitions and locks take priority over this default: if they rule out the theme or later returns, do not force them or add sections. Apply the recurrence rule when compatible with the request; preserve untouched source fields in words-only edits and read-only extraction.

During the existing final review and after compression, verify the permitted presentation and returns, their shared identity and Styles/Lyrics agreement. Preserve these placements while shortening optional descriptions/ornaments first, then measure both selected ceilings and hard caps (Lyrics 5000; Styles 1000). This checks the written musical plan, not whether Suno actually repeated the melody; audio verification remains necessary.

## Working card

Choose only useful detail:

1. Carrier and desired timbre; name gear when it clarifies sound or the user requests it.
2. Key/mode where applicable; select a compatible target when delegated, omit for genuinely non-tonal material.
3. Melodic contour and rhythmic identity.
4. Register, attack, articulation and phrasing.
5. Emotion and its audible cause.
6. Intensity/character, without pretending to specify exact MIDI velocity.
7. Recognizable invariant: opening, rhythm, contour, interval gesture or ending.
8. Development and relation to vocals/secondary parts.

Major does not automatically mean happy; minor does not automatically mean sad. Context, rhythm, harmony and articulation determine the effect. Do not infer an exact key from an uncertain reference analysis.

## Global identity in Styles

Describe key, carrier/timbre, phrase character, emotional effect, intensity and vocal relationship within the existing readable categories. Original example, not a default: a Juno-106-like plucked lead in A minor, short rising figure with a held ending, restrained verse answers and a more open chorus. Equipment names request a sound; they do not guarantee a faithful model.

## Local life in Lyrics

Place the required presentation/returns above, then show useful withdrawals and transformations. Choose appropriate locations; this table is not a compulsory section list:

| Location | Possible function |
|---|---|
| Intro | Reveal a fragment or establish the complete theme |
| Verse | Leave room for words; answer between phrases |
| Pre-Chorus | Prepare anticipation or withhold the expected ending |
| Chorus | State the core, support the vocal or intentionally stay out |
| Breakdown | Retain a recognizable fragment in reduced texture |
| Final return | Restore identity with a purposeful variation |

```text
[Verse]
[Synth: short rising plucked motif with a held ending, sparse answers]
[Chorus]
[Synth: short rising plucked motif with a held ending, stronger attack]
[Breakdown]
[Piano: short rising motif with a held ending, soft echo]
[Final Chorus]
[Synth: short rising plucked motif with a held ending, octave doubling]
```

Original partial musical-map example with no Intro, not a preset/full song. Estimated medium-risk DESIGN cues, not a guaranteed score. A particular chorus may answer/support/contrast instead of repeating the theme, provided the required recognizable returns are explicitly placed elsewhere when the user permits them. When it repeats, preserve the described core rather than demanding every part double every note.

## Secondary themes and bass

A secondary theme has a source, recognizable pattern and a role: answer, support, contrast or counterpoint. Do not relabel any pad as a second theme or add one without a purpose.

Bass may ground harmony, drive rhythm, answer the lead or carry the main idea. Layer only when appropriate: a sustained sub can support an audible upper-bass pattern, with compatible harmony and separated registers/rhythmic duties. Define which layer enters, rests and returns, and how it relates to kick and lead. A continuous busy line cannot simultaneously be described as only a rare response. Do not force layered electronic subs into every acoustic form.

Original scenario: intro reveals the lead; verse uses brief lead answers and low bass alone; chorus restores the complete theme while upper bass answers hook endings; bridge rests the synth, leaves a piano contrast and low bass; final chorus restores the agreed layers. This is an option, not a mandatory architecture.

## Vocal material as the theme

A vocal riff, chops or humming can carry the core. Specify source voice, contour/rhythm, key where applicable and processing globally; mark selected returns and foreground relationships locally. An ad-lib, breath or laugh becomes the theme only by design. Formant shift changes color, not key; a local pitch effect does not automatically modulate the whole track. See [VOCAL_INSERTIONS_lib.md](../references/VOCAL_INSERTIONS_lib.md).

## Motif transformations

Added 2026-10-04; M02/M03 in [SOURCES_lib.md](../references/SOURCES_lib.md). Choose an invariant and a section-specific purpose. Exact user-locked phrases/melodies restrict permitted transformation; unchanged repetition remains valid.

| Technique | Change | Retained identity |
|---|---|---|
| Ending variation | Last motion, duration or rest | Opening and principal rhythm |
| Sequence | Repeat the pattern at another pitch level | Contour/rhythm; diatonic intervals may adapt |
| Rhythmic augmentation/diminution | Longer/shorter durations | Pitch order/contour; no necessary BPM change |
| Interval expansion/contraction | Selected interval distances | Rhythmic gesture and direction |
| Fragmentation | Use part of the core | Characteristic fragment |
| Recontextualization | Harmony, bass or texture underneath | The melodic idea, harmonically compatible |
| Transfer/revoicing | New source or register | Chosen contour, rhythm or ending |
| Contour inversion | Upward/downward motion reverses | Rhythm and relation; exact interval inversion requires notes |

A sequence can stay in the original key. Diminution of durations differs from deleting notes. If inversion obscures the core, call it related contrast rather than an exact audible return. Changing every property needs an artistic reason. Musical strict/balanced/free modes govern these choices independently of lyric freedom; none requires all techniques.

## Phrase architecture

A musical phrase is a perceived gesture, not necessarily one printed line or one breath. Rests, held notes and harmonic/rhythmic closure may define boundaries. L06 informs vocal breathing; M06/M07 describe classical period/sentence models, not universal song forms.

Options: question → answer; idea → repetition → continuation; short gestures → held accent; repetition with a new ending; open cycle; purposeful expansion/contraction. In precise usage, a period relates weaker and stronger endings; a sentence presents an idea then continues toward cadence. Verbal question/answer alone does not prove a classical period. A 4+4-bar example is not a quota for all sections and does not bind rhyme automatically to cadence.

## Two-field consistency

Styles may say: Main theme: warm synth lead, rising motif with a held ending, answering the vocal between phrases. Local cues may show opening fragment, full motif returns or longer notes preserve the motif contour. Do not invent a new experimental tag for each technique.

Review the same card: what is recognizable, who carries it, where the permitted initial presentation and later returns occur, what changes, whether words are masked, and whether Styles/Lyrics agree on key, carrier, invariant and intensity. When a theme is permitted, check the recurrence rule above even at basic detail and after compression. If the answer is vague, repair the musical description rather than add adjectives. Exact notes/samples/performance require audio verification. Use [HARMONY_lib.md](../references/HARMONY_lib.md) and [ARRANGEMENT_lib.md](../references/ARRANGEMENT_lib.md) only as needed.
