# Hybrid Route Selection

Choose the route by what must survive untouched. Read the selected model's reference in `pr0ta-video` before writing its prompt; grammars and reference fields are not portable.

The user's explicit route and workflow take precedence over this guide's default
recommendations. Explain a hard input or provider limitation when one prevents
that route; do not switch models or ask the same route question again after a
clear choice.

## Sequence-Source Omni Reference

Seedance 2.5 Omni Reference is a first-class route for hybridizing edited sequences.
Properly prompted, it is fully capable of maintaining actor identities and
performances and excels at carrying the supplied edit, camera coverage and action
through a transformed environment. Reference mode is not inherently a loss of
performance fidelity. Bind the source video to identity, performance, camera,
timing and cuts; bind each still to its actual appearance or environment role.
Inspect source pictures for silent gestures and exact cuts before writing timed
beats. Every beat must describe visible source action or a requested change:
an invented local gesture can override a global preservation instruction.

For Seedance 2.5 Omni Reference with the edited sequence as source, retain
that sequence workflow. Use the source edit as the sole video, split only
as needed for the live model's verified duration/input limits, and retain its
cuts within each contiguous chunk. Provider chunks are not newly invented shots.
Treat source text slugs as placeholders for new footage, as the user directs.
Use the requested native drafts first, review them, then finish accepted drafts
at the model's `draft_mode.final_resolution` (not an arbitrary new resolution). Reassemble against the original continuous recorded
audio; generated sound does not replace it. Compare the actual output against the
source to establish what the take preserved, as for any hybrid route. That quality
check does not authorize changing the
chosen route to SwitchX, adding matte work, or substituting a dedicated video-edit
modality. The edit-specific defaults below apply when an edit route was chosen.

**Use native drafts deliberately.** They make review and iteration before delivery
practical. Verify native-draft provenance (provider draft task and asset labels),
then use `finalize_draft` or the cut's draft-finish approval card to finish the
accepted draft. This retains the native draft-to-final workflow; a new video-edit
generation is a different operation. A standalone 480p preview is not proof of a
native draft. Read `pr0ta-video/reference/draft-to-final.md` for the exact contract.

## Contents

- Keep a performance: Seedance edit or SwitchX
- Seedance edits of recorded footage: input rules
- Decision table
- Notes per route
- Matte sources
- Escalation ladder

## Keep a Performance: Seedance Edit or SwitchX

Omni Reference above is a first-class performance-preserving choice. When the chosen workflow instead uses an edit route, compare Seedance edit and SwitchX below: both keep a recorded performance (faces and likeness, gestures, lip movements, timing, framing and cuts) while changing the world, in different ways.

**Seedance 2.5 edit** (`byteplus/seedance-2.5-video-edit`, the MuAPI video-edit routes, or Omni with `omni_reference_task_type: "edit"` and the plate as Video 1). It redraws every pixel and keeps the performance and likeness when the prompt locks them. Write that prompt with `pr0ta-video/reference/seedance-2.5-prompt-craft.md` → "Replace the World Around Live Action". It is a first-class route for keeping performances. Choose it when:

- the change is the world, the light, a wardrobe or prop change, or the style, around a performance that must be kept;
- the light on the people must change with the world, or the new world must sit naturally around them;
- the camera moves in ways SwitchX reads poorly (a low-parallax pan, a subject that defeats a matte);
- the whole frame changes style, or the action itself changes.

