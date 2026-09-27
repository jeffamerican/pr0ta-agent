# Seed Audio 1.0 on PR0TA

Read this when the resolved `dialogue_model` is Seed Audio 1.0
(`bytedance/seed-audio-1.0`). Seed Audio renders a whole sound brief as one
take: dialogue plus the room tone, ambience, music and effects you describe.
Prompt order by operation (text-to-audio, audio-reference, image-to-audio) is in
`pr0ta-prompting` → `reference/model-modality-guides.md` → "Seed Audio 1.0".
Confirm fields with `models_get_defaults(model_id)`.

## Request contract

| Field | Contract |
|---|---|
| `prompt` | Required. At most 2,048 characters; longer prompts are rejected, not truncated. On `generation_submit` the `text` you send becomes the prompt. |
| `audio_urls` | Up to 3 reference clips. The prompt names them by order: `@Audio1`, `@Audio2`, `@Audio3`. |
| `image_url` | One reference image. Cannot be combined with `audio_urls`. |
| `voice` | A preset voice name or cloned voice id. |
| `speed`, `volume` | Multipliers from 0.5 to 2. |
| `pitch` | Semitones from -12 to 12. |
| `output_format`, `sample_rate` | `mp3`, `wav`, `pcm` or `ogg_opus`; 8,000 to 48,000 Hz. |

Pass `audio_urls`, `image_url`, `speed`, `volume` and `pitch` inside
`voice_settings` on `generation_submit`; PR0TA forwards the fields the model's
schema defines.

Use one kind of voice source per request: reference clips, one reference
image, or one preset voice. PR0TA rejects `audio_urls` together with
`image_url`. A request carries at most one preset voice, and scene rendering
never mixes a preset voice with reference clips, so for a multi-speaker take
either give every speaker a reference clip or describe the voices in writing.

## Writing a Seed Audio prompt

Write a production brief in playback order: what the take is, the space, who
speaks, their exact lines, then ambience, music and effects, then how it ends.
Bind each reference to one job.

```text
Generate one continuous cinematic audio take in English. Keep dialogue clear and natural.
Include bracketed sound effects, room tone, music, pauses, and delivery notes as audio direction; do not speak bracketed cues or speaker labels.

Voice references:
- MARA: match @Audio1
- JONAS: match @Audio2

Audio script:
MARA (voiced by @Audio1) says: "[low, urgent] [rain on a tin roof] They're already inside."
JONAS (voiced by @Audio2) says: "[a long pause] Then we go out the back."
```

- Bracketed cues are direction, not words. Put them before the line they shape.
- Without a reference, describe each speaker's voice in a few words (age,
  timbre, accent, energy) and keep that description identical across requests.
- Keep reference clips short and clean: in scene rendering PR0TA uses only the
  first clip per speaker and trims it to under 30 seconds.

## Scene dialogue with Seed Audio

When a scene is rendered through the Performances path (`pr0ta-audio` → "Scene
dialogue takes") with Seed Audio, PR0TA builds the prompt above from the
scene's lines, speaker voices and cues, splits the scene into requests that fit
the 2,048-character prompt, about two minutes of speech, and the voice-source
rules above (keeping coached beats together where they fit), renders each
variant, and joins the parts into one take per variant. More splits mean more
seams: a scene whose speakers share one kind of voice source (all reference
clips, at most three speakers) renders in fewer, more continuous requests.

## Checks

- Listen for spoken cue text or speaker labels; if a take reads them aloud,
  move the direction into brackets or shorten it.
- Transcribe the take (`pr0ta-audio` → "Time-indexing") before cutting on its
  words; effects and music in the take do not index as words.
- A mixed take (dialogue with effects and music) is harder to rebalance in the
  timeline. When the mix must be adjusted later, render dialogue-only takes and
  add music and effects as separate assets (`pr0ta-music`).
