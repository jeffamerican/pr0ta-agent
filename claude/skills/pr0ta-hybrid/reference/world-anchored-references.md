# World-Anchored References

Recurring locations stay consistent when every shot draws geometry from one persistent world and appearance from the same approved plates. This reference covers the authority rule that makes that work and the PR0TA recipes that implement it.

## Contents

- The authority rule
- What PR0TA provides
- Recipe A: collider to structure passes to a designed-world still
- Recipe B: world-only previs guide as a clay-render video reference
- Recipe C: pose-bearing reference captures
- Recipe D: camera-take import
- Building the world from the location itself
- Roles and permissions
- What is pending

## The Authority Rule

Marble Gaussian splats are geometry evidence, not a look. Their visual quality is not production-ready, and the collider mesh is a coarse physics surface. So:

- A splat, collider, depth pass, flat render, or clay render controls camera, layout, occlusion, and scale only. It never carries palette, material, lighting, weather, or atmosphere.
- An approved location plate, scout photograph, or hero frame controls all visible appearance.
- Say both facts in every prompt that mixes them, using the designed-world contract in `pr0ta-prompting/reference/designed-world-reference-image.md` for stills and natural-language role assignment for Seedance 2.5 Omni video.

Never bend this for convenience. A prompt that lets a gray render "inspire the look" produces flat, dead plates.

## What PR0TA Provides

| Capability | Tool | Output |
|---|---|---|
| Persistent world from text, images, a panorama, video, or a depth panorama | `world_generation_submit` | World asset with SPZ splats, collider GLB, panorama, metric scale, and ground offset |
| Canonical set environment per Production Design variant | `set_environments_get`, `set_environment_upsert`, `set_environment_asset_link` | Typed asset roles: `world`, `blender_source`, `runtime_model`, `render_pass`, previews |
| Collider mesh as a Blender source | `set_environment_collider_materialize` | A stored `.glb` asset linked as `blender_source`; older collider links are retired |
| Structure passes from the shot camera | `blender_job_submit` with `source_world_asset_id` or `source_asset_id` and passes `flat_structural` plus `depth_normalized` | Trusted guidance passes with package identity, depth normalization, and QC metadata |
| Controlled still from structure plus appearance | `agent_chat_orchestrate_prompt` with `prompt_profile: "designed_world_reference_image"` | Generation package with the authority clause enforced |
| World-only previs guide | Previs stage, Render world only | Video asset with `guide_role: world_structure_reference` |
| Pose-bearing capture | Image Editor world viewer, Shoot reference | Reference image with `world_capture` labels |
| Camera-take import | Previs stage, Import camera take | Camera keyframes from a recorded camera-performance track |

## Recipe A: Collider to Structure Passes to a Designed-World Still

1. Find the world asset and the set environment with `set_environments_get` for the scene.
2. Call `set_environment_collider_materialize` with `environment_id` and `world_asset_id`. It downloads the collider once, registers it as a project GLB, links it as `blender_source`, and reuses the same asset on later calls.
3. Call `blender_job_submit` with `request.environment_id`, `request.source_world_asset_id`, a `scene_plan.camera` that matches the intended shot camera, and `render: {"kind": "still", "passes": ["flat_structural", "depth_normalized"]}`. Both passes are mandatory together and only stills are allowed for guidance renders. `source_world_asset_id` and `source_asset_id` are mutually exclusive.
4. Poll with `tasks_get`. The result lists `guidance_packages` with both pass asset IDs and their metadata.
5. Call `agent_chat_orchestrate_prompt` with `prompt_profile: "designed_world_reference_image"`, the guidance package, and an approved location still as the `appearance` reference. Generate only from a `generation_package`.
6. Use the resulting still as the SwitchX reference plate or as an Omni image reference.

The collider is coarse, which is acceptable: the flat pass only needs silhouettes, openings, and scale, and the depth pass only needs ordering.

## Recipe B: World-Only Previs Guide as a Clay-Render Video Reference

1. In the previs stage, attach the Marble world, block the camera move, or import a camera take.
2. Choose Render world only. The render hides the stage grid, mannequins, and props and uploads a `previs_guide` asset with `guide_role: world_structure_reference` and `guide_render.world_only: true`.
3. Submit Seedance 2.5 Omni Reference with the guide as a video reference and approved location stills as image references. In the prompt, state that the guide video controls camera trajectory, blocking, and layout only and that the stills control every visible appearance.
4. Inspect the result for camera agreement before trusting the look.

The normal guide with mannequins remains the motion reference; the world-only guide is a structure reference. Keep both if the shot needs both.

## Recipe C: Pose-Bearing Reference Captures

Shooting a reference from a splat, pano, or mesh view in the Image Editor now saves the camera with the image. The freeze-frame asset carries a `world_capture` label containing a JSON object with `mode`, `position`, `yaw`, `pitch` or `quaternion`, `focalLengthMm`, `fovDegrees`, `sensorHeightMm`, `coordinateSystem`, `worldAssetId`, `worldId`, `projectId`, and `capturedAt`, plus flat `world_capture_mode`, `world_focal_length_mm`, `world_asset_id`, and `world_id` labels for filtering. Use the stored pose to build the matching `scene_plan.camera` for Recipe A so the structure passes and the captured view agree. Captures from a library world carry `worldId` only, because there is no project asset yet.

## Recipe D: Camera-Take Import

A camera-performance take records position, quaternion, and focal length samples in the previs coordinate frame. Import it from the previs stage to replace the shot camera's keyframes; pre-roll samples and samples without tracking are dropped, other targets keep their animation, and the take's focal length maps one to one onto the previs lens. Then render a world-only guide from that camera for Recipe B.

## Building the World from the Location Itself

When the production has scout photographs or footage of the real location, build the Marble world from them: multi-image reconstruction from two to eight overlapping stills, or video-to-world from one steady sweep. The same photographs then serve as the appearance authority, so geometry and look cannot drift apart. Read `pr0ta-prompting/reference/marble-world-generation.md` for the input rules.

## Roles and Permissions

External MCP clients run every tool as the Operator, so `blender_job_submit`, `world_generation_submit`, and the set-environment tools are available directly. Internal department agents must run as the Set Designer to see them. Blender jobs are admission-controlled per project and per user; a capacity rejection is retryable after the reported delay.

## What Is Pending

World Labs announced Atlas on 1 September 2026 as a camera-conditioned world model that outputs video along a supplied camera trajectory together with splats and depth. It is in early access and is not integrated in PR0TA. Do not promise Atlas output, and keep the structure-versus-appearance discipline when it arrives, because generated plates will still need to match hero plates shot on the day.