Render it at 720p or 1080p when faces matter, keep the plate as the only video, and check the take against the source before calling anything kept (the recipe's "Check the take").

**SwitchX** (`switchx.md`). The kept region's pixels pass through, so faces, hands, lip sync, wardrobe and timing are the recorded pixels. The matte's black region is regenerated from one look image and the prompt, and the kept people are relit to match that image. Choose it when:

- the plate's pixels must come through exactly (a hero close-up, a face that must not move by a pixel);
- Seedance attempts at the shot failed the check after the recipe's reruns;
- the take must come back at the source's exact length, frame rate and ratio (hybrid sequence assembly checks them).

On the picnic plate (C010, 2026-10-27) SwitchX with a `custom` matte kept both actors pixel-exact and relit them. A 480p Seedance edit of the same plate redrew their faces and turned the grass to gravel. The recipe now targets both failures (a higher resolution, a face lock, the ground named), but no rerun of that edit recipe has tested it yet. That individual low-resolution edit is not evidence that Omni Reference cannot preserve identities or performances.

Plan for SwitchX's limits:

- 720p or 1080p output through PR0TA.
- 240 frames per Beeble job. PR0TA chunks longer plates, and a seam can show at a chunk join (`switchx.md` → troubleshooting).
- One look image.
- Camera motion is read only from the kept pixels, so a low-parallax pan can slide.
- `auto` needs the subject visible from the first frame.
- It does not change what the people do.

Its prompt is a short, specific description of place, light, weather and materials (up to 2,000 characters). The look image decides the light direction, so fix the light in the image, not in the prompt.

The other pixel-preserving option is a matte plus a separately generated background, composited on the timeline (ladder rung 5). The actors stay recorded pixels, but nothing relights them, so match the background's light to the plate.

**Other generative edits** (Kling O3 V2V edit, Gemini Omni Flash edit, Pixverse swap; table below) reinterpret the plate without Seedance's reference roles. Use them for the jobs their rows name.

When the shot keeps a real performance, tell the person which route you chose and how you will check it. For example: "A Seedance edit at 1080p with the faces locked; I'll compare the faces and the soundtrack with your footage before calling it kept. SwitchX keeps your actors' exact pixels if you'd rather."

## Seedance Edits of Recorded Footage: Input Rules

These hold whatever the prompt says:

- **The source is the only video.** With several videos, the model picks which one to edit from the prompt and uses the others as references. A previous take sent as `Video 2` "for continuity only" replayed its gestures and lines in the new take (a Lago di Como hybrid chunk, 2026-10-28). Carry continuity from the previous chunk as a still of its last frame in the image references; the source already carries the motion. A submit or quote result's `request_advisories` flags a second video. This also applies to sequence-source Omni Reference reconstruction: the source already carries the performance. A previous take as a continuity video belongs to a deliberately chosen generation/continuation workflow (`pr0ta-video` → "Continuity Workflows"), not an automatic extra input for reconstruction.
- **Distinguish operations.** `seedance-2.5-video-edit` (ModelArk or MuAPI) takes the plate as its source and exposes `generate_audio`. Omni with `omni_reference_task_type: "edit"` edits too, when the plate is its only video. Omni `reference` is also fully capable of preserving identities and performances with source-bound prompting and is especially useful across edited sequences with native drafts; apart from the sole-source-video rule for reconstruction above, it is not subject to the other edit-specific defaults.
- **Recorded speech is the authority.** Generated speech never replaces it. On the video-edit routes, send `generate_audio: false` when the recorded sound or dialogue must survive (usually so in a hybrid with speech); otherwise the route's generated sound stays the default. MuAPI Omni has no `generate_audio` and always generates its soundtrack, so lay the source's soundtrack back under the take in Post. First check native-draft provenance: finish an accepted native draft with `finalize_draft` or its draft-finish card (`pr0ta-video/reference/draft-to-final.md`), without making a new edit. The following advice applies only to a separately requested re-edit of a standalone preview or take without native finish support. For that re-edit, use the video-edit route of that resolution with `generate_audio: false`, not Omni: an Omni re-edit's generated soundtrack recreates the recorded dialogue, and the provider refused one for it ("the output audio may be related to copyright restrictions", code `InputVideoSensitiveContentDetected.PrivacyInformation`, which identifies an audio check rather than establishing a real-person violation; bug e9a6e90c). PR0TA re-runs such a refused MuAPI Omni edit with one video and no audio once, quietly, on that video-edit route; do not resubmit. A hybrid sequence's assembly uses the original sequence audio. Check lip sync against the recorded track.
- **Grade honestly.** Prose such as "Video 1 is the sole action timeline" or "the soundtrack is the editorial authority" earns nothing by itself. The inputs above and a check against the source do (`pr0ta-prompting/reference/prompt-rubric.md`, items 1, 2 and 15).

## Decision Table

| Route | Preserves | Changes | Reference inputs | Best for |
|---|---|---|---|---|
| `beeble/switchx` | Source pixels in the kept region, timing, frame rate, aspect | Masked region, lighting on the kept subject | One look image, optional matte | Background swap, set extension, sky, day-for-night, wardrobe and prop swaps behind a real performance |
| `beeble/switchx-image` | Kept pixels of one frame | Masked region, relight | One look image, optional matte image | Angle-matched reference plates |
| `muapi/seedance-2.5-omni-reference` with source-bound reference prompting | Actor identities, performances, camera and edited coverage when properly prompted and handled; verify the take against its source | Environment, light, wardrobe, style and requested action changes | Edited source video plus clearly bound appearance/environment references | First-class hybridization across edited sequences, with useful native drafts and finishing of accepted takes |
| `byteplus/seedance-2.5-video-edit` | Performance, likeness, timing, framing and camera when the prompt locks them (pixels are redrawn: check against the source); source length and ratio; source sound with `generate_audio: false` | Environment, light, wardrobe, style, action detail | Up to 30 images, 10 audio | Keeping a recorded performance in a new world, and global restyles, at 480p, 720p, or 1080p (`resolution`; 720p or more when faces matter); the default Seedance edit |
| `byteplus/seedance-2.5` (Hybrid runs it as an edit task) | As above, through the reference route, with the plate as the only video; re-lay the source sound in Post (keeping it via `generate_audio: false` is verified only on the video-edit route) | As above | Images, videos, audio | Same intent when audio references must ride along, up to 1080p |
| `muapi/seedance-2.5-video-edit` (`-480p`, `-1080p`, `-4k`) | As the ModelArk video edit | As above | Up to 30 images, 10 audio | 4K delivery (an upscale), or the Spicy/International 4K variants; a ModelArk real-person refusal falls back here by itself (do not resubmit) |
| `muapi/seedance-2.5-omni-reference` with `omni_reference_task_type: "edit"` | As above, with the plate as the only video (no source field: with several videos the prompt decides which one is edited) | As above; the soundtrack is always generated (the provider can refuse it as possibly copyrighted audio) | Images, videos, audio | Edits on MuAPI where other references must ride along; re-lay recorded dialogue in Post. Not for a finishing re-edit that keeps recorded sound: use the video-edit route |
| `google/gemini-omni-flash/v1.1/edit` | Scene continuity by reinterpretation | Natural-language change | None | Prompt-only edits; inspect the boundary near five seconds |
| `muapi/gemini-omni-video-edit` | Motion and audio continuity | Restyle, relight, subject swap | Image references, character IDs | Reference-driven Gemini edits |
| `fal-ai/minimax/hailuo-03/reference-to-video` with the source as `Video 1` | Motion from the reference | Focused edit | Images, videos, audio | H3-native focused edits with native audio |
| `fal-ai/kling-video/o3/pro/video-to-video/edit` | Timing | Characters, objects, backgrounds | Elements and images | Subject replacement; source must be 24 to 60 fps |
| `fal-ai/pixverse/swap` | Timing | Person, object, or background | Reference images | Quick swaps where pixel fidelity is not required |
| `fal-ai/lightx/relight` | Content | Illumination and camera | Prompted lighting | Generative relight with camera control |
| `topaz/video-relight` | Content | Lighting and color | Controls | Utility relight and color adjustment |
| `topaz/upscale/video/precision`, `topaz/denoise/video` | Content | Resolution, noise | None | Cleanup before or after a SwitchX pass |

## Notes per Route

- SwitchX is the only route that passes the plate's pixels through. Every other route redraws them: a Seedance edit prompted with the recipe keeps faces, performance and timing, but compare faces, hands and edges with the source before calling the take kept.
- SwitchX cost grows with the plate: 30-frame blocks per Beeble job (per chunk of a long plate), and 1080p costs three times 720p (a plate that renders at 720 or less is always sent, and priced, at 720). Explore looks at 720 or on a SwitchX still, then run the 1080 final; quote with the real plate, since the price comes from its frames and size.
- SwitchX infers camera motion only from the kept region. When the kept region is a static subject on a lateral pan, expect background drift; either keep more of the real set unmasked or move to a Seedance edit with the plate as its only video.
- Seedance edits default to BytePlus ModelArk up to 1080p (cheaper per second than MuAPI). ModelArk refuses a source clip or reference that may show a real person, which live-action plates often do; Hybrid Studio then renders the same edit on MuAPI's route of the same resolution automatically (the refused attempt is hidden; do not resubmit). Choose a MuAPI route directly only for 4K or the Spicy/International variants.
- Seedance 2.5 Video Edit exposes `generate_audio`; set it false to request source-audio preservation and verify the delivered soundtrack. Seedance 2.5 Omni on MuAPI has no such field: its edits always generate sound.
- Gemini Omni Flash 1.1 edit has no reference-image field; use it for prompt-only changes only.
- Kling O3 V2V edit rejects 23.976 fps sources; conform to 24 fps first.
- Relight-only routes do not change the background; pair them with a matte-based composite when both must change.

## Matte Sources

BiRefNet v2 video with `output_mask` is the native grayscale matte source; SAM 3 finds and tracks objects but returns segmented video, not a matte; Bria returns RGBA when asked for a transparent background; a previous SwitchX take returns its own alpha as `result_refs.alpha_asset_id`. Read `reference/matte-and-alpha.md`.

## Escalation Ladder

1. Seedance 2.5 edit with the preservation recipe: the plate as the only video, 720p or 1080p.
2. The same edit, narrowed to what failed: add what drifted to the lock list, one change per pass, a shorter source, an identity still from the plate (untested).
3. SwitchX `custom` with a BiRefNet or previous-take matte (`auto` only when the subject is visible from the first frame and the plate is not chunked).
4. SwitchX still pass to fix the reference, then rerun the video.
5. Generate the background as its own plate from the world and composite on the timeline.

Start at rung 3 when the plate's pixels must come through exactly. These are options to propose when the user requests a correction. A QC failure does not authorize moving down the ladder: retain the take and findings, follow the user's decision, and change routes only with their direction.
