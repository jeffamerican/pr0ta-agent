# Set builds: blockout or premium, and the routes that combine with them

A Blender set build is made at one of two tiers. Pick the tier from what the
person asked for, set it on the build, and say which you chose.

## Pick the tier

- **Blockout**: simple and cheap. Layout, scale, blocking and shot cameras for
  reference, previs, the Blocking page and guidance renders. Choose it when the
  set only has to be right in space, or when the request says nothing about how
  real the set must look.
- **Premium**: detailed and costly, meant to look real in its own right. Choose
  it when the person wants the set itself to look real: "photoreal", "a proper
  replica", "make it look like the real place", set renders used as finals, or
  "view it in the Space app" / "walk around it on my phone".

A premium build's main deliverable is a **real-time asset**: the set with its
light baked in, delivered as `set_environment_realtime.usdz` and
`set_environment_realtime.glb` (role `realtime_model`). Publish it with
`review_submit_assets` and the ProtaFilm|maker Space app opens it on iPhone
with no extra steps; Quick Look opens the USDZ too. The build's Cycles stills
are previews of it. Build premium with `render.passes []` so the bake gets the
whole job, and render stills in a later job on the saved `.blend`. Details,
limits and the re-bake: `reference/set-materials.md`, "Real-time asset".

On today's CPU worker premium video is short (48 frames, 2 s, per job) and one
premium job runs at a time across the platform. Make premium stills and the
real-time asset; render a moving premium shot in 2 s pieces, or use a blockout
for motion until the GPU worker exists.

When the tier is unclear, ask, or offer a blockout first with premium as the
next step. Premium costs more: the person sees its cost through the normal
quote before it runs, never after.

## Build premium properly

Use what the live `blender_job_submit` schema offers for the premium tier (read
it first; the set of features grows):

- Real-world dimensions taken from reference photos and any known measurements:
  room size, opening widths, ceiling height, step and plinth heights.
- Bevelled and subdivided architecture: no hard, faceted primitive edges.
- Mouldings, cornices, coffers, columns and other repeats from profile sweeps,
  arrays and geometry nodes rather than stacked boxes.
- PBR or procedural materials from the material library at the correct texel
  scale for the surface's real size, with displacement or normal detail where
  the surface has relief (stone, plaster, wood, tile).
- Motivated lighting: an HDRI or sun and sky for daylight, practicals where the
  set has them, intensities that match the reference photos.
- Final-quality renders.

Then compare each render with the reference photos side by side (proportions,
materials, light direction and falloff) and iterate on what differs. A worker
receipt proves the job ran, not that it matches.

Upgrading a blockout to premium reuses the blockout's layout and dimensions:
refine it rather than rebuilding from scratch, so cameras and blocking already
approved on it still hold.

## Refining in steps

A refinement on a saved set that adds objects in several steps can skip the
runtime GLBs on the intermediate ones: `source_asset_id`, `export_glb: false`,
`save_blend: true`. Each step is still a build against the set's budget. Export
on the last step, which the person reviews. Until then the set's
`runtimeDelivery.newerSourceWithoutRuntime` names the newest `.blend`, viewers
show the older build, and approving without a revision is refused: export first.

With `save_blend: true` the runtime GLBs never cost the build. A desktop or Quest
GLB that fails, stays over its size cap after its textures are shrunk, or would
not finish inside the worker's time is skipped, and the `.blend` is still
delivered. `result_refs.delivery_notes` (`runtime_export_missing`,
`realtime_asset_missing`, `interrupted`, `renders_missing`) and the task message
say what was not delivered and why; `scene_inventory.runtime_export.skipped`
lists each skipped profile. A job stopped after its save keeps what it finished
(the `.blend`, GLBs, renders already made). Stopped by the worker's limit, it is
charged only the build; `interrupted.error` means Blender failed: nothing is
charged, and a rerun meets the same error, so fix its cause before rendering
again. Export the missing GLBs with
a job of their own on that `.blend`: no objects, `export_glb: true`,
`render.passes []`.

## Other routes, combined with either tier

- **A world from photos of the real place**: when the person wants the actual
  captured space, build a Marble world with `world_generation_submit` from real
  photographs of it (multi-image reconstruction when views overlap). Input
  rules: `pr0ta-prompting/reference/marble-world-generation.md`; using a world
  as shot structure: `pr0ta-hybrid` → world-anchored references.
- **An existing model or scan**: for an existing object or space (a statue, a
  landmark, a vehicle), import an existing model or scan with
  `assets_import_url` and place it in the build.
- **Image-to-3D for props**: unified generation's image-to-3D mode
  (`pr0ta-api` → unified generation).

These mix freely: a premium build around an imported scan, a blockout for
cameras registered to a photo-built world, and so on.

## Before reporting a capability as missing

Check these routes and the full Blender toolset first: the premium tier's
features, imports, worlds from photos, image-to-3D. Report a gap only when
none of them can deliver what was asked, and say which you checked.
