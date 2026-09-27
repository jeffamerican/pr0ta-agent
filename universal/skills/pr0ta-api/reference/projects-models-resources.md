# Projects, Models, and Consistency Resources

## Project Management (Auth Required)

Every project route takes the project's UUID or slug in the path. Pass it
explicitly; no API call depends on an active project.

| Operation | Route |
| --- | --- |
| List projects the user can access | `GET /api/v2/projects` |
| Create | `POST /api/v2/projects` with `{"name": "...", "description": "..."}` |
| Get | `GET /api/v2/projects/{project_id}` |
| Update | `PATCH /api/v2/projects/{project_id}` |
| Archive | `POST /api/v2/projects/{project_id}/archive` |
| Delete | `DELETE /api/v2/projects/{project_id}` |

Each project includes `id`, `name`, `created_at`, `asset_count`, `settings`, and
`is_active_project`. The web app's active project (`POST
/api/v2/projects/{project_id}/select`, `DELETE /api/v2/projects/active`,
`?select=true` on create) is a browser-session convenience: PATs cannot set it,
and generation and every other project route take `project_id` instead.

MCP: `project_metadata_get`.

MCP-only project tools: `list_projects`, `create_project`,
`get_project_metadata`.

---

## Model Discovery

### Preferred model per modality

```
GET /api/v2/models/preferred
GET /api/v2/models/preferred?modality=image_model
```

MCP: `models_preferred(modality=...)`. Returns `resolution_order`
(`user_default`, then `admin_pin`), `when_unresolved`, and `modalities`, keyed by
modality. Each entry has `modality`, `model_id` (null when nothing is set or
pinned), `source`, `resolved_from`, `pin_rank`, `pinned` (the admin's pins along
the modality's fallback chain), `fallback_modalities`, `in_catalog`, and the
catalog fields `display_name`, `alias`, `generator`, `provider`,
`supported_modes`, `generation_submit_supported`, and `image_kind` when the
model is cataloged. The caller's Settings → Tools choices apply only to
authenticated requests. An unknown modality returns `400` with
`known_modalities`. How to use it: `SKILL.md` → "Choosing a model".

### Filtered catalog

```
GET /api/v2/models
GET /api/v2/models?generator=image&image_kind=text_to_image
GET /api/v2/models?generator=image&image_kind=image_edit
GET /api/v2/models?generator=video
GET /api/v2/models?search=sam%203d
```

No auth required. Returns the complete visible provider catalog: generation
models, 3D and world endpoints, analysis and utility tools, training endpoints,
transcription and voice models, and LLMs. Filter by `generator` (`image`,
`video`, `motion`, `3d`, `world`, `lipsync`, `audio`, `music`, `voice`,
`transcription`, `training`, `utility`, `llm`), optionally `image_kind`, or
`search` across ids, names, providers, tags, and descriptions. With
`project_id`, each row also carries its rights-policy status for that project.

Every row includes `id`, `alias`, `provider_model_id`, `display_name`,
`generator`, `provider`, `supported_modes`, `generation_submit_supported`, and
`api_access`, so clients can tell normal generation from catalog-only or
dedicated workflows. Image rows include `image_kind`; upscalers are utilities
because they use a dedicated route. Pass `provider_model_id` (or a listed
`alias`) as the request's `model`.

MCP: `models_list` pages the same catalog (`offset`, `limit` up to 200, `total`,
`has_more`). With `modality`, it returns that modality's curated models, pinned
first, marked `pinned` and `pin_rank`; `curated_only=true` limits a category to
the admin-curated list.

### Parameters, defaults, and pricing

```
GET /api/crew/model_defaults?model_id={model_id}  — parameter schema and defaults for a model
GET /api/crew/model_pricing?model_id={model_id}   — billable and display pricing
GET /api/crew/providers                           — provider list (all modalities)
```

`model_defaults` returns the authoritative parameter list and types before you
call `/generate`. Catalog aliases resolve first: `requested_model_id` keeps the
caller's input and `resolved_model_id` names the canonical provider endpoint.
MCP `models_get_defaults` adds `supported_modes` and, for models unified
generation accepts, `request_defaults` (`generator`, `mode`, `model`).

An unavailable or non-submittable model returns `400` naming why; requests are
never rerouted to a different model.

---

## Reusable Consistency Resources

The project API exposes persistent, reusable consistency resources for maintaining character, prop, and location consistency across generations.

### Element Bundles (Kling)

Elements are project-scoped Kling reference bundles for character/prop/location consistency. Create them once, reuse across all generations in the project.

**Create Element:**
```
POST /api/v2/projects/{project_id}/elements
```
```json
{
  "name": "Lead Hero Element",
  "provider": "kling",
  "provider_resource_id": "101",
  "reference_asset_ids": ["c4f3bdf3-472a-4d6a-ad08-ea3872b8ed0c"]
}
```

**List Elements:**
```
GET /api/v2/projects/{project_id}/elements
```

**Get Element:**
```
GET /api/v2/projects/{project_id}/elements/{element_id}
```

**Update Element:**
```
PATCH /api/v2/projects/{project_id}/elements/{element_id}
```

**Delete Element:**
```
DELETE /api/v2/projects/{project_id}/elements/{element_id}
```

Both project element IDs and Kling provider element IDs are accepted during resolution.

### Character Profiles (Seedance / MuAPI)

Characters are project-scoped Seedance/MuAPI character identities for persistent character consistency. A Seedance character is built from a **frontal image** (identity anchor), a **character sheet** (multi-panel reference at 4K 21:9 showing front, back, side, poses, expressions), and optionally one or two more images. Generate the character sheet first (see `pr0ta-consistency`), then register the character here. Seedance 2.0 Omni is the route that consumes trained character tokens; Seedance 2.5 Omni Reference takes approved reference assets instead.

**Create Character:**
```
POST /api/v2/projects/{project_id}/characters
```
```json
{
  "name": "Lead Hero",
  "provider": "muapi",
  "provider_resource_id": "char_approved_hero_v1"
}
```

**List Characters:**
```
GET /api/v2/projects/{project_id}/characters
```

**Get Character:**
```
GET /api/v2/projects/{project_id}/characters/{character_id}
```

**Update Character:**
```
PATCH /api/v2/projects/{project_id}/characters/{character_id}
```

**Delete Character:**
```
DELETE /api/v2/projects/{project_id}/characters/{character_id}
```

### Character Consistency Bundles

Before multi-shot character-consistent generation, read the character's consistency bundle — a single endpoint that returns all approved reference assets, stored Kling Elements, stored Seedance/MuAPI tokens, and provider-ready payload snippets in one response.

**Get Consistency Bundle by Character ID:**
```
GET /api/v2/projects/{project_id}/characters/{character_id}/consistency
```

**Get Consistency Bundle by Character Name:**
```
GET /api/v2/projects/{project_id}/characters/consistency?name={character_name}
```

Response includes:
- `reference_assets[]` — approved portraits and turnaround sheets tagged as `character_reference`
- `kling_elements[]` — stored Kling Elements with `provider_resource_id`
- `seedance_characters[]` — stored Seedance/MuAPI characters with `provider_resource_id`
- `provider_payloads` — ready-to-use snippets:
  - `provider_payloads.assets` — `reference_asset_ids`, `portrait_asset_ids`, `turnaround_asset_ids`
  - `provider_payloads.kling` — `element_ids[]` for direct use in generation requests
  - `provider_payloads.seedance` — `character_ids[]` and `prompt_tokens[]` for Omni Reference

**Workflow:** Tag approved reference images with `reference_type: "character_reference"` and `category: "portrait"` or `"character_sheet"` via `PATCH /api/assets/{project_name}/annotations`. Store Kling Elements via `POST /elements` and Seedance tokens via `POST /characters`. Then read the bundle before generation and use the `provider_payloads` directly. See `pr0ta-consistency` → "Character Consistency Bundles" for the full workflow.

---
