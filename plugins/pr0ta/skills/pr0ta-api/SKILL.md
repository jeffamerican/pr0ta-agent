---
name: pr0ta-api
description: "PR0TA MCP and REST API reference for auth, agent tool calls, raw endpoint schemas, task polling, assets, model discovery, timeline/debug APIs, review-room APIs, and MCP setup. Read when a domain skill does not include the exact route contract or when debugging API failures."
---

# PR0TA API Reference

This reference covers the PR0TA MCP tool surface and REST API endpoints available for programmatic access.

## Agent Execution Default: MCP First

PR0TA distributions bundle the remote MCP connector or its setup details, pointing at `https://app.pr0ta.com/api/mcp/mcp`.

For agent workflows, prefer MCP tools over ad hoc REST/curl calls whenever an MCP tool exists. Use REST for routes not yet exposed through MCP, high-volume scripts, and direct file downloads from MCP-provided links.

**MCP call pattern:**

1. Call `list_projects`, or call `create_project` when the requested project does not exist.
2. Pass `project_id` to every project-scoped tool. `create_project` and `list_projects` are not project-scoped.
3. Call `memory_context_pack` before prompt-building, generation, editorial, or department decisions.
4. For guided stylized designed-world references, call `agent_chat_orchestrate_prompt` with `prompt_profile: "designed_world_reference_image"`. Prefer `guidance_package` with paired `flat_structural` and `depth_normalized` passes, then submit the approved appearance and required continuity references. The legacy semantic-structure plus appearance pair remains supported.
5. Submit long-running media work with `generation_submit` or `generation_batch_submit`.
6. Poll with `tasks_get`; cancel stuck work with `tasks_cancel`. Call `agent_chat_resume` only when the failure actually includes `error.details.retry_token`; exhausted provider or repair attempts intentionally omit it.
7. Resolve assets with `assets_list` or `assets_download`.
8. Record accepted decisions or durable notes with `memory_record_decision` or `memory_record_note`. When an explicit approval is not already bound to the Operator turn, call `memory_get_confirmation` for PR0TA-chat approval or `memory_request_confirmation` for interactive MCP approval, then pass the returned reference unchanged.

Submit tools return task IDs, not completed media. Treat `tasks_get` as the canonical state and result contract.

## ProtaFilm|memory MCP Tools

ProtaFilm|memory is the shared project intelligence layer for PR0TA agents. It is not a chat-history substitute and not just semantic search: it stores cited sources, extracted claims, decisions, graph relationships, context-pack usage, conflicts, and provenance. Every agent should read from it before significant work and write durable conclusions back into it.

**Use before agent work:**

```json
{
  "project_id": "project-uuid-or-slug",
  "agent_role": "director",
  "task_intent": "storyboard_prompt",
  "scope": {"scene_id": "12", "asset_id": "optional-asset-id"}
}
```

Call with `memory_context_pack`. The response contains compact, prompt-ready JSON:

- `approved_facts`: approved claims ranked highest.
- `candidate_claims`: usable immediately but must remain marked as candidate.
- `decisions`: approved or candidate creative/production decisions.
- `references`: cited source/reference material.
- `continuity_constraints`: facts that should constrain prompt generation, styling, shot lists, edits, and reviews.
- `conflicts`: contradictions or stale downstream work to surface before acting.
- `open_questions`: missing or unresolved project questions.
- `citations`: source labels and claim/source IDs.

**Targeted lookup:** use `memory_search` with `query`, `department`, `scope_type`, `scope_id`, and `limit`.

**Graph inspection:** use `memory_graph` with `lens` (`scene`, `department`, `decision`, `conflict`, or `asset_provenance` where available), plus optional `scene` or `department` filters. Prefer graph views when you need to understand source -> claim -> decision -> affected assets/agents.

**Write-back after work:**

- `memory_get_confirmation`: resolve the latest eligible persisted user approval for the calling role; pass the returned message ID unchanged as `memory_record_decision.user_confirmation_ref`. An actor-attributed `approved` or `approved_with_notes` review-event ID can be passed instead when paired with that submission's exact `approved_asset_id` and an asset/reference/selection/approval semantic facet.
- `memory_request_confirmation`: in an elicitation-capable MCP client, ask the authenticated user to approve the exact decision, semantic key, and asset. Pass the returned short-lived signed token unchanged to `memory_record_decision`; it cannot authorize another user, project, asset, semantic key, or decision text.
- `memory_record_decision`: record accepted creative or production decisions. Include `department`, `scope_type`, `scope_id`, `status`, and `source_claim_id` when known. When confirmation is a review event, Current memory is canonically bound to that event's approved asset and semantic key; agent-authored `decision` text cannot substitute another asset.
- `memory_record_note`: record durable notes that future agents should see. Use this for selected references, continuity constraints, accepted prompt strategy, client/director notes, and editorial conclusions.

**Status rules:** Approved memory ranks above candidate memory. Candidate memory is available to agents immediately but should be identified as candidate in reasoning and user-facing summaries. Rejected memory is excluded. Superseded memory remains visible for provenance but should not be used by default.

Do not flatten memory into anonymous prose. Preserve citations and claim IDs when passing memory into prompt builders or explaining why an agent made a decision.

## Authentication

PR0TA supports remote MCP OAuth for hosted connectors and PAT bearer auth for REST/local stdio fallback.

When PR0TA tools are not discoverable, connect `https://app.pr0ta.com/api/mcp/mcp` through the host's remote MCP settings and complete browser OAuth. Use the host-specific helper or instructions included in the installed distribution when available. Start a fresh session if the host retains its original tool inventory. If the host cannot detect PR0TA OAuth, check the live metadata before falling back to REST; public PKCE clients require `token_endpoint_auth_methods_supported` to include `none`. If the host lists the authenticated tools but the model cannot call them, the remaining fault is host-side tool admission, not PR0TA auth/schema exposure.

### Personal Access Tokens (REST and Local Stdio Fallback)

Remote MCP clients use PR0TA OAuth through the host connector. A PAT is required for reliable REST fallback workflows and local stdio MCP workflows. PATs are long-lived tokens that don't require email/password. Always ensure you have a PAT before starting REST/local stdio work.

If the user does not have a PAT, guide them to `app.pr0ta.com/settings` → **General** → **API Keys** → **Generate New Key**. The token starts with `pat_` and is shown only once.

**Using a PAT for REST/local stdio fallback:**
```bash
export PR0TA_PAT="pat_xxxxxxxxxxxxx"
curl -H "Authorization: Bearer $PR0TA_PAT" https://app.pr0ta.com/api/v2/projects
```

