# Parts, patterns, articulation and effects

Choose audible decisions rather than treating this vocabulary as official tags. Distinguish source/device, role, timbre, pattern and action; specify only useful layers. Example: TB-303 resonant offbeat bass, filter opens before the drop.

## Rhythm and low end

| Term | Meaning / distinction |
|---|---|
| Four-on-the-floor | Quarter-note kick, usually in 4/4; not the only house/techno pattern |
| Backbeat | Usually snare/clap accents on beats 2 and 4, independent of kick rate |
| Offbeat | Between principal beats; applies to bass, hats or stabs without changing meter |
| Syncopation | Accents displaced from or opposing strong beats; identify the part |
| Swing / shuffle | Unequal subdivisions; choose the groove rather than impose a genre rule |
| Breakbeat | Broken drum pattern, distinct from a Break section; request original chopped breaks rather than a third-party recording |
| Half-time / double-time feel | Perceived pulse changes at the same BPM, not necessarily a tempo change |
| Sub bass | Low-frequency foundation, possibly paired with an audible upper layer |
| Reese bass | Detuned moving bass character, not a universal device model |
| Rolling / offbeat bass | Frequent continuous motion versus between-beat placement |
| Walking bass | A steady pulse, commonly quarter notes, connecting chord tones with scalar/chromatic approaches and purposeful leaps; not random notes or exclusively stepwise motion |

Walking-bass terminology is supported by M08 in [SOURCES_lib.md](SOURCES_lib.md); prompt choices remain design guidance.

## Theme and texture

Lead carries a foreground phrase; pad sustains a harmonic texture; pluck describes short attack; stab is a short chord accent. They are roles/timbres, not genres or synthesizer names. An instrument can change roles.

Riff: recognizable short phrase. Ostinato: persistent repeated figure. Arpeggio: successive chord tones. Step sequence: programmed event order. Do not swap these terms for cosmetic variety. A hook can be vocal or instrumental.

Legato connects notes; staccato separates them. Portamento slides between pitches; pitch bend changes pitch as a gesture. Vibrato varies pitch; tremolo varies amplitude. Flutter-tonguing belongs to wind articulation rather than a synth control. Choose guitar muting, strumming, fingerpicking and bends by function. These descriptions do not guarantee exact Suno performance.

## Effects and filters

| Effect | Audible purpose |
|---|---|
| Low-pass sweep | Timbre gradually opens/closes, often around build/breakdown |
| Resonance / acid squelch | Resonant emphasis attached to the bass figure |
| Delay | Rhythmic response, short slap or long echo |
| Reverb | Close/dry versus spacious tail; plate/hall-like as sound targets |
| Gated reverb | Truncated spatial tail, often a drum accent |
| Chorus / detune | Thickness/motion, not necessarily a new melody |
| Saturation / distortion | Soft density or rough attack attached to a part |
| Sidechain-like pumping | Audible rhythmic breathing between kick and layers, not guaranteed routing |
| Bitcrush / sample grain | Digital or sampled texture |
| Riser / downlifter / reverse tail | Purposeful preparation or tail, not every boundary |

Effects are allowed; do not inherit the old blanket prohibition on reverb/delay/EQ/sidechain. Exact plugin chains, Hz, MIDI and timecodes are unnecessary by default and do not guarantee precise automation. Requested specifics remain wishes with honest limits.

## Emotion into music

Nostalgia: recognizable theme, appropriate era palette, softened articulation/space, without compulsory vinyl noise. Tension: unresolved motif, pauses, density or sharp accents, without compulsory faster BPM. Uplift: clear arrival, opening texture or melodic rise, without compulsory major key. Intimacy: close voice, fewer competing parts and natural phrases. Connect the desired feeling to an audible cause.

## Harmony and notation

Added 2026-10-04. S02 explains musical terms; S10 supports describing harmony/instruments and using an audio input with a progression, not guaranteed exact reproduction. ChordPro inline brackets are documented by M01; Suno support was not confirmed. Risk/syntax: [SUNO_TAGS_lib.md](../references/SUNO_TAGS_lib.md). Harmonic development: [HARMONY_lib.md](../references/HARMONY_lib.md); interaction: [ARRANGEMENT_lib.md](../references/ARRANGEMENT_lib.md).

Harmony supports the motif. Relate key/mode, progression, harmonic rhythm, source/register/articulation and section development. Bass may use roots, inversions, passing notes or an independent line. Melody may create tension and resolution beyond current chord tones.

| Notation / concept | Use |
|---|---|
| Am, F, C, G | Chord names; m means minor. First chord alone does not establish tonic |
| Am7, Fmaj7, E7 | Different harmonic colors; maj7 and dominant 7 are not interchangeable |
| C/G | C chord with G in bass, not two sequential chords or a complete voicing |
| i - VI - III - VII | Relative notation needs an established mode/center; not special Suno syntax |
| Sustained chords / arpeggiated harmony / short chord stabs | Different articulation of potentially identical harmony |
| Slow harmonic changes / pedal bass / delayed resolution | Less exact alternatives when notation is unnecessary or risky |

Styles may include a target A-minor progression Am - F - C - G and sustained synth chords supporting the motif; this original example is not a default. Preserve requested chords; a non-diatonic chord may be borrowing/tension rather than error. Mark uncertain analysis instead of inventing certainty.

In Lyrics mark meaningful changes: held intro harmony, bridge movement, chorus return. Do not annotate every syllable or assign every section a new progression. Bars/pipes and chord count do not determine duration or meter. Exact harmony as an acceptance criterion requires listening and possibly the user's own audio/editing workflow; do not launch/upload audio or promise retention without authorization and evidence.

## Drums as events

Choose the function, then necessary kit elements, pattern, era/timbre and entrance/withdrawal. A machine name does not establish the groove; an era does not require one device.

| Event | Clarification |
|---|---|
| Drum-machine intro | For drums alone, defer bass/voice/lead and mark their later entrances |
| Four-on-the-floor re-entry/drop | Quarter-note kick returns; choose snare/clap/hats/bass independently |
| Gated snare fill | Short snare figure plus truncated reverb; not a device identity |
| Snare roll | Repeated growing figure, distinct from any fill; a brief rest may separate the next attack |
| Drum-machine bridge | Specify rhythm contrast, absence of lead vocals and remaining parts separately |
| Funky drum break | Syncopated episode; drums alone and drums-plus-bass differ; not necessarily chopped samples |

Global kit/groove belongs in Styles; local action under existing Lyrics sections. Examples: [Intro] with [Drums: solo drum machine groove], [Drop] with [Drums: four-on-the-floor kick returns], or [Transition: brief gated snare fill]. Estimated medium-risk DESIGN cues, not official commands or a required combination.

For a local drums/bass-only passage, describe withdrawal and vocal/theme return without setting global no vocals or excluding vocals from a vocal song. Keep instrumental passages separate from performed lines. Exact beat/bar placement is a target until heard. Feedback repairs only the conflicting event while preserving words, cast and main motif.
