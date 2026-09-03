# Wan 3.0 and Wan 3.0 Prime

**Start here:** read this file before writing a prompt or payload for any `muapi/wan3.0-*` or `alibaba/wan-3.0-prime/*` video model. Wan 3.0 uses natural-language reference roles and default-on generated audio. Do not transfer Seedance or Kling tokens, and do not mix MuAPI and Fal field names.

Official sources: [MuAPI Wan 3.0 family](https://muapi.ai/wan-3), [text-to-video](https://muapi.ai/playground/wan3.0-text-to-video), [image-to-video](https://muapi.ai/playground/wan3.0-image-to-video), [reference-to-video](https://muapi.ai/playground/wan3.0-reference-to-video), and Alibaba's [Wan 3.0 release](https://modelstudio.console.alibabacloud.com/model-releases/wan3.0-video) and [API reference](https://help.aliyun.com/en/model-studio/wan3-video-generation-api-reference). Alibaba's [Wan prompting guide](https://www.alibabacloud.com/help/en/model-studio/text-to-video-prompt) supplies useful family-level technique, but its sound, multi-shot, and reference sections currently name Wan 2.5–2.7 rather than Wan 3.0. Treat those sections as transferable craft guidance, not proof of a Wan 3.0 feature.

## Exact Model and Modality Contract

| Operation | Standard model | Prime model | Required inputs | Optional guidance |
|---|---|---|---|---|
| Text-to-video | `muapi/wan3.0-text-to-video` | `muapi/wan3.0-prime-text-to-video` | `prompt` | None |
| Image-to-video | `muapi/wan3.0-image-to-video` | `muapi/wan3.0-prime-image-to-video` | `prompt`, opening image | `last_image` terminal frame |
| Reference-to-video | `muapi/wan3.0-reference-to-video` | `muapi/wan3.0-prime-reference-to-video` | `prompt` | Up to 10 images, 5 videos, and 5 audios |

Fal-native Prime uses `alibaba/wan-3.0-prime/{text,image,reference}-to-video`. Its I2V field is `start_image_url` with optional `end_image_url`; R2V uses `reference_image_urls`, `reference_video_urls`, and `reference_audio_urls`. Fal also exposes `audio`, `enable_thinking`, and `enable_prompt_expansion`; optional R2V `file_url` or `web_url` requires `enable_thinking: true`. Keep these routes distinct from MuAPI's `image_url`/`last_image`, `images_list`/`videos_list`/`audios_list`, `enable_audio`, and `thinking_mode` contract.

Use the dedicated T2V route for prompt-only work even though the provider-native R2V arrays are optional. R2V is the deliberate multimodal-reference branch, not a substitute T2V endpoint.

Prime is a drop-in higher-fidelity tier with the same request shape. Use standard Wan 3.0 while discovering motion, timing, framing, and sound direction; promote an approved prompt and reference package to Prime for hero shots or delivery candidates when sharper detail and steadier motion justify the higher cost.

## Shared Controls

| Field | Contract | Default |
|---|---|---|
| `resolution` | `480p`, `720p`, `1080p` | `720p` |
| `aspect_ratio` | `16:9`, `9:16`, `1:1`, `4:3`, `3:4` | `16:9` |
| `duration` | Whole seconds from 2 through 30 | `5` |
| `thinking_mode` | Boolean; use for genuinely complex prompts | `false` |
| `enable_audio` | Boolean generated-audio control | `true` |
| `seed` | Integer; `-1` requests a random seed | `-1` |

A fixed seed can support controlled iteration, but do not promise bit-identical reproduction. Wan 3.0 has no documented negative-prompt field. Query `models_get_defaults` before submission rather than treating this prose reference as the live schema.

## Model Selection

- **No visual authority and the shot is intentionally exploratory:** T2V.
- **One approved image must own frame zero:** I2V.
- **An approved terminal frame matters:** I2V with `last_image`; this is not a separate first/last endpoint.
- **Several image, video, or audio authorities must shape one shot:** R2V.
- **Exact reusable character tokens or persistent identity resources are required:** use a verified consistency system instead. Wan R2V references are shot inputs, not persistent trained characters.
- **Silent post-production workflow:** set `enable_audio: false`. Do not rely on omission or prose such as "no sound" because audio defaults on.

## Text-to-Video Prompting

Write one chronological audiovisual shot:

`framing and setting -> subject and action -> camera path -> dialogue/sound -> final visible state`

Name the subject, environment, physical action, motion speed or intensity, and the one camera path that matters. Describe lighting, lens, or style only when they change the intended result. Keep the number of beats proportional to `duration`; a long list of actions does not become more feasible because the route permits 30 seconds.

Example:

```text
Medium-wide night exterior outside a rain-soaked neighborhood cinema. A woman in
a red wool coat crosses the empty sidewalk, pauses beneath the flickering marquee,
and looks through the locked glass doors. The camera tracks beside her, then makes
a slow push-in as she realizes the lobby lights are still on. Rain strikes the
awning, distant traffic passes, and a low electrical hum comes from the sign. End
on her reflection overlapping the illuminated lobby.
```

## Image-to-Video Prompting

The opening image already defines the subject, scene, composition, and style. Spend the prompt on what changes after frame zero:

`motion onset -> causal action -> camera evolution -> sound -> end state`

- State what begins moving and what must remain visually stable.
- Use one dominant camera path and a readable action arc.
- If `last_image` is present, describe the physical progression that lands on it rather than introducing it as an unrelated scene.
- Do not waste prompt space reconstructing visible details unless a trait must remain locked through motion.

Example:

```text
The subject lifts her eyes toward the window as wind gradually moves the curtains
and loose strands of hair. The camera makes a restrained clockwise orbit while the
room's warm practical lights dim into cool dawn light. Floorboards creak softly and
the curtains rustle. End with her facing the window in the supplied final frame.
```

## Reference-to-Video Prompting

Finalize array order first, then write a plain-language reference-role ledger. Reference numbering is separate within each media array.

```text
The first reference image controls the lead's face, hair, and red coat. The second
reference image controls the cinema lobby and marquee design. The first reference
video controls walking pace and the lateral tracking camera. The first reference
audio controls rain intensity and the sign's electrical hum.
```

After the ledger, write the chronological action, camera, sound relationship, and landing state. Give each reference one primary job. Video references should control a named contribution such as performance, blocking, camera, or pacing; audio references should control a named timing, voice, ambience, or sound-character contribution.

Provider limits:

- Up to 10 `images_list` entries.
- Up to 5 `videos_list` entries.
- Up to 5 `audios_list` entries.
- Each reference video is 1–15 seconds.
- Total reference-video duration plus requested output duration must not exceed 30 seconds.
- Total reference-audio duration must not exceed 15 seconds.

Do not invent `@imageN`, `@videoN`, `@audioN`, `@ElementN`, trained-character syntax, or a negative-prompt field.

## Audio Direction

When `enable_audio` is true, describe audible events in playback order beside their visible causes:

- Dialogue: named speaker + short line + emotion + tone + speed + timbre/accent when important.
- Sound effects: source material + action + resulting sound + surrounding ambience.
- Music: score presence + style + intended narrative function.

Keep visible-speaker dialogue short and inspect every take for wording, speaker attribution, lip sync, ambience, and mix. Exact scripted wording and phoneme-level lip sync are not reliable enough to promise; use separate TTS plus a verified lip-sync workflow when exact performance is mandatory. Every speech-bearing Wan result must pass the Scribe V2 transcription gate before timeline editing. Instrumental-only results must pass music analysis.

## Typography and On-Screen Copy

Wan 3.0 advertises advanced multilingual text rendering and is a valid candidate for native titles, signs, charts, formulas, infographics, and motion typography. Do not reject this approach merely because older video models struggled with text. Exactness is still take-dependent, so treat capability and acceptance as separate questions.

Put the literal copy early in the prompt and in quotation marks. Specify language, placement, type style, size hierarchy, contrast, motion, and how long the finished text must hold unchanged. Keep each animated unit short enough to read and say `no additional words` when appropriate.

For I2V, the source still may establish the typography while the prompt defines its animation. State which letters or design elements move and which copy remains unchanged. For R2V, give the typography reference one explicit role rather than expecting general reference conditioning to preserve every glyph.

Inspect every frame for spelling, substitutions, extra glyphs, temporal flicker, and readability at delivery resolution. Generate alternatives when needed. If legal, credit, or brand-critical text fails, use a verified premium image result and deterministic timeline animation; that fallback does not make native Wan typography an invalid production choice.

## Thinking Mode

Enable `thinking_mode` when the shot contains multiple subjects, several causal actions, an optional terminal frame with a difficult transition, or several references with distinct roles. Leave it off for simple drafts and do not use it as a repair for conflicting direction, overloaded choreography, or ambiguous reference ownership.

## Unsupported or Unverified Claims

Do not claim any of the following without a newer Wan 3.0-specific source or field test:

- Timestamped native multi-shot grammar from Wan 2.6/2.7.
- Exact dialogue preservation or exact lip sync.
- Persistent characters, LoRAs, or trained identity tokens.
- Negative prompts or Seedance/Kling positional tokens.
- Bit-identical generation from a fixed seed.
- Coming-soon Wan image, image-edit, or Spicy endpoints as available PR0TA routes.

## Production Check

Before approval, verify the opening authority, motion arc, camera path, reference-role adherence, terminal-frame landing when present, audio presence or intentional silence, dialogue wording/sync, actual duration, and output resolution. For exact unified payloads, read `video-reference-field-matrix.md`.
