# Hybrid Route Selection

Choose the route by what must survive untouched. Read the selected model's reference in `pr0ta-video` before writing its prompt; grammars and reference fields are not portable.

## Contents

- Decision table
- Notes per route
- Matte sources
- Escalation ladder

## Decision Table

| Route | Preserves | Changes | Reference inputs | Best for |
|---|---|---|---|---|
| `beeble/switchx` | Source pixels in the kept region, timing, frame rate, aspect | Masked region, lighting on the kept subject | One look image, optional matte | Background swap, set extension, sky, day-for-night, wardrobe and prop swaps behind a real performance |
| `beeble/switchx-image` | Kept pixels of one frame | Masked region, relight | One look image, optional matte image | Angle-matched reference plates |
| `muapi/seedance-2.5-video-edit` | Identity, composition, and motion by reinterpretation | Whole frame style, environment, action detail | Up to 30 images, 10 audio | Global restyles where the camera may be reinterpreted |
| `muapi/seedance-2.5-omni-reference` with `omni_reference_task_type: "edit"` | As above, through the Omni route | As above | Images, videos, audio | Same intent when other references must ride along |
| `google/gemini-omni-flash/v1.1/edit` | Scene continuity by reinterpretation | Natural-language change | None | Prompt-only edits; inspect the boundary near five seconds |
| `muapi/gemini-omni-video-edit` | Motion and audio continuity | Restyle, relight, subject swap | Image references, character IDs | Reference-driven Gemini edits |
| `fal-ai/minimax/hailuo-03/reference-to-video` with the source as `Video 1` | Motion from the reference | Focused edit | Images, videos, audio | H3-native focused edits with native audio |
| `fal-ai/kling-video/o3/pro/video-to-video/edit` | Timing | Characters, objects, backgrounds | Elements and images | Subject replacement; source must be 24 to 60 fps |
| `fal-ai/pixverse/swap` | Timing | Person, object, or background | Reference images | Quick swaps where pixel fidelity is not required |
| `fal-ai/lightx/relight` | Content | Illumination and camera | Prompted lighting | Generative relight with camera control |
| `topaz/video-relight` | Content | Lighting and color | Controls | Utility relight and color adjustment |
| `topaz/upscale/video/precision`, `topaz/denoise/video` | Content | Resolution, noise | None | Cleanup before or after a SwitchX pass |

## Notes per Route

- SwitchX is the only route that treats the plate as pixel authority. Every other route reinterprets the plate and will move faces, hands, and edges.
- SwitchX infers camera motion only from the kept region. When the kept region is a static subject on a lateral pan, expect background drift; either keep more of the real set unmasked or move to a Seedance edit with the plate as a video reference.
- Seedance 2.5 Video Edit exposes `generate_audio`; set it false to request source-audio preservation and verify the delivered soundtrack.
- Gemini Omni Flash 1.1 edit has no reference-image field; use it for prompt-only changes only.
- Kling O3 V2V edit rejects 23.976 fps sources; conform to 24 fps first.
- Relight-only routes do not change the background; pair them with a matte-based composite when both must change.

## Matte Sources

BiRefNet v2 video with `output_mask` is the native grayscale matte source; SAM 3 finds and tracks objects but returns segmented video, not a matte; Bria returns RGBA when asked for a transparent background; a previous SwitchX take returns its own alpha as `result_refs.alpha_asset_id`. Read `reference/matte-and-alpha.md`.

## Escalation Ladder

1. SwitchX `auto` with a strong reference plate.
2. SwitchX `custom` with a BiRefNet or previous-take matte.
3. SwitchX still pass to fix the reference, then rerun the video.
4. Seedance 2.5 Video Edit with the plate as source and location stills as references.
5. Generate the background as its own plate from the world and composite on the timeline.

Move down the ladder only when the previous rung fails QC for a reason the next rung addresses.
