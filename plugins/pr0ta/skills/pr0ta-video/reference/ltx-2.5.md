# LTX 2.5 on Fal

Use this reference for the six canonical LTX 2.5 routes in PR0TA. Choose Pro or Fast and the exact T2V, I2V, or audio-to-video operation before writing the payload. PR0TA aliases these Fal endpoints internally; submit the canonical `lightricks/ltx-2.5/` model IDs without adding `fal-ai/`.

## Contents

- [Endpoint selector](#endpoint-selector)
- [T2V and I2V contracts](#t2v-and-i2v-contracts)
- [Audio-to-video contract](#audio-to-video-contract)
- [Prompt method](#prompt-method)
- [Operation templates](#operation-templates)
- [Camera and audio control](#camera-and-audio-control)
- [Typography and designed text](#typography-and-designed-text)
- [Failure repair](#failure-repair)
- [Authority and sources](#authority-and-sources)

## Endpoint Selector

| Operation | Pro | Fast |
|---|---|---|
| Text-to-video | `lightricks/ltx-2.5/text-to-video/pro` | `lightricks/ltx-2.5/text-to-video/fast` |
| Image-to-video | `lightricks/ltx-2.5/image-to-video/pro` | `lightricks/ltx-2.5/image-to-video/fast` |
| Audio-to-video | `lightricks/ltx-2.5/audio-to-video/pro` | `lightricks/ltx-2.5/audio-to-video/fast` |

Select **Pro** for the strongest final-render fidelity at 720p/1080p and a 6/8/10-second shot. Select **Fast** for iteration, 12–20-second work, or 1440p/2160p delivery where its duration/FPS matrix allows it. Use audio-to-video when a finished source audio file must own timing and remain in the output.

Current LTX 2.5 Fast and Pro support only T2V, I2V, and A2V. They do **not** support Retake, Extend, or Reframe. Those operations belong to LTX 2.3 Pro in Lightricks' current compatibility matrix and are not part of PR0TA's six LTX 2.5 Fal routes. Never relabel an LTX 2.3 operation as LTX 2.5; resolve the exact current model before dispatch.

## T2V and I2V Contracts

Shared generation fields:

- `prompt` is required.
- `generate_audio` defaults to `true`.
- T2V aspect ratio is `16:9` or `9:16`.
- I2V requires `image_url` and accepts `aspect_ratio: "auto" | "16:9" | "9:16"`.
- I2V optionally accepts `end_image_url`. Do not combine an end image with automatic duration selection.
- Current camera motion values are `dolly_in`, `dolly_out`, `dolly_left`, `dolly_right`, `jib_up`, `jib_down`, `static`, and `focus_shift`.

### Pro

- `duration`: `"auto"`, 6, 8, or 10 seconds.
- `resolution`: `720p` or `1080p`; default `1080p`.
- `fps`: 24, 25, or 50; default 25.

### Fast

Fast accepts even durations from 6 through 20, but not every resolution/FPS combination supports the full range:

| Resolution | FPS | Valid duration |
|---|---|---|
| 720p / 1080p | 24 / 25 | 6, 8, 10, 12, 14, 16, 18, 20 |
| 720p / 1080p | 48 / 50 | 6, 8, 10 |
| 1440p / 2160p | 24 / 25 / 48 / 50 | 6, 8, 10 |

Do not infer that Fast's 20-second ceiling applies at 4K or high frame rate. Validate the exact triple of resolution, FPS, and duration before submission.

## Audio-to-Video Contract

Audio-to-video is a distinct modality, not I2V with an audio reference.

- `audio_url` is required and the source audio owns timing, rhythm, energy, and the output soundtrack.
- Omit a separate `duration`; A2V derives output timing from the source audio.
- `image_url` is optional. With an image, use it as frame-zero visual authority.
- `prompt` is required when no image is supplied and optional when an image supplies the scene. Even when optional, add a concise motion/camera prompt when the desired performance is not obvious.
- `guidance_scale` defaults to 5 for prompt-led/no-image work and 9 for image-conditioned work.
- Aspect ratio is `auto`, `16:9`, or `9:16`.
- The checked Fal surface accepts 2–20-second source audio, while current Pro documentation caps Pro output at 10 seconds. Cap Pro work at 10 seconds and query live defaults before dispatch; use Fast for a longer eligible source.
- PR0TA's checked Fal A2V schemas do not expose T2V/I2V `resolution`, `fps`, `camera_motion`, or `end_image_url`. Do not send them unless the live selected route begins exposing them.

Minimal prompt-led A2V:

```json
{
  "generator": "video",
  "mode": "audio_to_video",
  "model": "lightricks/ltx-2.5/audio-to-video/fast",
  "audio_url": "https://.../approved-performance.wav",
  "prompt": "A close three-quarter portrait of the singer in a small amber rehearsal room. Her visible breath, phrasing, and restrained hand movement follow the supplied vocal performance while the camera makes a slow dolly in.",
  "aspect_ratio": "16:9",
  "guidance_scale": 5
}
```

## Prompt Method

LTX recommends a concrete audiovisual description, normally four to eight sentences for a simple shot:

1. **Shot** — scale, viewpoint, lens feel, and initial camera relationship.
2. **Scene** — location, time, light logic, palette, weather, and texture.
3. **Subject** — stable physical description, wardrobe, and props.
4. **Chronological action** — visible action and reaction in causal order.
5. **Camera relative to subject** — say what the camera does and how the subject changes within frame.
6. **Audio** — ambience, effects, dialogue/singing, music, and silence.
7. **Landing** — exact final physical and emotional state.

Express emotion physically: posture, breath, eye line, pace, grip, and facial tension. Avoid abstract labels such as “sad” without visible behavior.

For native multi-shot, write chronological prose and name each cut. Prefer 2–4 shots. After each cut, re-establish the subject identifier, framing, light, and audio continuity; do not rely on “same person” alone.

## Operation Templates

### Text-to-video

```text
Medium-wide eye-level shot inside a coastal bus shelter at dawn. A courier in a faded orange rain jacket stands beside a silver bicycle under cold fluorescent light. Wind drives mist across the road as she checks a folded map, hears an approaching engine, and steps toward the curb. The camera dollies left with her while keeping the bicycle in the foreground. Wet tires hiss on asphalt; the shelter roof rattles; no music. End with the bus headlights filling the glass behind her.
```

### Image-to-video

```text
The supplied image owns frame-zero identity, wardrobe, composition, and light. The subject inhales, tightens her grip on the paper, then looks toward the window as the curtain lifts in a steady draft. The camera makes a restrained dolly in relative to her face while the background remains spatially stable. Preserve the blue coat, silver ring, face, and warm window light. Quiet room tone and cloth movement; no music. End on her resolved gaze toward the window.
```

When `end_image_url` is present, append:

```text
Progress through one plausible continuous action and land exactly on the supplied end image without an early morph or a second ending.
```

### Audio-to-video

```text
Close portrait of a baritone singer in a dark recording room, lit by one soft overhead practical. His breath, mouth movement, gaze, and small shoulder shifts follow the supplied vocal track exactly. The camera stays nearly static with a subtle focus shift from the microphone grille to his eyes during the sustained phrase. Preserve the supplied audio without added music or effects. End on the final breath and held eye line.
```

### Native multi-shot

```text
Shot 1: Medium-wide view of Mara in her charcoal coat waiting beneath the station clock, cold dawn light and low platform ambience. She sees the arriving train and closes the notebook in her left hand. Cut to Shot 2: Close profile of Mara, preserving the same coat, silver lapel pin, dawn light, and train ambience; the camera tracks with her as she walks. Cut to Shot 3: Over-shoulder view from behind Mara as the carriage door opens; preserve her silhouette and screen direction, let the brakes release with a soft hiss, and end as she steps aboard.
```

## Camera and Audio Control

Use `camera_motion` only when the route exposes it and the shot needs one dominant move. Keep prompt prose compatible with the structured value:

| Value | Prompt relationship |
|---|---|
| `dolly_in` / `dolly_out` | Move camera toward/away from the subject; do not describe a conflicting zoom. |
| `dolly_left` / `dolly_right` | Translate laterally and state how subject placement changes in frame. |
| `jib_up` / `jib_down` | Move vertically and describe the reveal or compression it creates. |
| `static` | Keep camera locked; motion must come from subject/environment. |
| `focus_shift` | Name the foreground and background focus targets in order. |

For generated dialogue or singing:

- Quote exact words and identify speaker, language, accent, and delivery.
- Keep the line proportional to duration.
- Describe visible delivery and reduce competing action.
- Separate dialogue, ambience, effects, and music in the prose.
- Set `generate_audio: false` when exact wording or an isolated post-production mix matters more than native sync.
- Transcribe every speech-bearing generated result before timeline placement.

## Typography and Designed Text

Lightricks documents stronger typography in LTX 2.5, so it is a valid candidate for generated signs, interface copy, titles, and designed text that belongs inside an audiovisual shot. Put the exact copy in quotation marks, define its placement, type treatment, motion, and unchanged hold interval, and request no additional words when appropriate.

Treat exactness as take-level acceptance rather than a guaranteed field contract. Inspect every frame for spelling, substituted glyphs, line-break drift, flicker, and readability. If the selected take fails, simplify the copy or motion, fan out alternatives, try an approved text-bearing I2V start frame, or use a verified still and deterministic timeline animation.

## Failure Repair

| Symptom | Repair |
|---|---|
| Fast request rejected | Check the exact resolution/FPS/duration row; do not validate each field independently. |
| Pro request longer than 10s | Use Fast when its matrix supports the desired output or split at a natural edit. |
| I2V frame drifts immediately | Stop redescribing the image; state frame-zero authority and prompt only motion/camera/audio. |
| End image ignored or morphs early | Use explicit duration, simplify the bridge, and reserve the landing for the final beat. |
| Multi-shot identity drifts | Repeat the same subject/wardrobe/light anchors after each named cut and reduce to 2–4 shots. |
| A2V lacks a coherent scene | Without `image_url`, fully establish subject, setting, framing, light, and responsive motion in `prompt`. |
| A2V rejects copied fields | Remove `resolution`, `fps`, `camera_motion`, and `end_image_url`; recheck the A2V schema. |
| Dialogue is garbled | Shorten it, specify language/accent, simplify action, or disable native audio and author speech in post. |
| Physics becomes chaotic | Reduce subject count and simultaneous interactions; use concrete, plausible cause and effect. |
| Retake, Extend, or Reframe is requested | Use a currently exposed LTX 2.3 Pro route or another matching model; LTX 2.5 does not support these operations. |

## Authority and Sources

Use this order when sources differ:

1. PR0TA live model catalog and `models_get_defaults` for exposed route fields, enums, and limits.
2. Checked-in Fal schemas for the canonical PR0TA provider contract.
3. Lightricks documentation for prompt semantics and direct-API context.

Official sources:

- [LTX 2.5 model matrix](https://docs.ltx.io/models/ltx-2-5)
- [LTX prompting guide](https://docs.ltx.io/api-documentation/implementation-guides/prompting-guide)
- [Text-to-video API](https://docs.ltx.io/api-documentation/api-reference/video-generation/text-to-video)
- [Image-to-video API](https://docs.ltx.io/api-documentation/api-reference/video-generation/image-to-video)
- [Audio-to-video API](https://docs.ltx.io/api-documentation/api-reference/video-generation/audio-to-video)
- [Fal LTX 2.5 Fast T2V](https://fal.ai/models/lightricks/ltx-2.5/text-to-video/fast/api)
- [Fal LTX 2.5 Pro A2V](https://fal.ai/models/lightricks/ltx-2.5/audio-to-video/pro/api)

Do not copy fields from LTX's direct API into PR0TA without checking the selected Fal-backed route. Prompt practices transfer; payload surfaces can differ.
