# ElevenLabs v3 Audio Tags

Read this when the resolved `dialogue_model` is ElevenLabs v3 (`eleven_v3`),
or when a scene dialogue take renders on it. Prompt guidance for the family is
also in `pr0ta-prompting` → `reference/model-modality-guides.md` →
"ElevenLabs V3".

## Voices

Use an ElevenLabs `voice_id`: from `voices_list(provider: "elevenlabs")`
(copy `selection.voice_id`), from the cast, or from `voices_clone` /
`voices_design_commit`. Do not decide v3 compatibility from voice metadata
(`high_quality_base_model_ids`, `verified_languages`); ElevenLabs changes v3
support without updating those fields. Submit with the voice; if v3 rejects it
with a model-compatibility error, tell the user and offer another voice, or
another model from `models_list(modality: "dialogue_model")` that the voice
supports.

## Syntax

Eleven v3 interprets words in square brackets as performance directions. Tags are v3-specific; older ElevenLabs models ignore them.

Place tags inline in the text, before or within the speech they modify:

```text
[sorrowful] I couldn't sleep that night... [quietly] And suddenly, that's when I saw it.
```

Tags can be combined:

```text
[hesitant][nervous] I... I'm not sure this is going to work. [gulps]
```

## Tag Reference

**Emotional states:** `[excited]`, `[nervous]`, `[frustrated]`, `[sorrowful]`, `[calm]`, `[angry]`, `[sad]`, `[cheerfully]`, `[flatly]`, `[deadpan]`, `[playfully]`, `[annoyed]`, `[flustered]`, `[casual]`, `[tired]`, `[curious]`, `[resigned]`

**Reactions and human sounds:** `[sigh]`, `[laughs]`, `[gulps]`, `[gasps]`, `[whispers]`, `[shouts]`, `[clears throat]`, `[soft chuckle]`, `[crying]`, `[breathes]`, `[swallows]`

**Delivery and pacing:** `[pause]`, `[continues after a beat]`, `[rushed]`, `[slows down]`, `[deliberate]`, `[rapid-fire]`, `[stammers]`, `[drawn out]`, `[timidly]`, `[emphasized]`, `[understated]`, `[continues softly]`, `[hesitates]`

**Narrative tone:** `[dramatic tone]`, `[lighthearted]`, `[reflective]`, `[serious tone]`, `[conversational tone]`, `[sarcastic tone]`, `[wistful]`, `[matter-of-fact]`, `[awe]`

**Character and accent:** `[British accent]`, `[Australian accent]`, `[Southern US accent]`, `[French accent]`, `[American accent]`, `[childlike tone]`, `[fantasy narrator]`, `[sci-fi AI voice]`, `[classic film noir]`

**Sound effects, experimental:** `[gunshot]`, `[applause]`, `[explosion]`, `[leaves rustling]`, `[gentle footsteps]`, `[clapping]`

## Dialogue

Tag the emotional shift, not just the base emotion:

```text
[excited] You won't believe what I found down there!

[skeptical][dry] Let me guess -- another "ancient artifact" that turns out to be a pipe fitting.

[defensive] No, this is different. [quieter, more serious] This one was moving.
```

Use reaction tags between lines for conversational texture. Use dashes for interruptions and ellipses for trailing thoughts.

## Narration

Set a base tone at the start of a passage, then add moment-specific tags sparingly:

```text
[reflective] I never thought I'd say this, but... [pause] maybe the machine was right.

[building intensity] The signal was getting stronger. Every reading confirmed what we'd feared.
[whispers] And then -- silence. Complete, absolute silence.

[awe] When I opened my eyes, the sky had changed color.
```

Use `[pause]` and `[continues after a beat]` for dramatic pacing when punctuation is not enough.

## Punctuation

Eleven v3 treats punctuation as implicit delivery direction:

- Ellipses create pauses and trailing-off effects.
- Dashes create abrupt stops and interruptions.
- Caps add emphasis to specific words.
- Exclamation marks increase energy; question marks add rising inflection.
- Short sentences speed up pacing; long flowing sentences slow it down.

## Constraints

- SSML is not supported in v3. Do not use `<break>`, `<phoneme>`, or other SSML tags.
- Voice selection matters more than tags. Match the voice to the emotional range you need.
- Professional Voice Clones are not optimized for v3. Use Instant Voice Clones or prompt-designed voices for better tag responsiveness.
- Tags are suggestive, not deterministic. Regenerate if a take does not land.
- Stability affects expressiveness. Higher stability is more consistent but less dynamic.
- Single-voice TTS takes up to 5,000 characters per call. Scene dialogue requests (Text to Dialogue) take at most 2,000 characters and 10 distinct voices each; PR0TA splits a scene to fit and joins the parts. In scene lines, SSML `<break>` tags become ellipses and line `cues` become leading tags.
