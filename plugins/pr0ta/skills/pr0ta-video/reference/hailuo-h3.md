# MiniMax Hailuo H3 on Fal

Use this reference for the Hailuo H3 and H3 Max PR0TA endpoints. H3 has a model-specific audiovisual prompt grammar. Do not reuse Kling `@Element` tokens, Seedance `@image` tokens, or older Hailuo bracketed Director commands.

## Contents

- Endpoint selector and Fal limits
- Base, camera, temporal, T2V, and I2V grammar
- Native dialogue and audio
- Typography and brand rendering
- Reference-to-video grammar and limits
- Unsupported fields and failure repairs

## Endpoint Selector

| PR0TA model ID | Use when | Required input | Important limits |
|---|---|---|---|
| `fal-ai/minimax/hailuo-03/text-to-video` | The model should invent the full scene | `prompt` | 5–15 whole seconds, fixed `2K`, six fixed aspect ratios |
| `fal-ai/minimax/hailuo-03/image-to-video` | An approved still must be frame zero | `prompt`, `image_url` | 5–15 seconds, fixed `2K`; output ratio follows the first image |
| `fal-ai/minimax/hailuo-03/image-to-video` with `end_image_url` | The shot must also land on an approved final frame | first-frame inputs plus `end_image_url` | Prompt the observable bridge between frames |
| `fal-ai/minimax/hailuo-03/reference-to-video` | Identity, style, motion, camera, voice, sound, rhythm, or a focused source-video edit comes from mixed references | `prompt` plus at least one image or video | Up to 9 images, 3 videos, 3 audios; fixed `2K`; `adaptive` or six fixed ratios |
| `minimax/h3-max/text-to-video` | H3 Max should invent the full scene | `prompt`, `prompt_expansion_mode` | 5–15 seconds; `480P` or `768P`; six aspect ratios |
| `minimax/h3-max/image-to-video` | H3 Max should animate a supplied frame | `prompt`, opening image, `prompt_expansion_mode` | Optional `end_image_url`; output ratio follows the first image |
| `minimax/h3-max/reference-to-video` | H3 Max should bind mixed continuity or audio references | `prompt`, `prompt_expansion_mode`, at least one image or video | Up to 9 images, 3 videos, 3 audio clips; 12 combined files; video and audio each total at most 15 seconds; `480P` or `768P` |

H3 Max is a separate Fal contract, not a replacement identifier for H3. T2V/I2V `prompt_expansion_mode` is `disabled`, `balanced`, or `quality`; R2V requires `balanced` or `quality`. All default to `balanced`. PR0TA's I2V modality deliberately requires an image even though Fal can fall back to T2V when the raw endpoint omits it. Query live defaults before carrying fixed-2K H3 assumptions into H3 Max.

H3 Max Turbo adds `minimax/h3-max-turbo/text-to-video` and `minimax/h3-max-turbo/image-to-video`, verified 2026-09-04. Both generate 5–15 seconds at 480P/768P with native audio and `prompt_expansion_mode` balanced/quality. The I2V route accepts optional `end_image_url` for first/last-frame work. No Turbo R2V route was confirmed. Pricing is resolution- and date-dependent, including launch promotions; query the live estimate before generation.

For H3 Max R2V, finalize ordered `reference_image_urls`, `reference_video_urls`, and `reference_audio_urls`, then bind literal `Image 1`, `Video 1`, and `Audio 1` roles in the prompt. Audio cannot be the only reference. Each video/audio clip must be 2–15 seconds, video references together and audio references together each must not exceed 15 seconds, with at most 9 images, 3 videos, 3 audio clips, and 12 files overall. Fal bills $0.08 per output second plus pooled reference tokens beyond the first 4,096; audio contributes approximately 80 tokens/second to that pool. Obtain and approve the preflight estimate before submission.

Aspect ratios for T2V are `21:9`, `16:9`, `4:3`, `1:1`, `3:4`, and `9:16`. Reference-to-video also accepts `adaptive`. I2V has no aspect-ratio field: prepare the first image at the delivery ratio.

