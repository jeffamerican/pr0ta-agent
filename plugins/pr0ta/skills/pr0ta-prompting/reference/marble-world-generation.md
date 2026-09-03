# World Labs Marble World Generation

Use this reference when a Set Designer or other agent must choose, prompt, create, or review a World Labs Marble world.

Marble creates a persistent navigable 3D environment. It is not a still-image prompt, a shot prompt, or a substitute for camera blocking. The visual environment is delivered primarily as Gaussian splats; the collider GLB is a coarse physics surface, not the beauty mesh.

## Choose the input modality

| Modality | Use it when | Source discipline |
|---|---|---|
| Text | Exploring a new location quickly and allowing Marble to invent unspecified parts | Describe a location, not a shot. Prompt limit is 2,000 characters. |
| Single image | Lifting one approved concept frame or location photo | Use a sharp, well-lit image with clear perspective, visible floors/walls/ground, and foreground, midground, and background. Avoid close-ups, flat graphics, borders, characters, and animals. |
| Multi-image, reconstruction | Reconstructing one real or designed space from several views | Use 2-8 sharp images from close vantage points with the same aspect ratio and resolution, overlapping features, consistent lighting, and different viewing directions. Set `reconstruct_images=true`; do not provide panoramas. |
| Multi-image, directed | Creatively defining or connecting different sides of a designed world | Use 2-4 views and assign azimuths: front `0`, right `90`, back `180`, left `270`. Non-overlapping views intentionally leave Marble room to invent transitions. |
| 360 panorama | Maximum layout control from one vantage point | Use one seamless equirectangular 2:1 panorama, ideally 2560 px wide, with full vertical sky-to-ground coverage. Set `is_pano=true`. Do not combine it with other images or video. |
| Video | Capturing richer spatial evidence than one image | Record one uninterrupted, steady 180-360 degree sweep of a static space. Keep focal length and exposure fixed; avoid zoom, moving people/objects, shake, and motion blur. Maximum 30 seconds and 100 MB. |
| Depth panorama | Geometry is more authoritative than RGB appearance | PR0TA extension: upload an equirectangular EXR depth map, or a normalized PNG plus real `depth_z_min` and `depth_z_max`. PR0TA synthesizes the RGB panorama before Marble world generation. |

World Labs' official modality guidance is documented in its [image](https://docs.worldlabs.ai/marble/create/prompt-guides/image-prompt), [multi-image](https://docs.worldlabs.ai/marble/create/prompt-guides/multi-image-prompt), [panorama](https://docs.worldlabs.ai/marble/create/prompt-guides/pano-prompt), and [video](https://docs.worldlabs.ai/marble/create/prompt-guides/video-prompt) guides.

## Write a Marble location prompt

Start with the location itself. Then specify only durable spatial facts that should remain true while a viewer moves through it:

1. Location type and overall footprint.
2. Spatial layout, connected zones, entrances, exits, circulation, and ground plane.
3. Architectural language, structural elements, ceiling or terrain, and scale cues.
4. Persistent furniture, fixtures, practical props, landmarks, and signage.
5. Materials, finishes, age, wear, damage, dressing, and set condition.
6. Physical light sources, time of day, weather, atmosphere, and exterior context.
7. The approved visual style, only when Production Design or the Director supplied it.

Do not spend the prompt on lenses, focal lengths, camera movement, shot size, cuts, actor performance, or temporary action. Those belong to cinematography, staging, and previs after the persistent world exists. Characters and animals are also weak Marble structure references.

Example:

> A two-storey 1930s municipal library reading hall, approximately 18 metres long, with a central oak circulation desk and clear aisles to two matching stair doors on the rear wall. A mezzanine gallery wraps three sides above dark green steel columns. Worn terrazzo floor, cream plaster walls, oak shelving, brass task lamps, and rain-streaked east windows. Late-afternoon overcast daylight enters from the windows while warm practical lamps define the desk and reading tables. The room is maintained but visibly aged, with patched plaster and polished traffic wear along the main path.

Let Marble recaption by default. Use `disable_recaption=true` only when the exact text must be preserved. A source image or video may omit `text_prompt` and allow Marble to derive its own caption, but a concise location prompt is useful when approved design intent must constrain the lift.

## Choose the model

- `marble-1.1`: recommended default and fixed-cost current-quality model.
- `marble-1.1-plus`: largest worlds; dynamically expands 3D coverage for large outdoor or indoor spaces and can cost more.
- `marble-1.0-draft`: fast, low-cost prompt and layout exploration.
- `marble-1.0`: legacy model retained for ongoing explorations.

Check the current [World Labs model guide](https://docs.worldlabs.ai/marble/models) and PR0TA model pricing before submission rather than relying on remembered costs.

## PR0TA submission and receipt contract

Use `world_generation_submit` with the endpoint operation (`text_to_world`, `image_to_world`, or `video_to_world`) and the selected `world_model`. For set work, always include the active `set_environment_id`; the backend validates the environment, derives canonical entity/variant/scene lineage, and attaches the completed asset with role `world`.

Local image/video inputs must be uploaded to World Labs first and referenced by `image_media_asset_id`, `video_media_asset_id`, or `multi_image_inputs[].media_asset_id`. A submission returns a task receipt, not a finished world. Poll with `tasks_get` until `succeeded`, `failed`, or canceled.

On success, distinguish the artifacts:

- SPZ splats: visual rendering; prefer full resolution for final quality and a lower-resolution SPZ for interactive preview.
- Collider GLB: coarse physics, navigation, and raycasting only.
- Panorama and thumbnail: 2D review.
- `metric_scale_factor` and `ground_plane_offset`: alignment with real-world units and ground.
- Marble URL and world ID: provider provenance and later library access.

Never claim creation, attachment, approval, or readiness without the corresponding task and asset receipts.