**Managing PATs (requires JWT session -- PATs cannot manage PATs):**

Create: `POST /api/auth/personal-access-tokens`
```json
{
  "name": "Skill Runner",
  "expires_in_days": 180
}
```
Response includes the full `token` (only shown once) and a `token_record` with `id`, `name`, `token_prefix`, `created_at`, `expires_at`.

List: `GET /api/auth/personal-access-tokens`
Revoke: `DELETE /api/auth/personal-access-tokens/{token_id}`

### JWT (Fragile Fallback — Avoid)

JWT extraction from the browser is a fragile fallback. **Always prefer a PAT.** Only use JWT if the user explicitly cannot create a PAT.

```bash
# Get bearer token (fragile — expires, requires email/password)
TOKEN=$(curl -s -X POST https://app.pr0ta.com/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"password"}' | jq -r '.access_token')

# Use token in subsequent requests
curl -H "Authorization: Bearer $TOKEN" https://app.pr0ta.com/api/v2/projects/PROJECT_ID/assets
```

**Important:** Project asset `/download` and `/thumbnail` require a PAT/JWT bearer token or a scoped `asset_token` delivery URL. Model discovery (`GET /api/v2/models`) is public; other project endpoints require authenticated project access.

### Rate Limits (Per-Minute, Per-Authenticated-User)

PR0TA applies a global per-minute request limit at the subscription-tier level. There is no dedicated generate-only concurrency limit published on the unified route itself; this same budget covers generation, polling, asset reads, etc.

| Tier | Requests / minute |
|---|---|
| `FREE` | 50 |
| `CREATOR` | 100 |
| `PRO` | 200 |
| `ENTERPRISE` | 500 |

**Operational rule:** 3–5 parallel generations with 2s polling is comfortably inside any tier's budget. Keep per-request polling intervals at ≥2s and avoid tight event-listener loops that hammer `/events`. If you hit a 429, back off — the platform does not certify a specific concurrency guarantee beyond the tier budget above.

---

## API Base URL

Both `app.pr0ta.com` and `api.pr0ta.com` accept API requests (the app domain proxies to the API domain). **Use `app.pr0ta.com` as the canonical base URL** — it's what the platform documentation uses and it works for both browser and API access. All examples in this skill use `app.pr0ta.com`.

Use `BASE_URL="https://app.pr0ta.com"`. `https://api.pr0ta.com` also works through proxying, but is not canonical.

---

## Minimal Python Client (REST Fallback)

Prefer MCP for agent work. The complete Python REST fallback client with all 5 core functions (`upload_images`, `submit_generation`, `poll_task`, `download_asset`, `list_assets`) plus a fan-out example is at **`reference/python-client.py`**. Copy it into your project as `pr0ta_client.py` and run it when you need standalone scripting.

