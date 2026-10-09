---
name: pr0ta-prep
description: "PR0TA pre-production from an approved direction to a generation-ready queue: script breakdown, Script Supervisor questions, element review, project memory, style worlds, casting and voices, locations and set design, looks, props, shot lists, storyboards, and the Production Queue. Read after Creative Direction is approved, or when a project already has a breakdown."
---

# PR0TA Prep

After Creative Direction is approved (`pr0ta-development`), PR0TA breaks the
published screenplay down and its departments prepare the production. This
skill works that pipeline in order:

**Breakdown → review → style → casting → locations/sets, looks, props → shot lists → storyboards → Production Queue**

Each stage reads the approved results of the stages before it, so work in order
and let each finish. `prep_production_capabilities` maps each page to its
tools. Call `memory_context_pack(task_intent, scope)` before each department's
creative work; project memory holds the approved decisions, and approved
memory outranks everything else. Record accepted decisions with
`memory_record_decision` and notes with `memory_record_note` (contract:
`pr0ta-api` → "Project memory").

## 1. Follow the breakdown

After approval the Script Supervisor reads every scene, then Casting,
Production Design (locations), the Stylist (looks) and the Propmaster (props)
run in parallel. `breakdown_status` reports each stage, what failed, and what
waits on the user. Poll it with backoff; the breakdown of a feature-length
script takes a while.

`breakdown_rerun(scenes?)` reruns departments for the given scenes (for example
after a location moved to another style world), or resumes the whole breakdown.
It spends credits: rerun only when the user asks.

## 2. Work the review queues

The Script Supervisor asks about what verification could not settle, and the
element review holds identity and classification decisions. These are the
user's calls; bring them to the user in batches.

- `supervisor_review_list` lists open questions: omissions, removed claims or
  elements, uncertain classifications, withheld synopses.
  `supervisor_review_answer(flag_id, action, value?, scene_number?)` answers one.
  Actions by flag type: omission `add` | `dismiss`; removed claim or element
  `restore` | `keep_removed`; uncertain classification `classify` |
  `leave_out`; withheld synopsis `write` | `keep_blank`.
- `get_breakdown_element_review(scene_number)` pages a scene's element
  mentions. `breakdown_element_review_decide(scene_number, fingerprint,
  version, mention_id, action, target_id?)` decides one mention: `action` is
  `link` (to the existing element named by `target_id`, required for a link),
  `separate`, `unresolved`, or `exclude`. Take `fingerprint`, `version` and
  `mention_id` from the read.

Answer only with the user's decision or with what the screenplay itself states.

## 3. Read the breakdown

- `get_scene_breakdown(scene_number, scene_range_end?)`: the Supervisor's
  scenes: characters, locations, props, wardrobe, continuity.
- `production_context_get(scene_number?, shot_number?, character_names?)`:
  breakdown, casting, sets, props, looks and approved references for a scene or
  shot, in one call. Use it before any generation.
- `get_character_references`, `get_set_references`: department results for one
  character or location.

## 4. Style

The Director read seeds style worlds: named visual languages, one default, with
scene assignments. `style_package_get` reads them. Refine with
`style_world_update`, add with `style_world_create`, move scenes with
`style_world_assign_scenes`. Moving scenes does not reread them by itself:
when the user wants the departments to follow the new world, run
`breakdown_rerun(scenes)` for the moved scenes. `style_package_save` persists the whole Style page with its reference
assets. Style prompts feed every downstream prompt; agree them with the user.

## 5. Casting and voices

`cast_list_get` returns the cast with portraits, character sheets and voices.
Casting runs in the breakdown; refine with the user, then `cast_list_save`
(`reconcile_existing: true` changes the fields you send for the members you
list and keeps the rest; without it the list you send is the whole cast).

- Portrait prompts: `casting_portrait_prompt_write(character, direction)` has the
  Casting Director write the prompt from the screenplay, Producer and Director
  reads, the Style world, project memory and the person's description in
  `direction`, and saves it to the cast record where Casting shows it. It works
  without a breakdown, for characters described only in conversation, and
  revises an existing prompt. Do not write portrait prompts yourself or
  delegate them to a Casting worker.
- Portraits and character sheets: generate the portrait with `generation_submit`
  (`category: "portrait"`, `subject`: the character) so it lands in Casting; resolve the model with
  `models_preferred(modality: "image_model")` (or `image_edit_model` for edits of
  an approved portrait); `casting_character_sheet_prompt_resolve` builds the
  app's character-sheet brief; `casting_descriptive_prompt_generate` describes
  an approved portrait for reuse.