Fal's H3 prompt ceiling is 2,000 characters. Fal exposes only `2K`, 24 fps output, and 5–15 seconds even where upstream MiniMax documentation describes a broader H3 service. The checked-in Fal schema is authoritative for PR0TA payloads.

## H3 Base Prompt Grammar

For T2V and I2V, use MiniMax's H3 audiovisual structure:

```text
integrated_multimodal_description: [Shot 1] ...

overall_soundscape: ...

non_diegetic_music: ...
```

Write the visual description in playback order:

1. Begin `[Shot 1]` with visual style and initial composition.
2. Establish subject appearance, position, environment, light, and relevant props.
3. Describe action, physical reaction, and resulting state chronologically.
4. Put camera movement inside the action description.
5. Include synchronized physical sounds where they occur.
6. Summarize ambience and sound effects in `overall_soundscape` without repeating dialogue.
7. Describe audience-only score in `non_diegetic_music`, or write `N/A` when no score is wanted.

Use one coherent action arc and one dominant camera path unless the duration genuinely supports more. This is a production-density rule, not a schema constraint.

### Camera Language

Use natural English rather than stacked bracket commands. A strong camera instruction combines:

`motion type + amplitude + speed + visual target`

```text
The camera pushes in with small amplitude at slow speed toward the folded letter.
The camera pans right with large amplitude at fast speed, revealing the doorway.
The camera holds a static shot as the runner exits frame.
```

Reliable H3 vocabulary includes Push In, Pull Out, Zoom In/Out, Pan, Truck, Tilt, Pedestal, Arc Shot, Tracking Shot, Static Shot, POV, Roll, and slight or strong shake.

### Multiple Shots and Time

`[Shot 1]` has no timestamp. Begin every later shot with a strictly increasing cut time inside the requested duration:

```text
[Shot 1] A wide static composition establishes the empty platform...
[Shot 2] At 00:03.500, the camera cuts to a close view of the arriving train...
```

Use a cut only to reveal a materially new subject, space, state, viewpoint, or time. Use camera movement for a modest angle or distance change.

## Text-to-Video Template

```text
integrated_multimodal_description: [Shot 1] [visual style and initial composition]. [Named subject with stable appearance] [chronological action and physical result]. The camera [one precise path]. [Lighting and environmental evolution]. [Synchronized physical sounds].

overall_soundscape: [ambience and important SFX].

non_diegetic_music: [score description or N/A].
```

For dialogue, use the H3 dialogue contract below rather than ordinary prose quotation.

## Image-to-Video and First/Last Frames

For a single first frame, begin with:

```text
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.
```

Then prompt:

`first-frame anchor → action onset → continuous development → result/reaction`

The first image already owns identity, clothing, colors, objects, composition, and spatial relationships. Describe how those visible facts evolve; do not contradict or needlessly re-invent them.

With `end_image_url`, begin with the alignment statement from MiniMax's first/last-frame grammar:

```text
How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot N) aligns with the S.SS-second mark of the target video.
```

Replace `N` and `S.SS` with the final shot number and requested final time. Describe observable intermediate motion and progressively narrow differences until the exact final-frame landing. Prefer one continuous shot unless the brief genuinely requires cuts.

## Native Dialogue and Audio

Assign stable speaker IDs only to vocal sources and preserve them across shots:

```text
The young woman with a quiet, breathy voice (S1) says:
<d>[English] I get off at the next station.</d>
```

Rules:

- On a speaker's first appearance, define visible identity and useful voice traits such as pitch, timbre, rate, and accent.
- Put only the language tag and exact spoken words inside `<d>`. Preserve wording and punctuation.
- Use `(S1,S2)` for group speech.
- For intentional voiceover, write `says in an off-screen voiceover` and state that the visible character's lips remain closed.
- Use `<scenetrans>` in both pieces when dialogue continues across a cut.
- Use `<cutoff>` when the clip intentionally truncates speech.
- Put visible on-screen text in English double quotes.
- Do not repeat dialogue inside `overall_soundscape`.
- Put diegetic music in the shot; put audience-only score in `non_diegetic_music`.
- Use `overall_soundscape: N/A` only for complete silence. Use `non_diegetic_music: N/A` when no score is wanted.

H3 produces an audio-bearing video, but these Fal schemas do not expose a sound toggle. Time-index every result before editorial use and verify what was actually rendered; prompt structure is not a guarantee of exact dialogue or mix.

## Typography and Brand Rendering

MiniMax identifies accurate text and brand rendering as an H3 strength. Use H3 for native titles, product marks, packaging, signs, interfaces, and typography that must participate in camera motion, materials, lighting, or physical interaction.

Put visible copy in English double quotes inside `integrated_multimodal_description`. State its placement, type style, hierarchy, color/material, animation, and required unchanged hold interval. Keep `overall_soundscape` and `non_diegetic_music` focused on sound rather than repeating the words.

```text
integrated_multimodal_description: [Shot 1] Premium black product-film background. The exact title "HORIZON" appears centered in large brushed-silver geometric capitals, with no additional words. The letters catch a narrow moving highlight as the camera makes a slow arc. From 00:02.000 through 00:07.000, the complete word remains unchanged and fully legible; fine particles drift behind it without crossing the letterforms.

overall_soundscape: A restrained metallic shimmer as the title resolves.

non_diegetic_music: Minimal low electronic pulse.
```

For I2V, treat the approved text-bearing image as frame-zero authority and name the exact typography that must remain stable. For R2V, bind the design as `Image N` and give it the explicit role of typography/brand authority. Inspect every frame at delivery resolution and generate alternatives when spelling or glyph stability fails.

## Reference-to-Video Grammar

Bind references by modality and list order using literal prose names:

- `Image 1`, `Image 2`, ...
- `Video 1`, `Video 2`, ...
- `Audio 1`, `Audio 2`, ...

Do not use `@Image1`, `@Video1`, `@Audio1`, or `@Element1` in an H3 prompt.

MiniMax's full-reference structure is:

```text
subject_definitions:
summary:
retention_analysis:
detailed_description:
overall_soundscape:
non_diegetic_music:
```

Fal's 2,000-character limit is much shorter than MiniMax's full upstream reference template. Preserve the section semantics but compress aggressively:

```text
subject_definitions:
<Subject 1> is the woman from Image 1; preserve [identity traits].
<Subject 2> is the location from Image 2; preserve [set traits].
Video 1 supplies [camera trajectory or performance blocking].
Audio 1 supplies [voice timbre, beat, delivery, or sound texture] for (S1).

summary: [reference-generation intent in one sentence].

retention_analysis:
<Subject 1>: fully_preserved — [critical traits].
<Subject 2>: fully_preserved — [critical traits].

detailed_description:
[Shot 1] [chronological audiovisual shot].
[Shot 2] At 00:04.000, [new shot if needed].

overall_soundscape: [ambience and SFX].
non_diegetic_music: N/A
```

Reference roles:

- Use images for visible identity, wardrobe, props, sets, composition, or style.
- Use videos for performance, physical motion, camera trajectory, edit rhythm, or continuation.
- Use audio for voice timbre/delivery, exact supplied speech, beat, rhythm, sound texture, or continuity.
- State every reference's single primary job. A video does not automatically make its embedded audio a controlled audio reference; provide a separate audio reference when sound matters.
- R2V references are guidance, not exact opening or ending frames. Use I2V for exact keyframes.
- Keep the reference set coherent. Maximum counts are ceilings, not quality targets.

### Focused source-video edits

Use R2V when `Video 1` should remain the source authority and the request changes one focused property. State both the transformation and the invariants:

```text
Video 1 is the source authority for identity, performance, camera path, timing, composition, and existing audio. Change only [one focused transformation]. Preserve [specific unaffected traits and beats]. The edited result [new visible state and landing].
```

For example, change wardrobe color, weather, a prop, or one environmental condition while retaining source blocking and camera motion. Do not ask for a full scene rewrite and call it a source-preserving edit. Inspect the output against the original clip frame by frame; reference prompting guides the edit but does not guarantee pixel-exact preservation.

```json
{
  "generator": "video",
  "mode": "ref_to_vid",
  "model": "fal-ai/minimax/hailuo-03/reference-to-video",
  "reference_video_urls": ["https://.../source.mp4"],
  "prompt": "Video 1 is the source authority... Change only the clear weather into steady rainfall... Preserve identity, performance, camera path, timing, composition, and unaffected audio.",
  "duration": 10,
  "aspect_ratio": "adaptive"
}
```

For the strongest timing preservation, request the source clip's whole-second duration when it already falls within 5–15 seconds. Otherwise choose an allowed output duration and expect some timing reinterpretation.

### Reference Limits

- Up to 9 image URLs.
- Up to 3 video URLs; each 2–15 seconds and at most 15 seconds combined.
- Up to 3 audio URLs; each 2–15 seconds and at most 15 seconds combined.
- Audio cannot be the only reference; include at least one image or video.
- MiniMax's upstream H3 service also documents a 12-file combined mixed-reference cap and media-format constraints that Fal's schema does not express. Stay at or below 12 total references unless a live Fal schema or successful probe confirms otherwise.

## Unsupported Fields and Syntax

The PR0TA/Fal H3 schemas do not expose:

- `negative_prompt`
- `camera_control`
- `prompt_optimizer`
- `seed`
- `sound` or `generate_audio`
- Seedance/Kling reference tokens

State desired behavior and retained end states positively in the main prompt. Use the H3 sound/music fields for intentional absence. Do not send unsupported controls.

## Failure Repairs

| Failure | Repair |
|---|---|
| Extra or invented dialogue | Use a stable `(S1)` identity and exact `<d>[Language] ...</d>` block |
| Unwanted score | Set `non_diegetic_music: N/A` |
| Wrong reference applied | Bind literal `Image N` / `Video N` / `Audio N` and define its role |
| Identity drift across cuts | Reuse stable `<Subject N>` labels and list `fully_preserved` traits |
| First/last morph or jump | Prompt observable intermediate transformations and favor one shot |
| Random cut timing | Use increasing `[Shot N] At MM:SS.mmm` cut markers |
| Camera conflict | Keep one dominant path with type, amplitude, speed, and target |
| I2V ratio surprise | Prepare the first image at the delivery ratio |
| Provider rejection | Re-check 2,000 characters, 5–15 seconds, fixed `2K`/24 fps, reference counts, and media durations |
| Audio-only R2V rejection | Add an image or video reference |
| Critical typography mutates | Quote the copy once, simplify motion, bind a typography authority image, and fan out; use deterministic still animation only if native attempts fail QC |

## Sources

- [MiniMax H3 model card](https://huggingface.co/MiniMaxAI/MiniMax-H3)
- [Official H3 T2V/I2V prompt-writing guide](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md)
- [Official H3 full-reference prompt-writing guide](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md)
- [MiniMax H3 API](https://platform.minimax.io/docs/api-reference/video-generation-v2-create)
- [MiniMax H3 launch and commercial capability overview](https://www.minimax.io/blog/minimax-h3)
- [Fal H3 T2V](https://fal.ai/models/fal-ai/minimax/hailuo-03/text-to-video/api)
- [Fal H3 I2V](https://fal.ai/models/fal-ai/minimax/hailuo-03/image-to-video/api)
- [Fal H3 R2V](https://fal.ai/models/fal-ai/minimax/hailuo-03/reference-to-video/api)

Treat the checked-in Fal OpenAPI files and current `models_get_defaults` response as the final payload authority for PR0TA.
