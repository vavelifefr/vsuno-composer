# Contextual negative styles

Every full parser chunk requires nonempty Exclude on the second MO line. Derive exclusions from this track, not a fixed blacklist. See [PARSER_spec.md](../references/PARSER_spec.md).

1. Identify the positive boundary: main style/blend and permitted parent categories, groove, era, arrangement, voices and instruments.
2. Select plausible neighboring directions that would contradict it: a related but wrong rhythm, era, form, aggression or acoustic/electronic character. Each candidate must prevent a specific unwanted departure from this composition; unrelated genre names do not qualify.
3. Rank by relevance and remove duplicates. Use the target range for the chosen Lyrics detail in [INTAKE_flow.md](INTAKE_flow.md#automatic-more-options-and-exclude-targets), independently of Styles detail or field length. These are flexible ranges: never add random/unrelated styles to meet a minimum. If fewer valid neighbors exist, keep the meaningful set and briefly explain the smaller count outside the chunk.
4. Check that no target style, necessary parent category, requested blend, voice, rap passage or instrument is excluded. Specific neighboring substyles are preferable to a broad exclusion that also removes a desired component.

Instrument/performance exclusions may supplement style exclusions, but do not count them as distinct anti-styles; no vocals alone does not fulfill the negative-style requirement. Keep positive descriptions in Styles and negatives in Exclude. Avoid contradictory lists such as synthpop paired with excluded pop when its relevant parent qualities are needed. Random full-freedom profile selection still requires semantic exclusions for the resulting concept, not random exclusions or a permanent blacklist.

## Conditional examples

| Requested boundary | Possible exclusions | Protect |
|---|---|---|
| Melodic house without hard drops | hardstyle, hard techno | Needed house/electronic elements |
| 1990s eurodance, male rap and female chorus | trap, big room EDM, acoustic ballad | Rap and pop-derived song form |
| Early rave with breaks and hoover | big room house, psytrance | Rave, techno and breakbeat elements |
| Chamber acoustic ballad | hardstyle, trap | Any explicitly requested hybrid elements |

These are examples, not automatic presets. Preserve explicit user Exclude values unless they conflict with the positive request; resolve the intended priority rather than silently replacing them. A lyric-subject revision normally preserves Exclude. Update only when musical scope changes or a contradiction requires an authorized repair.
