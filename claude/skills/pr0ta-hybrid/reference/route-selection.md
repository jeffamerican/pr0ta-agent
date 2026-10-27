# Hybrid Route Selection

Choose the route by what must survive untouched. Read the selected model's reference in `pr0ta-video` before writing its prompt; grammars and reference fields are not portable.

## Contents

- Keep the plate or re-render it
- Decision table
- Notes per route
- Matte sources
- Escalation ladder

## Keep the Plate or Re-render It

Decide this before choosing a model. The routes do different jobs.

**Plate-preserving: SwitchX** (`switchx.md`). The kept region's pixels pass through, so faces, hands, lip sync, wardrobe and timing are the recorded ones. The matte's black region is regenerated from one look image and the prompt, and the kept people are relit to match that image. Choose it when:

- the recorded performance is the point (dialogue, faces, an actor's work) and the shot is headed for the cut;
- the change is the world around the people: background, set extension, sky, time of day, weather, or a wardrobe or prop region (`select` or `custom` matte);
- the take must come back at the source's exact length, frame rate and ratio (hybrid sequence assembly checks them).

Plan for its limits: 720p or 1080p output through PR0TA; 240 frames per Beeble job (PR0TA chunks longer plates); one look image; camera motion read only from the kept pixels, so a low-parallax pan can slide; `auto` needs the subject visible from the first frame. It does not change what the people do. Its prompt is a short, specific description of place, light, weather and materials (up to 2,000 characters); the look image decides the light direction, so fix light in the image, not the prompt.

The other pixel-preserving option is a matte plus a separately generated background, composited on the timeline (ladder rung 5): the actors stay recorded pixels, but nothing relights them, so match the background's light to the plate.

**Full re-render: Seedance Video Edit and the other generative edits.** Every pixel is redrawn, the actors included, and faces and hands soften most at 480p. Choose it when:

- it is a look draft: testing a world, light or grade before a SwitchX final;
- the whole frame changes style (animation, painterly, period stylization) or the action itself changes;
- the plate defeats SwitchX after the ladder's SwitchX rungs (a pan that keeps sliding, a subject no matte holds);
- the person has said re-rendered actors are acceptable.

Then write the prompt with `pr0ta-video/reference/seedance-2.5-prompt-craft.md` → "Replace the World Around Live Action" (or the resolved model's reference), grade it with `pr0ta-prompting/reference/prompt-rubric.md`, and compare faces, hands and lip sync with the source before calling anything kept.

When the shot keeps a real performance, tell the person which you chose and why: "SwitchX keeps your actors' pixels; a Seedance edit would redraw them."

## Decision Table

| Route | Preserves | Changes | Reference inputs | Best for |
|---|---|---|---|---|
| `beeble/switchx` | Source pixels in the kept region, timing, frame rate, aspect | Masked region, lighting on the kept subject | One look image, optional matte | Background swap, set extension, sky, day-for-night, wardrobe and prop swaps behind a real performance |
| `beeble/switchx-image` | Kept pixels of one frame | Masked region, relight | One look image, optional matte image | Angle-matched reference plates |
| `byteplus/seedance-2.5-video-edit` | Identity, composition, and motion by reinterpretation; source length and ratio | Whole frame style, environment, action detail | Up to 30 images, 10 audio | Global restyles where the camera may be reinterpreted, at 480p, 720p, or 1080p (`resolution`); the default Seedance edit |
| `byteplus/seedance-2.5` (Hybrid runs it as an edit task) | As above, through the reference route | As above | Images, videos, audio | Same intent when other references must ride along, up to 1080p |
| `muapi/seedance-2.5-video-edit` (`-480p`, `-1080p`, `-4k`) | Identity, composition, and motion by reinterpretation | Whole frame style, environment, action detail | Up to 30 images, 10 audio | 4K delivery (an upscale), or the Spicy/International 4K variants |
| `muapi/seedance-2.5-omni-reference` with `omni_reference_task_type: "edit"` | As above, through the Omni route | As above | Images, videos, audio | Same intent on MuAPI when other references must ride along |
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
- SwitchX cost grows with the plate: 30-frame blocks per Beeble job (per chunk of a long plate), and 1080p costs three times 720p (a plate that renders at 720 or less is always sent, and priced, at 720). Explore looks at 720 or on a SwitchX still, then run the 1080 final; quote with the real plate, since the price comes from its frames and size.
- SwitchX infers camera motion only from the kept region. When the kept region is a static subject on a lateral pan, expect background drift; either keep more of the real set unmasked or move to a Seedance edit with the plate as a video reference.
- Seedance edits default to BytePlus ModelArk up to 1080p (cheaper per second than MuAPI). ModelArk refuses a source clip or reference that may show a real person, which live-action plates often do; Hybrid Studio then renders the same edit on MuAPI's route of the same resolution automatically (the refused attempt is hidden; do not resubmit). Choose a MuAPI route directly only for 4K or the Spicy/International variants.
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
4. Seedance 2.5 Video Edit (`byteplus/seedance-2.5-video-edit`) with the plate as source and location stills as references. This redraws the actors; say so before using it for a final.
5. Generate the background as its own plate from the world and composite on the timeline.

Move down the ladder only when the previous rung fails QC for a reason the next rung addresses.
