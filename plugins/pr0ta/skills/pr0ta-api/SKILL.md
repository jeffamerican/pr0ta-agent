---
name: pr0ta-api
description: "PR0TA MCP and REST contract reference: connecting and auth, project_id handling, model resolution with models_preferred, the unified generation request, task lifecycle, polling and cancel, completion subscriptions, errors, rate limits, development and Operator mission endpoints, and an index of route references (assets, timeline, narration, voices, review rooms). Read when a workflow skill does not give the exact contract or when debugging an API failure."
---

# PR0TA API contract

This skill is the contract: what a call must contain, what comes back, and
where each full route reference lives. Workflow skills say when to call what:
the `pr0ta` hub, `pr0ta-development`, `pr0ta-prep`, `pr0ta-operator`, and the
media skills.

MCP tools and REST routes are two doors to the same services, with the same
access checks, credits, and durable tasks. Use the MCP tool when one exists;
REST is for routes MCP does not expose, standalone scripts, and fetching file
bytes from links MCP returns. Call `prep_production_capabilities` for the
page-to-tool map; `reference/mcp-tools.md` is the complete generated tool
catalog.

## Connecting

**MCP.** Connect `https://app.pr0ta.com/api/mcp/mcp` through the host's
remote-MCP settings and complete PR0TA's browser OAuth. The installed
distribution carries host-specific setup; `reference/mcp-server.md` has the
OAuth metadata and troubleshooting. Start a fresh session if the host keeps its
old tool inventory, then run the connect canary: call `list_projects`. If it
returns the user's projects, the connection works.

**REST.** Send a bearer token to base URL `https://app.pr0ta.com`. Use a
personal access token (PAT): the user creates one at app.pr0ta.com → Settings →
General → API Keys → Generate New Key. It starts with `pat_` and is shown once.

```bash
export PR0TA_PAT="pat_..."
curl -H "Authorization: Bearer $PR0TA_PAT" https://app.pr0ta.com/api/v2/projects
```

PATs are automation credentials. They cannot reach account, admin, or billing
routes; the exceptions are `GET /api/auth/me` and
`GET /api/billing/credits/balance`. Create, list, and revoke PATs
(`/api/auth/personal-access-tokens`) from a signed-in browser session. Project asset downloads accept the bearer token or the scoped
`asset_token` URL PR0TA hands out. `GET /api/v2/models` needs no auth.

A standalone Python REST client lives in `reference/python-client.py`.


## Projects

Every project-scoped tool and route takes `project_id` (UUID or slug). Pass it
explicitly on every call; there is no active-project step, and generation never
depends on one. Read project state with `project_metadata_get`.

Find or make the project with `list_projects` or `create_project` (REST `GET`
and `POST /api/v2/projects`); these and `get_project_metadata` and
`get_project_development_context` are MCP-only project tools.

Project CRUD and consistency resources (Kling Elements, Seedance Characters,
consistency bundles): `reference/projects-models-resources.md`.

## Choosing a model

The platform owns model choice. The admin pins models per modality, and each
user may set their own in Settings → Tools. Resolve before every generation:

1. Call `models_preferred(modality=...)` (REST
   `GET /api/v2/models/preferred?modality=...`) and pass
   `modalities[<key>].model_id` as the request's `model`.

   ```json
   {
     "resolution_order": ["user_default", "admin_pin"],
     "modalities": {
       "image_model": {
         "modality": "image_model",
         "model_id": "<resolved id or null>",
         "source": "user_default | admin_pin",
         "pinned": ["<admin pins along this modality's fallback chain>"],
         "fallback_modalities": [],
         "display_name": "...", "generator": "image",
         "supported_modes": ["txt_to_img"], "generation_submit_supported": true
       }
     }
   }
   ```

   Omit `modality` to list every modality that resolves. An unknown key returns
   `400` with `known_modalities`. Over REST, the caller's own Settings → Tools
   choices apply only when the request is authenticated.
2. When `model_id` is null, nothing is set or pinned. Call
   `models_list(modality=...)`: it returns that modality's curated models,
   pinned ones first, each row marked `pinned` and `pin_rank` (modality → rank,
   0 is the top pin). Choose one and tell the user which and why.
3. Call `models_get_defaults(model_id)` (REST
   `GET /api/crew/model_defaults?model_id={model_id}`) for the parameter schema,
   `supported_modes`, and, for models unified generation accepts,
   `request_defaults` (`generator`, `mode`, `model`) to start the request from.
   Follow `supported_modes`: several image-to-video routes accept only
   `ref_to_vid`.

