---
name: pr0ta-hybrid
description: "PR0TA hybrid production for live-action plates and 3D worlds: Beeble SwitchX background swap/relight, matte and alpha sourcing, reference-plate authoring, and world-anchored structure references. Read when a shot starts from footage, a scan, or a Marble world instead of a blank prompt."
---

# PR0TA Hybrid Production

Hybrid production keeps something real and regenerates the rest. The plate's performance, the scan's geometry, or the Marble world's layout stays authoritative; a model paints the background, the lighting, or the missing angle around it. This is a different discipline from the generative workflows in `pr0ta-video` and `pr0ta-image`: the inputs are plates, mattes, and passes, the risk is identity and edge drift instead of prompt adherence, and the QC gate is a frame-by-frame compare against the source.

Read `pr0ta` first for the production hub, then this skill for any shot that starts from footage or a world. Seedance 2.5 Omni Reference remains the preferred route for generative shots; this skill covers the plate-based exceptions.

## When to Use This Skill

- A live-action or previously generated clip must keep its performance while the background, sky, set extension, props, wardrobe, or time of day changes.
- A plate must be relit to match a new environment, or an environment must be relit to match a plate.
- A single frame must become an angle-matched reference plate before a video pass.
- Recurring locations must stay geometrically consistent across shots by anchoring generation to a Marble world, a scan, or a collider mesh.
- A recorded camera performance must drive a previs or structure reference.

If none of these apply, stay in `pr0ta-video` or `pr0ta-image`.

## Mandatory Steps

1. **Read project memory first.** Call `memory_context_pack` for the scene, location, and shot. Approved location plates, set environments, and world decisions are the source of truth for what may change and what must stay.
2. **Probe the plate before you plan.** Inspect the source asset's duration, frame rate, pixel dimensions, and codec. SwitchX accepts at most 240 frames and 2,770,000 pixels in one generation and needs a constant frame rate. PR0TA chunks a longer plate automatically: one Beeble job per chunk, each billed on its own, stitched back into one render and one alpha, with the plan recorded in the task's `metadata.switchx_chunks`. Chunk boundaries can show a seam, so cut at a motivated edit yourself when the shot allows it.
3. **Decide the matte before the look.** Choose `auto`, `fill`, `select`, or `custom` from `reference/matte-and-alpha.md`. A wrong matte cannot be fixed by a better prompt. `auto` locks onto the subject in the first frames, so a plate that opens on an empty frame, a prop, or an occluded actor, and any plate PR0TA will chunk, needs a `custom` matte from BiRefNet; in a production test `auto` regenerated the couple as different people in the first chunk while the same plate with a BiRefNet matte kept them.
4. **Author the look as a plate, not a sentence.** For any background swap, build or approve a reference image that matches the plate's lens, horizon, camera height, and subject scale, then let the prompt describe lighting and mood. Read `reference/reference-plate-authoring.md`.
5. **Keep structure and appearance authorities separate.** A splat, collider, depth pass, or clay render controls geometry and camera only. Approved location plates control palette, material, light, and atmosphere. Never let a grayscale or neutral pass carry appearance authority. Read `reference/world-anchored-references.md`.
6. **Review every output against the source.** Compare faces, hands, hair edges, contact shadows, and camera motion frame by frame. SwitchX identity preservation can vary across identical runs, so review before editorial approval and rerun rather than accept drift.
7. **Record the decision.** After a take is approved, call `memory_record_decision` with the plate, matte, and reference asset IDs so later shots reuse the same authorities.

## Route Selection

Choose the narrowest tool that preserves what must stay. Read `reference/route-selection.md` for the full comparison.

| Need | Route | Why |
|---|---|---|
| Keep the performance pixels, change background, lighting, props, or wardrobe | `beeble/switchx` (`video_to_video`) | Source pixels drive the output; the masked region is regenerated and the kept subject is relit to the reference |
| Angle-matched reference plate from one frame | `beeble/switchx-image` (`edit_img`) | Same engine on a still; fast iteration before a video pass |
| Reinterpret the whole frame while keeping motion and timing | Seedance 2.5 Video Edit, or Omni with `omni_reference_task_type: "edit"` | Global restyle with image and audio references; camera can be reinterpreted |
| Natural-language change with no reference image | `google/gemini-omni-flash/v1.1/edit` | Prompt-only source edit; inspect the result near the five-second mark |
| Replace the subject as well as the background | Kling O3 Pro V2V edit, Pixverse swap | Element and reference driven replacement; not pixel-preserving |
| Relight only, no background change | LightX relight, Topaz video relight, or SwitchX `fill` | Illumination change without a new plate |
| Clean matte from footage | `fal-ai/birefnet/v2/video` (`video_to_video`, no prompt) with `output_mask` | Returns a grayscale matte video PR0TA registers as a matte asset and exposes as `matte_asset_id` |

