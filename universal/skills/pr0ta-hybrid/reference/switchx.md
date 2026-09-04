# Beeble SwitchX in PR0TA

Use this reference for `beeble/switchx` (video) and `beeble/switchx-image` (still). SwitchX is Beeble's video-to-video compositing and relighting model: the source pixels drive the output, the masked region is regenerated from a reference image and prompt, and the kept subject is relit to match. Beeble's developer API exposes only SwitchX and uploads; Background Remover, VFX Pass Generator, 3D Relight, SDR to HDR, and Canvas are app-only tools, so PR0TA supplies its own equivalents for mattes, depth, and relighting.

## Contents

- Provider contract and limits
- Alpha modes
- Reference image semantics
- What PR0TA does before and after the job
- Payloads by alpha mode
- Still-image edits
- Failures and repairs
- Sources

## Provider Contract and Limits

| Item | Contract |
|---|---|
| Source video | MP4 or MOV, H.264 or HEVC, constant frame rate, at most 2,770,000 pixels; at most 240 frames per Beeble job, and PR0TA chunks longer plates automatically |
| Source still | PNG, JPEG, or WebP, same pixel budget |
| Prompt | Up to 2,000 characters; required unless a reference image is supplied |
| Reference image | One image; strongly recommended for any background change |
| Alpha | Optional matte; required for `custom` and `select` |
| `max_resolution` | `720` or `1080`; aspect ratio and frame rate follow the source |
| Outputs | `render`, preprocessed `source`, and `alpha`, each as a signed URL valid for 72 hours |

Beeble publishes create and status routes but no cancellation route. Cancelling the PR0TA task stops polling and registration only; the provider job runs to completion.

## Alpha Modes

| Mode | What Beeble does | Use it for | Matte input |
|---|---|---|---|
| `auto` | Detects and tracks the main subject from the first frames of the clip, and of each chunk | Background replacement and relighting behind one clear subject that is visible from frame one | None |
| `fill` | Keeps the whole frame and preserves geometry while restyling and relighting | Day-for-night, weather, and global look changes with no new background | None |
| `select` | Propagates one grayscale keyframe across the clip | Wardrobe, prop, and partial-region swaps; invert the keyframe to generate only inside a region | One grayscale image |
| `custom` | Uses a full-length matte with the source timing | Roto-quality control from BiRefNet, a ProRes alpha, or a previous SwitchX alpha | One grayscale video |

White keeps the source; black is regenerated. For stills PR0TA sends `custom` for both `custom` and `select` because a still only has one frame.

## Reference Image Semantics

- The masked region is generated from the reference's content, so the reference must show the environment as it should appear from this camera.
- The unmasked region keeps its pixels but is restyled to the reference's lighting and mood, so the reference's light direction and color temperature are the relighting decision.
- Camera motion is inferred only from the kept pixels. Shots with visible depth change, organic handheld motion, or complex subject movement track well. Simple lateral pans and tracking shots with little parallax in the kept region can drift, and masked-out tracking markers cannot help.
- Source compression propagates into the output. Prefer a clean intermediate over a re-encoded proxy.
- Beeble recommends highly specific prompts. Name the place, the light, the weather, and the materials rather than a mood word.

## What PR0TA Does Before and After the Job

Before submission:

1. Resolves `video_asset_id`, `reference_image_asset_ids`, and `alpha_asset_id` to signed provider-readable URLs.
2. Probes the source and counts its frames exactly when the estimate is near or over 240. A longer plate is cut into contiguous near-equal chunks of at most 240 frames, each chunk is verified frame-exact, and each runs as its own Beeble job in order with its own idempotency key. A `custom` matte is cut with the same plan; a `select` keyframe is chained by extracting the last alpha frame of the previous chunk. The plan, job ids, and chunk asset ids are written to `metadata.switchx_chunks` as the job advances.
3. Downscales and transcodes the source to fit `max_resolution` and the pixel budget, and registers the prepared file as a normalized asset.
4. Conforms the reference image to the prepared source dimensions.
5. Conforms a `custom` matte to the prepared source. The frame count must match exactly; a matte with the right frames but different frame-rate or duration metadata (BiRefNet writes 24 fps for a 23.976 fps source) is re-stamped frame-for-frame, never resampled. A matte with a different frame count is rejected.
6. Uploads source, reference, and matte to Beeble, retrying transient upload failures up to three times.

After completion:

- The render is registered as the task's primary asset.
- Beeble's alpha is registered with `labels.role = "switchx_alpha"` and returned as `result_refs.alpha_asset_id`.
- The preprocessed source is registered with `labels.role = "switchx_source"` and returned as `result_refs.source_asset_id`.
- For a chunked plate the chunk renders are stitched frame-exact with the source audio remuxed on, the chunk alphas are stitched into one matte, and each chunk is billed as its own usage event. The `switchx_source` output is not registered for chunked jobs; use the normalized source asset instead.
- Provider errors are preserved on the task; read `error` and `error_detail` before retrying.

## Payloads by Alpha Mode

All examples are `generation_submit` requests with `generator: "video"`, `mode: "video_to_video"`, and `model: "beeble/switchx"`.

Auto matte, background swap:

```json
{"prompt": "Night market alley behind the courier, neon signage, wet asphalt reflections, preserve the courier exactly.", "video_asset_id": "plate", "reference_image_asset_ids": ["look"], "alpha_mode": "auto", "max_resolution": 1080}
```

Fill, whole-frame relight:

```json
{"prompt": "Same scene at blue hour; cool ambient sky, warm practical lamps stay lit, no new objects.", "video_asset_id": "plate", "reference_image_asset_ids": ["blue-hour-look"], "alpha_mode": "fill", "max_resolution": 1080}
```

Select, one keyframe propagated:

```json
{"prompt": "Replace the jacket with the approved navy wool coat; keep face, hands, and background unchanged.", "video_asset_id": "plate", "reference_image_asset_ids": ["coat-reference"], "alpha_mode": "select", "alpha_asset_id": "first-frame-matte-png", "alpha_media_kind": "image"}
```

Custom, full matte video:

```json
{"prompt": "Golden-hour cliff road behind the car; low sun from camera left; new reflections across the windshield.", "video_asset_id": "plate", "reference_image_asset_ids": ["golden-hour-look"], "alpha_mode": "custom", "alpha_asset_id": "birefnet-matte-video", "alpha_media_kind": "video"}
```

## Still-Image Edits

`beeble/switchx-image` runs the same engine on one frame through the image-edit path: `generator: "image"`, `mode: "edit_img"`, `image_asset_id` as the plate frame, `reference_image_asset_ids[0]` as the look, optional `alpha_asset_id` as a grayscale image, and `max_resolution`. PR0TA resizes all three inputs to the fitted source size, uploads them, and registers the render plus Beeble's alpha image. Use it to author an angle-matched reference plate from an extracted frame, then feed that plate to the video route.

## Failures and Repairs

| Symptom | Repair |
|---|---|
| Visible seam at a chunk boundary | Chunks are generated independently; split the plate yourself at a motivated cut, or keep more foreground unmasked so the kept pixels hide the join |
| Chunk rejected for frame drift | The source has a variable frame rate; conform it to a constant frame rate and resubmit |
| Custom matte rejected for timing | Regenerate the matte from the prepared source asset (`result_refs.source_asset_id` or the normalized asset), not from the original upload |
| Background slides on a pan | Keep more foreground unmasked, switch to a Seedance edit with a reference video, or generate the background as a separate plate and composite |
| Identity drifts on faces | Rerun with the same inputs, tighten the matte so the face is fully kept, or lower the prompt's appearance claims on the subject |
| Subjects replaced by different people | `auto` never locked the subject because the clip or chunk opens without a visible face; rerun with a BiRefNet `custom` matte, which keeps the plate pixels regardless of where the subject enters |
| Halo or hard edge around hair | Use a BiRefNet matte in `custom` mode instead of `auto`; soften the edge in the matte, not in the prompt |
| Relight does not match the reference | Fix the light direction in the reference image; the prompt cannot override the plate |
| Result has no `alpha_asset_id` | The secondary registration failed and was logged; the render is still valid |
| Provider policy rejection | Preserve the terminal error and follow `pr0ta-video/reference/provider-recovery.md`; never switch providers to bypass policy |

## Sources

- [Beeble SwitchX documentation](https://docs.beeble.ai/beeble/switchx)
- [Beeble Developer API](https://developer.beeble.ai/docs)
- [SwitchX research page](https://beeble.ai/research/switchx)
- Checked-in provider spec: `Documentation/beeble_developer_api_openapi.json`; PR0TA implementation under `services/video/providers/beeble_*.py` and `services/beeble/`.