Modality keys: `image_model` (text-to-image), `image_edit_model`,
`elements_to_image_model`, `image_multi_edit_model`, `reference_to_video_model`,
`video_model` (text-to-video), `video_edit_model` (image-to-video),
`video_extend_model`, `video_to_video_model`, `lipsync_model`,
`motion_transfer_model`, `dialogue_video_model`, `dialogue_model` (TTS),
`voice_design_model`, `voice_to_voice_model`, `music_model`, `sfx_model`,
`audio_to_text_model`, `image_upscale_model`, `video_upscale_model`.

Without `modality`, `models_list` searches the whole catalog (`generator`,
`image_kind`, `search`, `curated_only`; paged with `offset`, `limit`, `total`,
`has_more`); REST `GET /api/v2/models`. Only rows with
`generation_submit_supported: true` go through unified generation; others use a
dedicated workflow. Pricing: `GET /api/crew/model_pricing?model_id={model_id}`.

## Unified generation

MCP `generation_submit` takes `{project_id, request}`; REST
`POST /api/v2/projects/{project_id}/generate` takes the request as its body.
Both return a task, never finished media.

```json
{
  "project_id": "project-uuid-or-slug",
  "request": {
    "generator": "image",
    "mode": "txt_to_img",
    "model": "<model_id from models_preferred>",
    "prompt": "Rain-slick neon alley at night, low angle, wet reflections.",
    "aspect_ratio": "16:9",
    "idempotency_key": "scene-12-keyframe-v1"
  }
}
```

| `generator` | Modes |
| --- | --- |
| `image` | `txt_to_img`, `img_to_img`, `ref_to_img`, `edit_img` |
| `video` | `ref_to_vid`, `txt_to_vid`, `extend_video` (alias `video_extend`), `video_to_video` |
| `motion` | `text_to_motion`, `video_to_motion` |
| `3d` | `image_to_3d`, `animate_3d` |
| `lipsync` | `lipsync`, `video_audio_to_video` |
| `audio` | `txt_to_speech`, `text_to_sound` |
| `music` | `txt_to_music` |

- `generator` is required; unsupported generator/mode pairs return `400`.
  Always name `model` (resolved above) and use a mode from its
  `supported_modes`. An image edit keeps its source through `image_asset_id`,
  `reference_image_asset_ids`, or their URL fields; do not "fix" an edit error
  by switching to text-to-image.
- Asset IDs (`image_asset_id`, `start_image_asset_id`,
  `reference_image_asset_ids[]`, `video_asset_id`, `audio_asset_id`, ...)
  resolve server-side; every referenced asset must belong to the same project.
  URL fields are accepted instead.
- Stored consistency resources resolve server-side: `element_ids[]` are Kling
  Elements, `character_ids[]` are Seedance/MuAPI Characters. Do not mix them.
- Prompt tokens are provider-specific. Kling uses `@Image1` for the start image
  and `@Element1`, `@Element2` for Elements; its end image is structural, so do
  not write `@Image2`.
  MuAPI Seedance 2.0 uses lowercase positional `@image1`, `@video1`, and `@audio1` tokens matching its submitted arrays.
- Audio fields are per model: send `sound` or `generate_audio` only when
  `models_get_defaults` exposes it. Some video models always return audio.
- Text-to-motion (`generator=motion`, `mode=text_to_motion`; `fal-ai/hunyuan-motion`
  is the only such route) resolves its model with
  `models_preferred(modality: "humanoid_motion_model")` and takes a
  short body-geometry prompt; read `pr0ta-prompting` → "Motion Prompting Is an
  Exception" first.
- Marble worlds use `world_generation_submit`, not this route.
- Retries must be idempotent: send the same `idempotency_key` (≤ 200 chars; REST
  may use the `Idempotency-Key` header) on every retry of one logical
  generation. PR0TA claims the key before provider submission, so a timeout
  cannot bill twice. A retry while the first is in flight returns `409`; after
  acceptance it returns the existing task.
- Batches: `generation_batch_submit` (REST
  `POST /api/v2/projects/{project_id}/generate/batch`) carries up to 10
  requests; more returns `413`. Items are validated up front and submitted one
  by one, so a batch can partly succeed.
- The initial task may show `provider: null` and `model_id: null`; that is
  normal.

