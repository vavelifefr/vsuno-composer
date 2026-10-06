# Highlighted lyrics: a separate read-only view

Triggered by an explicit request to highlight/show highlighted lyrics or their translation. Read the selected source under REVISION_flow; preserve words, section order, ownership and essential delivery. Translate only when requested, using the requested/default translation mode. Do not create a new song, ID or archive.

Use lyrics_view semantics: remove identified production/chord/drum cues, keep performed/quoted hook/backing words, preserve original lines and voice-switch order. Unknown/ambiguous cues require semantic review. A complete field or parser chunk retains its musical instructions.

Preferred: standalone HTML with readable line breaks; prominent mint words and muted gray-blue cues on dark background, dark-green words on light background. Use semantic text/cue blocks and safe escaped text, not untrusted HTML from lyrics. A Copy text control copies ordinary minimal text with sections/roles and no HTML/parser fields. If clipboard access fails, provide/select ordinary text for manual copying.

Markdown fallback: cues as inline code, performed words bold. Do not promise exact colors or clean clipboard content across chat renderers; provide ordinary structured text when requested. A plain-words request explicitly removes cues.

The complete parser chunk remains one uncolored text block. Highlight view never substitutes for it. Local helper text --highlight --output <new.html> writes only the view, does not translate or launch model/browser; no overwrite. --plain and --highlight are mutually exclusive. Colors/styles are presentation, not music instructions.