It bakes in the Cloudflare-safe download path (`curl` via subprocess — `urllib` is 403'd by Cloudflare), the PAT bearer pattern, the structured validation-error contract for unified v2, async provider error surfacing (`error_detail`), and paginated asset listing. Every gotcha in the skill pack that costs debug time is handled on the first copy-paste.

```bash
pip install requests
export PR0TA_PAT="pat_xxxxxxxxxxxxx"
export PR0TA_PROJECT_ID="your-project-uuid"
python pr0ta_client.py
```

Rate limits by tier: FREE 50/min, CREATOR 100/min, PRO 200/min, ENTERPRISE 500/min.

---

## Project, Model, and Resource Management — Reference

For the full endpoint catalogue covering **project CRUD** (list, create, rename, set active, delete), **complete searchable model/tool discovery** (`GET /api/v2/models` with `generator`/`image_kind`/`search` filters, `GET /api/crew/model_defaults`, `GET /api/crew/model_pricing`, invocation metadata, capability flags, pricing), and **reusable consistency resources** (Elements, Characters, element bundles, character profiles, create/list/update/delete), **Read `reference/projects-models-resources.md`** (sibling file in this skill directory).

Essential facts for any call:

- **Project endpoints require auth** (PAT bearer or JWT); project asset `/download` and `/thumbnail` also accept scoped `asset_token` delivery URLs. Model discovery (`GET /api/v2/models`) is public.
- **Project ID is required in the path** for every project-scoped endpoint. Use `GET /api/v2/projects` to list, then pick the one you need.
- **Default image model: Nano Banana 2** (`nano_banana_2`) — fast and cost-effective. Escalate to **GPT Image 2** (`openai/gpt-image-2` / `openai/gpt-image-2/edit`) for challenging prompt adherence or character consistency edits. Use `GET /api/crew/model_defaults?model_id={model_id}` for authoritative parameter schemas.
- **Elements** are reusable image bundles for Kling. **Characters** are reusable MuAPI identities for Seedance. Do not mix.
- **Character consistency bundles** — before multi-shot character generation, read `GET /characters/{id}/consistency` or `GET /characters/consistency?name=...` to get all approved references, Kling Elements, Seedance tokens, and provider-ready payloads in one call. Tag approved portraits/sheets with `reference_type: "character_reference"` via `PATCH /annotations`. See `reference/projects-models-resources.md` → "Character Consistency Bundles" and `pr0ta-consistency` → "Character Consistency Bundles".
- **Set-active-project** is a separate endpoint (`POST /api/v2/projects/{id}/select`) and must be called before generations that rely on the active-project context.

For actual request/response shapes and worked examples, Read the reference file.

## Unified Generation API and MCP Generation Tools — Reference

For World Labs Marble worlds, use `world_generation_submit` rather than the unified image/video generator. Read `pr0ta-prompting` → `reference/marble-world-generation.md` for source-backed modality selection and prompting, and `reference/mcp-server.md` for the exact tool schema. Set Designer submissions should include `set_environment_id` so completed worlds attach to the canonical set variant.

The primary agent path is the MCP `generation_submit` tool. The REST fallback is `POST /api/v2/projects/{project_id}/generate`. Both dispatch to the image, video, motion, 3D, Lipsync, audio, or music stack and return a task ID.

**MCP `generation_submit` input:**

```json
{
  "project_id": "project-uuid-or-slug",
  "request": {
    "generator": "image",
    "mode": "txt_to_img",
    "model": "nano_banana_2",
    "prompt": "Dark navy infographic showing global market growth, gold accent text, clean vector style.",
    "width": 1920,
    "height": 1080,
    "format": "jpeg"
  }
}
```

Poll the returned task with `tasks_get`.

**Essential facts:**
- **`generator` is required on every request.** Sending only `model` and `mode` fails validation. Valid generators: `image`, `video`, `motion`, `3d`, `lipsync`, `audio`, `music`.
- **Supported generator/mode pairs:** `image` (`txt_to_img`, `img_to_img`, `ref_to_img`, `edit_img`), `video` (`ref_to_vid`, `txt_to_vid`, `extend_video`/`video_extend`), `motion` (`text_to_motion`, `video_to_motion`), `3d` (`image_to_3d`, `animate_3d`), `lipsync` (`lipsync`, `video_audio_to_video`), `audio` (`txt_to_speech`, `text_to_sound`), `music` (`txt_to_music`). Unsupported combinations return `400`.
- **Hunyuan text motion:** use `generator=motion`, `mode=text_to_motion`, `model=fal-ai/hunyuan-motion`, and a short body-geometry prompt. Optional controls are `duration` (0.5-12), `guidance_scale` (1-10), `seed`, and `output_format` (`fbx` or `dict`). Read `pr0ta-prompting` → "Motion Prompting Is an Exception" before writing the prompt.
- **Image-to-3D is first-class:** use `generator=3d`, `mode=image_to_3d`, a cataloged model such as `fal-ai/sam-3/3d-body`, and `image_asset_id` or `image_url`. Meshy v6 and v7 additionally accept `enable_rigging`, `rigging_height_meters`, `enable_animation`, and one `animation_action_id`; those requested outputs are required before the task can succeed. Meshy v7 multi-image accepts one to four references through `parameters.image_urls`; project assets in `reference_image_asset_ids` are resolved into that array automatically.
- **Current Fal partner namespaces are canonical:** use `meshy/v7/image-to-3d` or `meshy/v7/multi-image-to-3d`, `lightricks/ltx-2.5/{text-to-video,image-to-video,audio-to-video}/{pro,fast}`, and `xai/grok-imagine-image/v2.0/{text-to-image,edit}` exactly as discovered. Do not prepend `fal-ai/` to these IDs.
- **LTX 2.5 audio-to-video:** use `generator=lipsync`, `mode=video_audio_to_video`, and `audio_url`/`audio_asset_id`. A prompt is required when no image reference is supplied; with an image, the prompt is optional motion direction. Source audio must be 2–20 seconds.
- **Grok Imagine Image 2.0:** T2I uses `generator=image`, `mode=txt_to_img`; edit uses `mode=img_to_img`, `ref_to_img`, or `edit_img` and accepts up to three `image_urls`. These xAI-namespaced v2 routes are Fal-hosted and use Fal task/webhook handling.
- **Rig & Animate is first-class:** use `generator=3d`, `mode=animate_3d`, `model=fal-ai/meshy/rigging/multi-animation`, a humanoid GLB via `model_asset_id` or `model_url`, and 1-10 unique `animation_action_ids` from 0-696.
- **Imported motion retargeting accepts Hunyuan SMPL-H:** `pr0ta/humanoid-retarget-v1` maps the SMPL-H body profile to compatible target humanoid rigs automatically. An incompatible-target response names the selected target asset so it is not mistaken for a motion-source failure.
- **Mode/model compatibility is validated.** Kling models are reference-only (`ref_to_vid`). Seedance and LTX support `txt_to_vid`. Crossing these returns `400`.
- **Asset IDs resolve server-side** to internal URLs. All referenced assets must belong to the same project. You can also pass URLs directly (`start_image_url`, `reference_image_urls[]`, etc.).
- **Stored consistency resources** resolve server-side too: `element_ids[]` → Kling element references, `character_ids[]` → Seedance/MuAPI character references. Do not mix — Elements are Kling, Characters are Seedance.
- **Prompt token rules are provider-specific:** Kling uses `@Image1` for Start Image and `@Element1`/`@Element2` for Elements; its End Image is structural, so do not invent `@Image2`. MuAPI Seedance 2.0 uses lowercase positional `@image1`, `@video1`, and `@audio1` tokens matching its submitted arrays.
- **Seedance storyboard sheets:** for advanced Omni chunks, list chunks with `storyboard_chunks_list`, generate sheet variations with `storyboard_reference_sheet_generate`, poll with `tasks_get`, then list/select sheets with `storyboard_reference_sheets_list`. Use the approved sheet as a normal image reference in the later `generation_submit` video request.
- **Audio output and audio controls are separate contracts.** Send `sound` only when live defaults expose it. Seedance 2.5 and Hailuo H3 always return audio-bearing video despite having no standard `sound` field. FLUX 3 and LTX 2.5 generation default to synchronized audio and expose schema-level `generate_audio`.
- **Video extension is first-class:** use `generator=video`, `mode=extend_video`, a source `video_url` or `video_asset_id`, a prompt, and an extension-capable model such as `muapi/seedance-2.5-video-extend`, `fal-ai/pixverse/v6/extend`, `fal-ai/veo3.1/extend-video`, `fal-ai/vidu/q2/video-extension/pro`, `fal-ai/magi/extend-video`, or `kling/v3/video-extend`. Seedance 2.5 Extend uses model-ID resolution variants and exposes `generate_audio` plus optional `last_image_url`.
- **Submission returns a task**, never a finished asset. Extract `task_id` and poll — do not assume 200 on submit means the job succeeds. Async provider errors surface only at terminal polling. The initial task may have `provider: null` / `model_id: null`; this is normal, not a failure.

**Full contract — request/response shapes for every generator, model-capability matrix, image resolution constraints, multi-prompt and camera-control fields, asset-ID resolution rules, submission response fields:** Read `reference/unified-generation.md`.

## Batch Generation and Event Queue — Reference

For the full endpoint specs covering **batch generation** (`generation_batch_submit` or REST `POST /api/v2/projects/{id}/generate/batch`, n-way fan-out, batch status) and the **generation event queue** (`GET /events?generator=<type>`, server-sent-event semantics, completion signaling, known gaps), **Read `reference/batch-and-events.md`** (sibling file in this skill directory).

Essential facts:

- **Events are an acceleration path, not the primary completion signal.** Image events in particular are best-effort and sometimes empty even after completion. Always use task polling (below) as the authoritative completion signal.
- **`POST /api/v2/projects/{id}/generate/batch` is the first-class fan-out mechanism.** One request can carry multiple generation payloads (up to **10** items per batch). Validation happens up front; submissions are processed item-by-item; partial-success reporting can occur if an early item is accepted and a later one fails. Oversized batches return `413`.
- **Batch vs. loop:** Use the batch route when you have N distinct payloads you want to queue in a single round-trip. Use independent `/generate` calls in a loop when you want finer-grained retry/cancel logic or when submissions are driven by incremental decisions.
- **Rate limits apply at the global per-minute tier level** (see "Authentication" section). There is no dedicated generate-only concurrency limit; 3–5 parallel generations is well within normal limits for any authenticated tier, but "well within limits" is not a certified concurrency guarantee.
- **Cost is model-dependent.** Image fan-out across Nano Banana 2 / GPT Image 2 / Ideogram is cheap enough to treat as a first-class editorial tool. Video fan-out across Kling or Seedance can add up quickly — use it deliberately, not reflexively.

For the full request/response shapes, Read the reference file.

## Task Polling — Reference

**Task polling is the primary completion signal.** Always poll a submitted task to terminal state — a 200 from `POST /generate` only means queued, not succeeded. Async provider errors (insufficient credits, model unavailable, provider timeout) surface only at terminal status.

**MCP tools:**
```
tasks_get
tasks_cancel
```

**REST endpoints** (project-scoped preferred):
```
GET  /api/v2/projects/{project_id}/tasks/{task_id}         ← preferred
POST /api/v2/projects/{project_id}/tasks/{task_id}/cancel  ← preferred
```

**Terminal states:** `succeeded`, `failed`, `canceled`/`cancelled` (both spellings normalized server-side).

**`result` is the canonical completion contract — read from `result`, not `result_refs`.** Generation tasks use `{ type, asset_id, asset_ids, download_url, urls, variant_count }`. Normal durable `agent_chat_send` tasks use `{ type: "agent_chat", response, role, topic, request_id }`. Typed `prompt_only` and Production Queue Cinematographer tasks normally return `{ type: "generation_package", final_prompt, model_id, modality, character_count, reference_plan, character_ids, validation, technical_params, lineage, cinematographer_finalized }` with current-task output only. Designed-world or reference-design prompt orchestration may instead succeed with `{ type: "prompt_assessment", prompt_assessment: { status: "needs_clarification" | "has_problems", issues, clarification_questions, adjustments, clarification_owner }, validation, lineage, cinematographer_finalized: false }` for explicit review; the compiler does not recursively call departments for clarification. Branch on `result.type`; never generate from a `prompt_assessment` or assume `final_prompt` exists merely because the task status is `succeeded`. `result_refs` is legacy compatibility only.

**Stall detection and cross-provider pivot** (reliability contract step, covered fully in `pr0ta-video`):
1. Same `progress` for >3 minutes → cancel via `POST /tasks/{task_id}/cancel`.
2. Resubmit identical payload (queue-reset often fixes it).
3. If the retry also stalls, pivot to the other video provider — Seedance → Kling V3 I2V, or Kling → Seedance Omni. Do not burn a third attempt on the same backend.
4. If both providers stall, surface status before degrading to a Ken Burns push on the still.

**Error-reason taxonomy** — use `error_reason` to decide retry vs fail-fast:
- `provider_timeout` → retry (transient).
- `provider_error` + `error_detail.code: 402` → do **not** retry; fix provider account credits first.
- `invalid_parameters` → do not retry; fix the payload.

**Full contract — route table, in-progress/succeeded/failed response shapes with full field lists, cancellation semantics, `created_at`/`submitted_at`/`error`/`error_reason`/`error_detail` field definitions, and the canonical `result` envelope spec:** Read `reference/task-polling.md`.

## Asset Management and Batch Workflow — Reference

For the full endpoint specs covering **asset management** (`assets_list`, `assets_upload_start`, `assets_upload_finalize`, `assets_get_download_link`, `assets_download`; REST listing with `offset`/`limit` pagination, filtering by kind/task_id/tag, asset metadata including `storage_uri`, deletion, tagging) and the **canonical batch workflow pattern** (submit → poll → collect → download → ledger), **Read `reference/asset-management.md`** (sibling file in this skill directory).

**Asset listing pagination:** `GET /api/v2/projects/{id}/assets` supports `offset`/`limit` pagination. Response includes `total` (total matching assets) and `next_offset` (for the next page, or `null` if no more). Default limit applies server-side; always check `next_offset` to paginate through large asset sets.

Essential facts:

- **Canonical pagination is `offset`/`next_offset`** — iterate until `next_offset` is `null`. The minimal Python client's `list_assets()` does this correctly. Do not hand-roll with `cursor`/`nextCursor` (that's the legacy shape for a non-project-scoped route).
- **Asset downloads must go through `curl` via subprocess** — see `pr0ta-downloading` for the Cloudflare bypass rationale. `urllib` will 403.
- **Assets now expose `generation_context`.** `GET /api/v2/projects/{project_id}/assets/{asset_id}/metadata` surfaces a `generation_context` block with `prompt`, `model`, `negative_prompt`, `seed`, `task_id`, `submitted_at`, `completed_at`, `status` when recoverable. This means assets are no longer opaque — you can walk backwards from an asset to the job that produced it via the API.
- **Provenance is a single local ledger (`assets.json`) plus the API-side `generation_context` fallback.** `assets.json` is the production-scoped ledger defined in the `pr0ta` hub. `generation_context` is the retrospective API lookup for any asset. There is no separate `results.json` file — it was dropped to avoid duplication.

