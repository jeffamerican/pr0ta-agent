# Seedance 2.5 on MuAPI

Use this reference when the resolved model is a Seedance 2.5 route: the MuAPI family below, Seedance 2.5 Motion Control, or the BytePlus ModelArk routes (`byteplus/seedance-2.5` and its task routes). Pick the route by operation: Omni Reference (`muapi/seedance-2.5-omni-reference`) for image-, video-, or audio-led shots, T2V for prompt-only, I2V for one opening image, first/last for two keyframes, Edit for a source clip, and Extend for continuation. Every standard modality has dedicated 480p, 720p, 1080p, and 4K routes selected by model ID. Seedance 2.5 renders natively up to 1080p; MuAPI's `-4k` routes upscale that native render to 4K. Standard, Spicy, and International 1080p and 4K routes are curated in each corresponding modality; the existing 720p Spicy/International T2V and I2V routes remain available. Every current route accepts optional `high_bitrate`; it defaults to `false` and trades larger output files for better visual fidelity. **Every Seedance 2.5 route returns audio-bearing video.** Standard T2V, I2V, first/last, and Omni routes expose no audio toggle; Edit and Extend expose `generate_audio` for route-specific regeneration or preservation behavior. Use each live endpoint schema for request fields without mistaking a missing audio field for silent output.

## Contents

- Endpoint selector and current standard contract
- Shared prompting principles
- T2V, I2V, first/last, Omni, Edit, and Extend techniques
- Identity/audio boundaries and failure repairs
- Sources and authority order

## Endpoint Selector

Mode by route: T2V routes use `txt_to_vid`; I2V, first/last, and Omni use `ref_to_vid`; Edit uses `video_to_video`; Extend uses `extend_video`. Confirm with `models_get_defaults(model_id).supported_modes`. The suffix selects the resolution tier; Spicy and International are regional or interpretive variants of the same request shape.

| PR0TA model ID | Resolution | Use when |
|---|---:|---|
| `muapi/seedance-2.5-text-to-video` | 720p | Invent a complete video from text |
| `muapi/seedance-2.5-spicy-text-to-video` | 720p | Favor bolder, more expressive motion and higher-contrast interpretation |
| `muapi/seedance-2.5-intl-text-to-video` | 720p | Route global text generation through MuAPI's international-region deployment |
| `muapi/seedance-2.5-text-to-video-480p` | 480p | Invent a complete video from text at 480p |
| `muapi/seedance-2.5-text-to-video-1080p` | Native 1080p | Deliver to a Full HD pipeline |
| `muapi/seedance-2.5-text-to-video-4k` | 4K (MuAPI upscale) | Deliver to a 4K pipeline |
| `muapi/seedance-2.5-image-to-video` | 720p | Animate one approved first image |
| `muapi/seedance-2.5-spicy-image-to-video` | 720p | Animate one image with bolder, more expressive motion |
| `muapi/seedance-2.5-intl-image-to-video` | 720p | Route global image animation through MuAPI's international-region deployment |
| `muapi/seedance-2.5-image-to-video-480p` | 480p | Animate one approved first image at 480p |
| `muapi/seedance-2.5-image-to-video-1080p` | Native 1080p | Deliver an image-led shot to a Full HD pipeline |
| `muapi/seedance-2.5-image-to-video-4k` | 4K (MuAPI upscale) | Deliver an image-led shot to a 4K pipeline |
| `muapi/seedance-2.5-first-last-frame` | 720p | Bridge two ordered approved keyframes |
| `muapi/seedance-2.5-first-last-frame-480p` | 480p | Bridge two ordered keyframes at 480p |
| `muapi/seedance-2.5-first-last-frame-1080p` | Native 1080p | Deliver a keyframe transition to a Full HD pipeline |
| `muapi/seedance-2.5-first-last-frame-4k` | 4K (MuAPI upscale) | Deliver a keyframe transition to a 4K pipeline |
| `muapi/seedance-2.5-omni-reference` | 720p | Guide the shot with images, videos, and/or audio |
| `muapi/seedance-2.5-omni-reference-480p` | 480p | Guide the shot with references at 480p |
| `muapi/seedance-2.5-omni-reference-1080p` | Native 1080p | Deliver a multimodal reference shot to a Full HD pipeline |
| `muapi/seedance-2.5-omni-reference-4k` | 4K (MuAPI upscale) | Deliver a multimodal reference shot to a 4K pipeline |
| `muapi/seedance-2.5-video-edit` | 720p | Modify a source video while preserving its content and motion |
| `muapi/seedance-2.5-video-edit-480p` | 480p | Modify a source video at 480p |
| `muapi/seedance-2.5-video-edit-1080p` | Native 1080p | Deliver a video edit to a Full HD pipeline |
| `muapi/seedance-2.5-video-edit-4k` | 4K (MuAPI upscale) | Deliver a video edit to a 4K pipeline |
| `muapi/seedance-2.5-video-extend` | 720p | Continue a source video from its last frame |
| `muapi/seedance-2.5-video-extend-480p` | 480p | Continue a source video at 480p |
| `muapi/seedance-2.5-video-extend-1080p` | Native 1080p | Deliver a continuation to a Full HD pipeline |
| `muapi/seedance-2.5-video-extend-4k` | 4K (MuAPI upscale) | Deliver a continuation to a 4K pipeline |

