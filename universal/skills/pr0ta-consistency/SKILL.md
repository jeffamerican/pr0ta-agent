---
name: pr0ta-consistency
description: "PR0TA visual consistency for recurring characters, locations, props, and wardrobe across shots: reuse approved Prep references (casting portraits, character sheets, looks, sets, props), generate only the missing ones, build provider consistency resources (Kling Elements, Seedance Characters), read character consistency bundles, and hold continuity through multi-shot and long-sequence generation. Read before generating any subject that appears in more than one shot."
---

# Visual Consistency & Continuity

A face that changes between shots breaks the film. This skill keeps recurring characters, locations, props, and wardrobe identical across generations.

**Who owns what.** Prep produces and approves the references: casting portraits and character sheets, looks, sets, and props, reviewed by the user in the Casting, Looks, Locations, Set Design, and Props pages. `pr0ta-prep` covers how Prep is run. This skill starts from those approved references and owns what comes next: the **provider consistency resources** (Kling Elements, Seedance Characters), the character consistency bundle, and continuity through shot generation.

Before choosing or creating references, call `memory_context_pack` for the scene, character, location, prop, wardrobe, or department scope. Approved memory is the source of truth for continuity; candidate memory can inform gap-filling but stays labeled as candidate. When the user approves a character sheet, an Element, a Seedance Character, a visual bible, or a wardrobe, prop, or set continuity rule, record it with `memory_record_decision` (or `memory_record_note` for context).

## The Rule

If the same character appears in more than one generated image or video shot, consistency is a hard requirement. Free-text-only prompts for a recurring character are a workflow error, not a shortcut.

Before any multi-shot generation with recurring characters:

1. Reuse the approved Prep references for every recurring subject.
2. Create or reuse the provider consistency resource for the route you will generate with: Seedance Characters for Seedance 2.0 Omni, Kling Elements for Kling routes that accept Elements.
3. Read the character consistency bundle and use its approved asset IDs, resource IDs, and provider payloads.
4. Repeat the same concrete description of the subject in every prompt, next to its resource token. The resource locks identity; the prose keeps the model oriented.

If approved references or resources are missing, create them and get them approved first.

## 1. Start From Approved Prep References

Read what Prep already has before creating anything. Do not keep a private continuity ledger alongside it unless the user asks for an export.

| Need | Tool |
|---|---|
| Everything for a scene or shot: breakdown, shot, cast with approved portraits and character sheets, stored Seedance IDs, voices, approved set/look/prop references, provider guidance, and missing-reference warnings | `production_context_get(scene_number, shot_number, character_names, include_provider_guidance: true)` |
| The cast with portraits, character sheets, and voices | `cast_list_get` |
| One character's portraits, description, wardrobe notes, and look timeline | `get_character_references(character_name)` |
| Locations, Looks, and Props department data for a scene range | `department_heads_get(start_scene, end_scene)` |
| Set references for a scene or location | `get_set_references(scene_number, location)` |
| 3D set environments, variants, and linked world assets | `set_environments_get(scene_number)` |
| Cast and reference elements for one Production Queue shot | `production_queue_character_elements_get(asset_uid)` |
| Tagged reference assets | `assets_list(reference_type: "character_reference", subject)` |

With a `scene_number`, `production_context_get` overlays the approved structured Prep references for that scene's sets, looks, and props, so it is the first call for any shot. Approved Prep references win over anything older or unlabeled.

Approval belongs to the user. Propose takes and let the user approve them in Prep; do not approve Prep takes on their behalf.

## 2. Generate Only the Missing References

When a recurring subject has no approved reference, or lacks an angle a resource needs:

1. **Resolve the model.** Call `models_preferred` with the modality for the job and pass the returned `model_id`:
   - `image_model`: a new portrait, character sheet, location plate, or prop reference.
   - `image_edit_model`: a new angle, expression, or wardrobe change from an approved reference, or a correction.
   - `elements_to_image_model`: a key frame composed from Element or reference bundles.

   If `model_id` is null, choose with `models_list(modality: ...)` and tell the user which model you chose and why. Read the model's notes in `pr0ta-image` and `pr0ta-prompting` before writing the prompt.