For the full request/response shapes and the end-to-end batch workflow walk-through, Read the reference file.

## Asset Tagging, Readability Filters, and Timeline Analysis — Reference

Assets are not just media files — they carry editorial intent. Tagging, annotating, and curating assets is how agents and users communicate which assets are hero takes, which are references (and for what), which are approved, and which should never be used. Without active curation, a project with dozens of assets becomes opaque to the next agent or collaborator who picks it up.

**For the full endpoint contracts** covering asset readability filters (`?favorite=true`, `?tag=`, `?reference_type=`), annotation mutation (`PATCH /annotations`), timeline mark labels/descriptions, timeline analysis (gaps, overlaps, reused media, track coverage), and per-clip reuse flags, **Read `reference/asset-tags-and-analysis.md`**.

Essential facts:

- **Filter by favorites, tags, or reference type** — `GET /api/assets/{project_name}?favorite=true`, `?tag=hero&tag=approved` (AND-joined), `?reference_type=character_reference`. Use these instead of fetching the full library and filtering client-side.
- **Annotate assets with `PATCH /api/assets/{project_name}/annotations`** — write `tags`, `notes`, `reference_type`, `character_name`/`set_name`/`prop_name`/`look_name`, `scene_number`/`shot_number`/`take_number`. Use `tags` for general readability (`approved`, `hero`, `do_not_use`), `reference_type` for durable semantic classification.
- **MCP annotation tools are available** — use `assets_annotations_update` for one asset or `assets_annotations_batch_update` for up to 100. For the Style page, use `style_world_create`, `style_world_update`, `style_world_assign_scenes`, or `style_world_delete` for focused world changes; prefer `style_package_save` when `styleReferences` metadata and asset annotations must be persisted together.
- **Timeline marks now support `label` and `description`** — use these fields (not the legacy `name`/`note` aliases) for editorial annotations on the timeline.
- **Timeline diagnostics (`GET /timeline/debug-report`)** — preferred agent preflight before render/export. It bundles track coverage, primary visual gaps, source shortfalls, retime state, audio asset presence, keyframe counts, and render-risk warnings. Use `GET /timeline/analysis` when you only need the raw gaps/overlaps/reuse/shortfall analysis.
- **Per-clip `isReusedMedia` and `sourceShortfall` flags** — available on the standard clip listing for lightweight reuse and shortfall checks without full timeline analysis.
- **Source shortfalls** — when a source clip is shorter than the requested program range, PR0TA inserts only the available source and leaves a real gap (no freeze-padding). For I2V card edits, compare source duration vs beat duration before placement; use `/timeline/edits` with `fitToFill: true`, generate/extend a longer clip, or warn about transparent/checkerboard tails. Analysis and debug reports include frame-safe timing (`renderedProgramFrames`, `renderedProgramDuration`) and render-risk warnings. See `reference/source-shortfalls-and-fit-to-fill.md` for the full contract.

