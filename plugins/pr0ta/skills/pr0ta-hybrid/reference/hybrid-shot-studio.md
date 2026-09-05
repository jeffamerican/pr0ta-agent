# Hybrid Shot Studio

The primary home is **Post → Hybrid Production**. `/hybrid?project=…` opens
sequences; existing `shot`, `foreground`, and `environment` links still open this
detailed editor. `standalone=1` starts a single-shot workspace. For an edited
sequence, read `hybrid-sequences.md` before preparing individual shots.

The project workspace stages a performance, authors a photographic background,
and directs model-driven hybrid edits. The UI and skill share versioned shot
records; the preview is visual direction, not a finished composite or tracker.

## Prepare and hand off

1. Read the project's approved appearance and environment decisions.
2. Call `hybrid_generation_capabilities` for available operations, models, accepted
   advanced settings, and input-role notes. Do not invent model IDs or carry
   settings from another model.
3. Call `hybrid_shots_create` with `request` containing a label, scene/shot/sequence,
   `foreground_asset_id`, `plate_asset_id`, optional `environment_id` and
   `environment_asset_id`. Standalone project GLBs and supported splats work too.
4. Open its `deep_link`, which includes project and shot identity. Stage,
   Background, and Result are views of the same shot.
5. After the user finishes, call `hybrid_shots_get` again. Saved state, not a
   screenshot or older conversation, supplies the camera and selected references.
6. Update with `hybrid_shots_update(shot_id, request: {expected_revision, changes})`.
   On 409, reread and reconcile; never blindly replay a stale full snapshot.

## Staging and background editing

- Foreground position, scale, and rotation are direction controls. Capture direction
  saves a reference still. Preview opacity is not a generation parameter.
- Environment views load GLBs and supported Gaussian splats, overlay a plate,
  and save geometry-only PNGs with camera provenance.
- Auto-match restores compatible saved cameras. Calibrated GLB feature/depth
  matching can solve a camera; poor fits are rejected. The separate 2D check
  never claims a homography recovers camera translation or scene depth.
- Camera/environment changes invalidate stale structure and staging references.
  Render again before using the changed camera as guidance.
- For **3D-guided extension**, widen the environment view, save its PNG as
  `structure_asset_id`, choose Nano Banana 2 `plate_edit`, and retain the
  photographic plate as appearance authority. The adapter separates geometry
  from photographic materials and lighting.
- `inpaint` and ordinary `outpaint` consume `plate_asset_id`, retaining camera,
  environment, structure, and staging as provenance. Inpaint masks must match
  that plate. To correct a different materialized image, explicitly select it
  as the plate; for geometry-guided extension use `plate_edit`.
- Background brush masks use **white edits, black preserves**. SwitchX foreground
  mattes use **white keeps**, so the two are not interchangeable.
- Generated images are candidates. Select a result as the photographic plate
  before the video pass; completion does not approve it automatically.

## Submit and resume

Call `hybrid_shot_generate(shot_id, request: {source_revision, idempotency_key})`
when generation is authorized. Use a stable key for one intended submission.
Retry an uncertain response with the same key and revision; a new key is a new
paid attempt. The service pins the immutable revision before dispatch.

The existing `tasks_get` tool polls the returned task. REST
`GET /api/v2/projects/{project_id}/hybrid-shots/{shot_id}/runs` reconciles bound
task receipts with ready project assets. The Result view can resume an unfinished
reservation and displays outputs against their original revisions. Completion
cannot overwrite newer edits.

SwitchX consumes the foreground and one photographic look plate. It does not
apply raw staging transforms or render the environment: author the photographic
framing first. Seedance edit consumes supported independent appearance, geometry,
and staging references with explicit roles. Neither guarantees exact placement
just because the direction preview does.

Use shared plate/environment IDs and the sequence field to relate shots. A shot
update never modifies another shot or the canonical set. For multiple-shot
changes, update each intended shot with its own current revision and report
conflicts individually.