Per-generator request shapes, capability notes, the asset-ID resolution table,
and the submission response: `reference/unified-generation.md`.
Batch and the event feed: `reference/batch-and-events.md`.

## Task lifecycle

Long-running tools return a task ID. Status moves `queued` → `running` →
`succeeded`, `failed`, or `cancelled` (the spelling `canceled` also appears;
treat both as terminal). A 200 on submit only means queued; provider failures
surface later on the task.

- **Read:** `tasks_get` or `tasks_batch_get` (REST
  `GET /api/v2/projects/{project_id}/tasks/{task_id}`). Task state is
  authoritative. Poll every 2 seconds or slower (video: first check after about
  a minute, then every 30 seconds); the full policy is in
  `reference/reliability-contract.md`.
- **Result:** a task has two result fields. `result_refs` is the raw record
  the task wrote; `result` is derived from it. For media, read `result` and
  branch on `result.type`: generation tasks return `{type, asset_id,
  asset_ids, download_url, urls, variant_count}`. Durable `agent_chat_send`
  tasks return `{type: "agent_chat", response, role, topic, request_id}`.
  Prompt orchestration and Production Queue analysis normally return `{type:
  "generation_package", final_prompt, model_id, modality, reference_plan,
  validation, technical_params, lineage, ...}`, but may succeed with `{type:
  "prompt_assessment", prompt_assessment: {status, issues,
  clarification_questions, ...}}` for review. It is a terminal assessment, not
  a generation package: never generate from a `prompt_assessment`, and do not
  assume `final_prompt` exists because the task succeeded.
- **Task-specific payloads** are only in `result_refs`; the media envelope in
  `result` drops them. Examples: drafted scenes (`result_refs.scenes`,
  `failed`, `notReached`), mission receipts (`mission_id`, `mission_status`,
  `summary`, `cursor`), trained Seedance character tokens (`character_id`),
  SwitchX alphas (`alpha_asset_id`, `source_asset_id`) and BiRefNet mattes
  (`matte_asset_id`, `plate_asset_id`). The skill for each workflow names the
  field it reads.
- **Cancel:** `tasks_cancel` (REST
  `POST /api/v2/projects/{project_id}/tasks/{task_id}/cancel`; the unscoped
  `POST /api/tasks/{task_id}/cancel` also exists). PR0TA picks up results
  whose provider webhooks were late, but it never cancels or resubmits a stalled
  job: a video whose `progress` has not moved for more than 3 minutes is
  stalled; cancel it and decide whether to resubmit.
- **Resume:** call `agent_chat_resume` only when a failure carries
  `error.details.retry_token`; exhausted attempts omit it on purpose.
- Response shapes, error fields, and cancellation semantics:
  `reference/task-polling.md`.

### Completion subscriptions

Polling needs nothing configured. To be woken instead, a host receiver must be
running: skill text alone cannot resume a stopped conversation. With one,
register the exact conversation with `tasks_subscribe`, pass the returned ID as
`completion_subscription_id` on each generation request (or `tasks_watch` for
existing tasks), acknowledge actual pickup with `tasks_acknowledge`, and read
`tasks_get` for the canonical result. `tasks_completion_events` recovers missed
receipts; `tasks_unsubscribe` stops delivery. Unacknowledged completions are
emailed to the project owner after a grace period.

| Read | For |
| --- | --- |
| `reference/task-completion.md` | Subscription contract, signed webhook, acknowledgement, owner email, REST equivalents |
| `reference/codex-completion.md` | Codex receiver setup, pickup, recovery with a stale tool inventory |
| `reference/completion-receiver.py` | Example HTTPS receiver with a durable inbox |
| `reference/codex_completion_adapter.py` | Codex adapter the receiver uses to queue a message |
| `reference/completion_client.py` | REST helper for `events`, `watch`, `acknowledge` |

## Errors

| Status | Meaning |
| --- | --- |
| `400` | Invalid payload; unsupported generator/mode; a model that does not serve the mode or is not submittable (the message names why; check `models_list` / `GET /api/v2/models`); cross-project asset references; unknown modality key |
| `401` | Missing or invalid bearer token |
| `402` | Insufficient credit balance |
| `403` | No access to the project, or a PAT on an account/admin/billing route |
| `404` | Project, task, asset, or mission not found (including a task from another project) |
| `409` | Same idempotency key still in flight; conflicting subscription registration; stale mission version |
| `413` | Batch over 10 requests, or text too long for the route |
| `422` | Request schema rejected (for example the wrong multipart field name) |
| `429` | Rate limit reached; honor `Retry-After` |
| `502` | The provider returned no usable result |