## Project Image Upload — Reference

Direct-multipart upload of local still images into a project, without the prepare/proxy/finalize workflow. Preferred path for ingesting existing photos, screenshots, key frames, or real-world references before generation.

```
POST /api/v2/projects/{project_id}/assets/upload
Content-Type: multipart/form-data
```

**Critical field-name gotcha:** the multipart field is `files` (plural), not `file`. Sending `file` returns `422`. Accepts one or more image files per request; non-image files are rejected with `400`.

**Response:** `assets[]` array using the standard `AssetRead` shape. The `id` on each asset is what you pass as `start_image_asset_id` / `reference_image_asset_ids[]` / etc. in follow-up `/generate` calls.

**Scope:** images only. For audio/video/document direct upload, use the legacy prepare/proxy/finalize flow (`/assets/uploads/prepare` → `/proxy` → `/finalize`).

**Full contract — request fields table, copy-paste curl examples (single and multi-file), response shape, usage patterns (reference images, Element/Character source material, image-editing input, batch upload), error cases:** Read `reference/image-upload.md`.

## Post-Production Timeline API — Reference

The **post-production timeline** is the primary editing surface for both AI agents and human collaborators — it stores clip state, Ken Burns presets, audio mix, and supports incremental edits. Base prefix: `/api/post-production/{project_id}`.

**For workflow guidance** (when to add clips, Ken Burns presets, preview/render loop, snapshot handoff), see `pr0ta-timeline`. **For the full API shapes** (timeline state, track creation, clip CRUD, audio mix, audio preview/analysis, snapshots, data model, and the `POST /timeline/clips` never-upserts gotcha), **Read `reference/timeline-api.md`**. **For the canonical backend-facing endpoint reference** (all post-production routes, contracts, and limits), **Read `reference/post-production-api.md`**. **For source shortfalls and fit-to-fill** (default gap behavior, `fitToFill`, four-point edits, speed semantics), **Read `reference/source-shortfalls-and-fit-to-fill.md`**.

Essential facts:
- **Concurrent audio on separate tracks.** Overlapping audio clips on the same track are invalid — the renderer rejects them. Create separate tracks (`dialogue`, `music`, `sfx`) via `POST /timeline/tracks` before adding clips.
- **Track creation** — `POST /timeline/tracks` creates individual tracks without rewriting the full `tracks[]` array. Preferred over `PATCH /timeline` for adding tracks.
- **Track targeting** — tracks support three selector forms: raw ID (`dialogue`), NLE alias (`A1`), or unique label (`Dialogue`). `PATCH /timeline/tracks/{id_or_alias}` renames, locks, or repositions tracks. Read `GET /timeline/tracks` first and use raw IDs in persisted scripts.
- **`duckedGain` is the canonical ducking field** (fraction of nominal volume: `1.0` = no duck, `0.0` = mute). `threshold` is a deprecated alias.
- **Audio level keyframes** — `volumeKeyframes` on tracks (absolute time) and clips (clip-relative time) for fine-grained mix automation. The renderer multiplies both. Supports `db`/`decibels` input, and negative gain-like values are treated as dB attenuation. `/audio/analyze` exposes the same frame/gain envelope that render uses; verify music with `/preview/audio`, `/audio/meter`, or a short render around a narration gap. See `reference/timeline-api.md` → "Audio Level Keyframes".
- **Audio analysis** — `GET /audio/analyze` returns render-envelope prediction, ducking impact, mix balance, and per-segment `render_gain_envelope` instantly (no media render).
- **Audio metering** — `GET /audio/meter` returns actual LUFS/LRA/true-peak via MLT + ffmpeg ebur128. Use for loudness spec compliance.
- **Audio-only preview** — `GET /preview/audio` renders a `.wav` without picture cost. Supports `tracks` param to solo specific tracks.
- **Preview defaults to full sequence resolution.** Send `quality=low` for lightweight previews; omit for pixel-accurate.
- **Render preview** — `POST /render` is the preview-task route (queues `timeline_render`). Loads saved timeline automatically. Control-only body (empty `{}` or `from`/`to`/`resolution`) is valid. Zero-clip timelines return `400`.
- **Final export** — `POST /export` is the final-export route for master delivery. Use `/render` for iteration, `/export` when the cut is locked.
- **Clip metadata** — timeline clips now expose `sourceMedia` (width, height, aspectRatio, duration, fitsSequence) and `generation_context` (prompt, model) for aspect-fit auditing and provenance checks.
- **Source shortfalls** — when source media is shorter than the requested edit duration, PR0TA inserts only the available source and leaves a real gap. No freeze-padding. Use `fitToFill: true` to retime explicitly, then verify the frame-safe fields and preview-render warnings. See `reference/source-shortfalls-and-fit-to-fill.md`.
- **Fresh sequence rebuilds** — use `POST /sequences` to allocate a named empty sequence, then `POST /timeline?sequence_id={id}` with the complete desired tracks/audio mix/metadata payload. To preserve settings from another sequence, read it first and copy only the intended fields into the new full payload. Render/export/review scripts must pass and record the intended `sequence_id`. See `reference/timeline-api.md` → "Create Fresh Sequence".
- **Clip at review timestamp** — use `GET /timeline/clips?sequence_id={id}` and select entries whose `start <= time < end`; each entry includes exclusive `end` and `trackMuted`. Prefer an unmuted visual track, and if none overlaps identify the nearest clip explicitly rather than calling it active.
- **Image fit and semantic reuse** — image clips accept `fitMode`/`background` for contain/cover/fill poster handling, and analysis reports `semanticReuse[]` for repeated `sourceGroup` / `usageFamily` families even when asset IDs differ.