- Voices: `voices_list` to browse, `casting_voice_design` or `voices_design` to
  design, `voices_clone` from a sample, `casting_voice_sample_generate` for a
  line in the character's voice. Model choices follow `models_preferred`
  (`voice_design_model`, `dialogue_model`). See `pr0ta-audio`.
- Recurring characters need provider consistency resources before shot
  generation; `pr0ta-consistency` owns that.

## 6. Locations, sets, looks, props

`department_heads_get(start_scene?, end_scene?)` loads the Locations, Looks and
Props pages. The two write tools name the departments differently:

- `department_heads_save(department, scenes, ...)` persists page edits through
  the same storage the pages use; `department` is `designer` (Locations),
  `stylist` (Looks) or `propmaster` (Props).
- `department_read_generate(department, scenes, producer_analysis,
  director_analysis)` regenerates a department read for chosen scenes;
  `department` is `locations`, `looks` or `props`.

3D sets: `set_environments_get` lists environments per Production Design
variant; `set_environment_upsert`, `set_environment_asset_link` and
`set_environment_collider_materialize` build them. See `pr0ta-hybrid` for
world-anchored references; its Recipe F inspects a set's objects and moves
existing ones by exact name with `blender_job_submit`
`scene_plan.object_updates`, never by recreating them. For a consistent
camera across a scene's boards, give every job the same `scene_plan.camera`
`gate` (`super35`, `full_frame`) or `sensor_width_mm` / `sensor_height_mm` and
`sensor_fit`, and confirm the lens and rendered FOV in
`result_refs.scene_inventory.camera`.

Characters in a set are `scene_plan.figures`, never cylinders or spheres. Each
figure is a posable mannequin: `body` (adult_male, adult_female, teen, child,
heavy, slim), `height` in meters from the cast, a named `pose` (stand, walk,
run, sit, sit_ground, crouch, kneel, lean_rail, point, wave, drink, phone,
throw_windup, throw_release, fight_stance, punch, charge, push, carry, climb,
lie_back, fall and more; the live schema lists them all), plus `look_at` and
left or right hand targets in world meters, and `joint_rotations` for fine
adjustments. Once a cast member has a rigged model (a Meshy `rigged_character`
GLB), set `character_asset_id` and the same plan poses that model. For video
blocking, give a figure timed `keys` (poses and positions over seconds), a
walk or run `path` that ends in `end_pose`, or `motion` with an animated
humanoid asset (Meshy walking/running or animation GLBs, DeepMotion Animate 3D,
Hunyuan motion FBX). Naming a figure that an earlier job built replaces it, so
re-pose a character by sending its figure again; move a whole figure with
`object_updates` on its name. Old primitive stand-ins (cylinders, spheres) are
deleted with `scene_plan.object_removals` by exact name, with their children,
in the same job that adds the figures; a figure may take a removed name.

Most library poses are recorded motion, not hand-set angles (kneel_sit is
kneeling back on the heels; kneel_both is kneeling tall). When no library pose
fits a beat, prefer recorded motion over `joint_rotations`: give the figure
`motion` from a Meshy animation preset GLB or a Hunyuan text-to-motion take
(12–20 words describing one body, ending with it holding still); in a still
render `clip_offset` picks the frame. A hand target the arm cannot reach makes
the figure stoop or lean toward it. After a job, read `figures` in its
`scene_inventory`: `hand_targets.*.hand_surface_m` is how far the deformed hand
is from each target and `mesh_lowest_z` shows whether the body rests on the
floor; report contact only when those agree. A set variant is a Locations look registered in
Prep: `department_heads_save` (designer) returns `set_variants`, mapping each
saved look to its `variantId`. `set_environment_upsert` takes that id, or the
look's id or label with `scene_number`; `set_environments_get(scene_number)`
lists `set_variants` and `unregistered_looks`. No generation is involved.

## 7. Shot lists

The Director writes shot lists per scene from the Supervisor's scene and the
approved reads:

- `shotlist_scene_descriptions_generate` first, for concise scene descriptions.
- `shotlist_generate(scene, producer_analysis, director_analysis)` for one
  scene, `shotlist_generate_batch(scenes, ...)` for many; both return tasks.
- `get_scene_shotlist(scene_number)` reads a result; `shotlist_scene_chat`
  asks the Director to revise a scene; `save_scene_shotlist` saves an edited
  list.