A failed task carries `error`, `error_reason`, and `error_detail`.
`provider_timeout` is worth one retry; `provider_error` with
`error_detail.code: 402` means the provider account needs credits, so do not
retry; `invalid_parameters` means fix the payload. Report platform faults with
`bug_report_create`.

## Rate limits and concurrency

Requests per minute per authenticated user, by subscription tier: FREE 50,
CREATOR 100, PRO 200, ENTERPRISE 500. The budget covers every request,
including polling. On `429`, wait for `Retry-After`.

Submit at most 5 video, 10 image, and 3 audio generations in parallel per
project; queue the rest.

## Project memory

ProtaFilm|memory is the project's cited store of claims and decisions. This
section owns the memory contract; other skills point here.

- **Read.** `memory_context_pack(task_intent?, scope?)` before prompt,
  generation, editorial, or department decisions. It takes only those two
  arguments (your role comes from the session) and returns a
  `memory_snapshot_id`. Keep its citations and each claim's candidate or
  approved status. `memory_search` answers targeted lookups.
- **Note.** `memory_record_note(body, title?, ...)` proposes an observation for
  review; it never becomes Current by itself.
- **Decide.** `memory_record_decision(decision, ...)` records a user's
  production decision. It requires:
  - `semantic_key` (a precise key for what is decided) or `replaces_claim_id`
    (the claim it supersedes);
  - `memory_snapshot_id` from the `memory_context_pack` you read, or
    `expected_head_ids`, so a decision made on stale memory is refused;
  - a confirmation reference, `user_confirmation_ref`:
    `memory_get_confirmation` (approval given in PR0TA chat),
    `memory_request_confirmation` (an elicitation-capable MCP client asks the
    user), or an approving review event from `get_review_annotations` passed
    with its exact `approved_asset_id`. Without one it returns
    `confirmation_required` and `created: false`; do not retry blindly or
    claim the decision was recorded.

Confirmation details: `reference/mcp-server.md` → "Compatibility rules".

## Development tools

Development and Creative Direction run through these tools; `pr0ta-development`
and `pr0ta-prep` own the workflow. Each calls the web app's own route as the
user, so access, credits, and side effects match the app.

| Tool | Route it calls |
| --- | --- |
| `development_logline_set` | `POST /api/projects/{project_id}/metadata` (`developmentSettings`) |
| `beat_sheet_generate` | `POST /api/projects/{project_id}/beat-sheet/generate` (task) |
| `beat_sheet_approve` | `POST /api/projects/{project_id}/metadata` |
| `documents_list`, `document_add_text` | `GET` / `POST /api/projects/{project_id}/documents` |
| `scripts_list`, `script_create` | `GET` / `POST /api/projects/{project_id}/scripts` |
| `screenplay_import` | `POST /api/projects/{project_id}/screenplay/preprocess` |
| `screenplay_save` | `POST /api/projects/{project_id}/screenplay/update` |
| `screenplay_draft_beats` | `POST /api/projects/{project_id}/screenplay/draft-beats` (task) |
| `get_screenplay_text` | Paged screenplay read (`scene_number`, `offset`, `limit`, `next_offset`). Default: the latest published revision, Fountain notes removed (`not_published` before the first publish). `working_draft: true` (Operator role, which MCP clients use): the working draft; read it before revising or saving, and always save the complete current draft, never published text over a newer draft |
| `screenplay_publish` | `POST /api/projects/{project_id}/screenplay/publish` |
| `breakdown_status` | `GET /api/projects/{project_id}/screenplay/breakdowns/status` |
| `direction_approve` | `POST /api/projects/{project_id}/screenplay/breakdowns/approve-direction` |
| `breakdown_rerun` | `POST /api/projects/{project_id}/screenplay/breakdowns/refresh` |
| `supervisor_review_list`, `supervisor_review_answer` | `GET /api/script_supervisor/{project_id}/review`, `POST .../review/{flag_id}` |
| `get_breakdown_element_review`, `breakdown_element_review_decide` | `GET /api/projects/{project_id}/breakdown-review`, `POST .../breakdown-review/decisions` |