## Editorial Primitives — Reference

The post-production timeline now exposes a first-class editorial primitive surface: **asset marks**, **program marks**, **3-point edits**, **trim operations**, and **clip link groups**. These are real shipped backend contracts.

**For workflow guidance** (when to use marks, editorial judgment), see `pr0ta-timeline` and `pr0ta-editorial`. **For the full endpoint contracts** (all CRUD endpoints, request/response shapes, mark anchoring, edit modes, trim modes, linked behavior, lock enforcement), **Read `reference/editorial-primitives.md`**.

Essential facts:
- **Asset marks** — source-media in/out points stored on the asset (`POST /api/v2/projects/{id}/assets/{asset_id}/marks`). Referenced in 3-point edits via `@mark:<name>` syntax.
- **Program marks** — story anchors on the timeline. Can be absolute (time-based) or transcript-word anchored. Anchored marks follow timeline changes automatically.
- **`clipId` is the preferred disambiguation field** for transcript-word anchored marks when the same dialogue asset appears multiple times.
- **3-point edits** — `POST /timeline/edits` (`insert`, `overwrite`). Specify three of four points; backend computes the fourth. Source/program points can reference marks.
- **Trim operations** — `POST /timeline/edits/{clip_id}/trim` (`ripple`, `roll`, `slip`, `slide`). All four modes support `linked: true` for linked companion clips. Only `ripple` supports `affectedTracks`.
- **Clip link groups** — persisted cross-track relationships (`POST /timeline/links`). `locked: true` is enforced — all mutating operations are rejected until unlocked.
- **Preview before committing.** `/edits/preview` and `/trim/preview` return the diff without persisting. Always preview when reasoning from marks.

## Client Review Room API — Reference

PR0TA exposes a client review workflow through MCP/agent tools: **`enable_studio_mode`**, **`review_submit_assets`** (preferred MCP alias), **`submit_assets_for_review`** (legacy alias), and **`get_review_annotations`**. Enable Studio mode on a project (required before first review), submit one or more project assets to a public review room, share the review URL with a client, and retrieve timestamped comments, visual annotations (pin, region, drawing), and approval/change-request decisions programmatically.

**For the full tool contracts** (arguments, response shapes, webhook payload, integration pattern, annotation types, resolution filtering), **Read `reference/review-room-api.md`**.

Essential facts:

- **`enable_studio_mode`** must be called before first review-room creation. Enables Studio mode on the project. REST equivalent: `PATCH /api/v2/projects/{project_id}/studio`.
- **`review_submit_assets`** creates a public review room and returns a `review_url` the reviewer opens in a browser — no PR0TA account required. Response includes `submissions[]` (per-asset status) and `review_round{}` (round metadata with share links). `submit_assets_for_review` remains a legacy alias.
- **`get_review_annotations`** retrieves all feedback: annotations with `annotation_type` (pin, region, drawing), time codes (`start_time_seconds`), normalized frame coordinates (`geometry`), and review events (`comment`, `approved`, `approved_with_notes`, `changes_requested`). Every event includes its resolved `asset_id`, and `review_submissions` supplies the durable submission-to-asset map for historical decisions.
- **Fetch notes from a public review link** — parse the share token from the review URL and call `GET /api/public/workspace/review-rounds/{share_token}/annotations`. Use this read route for note ingestion; authenticated write-oriented annotation routes require body/geometry fields and are not the right first call.
- **Verify review asset identity** — after creating a review link, confirm the submitted/review asset ID is the export asset you intended to show.
- **Completion webhook** — optional `webhook_url` on submission triggers a `review_round_completed` POST after all submitted assets have decisions. Treat as a wake-up signal, then call `get_review_annotations` for the full payload.
- **Role access** — available to `editor`, `director`, `producer`, `script_supervisor` roles.
- **Integration loop:** submit → share URL → wait for webhook or poll → pull feedback → apply in timeline using editorial primitives (see `pr0ta-editorial`, `reference/editorial-primitives.md`).

## MCP Server & Agent Tools — Reference

PR0TA provides an MCP server that exposes project-scoped tools to external agents (Codex, Claude Code, Cursor, ChatGPT, Claude connectors). The same tool registry also powers internal Gemini-backed agents (Editor, Director, Storyboarder, etc.).

**For the full MCP server setup** (stdio/SSE/HTTP transports, Claude Code and Cursor configuration, remote OAuth connectors, available tools table, role-tool access matrix, internal agent integration, adding new tools, troubleshooting), **Read `reference/mcp-server.md`**.

Essential facts:

- **Packaged setup:** Codex, Claude, and universal distributions include host-specific connection instructions.
- **Remote connectors:** `https://app.pr0ta.com/api/mcp/mcp` with PR0TA OAuth. It works with tool-capable LLM hosts that support remote MCP.
- **Local setup:** `python mcp_server.py` (stdio transport). Configure in `.claude/mcp.json` (Claude Code) or `.cursor/mcp.json` (Cursor) only for repo-local development.
- **Auth:** Local clients use `PR0TA_MCP_ACCESS_TOKEN` env var or per-call `access_token`. Remote connectors use OAuth bearer.
- **All project-scoped MCP tools require `project_id`.** `create_project` and `list_projects` are the two project-independent tools; use them to establish the project before project-scoped work.
- **Screenplay reads are durable and paginated.** `get_screenplay_text` prefers the active editor revision, accepts `scene_number`, `offset`, and `limit`, and returns `next_offset`. Workspace context is optional and same-user scoped; missing snapshots do not block saved screenplay text.
- **Prep/Production discovery:** call `prep_production_capabilities` for the current page-to-tool map.
- **Available Prep tools:** complete Producer, Director, Casting, and Script Supervisor read generation; Locations/Looks/Props read generation and partitioned persistence; Style and Choreography metadata/assets; department chat; Casting portraits/character sheets through unified generation; cast voice design/sample/clone/speech-to-speech; Seedance Character/Kling Element CRUD; and full ProtaFilm|memory overview, source ingestion, claims, conflicts, decisions, and notes. Call `prep_production_capabilities` for exact names and schemas.
- **Canonical cast persistence:** `cast_list_save` writes `castingRead`, `castingIndex`, and the cast CSV as one failure-safe operation. Use `reconcile_existing=true` only to repair a divergent project; it unions membership and preserves metadata visual references while preferring non-empty CSV voice fields.
- **Asset-only Cast visibility:** a named image annotated with `reference_type: "character_reference"`, `subject` and/or `character_name`, and category `portrait` or `character_sheet` appears as an unselected member in Prep → Cast. Do not omit the explicit character identity, and do not treat visibility as portrait-selection approval.
- **Available Production tools:** human/generative performances, shotlist generation/chat/save, storyboard generation/sequences/reference sheets, and complete Production Queue list/create/update/delete/prompt/take/component/regenerate/analyze/refresh/retry operations, plus generation, task, and asset tools.
- **Other available tools:** `create_project`, `list_projects`, `get_project_metadata`, `agent_chat_orchestrate_prompt`, `generation_submit`, `generation_batch_submit`, `voices_list`, `transcription_start`, `transcription_get`, `music_analyze`, `tasks_get`, `tasks_cancel`, `assets_list`, `assets_upload_start`, `assets_upload_finalize`, `assets_get_download_link`, `assets_download`, `audio_analyze`, `audio_meter`, `post_sequence_get`, `post_sequence_save`, `post_render_start`, `post_export_start`, `narration_timeline_get`, `narration_materialize_to_post`, `storyboard_chunks_list`, `storyboard_reference_sheet_generate`, `storyboard_reference_sheets_list`, `review_submit_assets`, `models_list`, `models_get_defaults`, plus legacy project-intelligence and review tools such as `get_scene_breakdown`, `get_scene_shotlist`, `get_character_references`, `get_set_references`, `get_shot_assets`, `get_screenplay_text`, `enable_studio_mode`, `submit_assets_for_review`, and `get_review_annotations`.

---

## Narration Timeline API — Reference

The **narration timeline** is a server-side timeline object per project that acts as the single source of truth for narration-driven productions. It ties together transcript word-level timing, visual asset registry with content affinity, a cut list with transcript anchors and editorial rationale, and alignment verification — all via API. Its output is materialized directly into the post-production timeline.

**The narration timeline feeds into the post-production timeline.** Build and verify your cut list in the narration timeline, then call `POST /narration-timeline/materialize-to-post-production` to convert it into a persistent post-production sequence with Ken Burns, transitions, and audio config already set. From that point, both agent and user collaborate on the post-production timeline.

**For the full endpoint reference, data model, request/response shapes, and worked examples, Read `reference/narration-timeline-api.md`.**

Essential facts:

- **Transcription auto-populates the transcript layer.** When `POST /api/audio/transcription/start` completes, the narration timeline's transcript is automatically built with word-level timestamps, sentence boundaries, and paragraph boundaries. Manual fallback: `POST /transcript/populate`.
- **Content tags bridge narration to visuals.** `PUT /transcript/tags` labels word ranges with content identifiers (e.g. `market_size`, `franchise_model`). Assets registered with matching `affinity_tags` become queryable: `GET /assets?affinity=market_size&status=unused`.
- **Every cut records a transcript anchor and rationale.** The cut list stores which words each visual is aligned to and why — enabling automated alignment verification (`GET /verify`) and human-readable audit trails.
- **Alignment verification is the quality gate.** `GET /verify` returns per-cut drift, gap detection, overlap detection, and misalignment flags. Call before rendering; fix flagged cuts; re-verify; then export.
- **Materialize to post-production.** `POST /narration-timeline/materialize-to-post-production` converts narration cuts into post-production timeline clips with stable IDs, Ken Burns metadata, transition metadata, narration/music audio clips, and ducking intent. Response includes `timeline`, `clip_count`, and `sequence_name`. This is the only supported output path for narration-first productions.
- **Snapshots replace the version-directory pattern** for timeline state. `POST /snapshot` saves a named snapshot; `GET /snapshot/{name}/diff` compares; `POST /snapshot/{name}/restore` rolls back.
- **All timestamps are stored in final-video time.** Query endpoints accept `?coordinate_space=narration|sequence|final` for conversion.

For the narration-first assembly workflow that consumes this API, see `pr0ta-sync`.

---

## Voice V2 API — Browser, Clone, Design, STS — Reference

Voice browsing, clone, design, and STS are project-scoped PR0TA endpoints under `/api/v2/projects/{project_id}/voices/...`. Agent workflows should use MCP `voices_list` first, then REST fallback only when MCP is unavailable.

**For workflow guidance** (when to browse vs clone vs design vs STS, decision tree, limitations), see `pr0ta-audio` → "Voice V2 API". **For the full endpoint contracts** (request/response shapes for all routes, V3 compatibility contract, model-ID table), **Read `reference/voice-v2.md`**.

Essential facts:
- **Voice browser** — MCP `voices_list` or REST `GET /api/v2/projects/{project_id}/voices/browser`. Supports `provider` (`all`, `elevenlabs`, `google`/`gemini`, `minimax`, `kling`, `xai`), `search`, `page_size`, `include_live`, and `include_custom`.
- **Voice selection** — each result includes `selection`; copy those fields into `generation_submit` or REST `/generate` instead of hand-mapping provider details. Gemini/Google voices include `selection.voice_settings.voice`.
- **ElevenLabs compatibility** — do **not** derive a `supports_v3` boolean from metadata. Use try-and-fallback (attempt v3, fall back to v2 on failure).
- **Voice clone** (`POST /voices/clone`) is synchronous — returns `voice_id` directly, no task polling. Pass `sample_asset_ids[]` (project assets) or `sample_urls[]` (external).
- **Prompt voice design** is two-step: `POST /voices/design` returns ephemeral `previews[]`, then `POST /voices/design/commit` turns the chosen preview into a permanent `voice_id`.
- **Speech-to-speech** (`POST /voices/sts`) returns the output audio URL directly. Model: `eleven_multilingual_sts_v2`. Audio-to-audio only on the v2 surface.
- **Model discovery** (`GET /api/v2/models?generator=audio`) now includes voice-design and STS models alongside TTS. New mode hints: `voice_design`, `voice_to_voice`.

---

## Voice Listing and Transcription — Reference

For the full endpoint specs covering **voice browsing/selection** (`voices_list`, `GET /api/v2/projects/{id}/voices/browser`) and **transcription** (`POST /api/audio/transcription/start`, `POST /api/v2/projects/{id}/transcribe`, batch variant, asset_id/source_url/file inputs, `timestamp_granularity`, async task shape), **Read `reference/voice-and-transcription.md`** (sibling file in this skill directory).