2. **Write the brief from Prep.** `casting_character_sheet_prompt_resolve` builds the app's character-sheet brief for a cast member; `casting_descriptive_prompt_generate` turns an approved portrait into a reusable description.
3. **Fan out and pick.** Generate four to six takes of each reference; the references set the ceiling for every shot that uses them. Results are candidates until the user approves one.
4. **Use real references when they exist.** Actor headshots, product photos, and location scouts upload as project assets (`pr0ta-image` → uploads) and are used like generated references.
5. **Label the approved reference** so bundles and Prep find it (next section), and save it back through the Prep page's save tool (`cast_list_save`, `department_heads_save`, `update_set_references`) when the user approves it.

### Label Approved References

Annotate with `assets_annotations_update` (or `assets_annotations_batch_update` for a set):

```json
{
  "asset_id": "asset_portrait_123",
  "reference_type": "character_reference",
  "character_name": "Sarah",
  "category": "portrait",
  "tags": ["reference", "character", "portrait", "approved"],
  "labels": { "reference_kind": "portrait" }
}
```

Use `category: "portrait"` for the front-facing hero and `category: "character_sheet"` (with `reference_kind: "character_sheet"`) for turnaround sheets. Sets, props, and looks use `set_name`, `prop_name`, and `look_name` the same way. `tags` replaces the asset's tag list. The bundle matches a character's references by `reference_type: "character_reference"` (or a portrait or character-sheet category) plus the character's name in `character_name` or `subject`, and always includes assets listed in a stored resource's `reference_asset_ids`.

## 3. Build Provider Consistency Resources

Provider resources turn approved references into an identity the video model holds. Build them from the approved Prep references, one per distinct subject, era or look, and wardrobe concept.

| Resource | Provider routes | Built from | Referenced in generation as |
|---|---|---|---|
| **Kling Element** (`resource_type: "element"`) | Kling routes that accept Elements | One frontal image plus one to three more angles of the same subject | `element_ids[]`; prompt tokens `@Element1`, `@Element2` |
| **Seedance Character** (`resource_type: "character"`) | Seedance 2.0 Omni | A trained Omni token from one clean portrait, or from a character sheet or up to three approved stills | `character_ids[]`; prompt token `@omni-character:<id>` |

Use Elements with Kling and Characters with Seedance 2.0 Omni; never mix the systems in one request.

**Steps:**

1. `consistency_resources_list(resource_type)` and reuse what exists. `consistency_resources_get` reads one.
2. Create what is missing:
   - **Seedance Character:** train the token with `generation_submit` on a Seedance character training route. On success PR0TA stores the Character for the project and returns its `project_character_id` with the token (`character_id`). Register a token trained outside PR0TA with `consistency_resources_create(resource_type: "character", resource: {name, provider: "muapi", provider_resource_id, reference_asset_ids})`.
   - **Kling Element:** create the Element on Kling from the approved frontal and angle images, then register its `element_id` with `consistency_resources_create(resource_type: "element", resource: {name, provider: "kling", provider_resource_id, reference_asset_ids, labels: {character_name}})`.
3. Make sure the resource's `reference_asset_ids` list the approved Prep references it was built from, so the bundle links them; `consistency_resources_update` adds references, changes labels or names, or archives a resource.
4. Read the bundle (next section) and confirm the new resource appears in `provider_payloads`.

`reference/provider-consistency-systems.md` has the training inputs, the Element creation route, the payload shapes, multi-modal references, multi-prompt, camera control, and correction edits.

## Character Consistency Bundles

Before generating a recurring character, read its bundle: one response with the approved reference assets, stored Kling Elements, stored Seedance Characters, and provider-ready payload fragments.

- MCP: `character_consistency_get(character_id)` or `character_consistency_get(name: "Kondiaronk")`.
- REST: `GET /api/v2/projects/{project_id}/characters/{character_id}/consistency` or `GET /api/v2/projects/{project_id}/characters/consistency?name=Kondiaronk`.

