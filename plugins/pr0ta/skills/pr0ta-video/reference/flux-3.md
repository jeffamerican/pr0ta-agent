# FLUX 3 Video on Fal

Use this reference for every `blackforestlabs/flux-3/` video route in PR0TA. FLUX 3 supports synchronized audiovisual generation, start/end and timed keyframes, source-video continuation, and a two-stage Draft/Enhance workflow. Select the endpoint by operation before writing the prompt or payload; fields are not portable across the family.

## Contents

- [Endpoint selector](#endpoint-selector)
- [Shared generation contract](#shared-generation-contract)
- [Prompt structure](#prompt-structure)
- [Operation-specific prompting](#operation-specific-prompting)
- [Dialogue and sound](#dialogue-and-sound)
- [Typography and animated design](#typography-and-animated-design)
- [Draft and Enhance lifecycle](#draft-and-enhance-lifecycle)
- [Failure repair](#failure-repair)
- [Authority and sources](#authority-and-sources)

## Endpoint Selector

### Standard routes

| Need | Exact model ID |
|---|---|
| Prompt-only video | `blackforestlabs/flux-3/text-to-video` |
| Animate one opening image | `blackforestlabs/flux-3/image-to-video` |
| Bridge exact opening and ending images | `blackforestlabs/flux-3/first-last-frame-to-video` |
| Place 1–10 visual targets at exact frame positions | `blackforestlabs/flux-3/keyframes-to-video` |
| Continue an existing source clip | `blackforestlabs/flux-3/extend-video` |

### Draft routes

| Need | Exact model ID |
|---|---|
| Draft prompt-only video | `blackforestlabs/flux-3/text-to-video/draft` |
| Draft from one opening image | `blackforestlabs/flux-3/image-to-video/draft` |
| Draft exact opening/ending bridge | `blackforestlabs/flux-3/first-last-frame-to-video/draft` |
| Draft timed keyframes | `blackforestlabs/flux-3/keyframes-to-video/draft` |
| Draft source continuation | `blackforestlabs/flux-3/extend-video/draft` |
| Enhance an approved Draft result | `blackforestlabs/flux-3/draft-enhance` |

Use Draft to validate staging, pacing, dialogue, and reference interpretation. Promote only the approved Draft cache through `draft-enhance`; do not regenerate a supposedly approved take on a standard route.

## Shared Generation Contract

- `prompt` is required on every generation route.
- T2V, I2V, and Extend accept `duration: "auto"` or a whole number from 5 through 20.
- First/last and Keyframes require an explicit whole-number duration from 5 through 20.
- Standard routes accept `resolution: "720p" | "1080p"`; the default is `720p`.
- Draft routes are 720p and do not accept `resolution`.
- Supported aspect ratios are `auto`, `21:9`, `2:1`, `16:9`, `4:3`, `1:1`, `3:4`, and `9:16` where exposed by the selected route.
- `generate_audio` defaults to `true` on generation routes. Set it to `false` when dialogue, narration, music, or effects will be authored separately.
- `safety_tolerance` accepts 0–4 and defaults to 2. Do not raise it to bypass policy.
- I2V requires `image_url`.
- First/last requires `start_image_url` and `end_image_url`.
- Extend requires `video_url`. Current standard input must be MP4, under 50 MB, and under 15 seconds; the Draft wrapper documents a 50 MiB ceiling. Recheck live defaults before dispatch.

### Timed keyframes

Keyframes require an array of 1–10 objects:

```json
{
  "generator": "video",
  "mode": "transition",
  "model": "blackforestlabs/flux-3/keyframes-to-video/draft",
  "prompt": "...causal motion through the three timed targets...",
  "keyframes": [
    {"image_url": "https://.../opening.png", "frame_index": 0},
    {"image_url": "https://.../turn.png", "frame_index": 144},
    {"image_url": "https://.../ending.png", "frame_index": 287}
  ],
  "duration": 12,
  "aspect_ratio": "16:9",
  "generate_audio": true
}
```

Submit both standard and Draft Keyframes routes with unified `mode: "transition"`. Each `frame_index` must be unique and must fit the 24 fps output timeline. For a 12-second request, valid positions end before frame 288. PR0TA's Fal wrapper uses frame positions; do not copy BFL Direct API examples that pair keyframes with seconds.

## Prompt Structure

BFL's FLUX 3 video guides support natural-language, structured, and timecoded prompts. Use this order for reliable production prompts:

1. **Core summary** — one sentence naming the essential event and intended shot.
2. **Scene** — location, time, weather, light, palette, and material texture.
3. **Subject description** — stable appearance, wardrobe, and prop identifiers. Keep this wording fixed across shots.
4. **Dynamic narrative** — chronological visible action, reaction, camera path, and final state.
5. **Audio** — dialogue, ambience, effects, music, and intentional silence.
6. **Style and color** — lens/format, visual treatment, palette, contrast, and grain only when they matter.

For a simple shot, write one coherent paragraph in that order. For a dense or multi-beat shot, use labeled fields or time ranges. Do not stack disconnected keywords.

### Timecoded template

```text
Core summary: [one-sentence event and shot].
Scene: [place, time, light, palette, texture].
Subject: [stable appearance and wardrobe].
0:00–0:04 — [opening action and camera]. [sound].
0:04–0:09 — [causal development and camera response]. [dialogue/effect].
0:09–0:12 — [landing action and exact final state]. [audio resolution].
Style and color: [specific treatment].
```

Keep the number of beats proportional to duration. Give each beat one main action and one camera intention.

## Operation-Specific Prompting

### Text-to-video

Establish everything visible and audible: framing, scene, stable subject description, chronological performance, camera, audio, and final state.

```text
Medium close shot in a rain-darkened railway café at blue hour. Mara, a woman in a charcoal coat with a silver lapel pin, watches the platform through fogged glass. She wipes a small circle clear, sees the arriving train, and turns toward camera as the lens makes a slow dolly in. Rain taps the window; cups clink behind her. She says softly, "It is here." End with her hand still against the glass.
```

### Image-to-video

Treat `image_url` as frame-zero authority. Do not redescribe or contradict the supplied composition. Prompt motion onset, physical development, camera response, sound, and final state.

```text
The supplied image owns identity, wardrobe, composition, and lighting. Wind first lifts the loose edge of the scarf, then the subject turns toward the approaching headlights. The camera tracks left at walking pace while the background rain continues naturally. Preserve facial structure and the red scarf. End with the subject looking just past camera.
```

### First/last frame

Treat both images as ordered anchors. Describe only the physically plausible bridge and one coherent camera path. Do not introduce a second ending.

```text
Begin exactly from the supplied start frame. The cyclist pushes off, crosses the wet intersection, and passes behind the foreground tram as the camera pans right. Use the tram occlusion to motivate the change in distance and land exactly on the supplied end frame. Preserve wardrobe, bicycle geometry, rain direction, and street lighting throughout.
```

### Keyframes

Finalize the `keyframes` array first. In the prompt, describe causal motion between the ordered visual targets without inventing reference-token syntax. Match each narrative beat to the intended frame region and preserve stable subject wording.

```text
Frames 0–143: begin from the opening target; the dancer advances through one controlled turn as the camera arcs clockwise. Frames 144–239: pass through the second target, continuing the same momentum while the blue backlight warms. Frames 240–287: decelerate naturally and land on the final target. Preserve face, costume, stage geometry, and musical tempo.
```

### Extend

Treat the source clip's final state, camera momentum, motion, and audio bed as continuity authority. Continue the next causal beat; do not recap the source.

```text
Continue directly from the source clip's last frame. The camera maintains the existing forward speed as the doorway opens and the subject steps into the corridor. Preserve identity, wardrobe, lens height, motion direction, ambient hum, and mix level. End when the subject reaches the first pool of warm light.
```

## Dialogue and Sound

- Quote exact dialogue and identify the speaker.
- State language and accent when they matter.
- Pair speech with visible delivery: gaze, breath, mouth movement, gesture, and camera distance.
- Describe ambience and point effects separately from music.
- State `Music: none` or `non-diegetic music: none` when dialogue must remain clean.
- Keep speech short enough for the shot; long copy competes with action and sync.
- Treat wording, pronunciation, lip sync, stereo placement, and mix as take-level QC.
- Transcribe every speech-bearing result before timeline placement.

## Typography and Animated Design

FLUX 3 is a preferred PR0TA video family for native motion typography because BFL explicitly documents strong typography generation and animated designs. Use it for title sequences, kinetic type, signs, product copy, interface motion, and designed information graphics when the words themselves need to move.

Put the literal text early in the prompt and in quotation marks. Specify the type style, size hierarchy, color, placement, material/effect, entrance and exit motion, and the interval during which the copy must remain unchanged. Say `no additional words` when only the supplied copy may appear.

```text
Animated title design. The exact headline "NIGHT SHIFT" appears centered in huge
condensed white sans-serif capitals, with no additional words. From 0:00–0:02 the
letters assemble from thin horizontal light streaks; from 0:02–0:07 the complete
headline remains unchanged and fully legible while the camera makes a restrained
push through blue haze; from 0:07–0:09 the letters separate into light streaks and
exit frame-right. Minimal black background, electric-blue edge light. No dialogue.
```

Review every frame, not only the thumbnail or first frame. Reject spelling changes, extra glyphs, unstable letterforms, flicker, or motion that destroys readability. Use Draft to validate design and timing, then Enhance the approved Draft. For legal, credit, or brand-critical copy that fails this QC pass, use a verified premium still and deterministic timeline animation.

## Draft and Enhance Lifecycle

1. Submit the appropriate `/draft` generation route.
2. Poll the task and inspect picture, action, dialogue, audio, and continuity.
3. Read the finished task's durable Draft cache URL from `result_refs.draft_cache_url`.
4. Submit `blackforestlabs/flux-3/draft-enhance` with `draft_cache_url`.
5. Poll and inspect the enhanced media; confirm that shot structure and audio remain the approved take.

Enhance accepts `draft_cache_url` as its required creative input. It does not accept a replacement prompt, source image/video, duration, aspect ratio, resolution, keyframes, or `generate_audio`. If the creative content is wrong, revise and regenerate the Draft; Enhance is not an edit pass.

```json
{
  "generator": "video",
  "mode": "video_to_video",
  "model": "blackforestlabs/flux-3/draft-enhance",
  "draft_cache_url": "https://.../approved-draft-cache"
}
```

## Failure Repair

| Symptom | Repair |
|---|---|
| Prompt is attractive but unfocused | Add one core summary, then rewrite action chronologically. |
| Identity changes after a cut | Reuse the exact subject-description sentence after every cut or beat. |
| Keyframe rejected | Use 1–10 unique `frame_index` values within `duration * 24`; do not send seconds. |
| First/last transition morphs | Reduce simultaneous actions and describe one plausible physical bridge. |
| Extension restarts the scene | Begin with “Continue directly from the source clip's last frame” and preserve camera/audio momentum. |
| Dialogue is wrong or crowded | Shorten the line, name the speaker/language, simplify action, and remove competing music. |
| Enhance cannot accept a prompt | Fix the Draft itself, then enhance its new `draft_cache_url`. |
| Unsupported-field validation | Remove fields copied from another FLUX route and query `models_get_defaults`. |

## Authority and Sources

Use this order when sources differ:

1. PR0TA live model catalog and `models_get_defaults` for exposed model IDs, fields, enums, and limits.
2. Checked-in Fal endpoint schemas for PR0TA's provider contract.
3. BFL's official FLUX 3 guides for prompt semantics and BFL-native capability context.

Official sources:

- [BFL FLUX 3 overview](https://docs.bfl.ai/flux_3/flux3_overview)
- [Video prompting overview](https://docs.bfl.ai/guides/prompting_video_overview)
- [Text-to-video prompting](https://docs.bfl.ai/guides/prompting_video_text_to_video)
- [Image-to-video and keyframe prompting](https://docs.bfl.ai/guides/prompting_video_image_to_video)
- [Audio and speech prompting](https://docs.bfl.ai/guides/prompting_video_audio)
- [FLUX 3 launch article](https://bfl.ai/blog/flux-3)
- [BFL typography prompting rules](https://github.com/black-forest-labs/skills/blob/master/skills/flux-best-practices/rules/typography-text.md)

Do not copy a BFL Direct API payload into PR0TA without reconciling it against the selected Fal-backed route. Prompt concepts transfer; field names and timing encodings may not.