Essential facts:

- **Scribe V2 is the default transcription provider.** Pass `model_id: "fal-ai/elevenlabs/speech-to-text/scribe-v2"` for speaker IDs, audio events, and per-word `event_type` classifications. Whisper (`fal-ai/whisper`) is still available as a fallback.
- **MCP is the default agent path.** Call `transcription_start`, poll with `tasks_get`, then call `transcription_get`. Use REST only when MCP is unavailable or for standalone upload/source-URL transcription.
- **Transcription is the primary tool for any word-level timing, sync, subtitle, or dialogue-matching work.** See `pr0ta-audio` for the provider comparison and `pr0ta-sync` for the narration-timeline workflow that consumes the output.
- **Transcription is async.** Submit, get a task_id, poll to completion.
- **Retrieve word-level data from the dedicated transcription endpoint** (see below), not from asset metadata internals.
- **Voice browsing uses PR0TA's provider-normalized browser.** Prefer MCP `voices_list`; REST fallback is `GET /api/v2/projects/{project_id}/voices/browser`. See `pr0ta-audio` for the voice browser workflow and `reference/voice-v2.md` for the full endpoint contract.

### Dedicated Transcription Retrieval (Preferred)

After transcription completes, retrieve word-level timing from the dedicated endpoint:

```
MCP: transcription_get
REST fallback:
GET /api/v2/projects/{project_id}/assets/{asset_id}/transcription
```

Response:
```json
{
  "success": true,
  "asset_id": "asset-123",
  "project_id": "project-1",
  "text": "Full transcript text",
  "segments": [...],
  "words": [...],
  "segment_count": 12,
  "word_count": 418,
  "timestamp_granularity": "word",
  "transcription_options": {...},
  "transcription_summary": {...}
}
```

Returns stored transcription text, segment list, and a flattened word list. If stored top-level transcript text is missing, `text` is synthesized from segment text on the fallback label-based path. Falls back to older label-based transcript storage where possible. This is the correct retrieval path for word-level timing.

Status semantics: `pending` (asset exists, no transcription yet) or `ready` (word-level data persisted). Use `words[]` for flat word-level timing, or `segments[].words[]` for segment-grouped timing.

This is the **only supported retrieval path** for transcription word-level timing.

### Transcription Route — Field-Name Compatibility

`POST /api/audio/transcription/start` is the **preferred route** for kicking off transcription when you want the narration timeline's transcript layer to be auto-populated on completion. It accepts **both** camelCase and snake_case field names:

```json
{"assetId": "...", "projectId": "..."}
{"asset_id": "...", "project_id": "..."}
```

Both forms work. The batch variant (`POST /api/audio/transcription/batch`) similarly accepts both `assetIds`/`asset_ids` and `projectId`/`project_id`.

For the full request/response shapes, Read the reference file.

## Music Analysis API — Reference

The **music analysis API** is the instrumental-music analogue of transcription — Scribe V2 is speech-only and doesn't detect musical beats. Use this for any instrumental music asset (score bed, underscore, stinger) driving cut timing. It's the required time-indexing pass for Path B of the mandatory time-indexing rule in `pr0ta-audio`.

Agents should call MCP `music_analyze` first and poll with `tasks_get`; the REST route is the fallback.

**For the full endpoint spec** (start analysis, get cached analysis, storage contract on `music_analysis` metadata, `editorial_anchors` consumer guidance), **Read `reference/music-analysis.md`** (sibling file in this skill directory).


## Audio Extraction and Video Transcription — Reference

PR0TA supports extracting a standalone audio asset from a project video (`POST /assets/{id}/extract-audio`), and `POST /transcribe` now accepts video assets, uploads, and source URLs in addition to audio assets. Video inputs are handled by extracting a derived audio asset first, then transcribing.

**For the full endpoint spec** (extract-audio request/response, provenance fields on derived assets, updated transcription behavior, when-to-use-each-path guidance, and failure modes), **Read `reference/voice-and-transcription.md`** → "Audio Extraction From Video Asset" (sibling file in this skill directory).

## Client Reliability Contract

For robust automation, route every generation call through a single wrapper that implements the full state machine, polling policy, asset correlation, download fallback, dead-task detection, and structured logging. **Read `reference/reliability-contract.md` for the complete specification, polling intervals/windows per generator, correlation scoring rules, acceptance tests, and a TypeScript reference implementation.**

Key rules to remember even before opening the reference:

- **Task polling is authoritative.** Events accelerate; assets correlate; only task status (or a validated asset+bytes) marks a job succeeded.
- **Always have a download fallback.** If `/assets/{id}/download` returns zero bytes, fall back to the authenticated `storage_uri` with redirect-following.
- **Detect stalls yourself.** Video tasks can freeze at 80-95%. If progress is unchanged for >3 minutes, cancel via `POST /api/tasks/{task_id}/cancel` and resubmit.
- **Handle both `canceled` and `cancelled` spellings** in terminal status checks.
- **Concurrency:** 5-7 parallel video tasks, 10-15 image, 3-5 audio/music.

For mixed image/video/audio/music batches, split event polling by `generator` where practical rather than scanning one mixed stream.

---

## Error Handling

Common responses:
- `400` -- unsupported generator/mode, invalid payload, invalid asset IDs, cross-project asset references
- `401` -- missing or invalid bearer token
- `402` -- insufficient credit balance
- `404` -- project or task not found
- `413` -- batch request exceeds maximum size (10 items)
- `500` -- incorrect model string (verify against `GET /api/v2/models`)
- `502` -- downstream provider returned no usable result

---

## Current Limitations

- The unified route is additive and does not replace older generation endpoints yet.
- `character_ids` currently resolves exactly one stored character per request.
- Some higher-level Prep entities still use their established REST persistence internally rather than new unified REST resources. MCP deliberately calls those same authenticated route/services so API users receive the app's canonical storage, credit, and durable-task behavior.
- No dedicated `prompt_contains` or `name` filter on asset listing.
- Asset metadata `duration` is `number | null`. Never parse it as a string. Invalid duration values are normalized to `null` server-side.
- **Video output dimensions are provider-dependent and not guaranteed to match your requested aspect ratio in exact pixels.** Some providers output square (e.g., 1440x1440); others output close-but-not-exact dimensions. The post-production timeline normalizes all clips to the delivery resolution automatically — you don't need to rescale locally. Check `result_refs.output_diagnostics` if present for requested vs actual dimensions.