Take `producer_analysis` and `director_analysis` from `project_metadata_get`
(`producerRead`, `directorRead`).

## 8. Storyboards

- `storyboard_generate(scene, director_shotlist, producer_analysis,
  director_analysis)` or `storyboard_generate_batch` writes storyboard prompts
  from the shot lists.
- `storyboard_sequences_get` / `storyboard_sequences_save` manage the
  Storyboarding sequences the Queue is built from.
- For multi-shot video routes that take storyboard sheets, `storyboard_chunks_list`
  assembles beat chunks and `storyboard_reference_sheet_generate` renders a
  reference sheet per chunk; see `pr0ta-video`.
- A chunk's sheet needs every shot's first frame approved, and only the person
  approves. Generate first-frame images (category `storyboard`), then
  `storyboard_first_frame_propose(scene, shot, asset_id)` puts one on the shot
  as its candidate. Show the candidates on their own review card
  (operator_checkpoint: requires_review=true, asset_ids,
  approves_first_frames=true): approving it approves them, asking for changes
  withdraws them. The person can also approve in Storyboarding. `get_shot_assets` reports each shot's
  `first_frame` state. Never approve on the person's behalf.
- A native storyboard is one first-frame image per shot. A multi-panel sheet
  is a reference, not per-shot frames: nothing splits it onto shots, so
  generate or edit one image per shot (the sheet can be a reference) and
  propose each.
- `storyboard_pdf_export(scene_number?, scene_range_end?, scene_numbers?,
  layout?, approved_only?, ...)` prints the board as the Storyboarding export
  does (six standard layouts, at most 600 panels), free. It files the PDF as a
  project document and returns `asset_id` and a `download_url` for the person.

## 9. Production Queue

The Queue turns storyboards into generation items with prompts, references and
takes. It is where scripted shots are generated; `pr0ta-image` and
`pr0ta-video` hold the per-model knowledge the prompts follow.

1. `production_queue_list(offset?, limit?)` pages the Queue; each item's `id`
   is the `asset_uid` the other Queue tools take. List first.
2. `production_queue_refresh(asset_uids, reset_analysis?, full_reconstruct?)`
   rebuilds those items from Storyboarding after the storyboards change.
3. `production_queue_analyze(asset_uids)` has the Cinematographer or Composer
   prepare prompts; `production_queue_prompt_set` and
   `production_queue_asset_update` edit them.
   `production_queue_character_elements_get(asset_uid)` resolves cast elements
   before character shots.
4. `production_queue_regenerate(asset_uid, generation_params,
   generation_prompt?)` generates a take and returns a task;
   `production_queue_regenerate_batch(asset_uids, generation_params)` does
   several. `generation_params` is an object and may be `{}`: the Queue then
   generates the item's own component (image, video or audio, from its type)
   with the prompt and parameters analysis saved for it. Optional keys:
   `generation_component` (`image`, `video` or `audio`), `prompt` (or
   top-level `generation_prompt`), and `model_id` only when the user names a
   model; otherwise the Queue resolves the model from the user's Tools
   settings and the admin pins, unless the item already names one. A
   storyboard-sequence or chunk video item fails with
   `cinematographer_optimization_required` until `production_queue_analyze`
   has finalized its prompt and model.
5. `production_queue_take_select`, `production_queue_take_favorite` and
   `production_queue_component_selection_set` record choices.

Generate in batches the user can review, not the whole Queue at once.

**From the Queue to Post.** Selected takes do not move to the timeline by
themselves. Two paths:

- **First Cut** (the Timeline toolbar in the app; REST
  `POST /api/editor/{project_id}/auto-assemble-async` with `scene_numbers?`,
  `style` `assembly` | `rough_cut` | `fine_cut`, `save_timeline: true`,
  `sequence_name`, `sequence_settings?`): the Editor assembles a new sequence
  from Queue items that have a finished take, using each item's selected take
  (else its favorite, else its first). It returns a task; the saved sequence is
  `result_refs.sequence_id`. There is no MCP tool for it; in-app or over MCP,
  ask the user to run First Cut.
- **Clip by clip:** place each selected take's asset on a sequence yourself
  (`pr0ta-timeline` → "Clips").

Either way, continue in `pr0ta-timeline`.

## When a project has no script

A short piece with no story (a promo, a montage, a title sequence) may skip
this pipeline: plan it with a cue sheet (`pr0ta-sync`) and generate directly
(`pr0ta-image`, `pr0ta-video`). Anything with characters and scenes goes through
the screenplay.
