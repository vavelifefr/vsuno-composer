# Voice, technique, role and processing

Choose voice/register, ensemble, interaction, delivery and processing as separate axes. All are desired performance, not guaranteed Suno settings. Global character belongs in Styles; local differences belong in Lyrics with [SUNO_TAGS_lib.md](../references/SUNO_TAGS_lib.md) risk assessment. Read [VOCAL_INSERTIONS_lib.md](../references/VOCAL_INSERTIONS_lib.md) or [PROSODY_lib.md](../references/PROSODY_lib.md) only for relevant functions.

| Axis | Options / purpose |
|---|---|
| Voice/register | Requested male/female lead; tenor/baritone/bass or soprano/mezzo/contralto as range/color targets |
| Ensemble | Solo, duet, small ensemble, choir; identify primary/supporting cast |
| Interaction | Unison, octave doubling, harmony, call-response, countermelody; harmony need not imply choir |
| Delivery | Intimate, spoken/half-spoken, rhythmic rap, sustained singing, whispered, raspy, belted, falsetto/head voice |
| Articulation | Legato, staccato, purposeful melisma/run |
| Processing | Dry/close, reverb, delay response, doubling, vocoder-like, talkbox-like, radio-filtered, bitcrushed |

Chest voice describes a fuller lower-register quality. Head voice and falsetto are not universal synonyms. Belting is a strong delivery, not a gender. Breathiness and microphone proximity differ. Song-form chorus differs from chorus effect.

Rap is rhythmically organized lyrical delivery; spoken word is primarily speech, and half-spoken singing blends speech with sung pitches. Recitative is speech-like singing, especially in opera, not a general English synonym for rap. Request rapid rap delivery when rap is intended; retain recitative for the corresponding sung delivery. M09 in [SOURCES_lib.md](SOURCES_lib.md) supports the operatic term.

Wordless vocalise, humming, chant, scat and chops still contain voice. Add none to a pure instrumental without agreed vocal elements. Scat, yodel, opera or choir can enter another style when purposeful; do not inherit absolute genre bans. A cappella means no instrumental accompaniment in the specified passage; choir plus piano is not a cappella. Beatbox is intentional vocal percussion. A local a cappella intro does not remove later instruments.

## Stable cast and explicit handoffs

Create a concise voice → function → sections/blocks map. Example: male baritone rap verses; female mezzo melodic choruses; both together only in the final refrain. It is a production decision, not a chain-of-thought transcript. Keep stable contrast for two voices of the same gender.

Singer and narrator are distinct: voice gender/register does not change characters, pronouns or viewpoint. Pitch/formant/FX processing does not create another singer.

Styles describes allocation, not merely both genders: male rhythmic lead in verses, female melodic lead in choruses, both in unison only in the final chorus. For a duet set MO Vocal Gender to none; the legacy userscript does not reset an existing UI gender when none, so manual verification may be needed.

Open every vocal section/block with [Male Vocal], [Female Vocal] or an agreed ensemble cue, plus brief compatible delivery where useful. Repeat ownership in a new section even when the same singer continues. At an internal handoff, put the new cue before that singer's block; repeated cues before every line are unnecessary. Place the ownership cue after instrumental cues immediately before its words. Following an instrumental interlude, assign the next singer again.

Do not print plain Male:, Female: or character names before sung lines. Do not stack male/female cues before an unallocated block. [Duet] is for simultaneous leads, with unison/harmony/octaves specified in Styles; call-response requires separate assigned blocks.

```text
[Verse 1]
[Synth: sparse motif answers]
[Male Vocal]
{Male verse lines}
[Chorus]
[Synth: full main motif]
[Female Vocal]
{Female chorus lines}
[Bridge]
[Male Vocal]
{Male statement}
[Female Vocal]
{Female answer}
[Chorus]
[Duet]
{Shared final chorus lines}
```

Placeholders illustrate organization and must be replaced before export.

## Lead and support

Lead owns the principal line; backing supports it; duet means shared leads. Describe male lead/female backing explicitly in Styles. A short [Backing Vocals: female, soft harmony] does not change ownership of the lead block. Backing with separate words receives its own assigned block, followed by explicit lead return; parentheses alone do not guarantee routing.

Chops/ad-libs also receive a source and purpose. Avoid simultaneously whispered/shouted instructions for the same voice/passage. Describe sound rather than a reference singer's identity, including INFO/Exclude. A words-only remix preserves the cast; a voice edit updates Styles and affected Lyrics blocks together.

## Interaction checks

| Scenario | Required clarity |
|---|---|
| Male verse / female chorus | Matching global allocation and explicit section ownership |
| Question/answer | Assigned handoffs with meaningful responses, not automatic alternation |
| Lead + backing words | Separate support block and explicit return |
| Lead + wordless harmony | Stable supporting cast without turning both into leads |
| Same-gender duet | Stable register/timbre contrast; no invented official Singer A/B control |
| Solo → choir/gang/unison | Ensemble role/location distinct from individual lines |
| Chops/ad-libs/nonverbal | Stable source, words/intentional syllables distinguished from sound directions |

Review every performed line for owner, backing, simultaneous singing and next handoff. Simple helper male/female checks do not validate all scenarios. If Suno confuses roles, simplify blocks/FX while preserving required cast, words and characters; agree any user-specified allocation change.

Voice tags/modifiers are working markup with estimated risk, not official singer routing. [Suno Vocal Gender](https://help.suno.com/en/articles/10153473) supports voice selection/Styles characteristics, not guaranteed per-line control.
