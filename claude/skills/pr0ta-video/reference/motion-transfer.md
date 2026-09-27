# Motion Transfer (Character Performance)

Use this reference when a driving video should supply body performance, choreography, or blocking and an approved character image should supply appearance. Resolve the model with `models_preferred(modality="motion_transfer_model")`; when it returns null, choose from `models_list(modality="motion_transfer_model")` and say why. Every route listed here uses mode `video_to_video`.

Motion transfer is not reference-to-video: the driving clip is authority for timing and movement, not a loose style cue. For a still that must speak a finished soundtrack, use `lipsync_model` instead.

## Submission Surface

Check each catalog row's `generation_submit_supported`. Where it is `true`, submit through `generation_submit`. Where it is `false`, the model is listed for discovery and runs from the Video Editor's **Character Performance** (Mot→Vid) panel, which maps the driver clip and target image for you.

| Model id | `generation_submit` | Inputs and limits |
|---|---|---|
| `fal-ai/kling-video/v3/standard/motion-control` | yes | `image_url` (character), `video_url` (driving performance), required `character_orientation`; optional `keep_original_sound`, one facial Element, prompt up to 2,500 characters |
| `fal-ai/kling-video/v2.6/pro/motion-control` | no | Character image plus reference video; Pro quality for complex movement |
| `kling/o3/motion-control` (alias `kling/v3-omni/motion-control`) | no | `image_url` appearance, `video_url` motion; Standard and Pro modes; Elements support |
| `muapi/seedance-2.5-motion-control` | no | `video_url` plus up to 30 character images in `images_list[]`; 4–30 second output; optional generated audio and high-bitrate mode |
| `fal-ai/scail-2` | no | Prompt, driver video, and target image; animation or replacement mode; human or animal subjects; 512p or 704p output |

Query `models_get_defaults(model_id)` before submission; the live schema is the field authority.

## Kling V3 Standard Motion Control

- `character_orientation: "video"` makes the character's facing follow the driving clip. It suits complex motion and accepts a driving clip up to 30 seconds. An optional facial Element (one only, referenced as `@Element1`) improves identity and works only in this orientation.
- `character_orientation: "image"` keeps the facing from the character image. It follows camera movement better and accepts a driving clip up to 10 seconds.
- `keep_original_sound` defaults to `true`; set it to `false` when post will supply the soundtrack.
- The character image should show clear body proportions, no occlusion, and the character filling more than about 5% of the frame. The driving clip should show a realistic full or upper body with the head visible and unobstructed.

## Seedance 2.5 Motion Control

The source performance keeps its choreography, timing, camera, and location; the character images replace who performs it. The prompt is optional. Use it only for focused deviations such as a wardrobe change or a lighting shift, and state what must stay. Seedance 2.5 grammar (natural-language roles, no `@` tokens) applies; read `seedance-2.5.md`.

## SCAIL-2

SCAIL-2 transfers acting and body motion to a character image, in animation mode (animate the target) or replacement mode (swap the performer). It needs a prompt, and it handles human and animal subjects. Use it when acting, pose fidelity, and body mechanics matter more than resolution.

## Preparing Inputs

1. Trim the driving clip to the exact beat. Output length follows the driver on most routes, and every frame of it is followed.
2. Match framing: a full-body driver with a head-and-shoulders character image, or the reverse, produces cropping and scale errors.
3. Use an approved character asset. Keep the character image's pose close to the driver's opening pose when possible.
4. Remove other people from the driver or crop to one performer unless the route documents multi-subject transfer.
5. Decide who owns sound (the driver, the model, or post) before submission.

## Review

Check hands, feet contact, occlusion crossings, face identity on turns, and whether the result drifts from the driver's timing. For dialogue, run the lip-sync route afterward on the accepted take rather than expecting motion transfer to reproduce mouth shapes.