The 1080p and 4K variants use `muapi/seedance-2.5-{intl|spicy}-{mode}-{1080p|4k}` for all six modes. Live MuAPI edit/extend schemas send `video_url`; Edit references use `images_list[]`/`audios_list[]`, and Extend uses optional `last_image`. PR0TA also sends `resolution` matching the model-ID suffix because dedicated high-resolution routes now default to 720p in the live OpenAPI schema. See [current provider documentation](https://muapi.ai/seedance-2.5).

Spicy uses the same request shape as standard 720p generation but favors more expressive motion and higher-contrast creative interpretation with reduced moderation. International uses MuAPI's international-region deployment for traffic outside mainland China. Neither variant adds an audio toggle, last-frame, resolution, or camera-fixed control to these text/image routes; their outputs still include native audio.

## Current Standard Contract

The standard sixteen T2V, I2V, first/last, and Omni routes plus the four curated Spicy/International routes share:

- Required `prompt`.
- Integer `duration` from 4 through 30 seconds; default 5.
- Aspect ratio `16:9`, `9:16`, `1:1`, `4:3`, `3:4`, `21:9`, or `9:21`; default `16:9`.
- Optional integer `seed`; `-1` means random.
- Optional boolean `high_bitrate`; default `false`. Enable it for final-quality output when better fine-detail and compression fidelity justify a larger file.
- Resolution tier is selected by model ID: unsuffixed route is 720p, while `-480p`, `-1080p`, and `-4k` select those output tiers. 1080p is the native ceiling; `-4k` is a MuAPI upscale of a native render, so judge fine detail at 1080p. PR0TA derives and sends the matching `resolution` value; do not pick a different tier with a raw `resolution` field.
- Audio-bearing output with no audio opt-out field.

The standard routes do not expose a user-facing `resolution` picker, `negative_prompt`, `sound`, `generate_audio`, `camera_fixed`, `character_id`, `character_ids`, CFG/strength, FPS, or output-format controls. Choose resolution by model ID.

The current Omni route also accepts `omni_reference_task_type` with `auto`, `reference`, `edit`, or `extend`. Use `reference` for PR0TA's normal reference-led generation path, `edit` only when the attached video is source material to transform, and `extend` only when continuing it. Use `auto` when intent is genuinely ambiguous. This is a routing hint, not prompt prose or a substitute for the dedicated Video Edit or Extend route contracts. The provider still re-derives task type from the prompt, so a mismatch can fail asynchronously.

Omni edits preserve the requested integer duration of 4–30 seconds. Do not send `duration=-1`: the [live MuAPI OpenAPI schema](https://api.muapi.ai/openapi.json), verified 2026-09-07, rejects that older sentinel. PR0TA sets `aspect_ratio=adaptive` for Omni edit/extend intent.

Each resolution tier is a separate endpoint. A seed can aid repeatability within one route, but it does not reproduce a take on another tier and is not an identity lock.

The Edit and Extend families use the same prompt, duration, aspect-ratio, seed, and `high_bitrate` contract. They additionally expose `generate_audio` and require a source video. Their resolution is selected by model ID. Do not send a separate `resolution` value.

## Prompting Principles

ByteDance does not publish an optimal word count for Seedance 2.5. Use the shortest prompt that fully specifies the shot. Order information by causality rather than by a keyword checklist:

`shot intent/framing → subject and setting → chronological performance → camera trajectory → light/atmosphere/style → observable end state`

For 15–30 second work, use a few compact timed beats or shot blocks: setup, development, turn, and resolution. One meaningful action and one camera instruction per beat is a conservative PR0TA production heuristic, not provider syntax.

Prefer concrete visible behavior:

- Describe body mechanics and object physics.
- Name how the camera moves and what it reveals or follows.
- State the final visible state.
- Phrase preservation requirements positively.
- Avoid competing camera paths, contradictory reference roles, and a cut list too dense for the duration.

## Text-to-Video

Use for a scene with no approved starting image.

```text
[Shot scale and initial composition]. [Named subject and setting]. First, [action and physical reaction]. Then, [development]. The camera [one precise trajectory and target]. [Lighting/atmosphere evolves]. The shot ends with [observable final state]. [Visual style].
```

For a longer sequence:

```text
[00:00-00:08] [one action beat, framing, camera behavior, and result].
[00:08-00:17] [next causally connected beat and camera behavior].
[00:17-00:25] [final beat and explicit landing state].
```

Timed blocks are useful only when the order matters. A 30-second limit is not permission to pack in many unrelated scenes.

## Image-to-Video

I2V requires exactly one public `image_url`. The image owns the opening composition and appearance. Prompt the desired motion rather than redundantly rewriting the still:

```text
[Subject] begins by [small action onset], then [continuous performance or physical change]. The camera [trajectory]. [Atmosphere or lighting changes]. Preserve [critical visible identity, wardrobe, object, and spatial traits]. End with [observable state].
```

Avoid generic instructions such as "bring this image to life." Name subject motion, environmental motion, camera motion, and end state. Do not add a last-image field to I2V; use the dedicated first/last route.

## First and Last Frame

This route requires exactly two ordered image URLs in `images_list[]`:

1. `images_list[0]` is the first frame.
2. `images_list[1]` is the last frame.

Prompt only the coherent bridge between them:

```text
Beginning from the supplied first frame, [subject/object] [physical transition in chronological order] while the camera [one path]. [Intermediate state changes]. Arrive precisely at the supplied last-frame composition by the end.
```

Choose compatible source frames when possible: matching subject identity, plausible placement, similar lens logic, and the intended delivery ratio reduce morphing. This is production guidance, not an API requirement.

## Omni Reference

Use Omni when at least one usable visual, motion, or audio authority exists. When none exists, create or approve a keyframe or visual-bible reference first unless the exploration is intentionally text-only.

Omni accepts:

- Up to 30 images in `images_list[]`.
- Up to 10 videos in `videos_list[]`.
- Up to 10 audio files in `audios_list[]`.
- Audio references share a **15-second maximum combined duration**. Trim or excerpt longer voice, mood, or pacing references before submission; PR0TA rejects an unknown or over-budget total locally.
- Up to 50 total inputs when all three media budgets are combined.
- At least one reference in the current PR0TA flow. Audio-only and video-only requests are valid.

MuAPI describes images as environment/style guidance, video as camera-motion/rhythm guidance, and audio as mood/pacing guidance. Its current route pages do not guarantee positional reference-token binding. Upstream ByteDance 2.5 examples use spaced, capitalized UI labels such as `@Image 1`, `@Video 1`, and `@Clay Render 1`, but that UI syntax is not the Seedance 2.0 lowercase compact token contract and is not documented by MuAPI for PR0TA's routes. In PR0TA, assign reference roles in natural language unless the exact live MuAPI route begins documenting token binding. Never invent a clay-render payload field; provide a clay render as an ordinary image reference and state that it controls blocking, composition, or camera motion. Seedance 2.5 also exposes no trained-character field.

Assign roles in natural language, then describe the shot:

```text
Use the supplied images for [character identity, wardrobe, set, composition, or style]. Use the supplied video for [camera trajectory, blocking, motion rhythm, or edit pacing]. Use the supplied audio for [mood or pacing]. [Chronological subject performance]. The camera [trajectory]. Preserve [critical identity/set traits]. End with [observable final state].
```

Use a small coherent reference set first. Maximum capacity is a ceiling, not a target. Each reference should have one primary job; remove redundant or conflicting inputs.

Before an expensive prompt-orchestration fan-out, verify that the actual pixels support every declared exact authority claim. A role such as "exact face identity" requires a readable face; exact prop, wardrobe, or set authority requires the claimed feature to be visible. Treat hidden faces, off-frame objects, incompatible angles, and unresolved prop state across requested actions as clarification needs. PR0TA defaults `reference_preflight_mode` to `enforce`, returning a typed `prompt_assessment` before department calls when the reference packet is insufficient. Use `shadow` only for non-blocking diagnostics and explicit `off` only for controlled rollback.

The Omni reference gates (an approved voice for every speaker, a selected portrait or turnaround for every visible character, the image-slot and 15-second reference-audio limits) can be relaxed only when the person asks, with `validation_overrides`: `native_voices`, `character_visual_references`, `reference_limits`. See `pr0ta-prompting` → "Validation overrides"; the result receipts every override applied.

### Advanced 2.5 reference patterns

- **Clay-render or previs control:** Attach the clay render as an image reference and say it controls spatial blocking, subject paths, camera height, and lens trajectory while approved identity/style images control final appearance.
- **Timestamp-targeted change:** Name the source video as timing authority, identify the precise time range to change, request one transformation in that range, and positively preserve the rest of the clip. Treat timing as prompt intent unless the active route exposes a dedicated edit-range field.
- **Green-screen or perspective transformation:** State the source/background role, desired camera perspective or compositing result, edge/light behavior, and preserved subject performance. Do not invent mask, green-screen, or camera-path fields absent from the schema.
- **Long-form beats:** For 15–30 seconds, use compact time ranges with setup, development, turn, and resolution. Re-establish identity, screen direction, and sound continuity after any named cut.

ByteDance's 2.5 launch examples demonstrate these creative intents, but the live MuAPI schema controls which media fields PR0TA can actually send. Complex multi-subject contact and implausible physics remain risk areas; simplify simultaneous interactions when physical continuity matters.

## Video Edit

Edit requires a source video and accepts up to 30 optional image references and 10 optional audio references. In PR0TA, supply assets through `video_url`, `reference_image_urls`, and `reference_audio_urls`; the provider adapter maps them to `video_url`, `images_list[]`, and `audios_list[]` on native 1080p endpoints (the existing other tiers retain `video`, `reference_images`, and `reference_audios`).

```text
Use the source clip as the authority for identity, composition, motion, and timing. [One focused transformation]. Use the supplied image references for [identity/style/detail role] and the supplied audio references for [sound role]. Preserve [actions, framing, timing, and sounds that must remain]. The result ends with [observable state].
```

Set `generate_audio=false` when the original source-video audio should be preserved. PR0TA forwards that flag exactly, but provider runs have preserved the original audio inconsistently; inspect or correlate the delivered soundtrack before accepting it. Request one coherent edit rather than a full scene rewrite.

## Video Extend

Extend requires a source video and continues from its last frame. An optional `last_image_url` steers the continuation toward a target final image; the provider adapter maps it to MuAPI's `last_image` field.

```text
Continue naturally from the source clip's last frame. [Next causal action]. Preserve [screen direction, subject identity, camera trajectory, lens logic, lighting, and audio character]. [Camera and sound evolution]. If a target image is supplied, arrive plausibly at its composition by the end.
```

Do not restart the source action or introduce an unrelated shot. A target last image is a landing constraint, not a replacement for describing the physical bridge.

## Other Seedance 2.5 Routes

### BytePlus ModelArk (`byteplus/seedance-2.5`)

A single first-party route that covers text-, image-, and reference-led generation, source-clip editing, and extension (`supported_modes`: `txt_to_vid`, `ref_to_vid`, `video_to_video`, `extend_video`). It differs from the MuAPI family:

- `resolution` is a request field: `480p`, `720p`, or `1080p` (1080p output is 10-bit).
- `output_format`: `mp4` or `mov`; `mov` is H.264 yuv444p (4:4:4) with PCM audio for colour-critical edit and extend work.
- `duration`: 4–30 seconds, or `-1` to let the model choose.
- References: up to 30 images, 10 videos, and 10 audio files, with at most 30 seconds of combined reference audio and video.
- `omni_reference_task_type`: `auto`, `reference`, `edit`, or `extend`. `edit` forces `aspect_ratio: adaptive` and `duration: -1` (the output keeps the source clip's ratio and length); `extend` forces `aspect_ratio: adaptive`.
- `generate_audio` and `return_last_frame` are exposed; the catalog does not certify native audio for this route, so inspect the delivered file.

Prompt it exactly like the MuAPI routes: natural-language reference roles, chronological action, one camera path per beat, explicit end state.

#### BytePlus task routes

Four task-specific model IDs run the same ModelArk model with the task fixed, so the request cannot drift into the wrong operation. All take `resolution` (480p/720p/1080p), `output_format` (mp4/mov), and `aspect_ratio: adaptive` (the output follows the input image or source clip).

| Model ID | Task | Notes |
| --- | --- | --- |
| `byteplus/seedance-2.5-image-to-video` | Image-to-video with the input image locked as the first frame | Optional last frame; 4–30 s or -1; **draft mode** |
| `byteplus/seedance-2.5-first-last-frame` | Generate between a start frame and an end frame | Exactly two ordered stills; 4–30 s or -1; **draft mode** |
| `byteplus/seedance-2.5-video-edit` | Restyle, relight, or replace elements of a source clip | Duration is forced to -1 and ratio to adaptive: the output keeps the source clip's length and ratio; up to 30 images + 10 audio references; no draft |
| `byteplus/seedance-2.5-video-extend` | New footage before or after a source clip | Say in the prompt whether to extend forward (after the last frame) or backward (before the first frame); 4–30 s or -1; no draft |

The frame-anchored routes are the draft-first choice on BytePlus: draft at 480p, review, then finish the approved draft at 1080p (`reference/draft-to-final.md`). Edit and extend cannot draft; review them at 480p or 720p before a 1080p run.

ModelArk refuses input images that may show a real person (`InputImageSensitiveContentDetected.PrivacyInformation`, "may contain real person"), which includes realistic character references from Prep. PR0TA resubmits such a refusal as the same task on MuAPI (`muapi/seedance-2.5-omni-reference`, `-image-to-video`, `-first-last-frame`, `-video-edit`, `-video-extend`) on every path; the submission result carries `model_fallback`. Do not resubmit it yourself; mention the switch in one line.

### Seedance 2.5 Motion Control (`muapi/seedance-2.5-motion-control`)

Transfers a source performance onto character images while keeping the source choreography, timing, camera, and location. Read `motion-transfer.md`.

## Typography and Designed Text

Seedance 2.5 is a strong premium candidate for generated titles, signs, interfaces, product copy, and animated typography, especially when the design can be supplied through Omni references or refined through Video Edit. Do not route away merely because older video models had weak text.

Quote the exact copy once and specify language, type style, hierarchy, placement, color/material, motion, and the interval during which the finished words must remain unchanged. For Omni, attach an approved typography design and describe its role in natural language. For Edit, make the source video authoritative and request one focused typography correction or transformation while preserving timing, camera, and unaffected pixels.

Inspect every frame at delivery resolution. Generate alternatives or use a focused Edit pass for spelling, glyph, layout, or flicker defects. Use a verified still plus deterministic timeline motion only after native generation/edit attempts fail the exact-copy gate.

### Identity and Audio Boundaries

- Seedance 2.5 has no provider character-token field in the current MuAPI schema. Repeat defining identity/wardrobe traits and supply clear, compatible images. Use Seedance 2.0 Omni when a trained character resource is required.
- Audio references are documented as mood/pacing guidance. They are not a documented verbatim dialogue or lip-sync input on these routes.
- Every Seedance 2.5 route returns audio-bearing video. T2V, I2V, first/last, Omni, Spicy, and International expose no audio opt-out. Edit and Extend expose `generate_audio`; disabling it requests source-audio preservation, but the delivered result still requires verification.
- Seedance 2.5 enforces a four-second minimum and can pad shorter requested material at native speed. Trim the completed asset to the intended duration; do not retime the padded output.
- Audio references are conditioning inputs, not the reason the output has audio and not a guarantee of verbatim reproduction. Time-index and verify every speech-bearing result before editorial use.

## Common Failures and Repairs

| Failure | Repair |
|---|---|
| Unsupported field on T2V, I2V, first/last, or Omni | Remove caller-supplied `resolution`, `negative_prompt`, `sound`, `generate_audio`, camera-fixed, character, CFG, and FPS fields; choose 480p/720p/1080p/4K by model ID |
| Unsupported field on Edit or Extend | Remove caller-supplied `resolution`, `negative_prompt`, `sound`, camera-fixed, character, CFG, and FPS fields; retain `generate_audio` only when the endpoint schema exposes it |
| I2V ignores desired motion | Replace "bring to life" with explicit subject, environment, camera, and end-state motion |
| First/last morphs badly | Use compatible frames and describe the observable physical bridge |
| Omni follows the wrong reference | State each modality's role in prose and remove redundant inputs |
| Omni reference claims unseen authority | Supply an image where the claimed face/object/state is visible, narrow the declared role, or resolve continuity before orchestration |
| Identity drifts | Use clearer images, repeat defining traits, or switch to a trained-character workflow on Seedance 2.0 Omni |
| Long clip meanders | Reduce beats; preserve one causal arc and explicit end state |
| 4K route or audio control rejected | Select 1080p or 4K (upscaled) with the suffixed model ID; PR0TA sends the matching `resolution`. Omit audio controls on standard routes and use `generate_audio` only on Edit/Extend. The absence of a control does not mean silent output |
| Positional reference label is ignored | Replace upstream UI labels with explicit natural-language roles unless the exact MuAPI route documents token binding |
| Edit changes too much | Request one focused transformation and list preserved source traits |
| Extend restarts or jumps | Continue the in-progress action and preserve screen direction, camera, light, and sound character |
| Seed does not match across tiers | Treat 480p and 720p as different endpoints; use seed only as a variation control |
| High-bitrate output is unexpectedly large | Enable `high_bitrate` only where compression fidelity matters |
| Typography changes or flickers | Quote copy once, bind a design authority, simplify motion, fan out, or make a focused Edit pass before using deterministic still animation |

## Sources and Authority

- [Official ByteDance Seedance 2.5 page](https://seed.bytedance.com/en/seedance2_5)
- [Official ByteDance Seedance 2.5 launch and prompt examples](https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5)
- [MuAPI Seedance 2.5 family page](https://muapi.ai/seedance-2.5)
- [MuAPI Seedance 2.5 Omni Reference API playground](https://muapi.ai/playground/seedance-2.5-intl-omni-reference/api)
- [MuAPI OpenAPI](https://api.muapi.ai/openapi.json), live contract verified 2026-09-19

MuAPI family pages and older blog posts may describe capabilities that are not present on the current standard endpoints. For PR0TA payloads, authority order is:

1. Current live route/task schema.
2. Checked-in PR0TA model defaults and request-builder tests.
3. Official model-family capability pages.
4. Older marketing or launch posts.

Query `models_get_defaults` immediately before a production pass because Seedance 2.5 remains early access.

## Sung performance and competing reference audio

Before combining a song with continuity video, follow the [qualified sync-sound recipe](seedance-2.5-sync-sound.md): explicitly choose one audible musical authority, prepare silent continuity derivatives, verify the black-video carrier, preserve reference order and native output sound, and review a canary. The recipe distinguishes the 15-second audio-array budget, the demonstrated 30-second carrier, and the output limit.