Rules:

- Use SwitchX when the shot's value is the real performance. Use Seedance or Kling edits when the shot's value is the reinterpretation.
- SwitchX infers camera motion only from the pixels it keeps. A lateral pan or tracking shot with little parallax in the kept region can drift; keep some foreground unmasked, add a reference video to a Seedance edit instead, or generate the background as its own plate and composite.
- For price-sensitive choices, query `models_list`, then `GET /api/crew/model_pricing?model_id={model_id}` for each exact candidate and requested output configuration. Do not infer live cost from this document.
- Query `models_get_defaults` or `GET /api/crew/model_defaults?model_id={model_id}` before production calls; alpha fields and resolution caps are model-specific.

## SwitchX Contract

Prefer MCP. Submit with `generation_submit`, poll with `tasks_get`, and inspect the finished asset before editorial use.

Video background swap with a project matte:

```json
{
  "project_id": "project-uuid-or-slug",
  "request": {
    "generator": "video",
    "mode": "video_to_video",
    "model": "beeble/switchx",
    "prompt": "Golden-hour coastal road behind the driver; warm low sun from camera left, soft haze, preserve the driver's face and hands exactly.",
    "video_asset_id": "plate-asset-id",
    "reference_image_asset_ids": ["approved-look-plate-asset-id"],
    "alpha_mode": "custom",
    "alpha_asset_id": "matte-video-asset-id",
    "alpha_media_kind": "video",
    "max_resolution": 1080
  }
}
```

Still reference plate from an extracted frame:

```json
{
  "project_id": "project-uuid-or-slug",
  "request": {
    "generator": "image",
    "mode": "edit_img",
    "model": "beeble/switchx-image",
    "prompt": "Replace the studio backdrop with the approved library hall; keep the actor, chair, and lens unchanged.",
    "image_asset_id": "extracted-frame-asset-id",
    "reference_image_asset_ids": ["approved-location-still-asset-id"],
    "alpha_mode": "auto",
    "max_resolution": 1080
  }
}
```

Field rules:

- `video_asset_id` (or `video_url`) is the plate. `image_asset_id` is the plate for stills. At least one of `prompt` or a reference image is required.
- `reference_image_asset_ids[0]` is the look reference. Only the first reference is used.
- `alpha_mode` is `auto` (detect and track the main subject), `fill` (keep the whole frame and relight it), `select` (one grayscale keyframe image that Beeble propagates), or `custom` (a full-length grayscale matte video). Stills treat `select` as `custom`.
- `alpha_asset_id` is a project matte asset; PR0TA resolves it to a signed `alpha_uri`, infers `alpha_media_kind` from the asset, and conforms it to the prepared source. Pass `alpha_uri` only for media that is not a project asset.
- `max_resolution` is `720` or `1080`. PR0TA downscales the source to fit both the cap and the pixel budget.
- The task result carries `asset_id` for the render, `alpha_asset_id` for Beeble's own matte, and `source_asset_id` for the preprocessed source. Reuse `alpha_asset_id` as the `custom` matte on later takes of the same plate.

Read `reference/switchx.md` for the alpha-mode semantics, camera-motion caveats, timing rules, output handling, and failure repairs. Use REST only when MCP is unavailable: `POST /api/v2/projects/{project_id}/generate` with the same request body, documented in `pr0ta-api/reference/unified-generation.md`.

## Matte Sourcing

A matte is a grayscale video or image where white keeps the source and black is regenerated. Sources, in order of preference:

1. Beeble's own alpha from a previous SwitchX take (`result_refs.alpha_asset_id`).
2. BiRefNet v2 video with `output_mask` enabled, submitted through `generation_submit` with no prompt. PR0TA registers the matte as a second asset with `labels.role = "matte"` and returns `matte_asset_id` and `plate_asset_id` in `result_refs`.
3. A ProRes 4444 alpha channel from the plate itself, which the Resolve plugin extracts automatically.
4. A single grayscale keyframe painted or segmented from the first frame, submitted as `select`.

Matte from a plate:

```json
{
  "project_id": "project-uuid-or-slug",
  "request": {
    "generator": "video",
    "mode": "video_to_video",
    "model": "fal-ai/birefnet/v2/video",
    "video_asset_id": "plate-asset-id",
    "parameters": {"model": "Matting", "output_mask": true, "refine_foreground": true}
  }
}
```

`parameters.model` is BiRefNet's own model enum (`Matting` for hair and soft edges), not an endpoint id; `output_mask` defaults on. Feed `matte_asset_id` to SwitchX as `alpha_asset_id` with `alpha_mode: "custom"`. SAM 3 returns a segmented video with the mask applied, not a matte; use it to find and track objects, then derive the matte with BiRefNet or a keyframe. Read `reference/matte-and-alpha.md` for timing rules and edge hygiene.

## Reference Plate Authoring

The reference image is the look authority for the masked region and the relighting authority for the kept subject. Extract the plate's first frame, edit it into the target world while holding lens, horizon, camera height, and subject scale, fan out three to five candidates, and pick one. Where the world already exists as a Marble environment, shoot the reference from the matching camera in the world viewer so structure comes from the world and appearance comes from an approved plate. Read `reference/reference-plate-authoring.md`.

## World-Anchored References

Recurring locations stay consistent when every shot draws geometry from the same world and appearance from the same approved plates. PR0TA gives you four anchors:

- **Collider to structure passes:** `set_environment_collider_materialize` turns a Marble world's collider mesh into a Blender source, and `blender_job_submit` with `source_world_asset_id` renders `flat_structural` and `depth_normalized` passes from the shot camera for the designed-world prompt profile.
- **World-only previs guide:** the previs stage can render the Marble world alone along the camera path, tagged `guide_role: world_structure_reference`, for use as a clay-render video reference with zero appearance authority.
- **Pose-bearing captures:** a reference shot from a splat, pano, or mesh view stores its camera pose, lens, and world identity in `world_capture` labels so the same view can be re-rendered as a structure pass.
- **Camera-take import:** a recorded camera-performance take can drive the previs camera, so a real camera move produces the structure guide.

Read `reference/world-anchored-references.md` for the recipes and the authority rules.

## Pricing

Pricing is intentionally omitted from skill documentation because it changes independently of the skill bundle. Query `models_list`, then `GET /api/crew/model_pricing?model_id={model_id}` for each exact candidate and requested output configuration. Do not infer live cost from this document. SwitchX is billed by Beeble credits through PR0TA; a rejected upload or a failed job still consumes preparation time, so probe and split plates before submitting.

## QC Gate

Before an output enters the timeline:

- Faces, hands, and hair edges match the source across the whole clip, not just the first frame.
- Contact shadows and reflections agree with the new light direction in the reference.
- Camera motion in the regenerated region agrees with the kept region; look for sliding backgrounds on pans.
- The output duration, frame rate, and dimensions match the prepared source; do not retime.
- Speech-bearing plates are re-transcribed with Scribe V2 after any edit, as required by `pr0ta-audio`.

If any check fails, change the matte or the reference before changing the prompt, and rerun.

## Cross-Skill Pointers

- **Generating the look reference?** Read `pr0ta-image` for Nano Banana 2 and Seedream edit modes and `pr0ta-prompting` for the designed-world contract.
- **Choosing a generative edit route instead?** Read `pr0ta-video` → `reference/seedance-2.5.md`, `reference/gemini-omni-flash-1.1.md`, `reference/hailuo-h3.md`, and `reference/kling-prompting.md`.
- **Building the Marble world?** Read `pr0ta-prompting` → `reference/marble-world-generation.md`.
- **Recurring locations across shots?** Read `pr0ta-consistency` for the continuity rules; this skill owns the mechanics.
- **Placing the result?** Read `pr0ta-timeline`; plate-based clips must keep their native frame rate on the sequence.
- **Raw endpoint contracts?** Read `pr0ta-api/reference/unified-generation.md` and `reference/mcp-server.md`.

## Deep References

- `reference/switchx.md` — Beeble SwitchX contract, alpha modes, limits, outputs, and repairs.
- `reference/matte-and-alpha.md` — matte sources, keyframe authoring, timing rules, and edge hygiene.
- `reference/reference-plate-authoring.md` — building angle-matched look references from a plate.
- `reference/world-anchored-references.md` — structure versus appearance authority and the world-anchor recipes.
- `reference/route-selection.md` — SwitchX versus Seedance, Gemini, Kling, Pixverse, LightX, and Topaz routes.