`project_metadata_get` returns the development state under
`developmentSettings` (`activeLogline`, `approvedLogline`, `approvedBeatSheet`,
`publishedScreenplay`). `screenplay_import` returns no script text; read the
imported draft with `get_screenplay_text(working_draft: true)`.

`get_project_development_context` returns the same under
`development_settings`; its top-level `logline` is the Producer read's, not the
working logline. `script_id` scopes it to one library script.

Approving a logline or beat sheet, publishing, approving direction, rerunning a
breakdown, and answering review questions are the user's decisions. Publishing,
approving direction, and rerunning spend credits. Call those tools only on the
user's explicit instruction.

## Operator missions


`operator_mission_start` hands a goal to PR0TA's own Operator as a durable
mission. It runs inside PR0TA under the project's Operator permissions and
credit budget, with review stops, on PR0TA's agent harness or, when the project
selects it in Settings → Agents, the Managed Codex runtime. The tools are the
same either way; `pr0ta-operator` owns when and how to delegate.

| Tool | Contract |
| --- | --- |
| `operator_mission_start` | `objective` (required), `title`, `scene_numbers`, `character`, `shot_number`, `client_id` (idempotency), `completion_subscription_id` → `mission_id`, `receipt_task_id` |
| `operator_missions_list` | Missions in the project; `archived` |
| `operator_mission_get` | Status, summary, checkpoint, actions pending review, usage, events after `after` (pass the previous `cursor`) |
| `operator_mission_send` | `text`, `mode` `steer` (change current work) or `follow_up` (queue next) → new `receipt_task_id` |
| `operator_mission_control` | `action`: `pause`, `resume`, `cancel`, `archive`, `unarchive`; resume returns a `receipt_task_id` |
| `operator_mission_review` | `effect_id`, `decision` `approve` or `reject`; only on the user's explicit instruction |

Each command returns a receipt task that settles when the mission next stops
(done, idle, review, attention, paused, failed, cancelled). Wait on it with
`tasks_get` or a completion subscription like any task. A settled receipt is
`succeeded` unless the mission failed or was cancelled; its `result_refs` hold
`mission_id`, `mission_status`, `summary`, and `cursor`. Then read
`operator_mission_get`.

REST: `/api/projects/{project_id}/operator-missions` (`GET` list, `POST`
create with `client_id`, `title`, `objective`, `scope`), `GET .../{mission_id}`,
and `POST .../{mission_id}/inputs`, `/controls`, `/reviews` (controls and
reviews take `expected_version`). REST commands return no receipt task; poll
the mission.

## Reference index

| Read | For |
| --- | --- |
| `reference/mcp-server.md` | MCP connection and OAuth, compatibility rules, prompt orchestration, pending Operator actions |
| `reference/mcp-tools.md` | Complete generated MCP tool catalog |
| `reference/projects-models-resources.md` | Project CRUD, model discovery routes, Elements, Characters, consistency bundles |
| `reference/unified-generation.md` | Request shapes per generator, capability notes, asset-ID resolution |
| `reference/batch-and-events.md` | Batch submission and the generation event feed |
| `reference/task-polling.md` | Task routes, response shapes, error fields, cancellation |
| `reference/reliability-contract.md` | Polling windows, stall handling, client wrapper and logging |
| `reference/asset-management.md` | Asset listing and paging, metadata, download, signed upload lifecycle |
| `reference/image-upload.md` | Direct multipart image upload (`files` field) |
| `reference/asset-tags-and-analysis.md` | Tags, annotations, readability filters, timeline analysis |
| `reference/timeline-api.md` | Post-production timeline: tracks, clips, audio mix, preview, snapshots |
| `reference/post-production-api.md` | Every post-production route, contract, and limit |
| `reference/source-shortfalls-and-fit-to-fill.md` | Short sources, `fitToFill`, four-point edits, speed |
| `reference/editorial-primitives.md` | Asset and program marks, 3-point edits, trims, link groups |
| `reference/narration-timeline-api.md` | Narration timeline: transcript layer, tags, cut list, verify, materialize |
| `reference/voice-v2.md` | Voice browser, clone, design, speech-to-speech |
| `reference/voice-and-transcription.md` | Transcription start and retrieval, audio extraction from video |
| `reference/music-analysis.md` | Beat, downbeat, and transient analysis |
| `reference/review-room-api.md` | Studio mode, review rooms, annotations, review webhooks |

Downloading bytes and exporting: `pr0ta-downloading`.