The bundle returns:

- `reference_assets[]`: approved portraits and sheets with `reference_kind` and stable URLs.
- `kling_elements[]` and `seedance_characters[]`: stored resources with their `provider_resource_id`.
- `provider_payloads`: `assets.portrait_asset_ids` / `turnaround_asset_ids`, `kling.element_ids`, and `seedance.character_ids` plus `seedance.prompt_tokens` (`@omni-character:<id>`).

Use `provider_payloads` directly: the `kling` block for Kling shots, the `seedance` block for Seedance 2.0 Omni shots, and the asset IDs as image references for any other route. If the bundle has references but no resource for the route you need, create it (section 3) and re-read the bundle.

**Several characters in one Seedance 2.0 Omni shot.** A request carries at most three `character_ids`, and every ID must appear in the prompt as its `@omni-character:<id>` token. `production_context_get` still flags more than one stored lock per request as unconfirmed, so test a take before relying on two or three; otherwise lock the primary character and pass the others as image references.

## Choosing a Consistency Route

Route choice follows `models_preferred` for the shot's modality (`pr0ta-video`). These capability facts decide how consistency is carried once the route is known:

- **Seedance 2.5 Omni Reference** has no trained-character field. Carry identity with approved images of the subject, each given one explicit job in the prompt (identity, wardrobe, set, prop, motion, or audio), and repeat the defining traits in prose.
- **Seedance 2.0 Omni** is the route with trained Seedance Characters (`character_ids[]`) and positional `@image1`/`@video1`/`@audio1` binding across images, videos, and audio.
- **Kling routes with Elements** carry identity through Element bundles, and add structured `camera_control`, multi-prompt shots, and Motion Brush.
- **Other routes** take the bundle's approved reference assets as image references.

When the user needs a capability only one route has (trained tokens, Elements, structured camera control), say so and let them choose.

## Continuity Workflow

1. **Resolve context**: `production_context_get` for the scene and shot.
2. **Fill gaps**: generate only missing references with the resolved model; the user approves; label them.
3. **Build resources**: Elements and Characters from the approved references.
4. **Read bundles** for every recurring character in the shot.
5. **Global visual bible and storyboard sheets** for reference-heavy Seedance productions: reuse one approved production bible as the first image reference; list beat chunks with `storyboard_chunks_list` and generate chronological sheets with `storyboard_reference_sheet_generate`; place the approved sheet and chunk references after the bible (`pr0ta-video` → `reference/seedance-global-storyboard.md`).
6. **Key frames**: compose scene key frames from Element or reference bundles (`elements_to_image_model`).
7. **Video**: pass the bundle's `provider_payloads` in every generation request for that character.
8. **Multi-shot sequences**: use multi-prompt when shots share a scene and must hold consistency within one generation.
9. **Long continuous sequences (30s and more)**: feed the previous clip to Seedance 2.0 Omni as `@video1` with the approved character stills, and treat the result as reference-guided continuation: inspect and trim every join. PR0TA's unified extend catalog does not expose MuAPI's provider-native extend path, which needs the original provider `request_id` (`pr0ta-video` → `reference/seedance-omni.md`).
10. **Correction passes**: fix drift in key frames with an image edit (`image_edit_model`) against the approved reference before generating video.
11. **Reuse**: Elements and Characters persist for the project. Reuse them for reshoots, added scenes, and variations.
12. **Location consistency via world models**: anchor a recurring location to one Marble world or scan as the structure authority and to the same approved location plates as the appearance authority; review every result against the plates (`pr0ta-hybrid` → `reference/world-anchored-references.md`).

## On-Screen Text Needs Its Own Check

Elements and identity tokens do not protect typography. Choose a text-capable route, quote the exact copy, and inspect every frame for spelling, glyphs, and layout stability. If native video text fails that check, generate a verified still and animate it on the timeline (`pr0ta-prompting` → "Line-Locked Poster Prompt", `pr0ta-video` on-screen text, `pr0ta-timeline` → "Ken Burns as a Clip Property").
