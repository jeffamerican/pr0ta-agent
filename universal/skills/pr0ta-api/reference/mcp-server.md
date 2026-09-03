# PR0TA MCP Server & Agent Tools

> **See also:** For review room tools exposed through this MCP surface, read `reference/review-room-api.md`. For the unified generation API, read `reference/unified-generation.md`.

## Overview

The PR0TA Agent Tool system provides a unified tool layer that serves two purposes:

1. **Internal agents** (Editor, Storyboarder, Director, etc.) use provider-native function calling through the BytePlus, Gemini, or OpenRouter adapter to query project data on demand.
2. **External tools** (Codex, Claude Code, Cursor, ChatGPT, Claude connectors, etc.) connect via an MCP server to query and interact with PR0TA project data.

Both share a single provider-agnostic tool registry — each tool is defined once and consumed everywhere.

---

## Available MCP Tools

### Agent-Complete Tools (require `project_id` unless noted)

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `generation_submit` | Submit one image, video, motion, 3D, Lipsync, speech, SFX, or music generation request | `project_id`, `request` |
| `generation_batch_submit` | Submit multiple generation requests in one call | `project_id`, `requests` |
| `memory_search` | Search cited ProtaFilm|memory claims for the current project | `project_id`, `query`, `department`, `scope_type`, `scope_id`, `limit` |
| `memory_context_pack` | Get role/task/scope-specific project memory for prompt building and agent decisions | `project_id`, `agent_role`, `task_intent`, `scope` |
| `memory_graph` | Get curated memory graph lenses for scene, department, decision, conflict, or provenance views | `project_id`, `lens`, `scene`, `department` |
| `memory_get_confirmation` | Resolve the exact latest persisted approval message ID accepted by `memory_record_decision` for the calling role | `project_id` |
| `memory_request_confirmation` | Ask the authenticated MCP user to approve one exact asset-bound decision and return a short-lived signed confirmation reference | `project_id`, `decision`, `semantic_key`, `approved_asset_id` |
| `memory_record_decision` | Record a durable creative or production decision in project memory; missing confirmation returns `confirmation_required` without creating a candidate | `project_id`, `decision`, `semantic_key` or `replaces_claim_id`, `memory_snapshot_id` or `expected_head_ids`; optional `user_confirmation_ref`; matching `approved_asset_id` and an asset/reference/selection/approval semantic facet for an approved review event |
| `memory_record_note` | Record a durable note for future agents | `project_id`, `title`, `body`, `department`, `scope_type`, `scope_id` |
| `voices_list` | Browse/search TTS voices across ElevenLabs, Gemini/Google, MiniMax, Kling, and xAI | `project_id`, `provider`, `search`, `page_size`, `include_live`, `include_custom` |
| `transcription_start` | Start Scribe V2 transcription and narration-timeline transcript auto-population | `project_id`, `asset_id`, `model_id`, `language`, `diarization`, `timestamp_granularity` |
| `transcription_get` | Retrieve stored transcript text, segments, and flattened word timing | `project_id`, `asset_id` |
| `tasks_get` | Poll canonical task state and result | `project_id`, `task_id` |
| `tasks_cancel` | Cancel a queued/running task | `project_id`, `task_id` |
| `assets_list` | List project assets with Prep/Production filters and pagination | `project_id`, `kind`, `category`, `reference_type`, `subject`, `source`, `favorite_only`, `asset_ids`, `folder_path`, `task_id`, `limit`, `offset` |
| `assets_upload_start` | Create a retry-safe upload handoff; reuse the same idempotency key after an ambiguous timeout, and storage events auto-finalize after PUT succeeds | `project_id`, `filename`, `content_type`, `kind`, `folder_path`, `idempotency_key`, `checksum_sha256` |
| `assets_upload_finalize` | Integrity-checking fallback finalizer; missing objects or declared size/SHA-256 mismatches fail without becoming ready | `project_id`, `asset_id`, `byte_size`, `checksum_sha256`, `duration_ms`, `metadata`, `category`, `subject`, `labels`, `status`, `folder_path` |
| `assets_annotations_update` | Write tags, notes, labels, and semantic reference metadata to one asset | `project_id`, `asset_id` or `url`, annotation fields |
| `assets_annotations_batch_update` | Annotate up to 100 Prep/Production assets in one call | `project_id`, `annotations` |
| `assets_favorite_set` | Favorite or unfavorite an asset | `project_id`, `asset_id`, `favorite` |
| `assets_get_download_link` | Return a short-lived scoped proxy URL without waiting for object-store signing | `project_id`, `asset_id`, `as_attachment`, `artifact` |
| `assets_download` | Alias for returning a download URL for an asset | `project_id`, `asset_id` |
| `audio_analyze` | Predict timeline audio levels for one range or multiple windows | `project_id`, `sequence_id`, `from_time`, `to_time`, `windows`, `track`, `tracks` |
| `audio_meter` | Run actual LUFS/true-peak metering for short ranges/windows | `project_id`, `sequence_id`, `from_time`, `to_time`, `windows`, `track`, `tracks`, `allow_long`, `timeout_seconds` |
| `music_analyze` | Start beat/downbeat/transient analysis for an instrumental asset | `project_id`, `asset_id`, `min_bpm`, `max_bpm`, `beats_per_bar`, include flags |
| `post_sequence_get` | Load the saved post-production sequence/timeline | `project_id`, `sequence_id` (optional) |
| `post_sequence_save` | Save or patch a post-production sequence/timeline payload | `project_id`, `timeline`, `sequence_id` (optional), `merge_existing`, `lock_token` |
| `post_render_start` | Start a post-production render task | `project_id`, `render_request`, `sequence_id` |
| `post_export_start` | Start a final master export task from a saved sequence; inline timeline payloads are rejected | `project_id`, `export_request`, `sequence_id` |
| `narration_timeline_get` | Load narration-timeline state | `project_id` |
| `narration_materialize_to_post` | Materialize narration cuts into post-production | `project_id`, `sequence_name`, `replace` |
| `review_submit_assets` | Publish project assets to a client review room | `project_id`, `asset_ids`, `title`, `description`, `review_notes`, `allow_download`, `webhook_url`, `webhook_secret` |
| `models_list` | Search the complete model/tool catalog with bounded pages | `generator`, `image_kind`, `search`, `curated_only`, `offset`, `limit` |
| `models_get_defaults` | Resolve a catalog alias or provider ID and return contract-equivalent defaults/schema, `requested_model_id`, `resolved_model_id`, and compatible `request_defaults` | `model_id` |
| `production_context_get` | Fetch existing script breakdown, casting, set, prop, look, and approved reference context for a scene/shot before generation | `project_id`, `scene_number`, `shot_number`, `character_names`, `include_provider_guidance` |
| `storyboard_chunks_list` | List 4-15s screenplay/storyboard chunks suitable for Seedance storyboard reference sheets | `project_id`, `scene_number`, `scene_range_end`, `max_duration_seconds` |
| `storyboard_reference_sheet_generate` | Generate chronological storyboard reference sheet variations for one chunk | `project_id`, `chunk_id`, `variation_count`, `reference_asset_ids`, `reference_image_urls`, `include_chunk_reference_urls` |
| `storyboard_reference_sheets_list` | List generated storyboard reference sheet assets for a chunk, optionally with download links | `project_id`, `chunk_id`, `include_download` |
| `prep_production_capabilities` | Map every Prep and Production page to its MCP tools | `project_id` |
| `project_metadata_get` | Read full project metadata or selected top-level Prep keys | `project_id`, `keys`, `lightweight` |
| `project_metadata_patch` | Merge editable Prep/Production metadata | `project_id`, `updates` |
| `style_package_get` | Load Style-page metadata and persisted style assets | `project_id`, `include_assets` |
| `style_package_save` | Persist `styleReferences` and annotate style/global-bible assets together | `project_id`, `styles`, `asset_annotations` |
| `style_world_create` | Create one Style world without replacing existing worlds; optionally claim scenes | `project_id`, `name`; optional `style_id`, `scope`, prompts, notes, `scene_numbers`, `is_default` |
| `style_world_assign_scenes` | Replace one alternate Style world's scenes and remove conflicts from other alternates | `project_id`, `style_id`, `scene_numbers` |
| `style_world_update` | Update one Style world's canonical prompts, scope, notes, model controls, or default status | `project_id`, `style_id`; optional revised fields |
| `style_world_delete` | Delete one Style world while retaining at least one valid default | `project_id`, `style_id` |
| `department_heads_get` | Load Locations, Looks, and Props partitioned data | `project_id`, `start_scene`, `end_scene`, `include_bootstrap` |
| `department_heads_save` | Persist Locations, Looks, or Props data | `project_id`, `department`, `scenes`, `breakdown`, `library`, `authoritative_scene_numbers` |
| `cast_list_get` | Load the canonical Casting-page cast list | `project_id` |
| `cast_list_save` | Failure-safely persist Casting metadata and cast CSV; optionally reconcile divergent stores | `project_id`, `cast_members`, optional `reconcile_existing` |
| `agent_chat_orchestrate_prompt` | Build a typed multi-department provider prompt; bootstrap net-new character, hero-prop, or wardrobe candidates without an existing reference, or use the designed-world/Seedance specialist profiles | `project_id`, `creative_brief`, `prompt_profile`; optional `references`, `guidance_package`, `role_chain`, `optional_roles`, `target`, `memory_scope`, `authority_plan` |
| `agent_chat_resume` | Resume a retryable failed orchestration from its preserved checkpoint without rerunning completed departments | `project_id`, `retry_token` from `tasks_get.error.details.retry_token` |
| `agent_chat_send` | Queue project-scoped department chat using app context, credits, and persistence; `generation_mode: "prompt_only"` returns a typed package through the Production Queue Cinematographer boundary | `project_id`, `role`, `topic`, `message`; use `topic.deliverable: "seedance_omni_prompt"` for final Seedance packages |
| `producer_read_generate`, `director_read_generate`, `casting_read_generate`, `script_supervisor_read_generate` | Queue durable Prep reads | `project_id` plus the prerequisite analysis payloads |
| `department_read_generate` | Queue Locations, Looks, or Props reads | `project_id`, `department`, `scenes`, prerequisite analyses |
| `shotlist_generate`, `shotlist_generate_batch`, `shotlist_scene_chat` | Generate or refine shotlists | `project_id` plus scene/analysis payloads |
| `save_scene_shotlist` | Save shots with canonical integer `shotNumber`; scene-prefixed display labels such as `1.01` are preserved as `shot_id` | `project_id`, `scene_number`, `shots` |
| `storyboard_generate`, `storyboard_generate_batch`, `storyboard_sequences_get`, `storyboard_sequences_save` | Generate and persist storyboards/sequences | operation-specific scene and sequence fields |
| `production_queue_*` | Complete Production Queue CRUD, prompting, selection, regeneration, analysis, refresh, and recovery | operation-specific queue fields |
| `memory_overview`, `memory_sources_*`, `memory_claims_list`, `memory_claim_update`, `memory_conflicts_list` | Full Memory workspace administration | operation-specific source, filter, and claim fields |
| `casting_voice_*`, `voices_*`, `consistency_resources_*` | Casting voice workflows and reusable Seedance/Kling resources | operation-specific request/resource fields |
| `performances_list` | List/search human-performance metadata | `project_id`, `scene_number`, `character`, `text`, `limit`, `offset` |
| `performances_create` | Create human-performance metadata | `project_id`, `performance` |
| `performances_update` | Update human-performance metadata | `project_id`, `performance_id`, `updates` |
| `performances_delete` | Delete human-performance metadata without deleting media | `project_id`, `performance_id` |

`cast_list_get` also projects explicitly named image assets tagged `reference_type: "character_reference"` and categorized as `portrait` or `character_sheet` into unselected member shells. Supply a consistent `subject` and/or `character_name`; Prep → Cast exposes the candidate but does not automatically approve or select its portrait or character sheet.

When present, `models_get_defaults.request_defaults` can be passed directly to `generation_submit`; voice and catalog-only tool models omit it because they use dedicated workflows. Catalog aliases resolve before schema lookup, and `resolved_model_id` names the canonical provider model. Unified image parameters advertised by that schema are forwarded or rejected before provider dispatch; image-edit tasks expose requested and normalized snapshots separately from `metadata.provider_request.parameters`. `models_list` searches the complete catalog and returns a bounded page (default 50, maximum 200) with `offset`, `limit`, `total`, and `has_more`; it accepts `curated_only=true` for a shorter administrator-curated menu. Image-to-3D uses `generator=3d`, `mode=image_to_3d`, and `image_asset_id` or `image_url`. Image `sync_mode` is boolean, `text_to_image` normalizes to `txt_to_img`, and the compatibility alias `image_edit` normalizes to `img_to_img`; agents should emit `img_to_img`, `ref_to_img`, or `edit_img` and preserve selected assets through asset-ID fields. `performances_list.scene_number` accepts an integer or numeric string.

Prompt-only generation packages, including direct `agent_chat_send` requests, freeze their project context before the first department call. Selecting Director, Storyboarder, or Cinematographer as the generic prompt entry role always invokes the complete configured Director → Casting → Production Designer → Stylist → Propmaster → Storyboarder → Cinematographer chain. A generic `contributed` Casting, Stylist, or Propmaster result must contain a prompt fact or reference recommendation. Contributed prompt facts are reserved inside the selected endpoint's prompt budget and remain required at the terminal Cinematographer boundary.

For a net-new reference, use `character_reference_design`, `prop_reference_design`, or `wardrobe_reference_design`. Every profile runs the configured Director, Casting, Production Designer, Stylist, Propmaster, Storyboarder, and Cinematographer. Director and Storyboarder must contribute; other departments return typed `referenceDesignStatus: "not_applicable"` with an empty `proposedPrompt` when the subject has no material decision inside their authority, rather than inventing unrelated design facts. The workflow accepts zero `references`. Zero-reference requests default to `nano_banana_2` plus `text_to_image`; requests with references default to `reference_to_image`. Reference `type` accepts the media values `image`, `video`, and `audio` plus the semantic image aliases `character_reference`, `style_reference`, `prop_reference`, and `wardrobe_reference`. Poll with `tasks_get`, require a `generation_package` whose `approval_status` is `candidate`, then call `generation_submit` only after explicit user approval. Read `pr0ta-prompting` → `reference/reference-design-bootstrap.md` for complete payloads and failure handling.

Hunyuan text motion uses `generator=motion`, `mode=text_to_motion`, `model=fal-ai/hunyuan-motion`, and a short body-geometry prompt. Optional controls are `duration` (0.5-12), `guidance_scale` (1-10), `seed`, and `output_format` (`fbx` or `dict`). Read `pr0ta-prompting` → "Motion Prompting Is an Exception" before writing the prompt.

### Project Intelligence and Legacy Review Tools

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `get_scene_breakdown` | Scene characters, locations, props, action, continuity notes | `scene_number` (required), `scene_range_end` (optional) |
| `get_scene_shotlist` | Director's shot list for a scene | `scene_number` (required) |
| `get_character_references` | Character portrait, voice config, wardrobe, look timeline | `character_name` (required) |
| `get_set_references` | Production design images and notes for a location/scene | `scene_number` (optional), `location` (optional) |
| `get_shot_assets` | Video/audio takes, storyboard frames for a shot | `scene_number` (required), `shot_number` (required) |
| `get_screenplay_text` | Active saved screenplay with scene selection, pagination, revision metadata, and optional live workspace context | `scene_number`, `offset`, `limit`, `include_workspace_context`, `workspace_session_id` (optional) |
| `enable_studio_mode` | Enable Studio mode so review-room tools can create submissions, rounds, and share links | (none) |
| `submit_assets_for_review` | Legacy alias for review-room submission | `asset_ids` (required); `title`, `description`, `review_notes`, `allow_download`, `webhook_url`, `webhook_secret` (optional) |
| `get_review_annotations` | Retrieve review comments, annotations, and decisions; every event includes `asset_id` and the response includes referenced `review_submissions` | `review_round_id`, `submission_id`, `resolution_status` (optional) |

Prefer `production_context_get` over a hand-rolled ledger when a project already has breakdowns, casting, department-head references, or contact/character sheets. It composes existing PR0TA prep state and returns provider guidance for Seedance and Kling. For Seedance 2.0 Omni storyboard-control workflows, use `storyboard_chunks_list` -> `storyboard_reference_sheet_generate` -> `tasks_get` -> `storyboard_reference_sheets_list`.

For World Labs Marble sets, call `world_generation_submit` with `mode: "text_to_world"`, `"image_to_world"`, or `"video_to_world"`. Image mode accepts `image_url`/`image_media_asset_id`, an explicit panorama via `is_pano: true`, or 2-8 `multi_image_inputs` rows containing `uri` or `media_asset_id` and optional `azimuth`. Use `reconstruct_images: true` for overlapping same-space auto layout. Use `world_model: "marble-1.1"` by default, `"marble-1.1-plus"` for larger environments, and `"marble-1.0-draft"` for inexpensive exploration. Set Designer requests should include `set_environment_id` so the completed world attaches to the validated canonical set lineage.

For a depth-guided set, use `mode: "image_to_world"`, a text `prompt`, and `depth_pano_url` or `depth_pano_media_asset_id`. Include `depth_pano_extension: "exr"` for metric EXR input. For normalized PNG input use `"png"` plus positive `depth_z_min` and `depth_z_max` metres, with max greater than min. The returned task covers both depth-to-RGB and panoramic world generation. The registered world preserves metric scale and ground offset; request SPZ, collider, or panorama files through `assets_get_download_link.artifact` using `world_splat_full_res`, `world_splat_500k`, `world_splat_100k`, `world_mesh_collider`, or `world_pano`.

Saved storyboard sequences are authoritative for manual grouping, title, duration, explicitly marked prompts, selected reference sheets, and the ordered reference package. `storyboard_sequences_save` preserves records omitted from a partial upsert unless their scene is listed in `replace_scene_numbers`; use replacement when saving a complete scene grouping. Prompt markers are `storyboardSheetPrompt`, `seedancePrompt`, `omniReferencePrompt`, and `motionContinuityPrompt`; snake-case aliases are accepted and normalized, while unknown markers fail with status 422. A one-call `storyboard_sheet_prompt` passed to `storyboard_reference_sheet_generate` has highest prompt precedence.

`production_queue_analyze` and typed `agent_chat_send` requests terminate at one shared Cinematographer boundary. A successful single-item analysis normally exposes the complete `generation_package` directly through `tasks_get.result`, including the final prompt, ordered multimodal reference plan, validated technical settings, prompt character count, Queue identity, and available stage lineage. Designed-world or reference-design prompt orchestration may instead succeed with `type: "prompt_assessment"` for explicit review; the compiler does not recursively call departments for clarification. Inspect `prompt_assessment.status`, do not assume `final_prompt` exists, and do not generate unless `result.type` is `generation_package`. The boundary repairs one invalid agent result, then fails with `AGENT_RESULT_CONTRACT_VIOLATION` without setting `cinematographer_finalized`.

For guided stylized designed-world generation, call `agent_chat_orchestrate_prompt` with `prompt_profile: "designed_world_reference_image"`. Preferred input uses `guidance_package` with exactly one neutral `flat_structural` pass and one `depth_normalized` pass sharing package ID, resolution, and camera/frame identity. Submit the approved `appearance` reference plus required character, styling, and prop authorities in `references`; the Storyboarder must select or exclude every candidate reference explicitly. Stylist and Propmaster are always consulted from Settings → Agents and return typed `not_applicable` results when their department has nothing to contribute; `subject_presence` is context for that agent decision, not a server-side skip instruction. Provider order is flat, depth, appearance, continuity. Depth requires finite visible-pixel percentile metadata and passing histogram QC; both package members are mandatory. The backward-compatible active `semantic_asset_id` plus `appearance` path remains available. Poll with `tasks_get`, generate only from `result.type: "generation_package"`, and inspect `generation_receipt` for selected/excluded references, normalization, QC, validation, and provider order.

### Discovery Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `create_project` | Create a PR0TA project for the authenticated user | `name` (required), `description`, `slug` (optional) |
| `list_projects` | List all available PR0TA projects | (none) |
| `get_project_metadata` | Project summary: logline, genre, tone, cast, visual approach | `project_id` (required) |

### Compatibility Rules

- Tool names use underscores, not dotted names.
- `app_navigate` is client-only and is not published through MCP. External clients should open returned app paths in their own browser environment.
- Every project-scoped tool requires `project_id`; `create_project` and `list_projects` are project-independent.
- Use `memory_context_pack` before prompt-building, generation, editorial, styling, writing, or production decisions. Preserve citations and do not merge candidate claims into approved facts.
- Use `memory_record_decision` or `memory_record_note` after accepted decisions, selected references, continuity constraints, client/director notes, and editorial conclusions.
- `memory_record_decision` only becomes Current from a signed Operator approval or a verified persisted user-message reference. A missing reference returns `confirmation_required` and `created: false`; do not retry blindly or claim the Bible changed.
- Call `memory_get_confirmation` after the user explicitly approves a memory write in PR0TA chat, then pass its `persisted-agent-chat-message-id` unchanged as `user_confirmation_ref`; quoted approval prose is not an ID. From Codex or another elicitation-capable MCP client, call `memory_request_confirmation` and pass its short-lived signed reference unchanged with the same `approved_asset_id`, `semantic_key`, and decision.
- An actor-attributed `approved` or `approved_with_notes` event returned by `get_review_annotations` is also a valid `memory_record_decision.user_confirmation_ref` when it remains that submission's active decision after the latest publish marker, the call passes the event's exact snapshotted `approved_asset_id`, and it targets an asset/reference/selection/approval semantic facet. The Current claim is canonically derived from the approved asset and semantic key, not agent-authored decision text, and records the review event, round, submission, reviewer, and immutable asset provenance; unrelated identity or continuity facets require their own chat or Operator confirmation.
- Use `voices_list` before TTS when the user has not provided an exact voice. Copy the returned `selection` fields into `generation_submit` or REST `/generate`.
- Long-running work returns task IDs. Poll with `tasks_get`; submit tools never imply completion.
- Prompt orchestration is a frozen single-pass compiler: department tools are disabled, each role resolves from the project's Settings -> Agents configuration and gets one compact structured call under a model-aware execution profile. The task snapshot includes the project orientation/casting slice used by every stage and derives handoff-summary length from the selected generation endpoint's published prompt limit. Supply `target.max_characters` only to assert an explicit endpoint contract; models whose schema declares no limit do not receive an invented summary ceiling. A transient provider failure may retry that same configured runtime once; it never substitutes a hard-coded model. A schema-invalid response may instead get one focused repair call. `timeout_seconds` is an independent soft latency target for each department rather than a cumulative workflow deadline: active streamed output may continue, stalled reads use the server idle timeout, and a higher fail-safe ceiling stops runaway calls. The profile applies the role budget only when the selected runtime publishes a completion limit or an operator supplies an explicit ceiling; it does not infer output capacity from the input context window. Active-generation and validation progress remain visible. Exhausted attempts set `resume_safe: false` and omit `retry_token`. `tasks_get.error.details.target_generation` and failure `result_refs` explicitly state whether the target provider was submitted and charged.
- Errors are structured with `error`, `error_reason`, `error_detail`, validation messages, and retry/fail-fast hints when available.
- File bytes are handed off through upload/download intents and links, not embedded in MCP payloads.
- Signed upload handoffs are completed by storage object-finalize events after a successful PUT to the returned upload URL. If event delivery is unavailable or delayed and the asset remains in `uploading` status, call `assets_upload_finalize` as a fallback; it verifies object existence and declared size/SHA-256 before making the asset ready.

### Role-Tool Access Matrix

Not all roles have access to all tools. The registry enforces access per role.

| Tool | writer | producer | director | casting | script_supervisor | acting_coach | production_designer | stylist | propmaster | storyboarder | cinematographer | editor | story_editor |
|------|--------|----------|----------|---------|-------------------|--------------|---------------------|---------|------------|--------------|-----------------|--------|--------------|
| `get_scene_breakdown` | Y | | Y | | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| `get_scene_shotlist` | | | Y | | | Y | Y | | | Y | Y | Y | |
| `get_character_references` | | | Y | Y | | Y | Y | Y | | Y | | Y | |
| `get_set_references` | | | Y | | | | Y | | | Y | Y | Y | |
| `get_shot_assets` | | | Y | | | | | | | | Y | Y | |
| `get_screenplay_text` | Y | | Y | | Y | Y | | | | | | Y | Y |
| `production_context_get` | | Y | Y | Y | | | Y | Y | Y | Y | Y | Y | |
| `storyboard_chunks_list` | | Y | Y | | | | | | | Y | | Y | |
| `storyboard_reference_sheet_generate` | | Y | Y | | | | | | | Y | | Y | |
| `storyboard_reference_sheets_list` | | Y | Y | | | | | | | Y | | Y | |
| `review_submit_assets` | | Y | Y | | Y | | | | | | | Y | |
| `submit_assets_for_review` | | Y | Y | | Y | | | | | | | Y | |
| `get_review_annotations` | | Y | Y | | Y | | | | | | | Y | |
| project metadata and Style tools | | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| asset annotation tools | | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| department-head tools | | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| Casting and performance tools | | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |

---

## MCP Server Setup

### Claude Code Plugin Setup

The PR0TA Claude Code plugin bundles the remote MCP connector. The plugin manifest (`.claude-plugin/plugin.json`) contains:

```json
{
  "mcpServers": "./.mcp.json"
}
```

The bundled `.mcp.json` points at production:

```json
{
  "mcpServers": {
    "pr0ta": {
      "type": "http",
      "url": "https://app.pr0ta.com/api/mcp/mcp"
    }
  }
}
```

After installing or updating the plugin, restart/reload Claude Code. The user authorizes PR0TA by running `/mcp` in Claude Code, selecting **pr0ta**, and completing the browser OAuth approval. If PR0TA tool names are not callable after loading the skill, the connector is not exposed or not authenticated in that session; reconnect the bundled MCP server before falling back to REST.

If PR0TA tools are not visible after restart, the agent should launch the connect canary instead of only telling the user to do it manually:

```bash
scripts/connect-mcp.sh   # relative to the plugin root
```

If the helper path is not available in the current install, register the server manually:

```bash
claude mcp add --transport http pr0ta https://app.pr0ta.com/api/mcp/mcp
```

Then ask the user to run `/mcp` in Claude Code and complete the PR0TA OAuth flow. Expected behavior: Claude Code opens or prints a PR0TA authorization URL. If it prints the URL, surface that URL to the user and ask them to complete browser approval. Complete the browser login, then check tool search (for example, ToolSearch) for `list_projects`; restart the session if the tools still do not appear. If the host reports it cannot detect OAuth or authorization support, verify the live authorization metadata includes `token_endpoint_auth_methods_supported` with `none`, and redeploy PR0TA before retrying. If tool search still finds no PR0TA tools after a completed OAuth login, debug plugin discovery; before login, no project, generation, or timeline tools are expected to be callable. If `/mcp` reports `Auth: OAuth` and lists the tools but the model still says they are unavailable, the server setup succeeded and the remaining defect is host-side tool admission. Do not replace MCP with PAT/REST/browser automation for that case.

### Local Development Prerequisites

```bash
pip install mcp
```

### Local Transports

**stdio** (Claude Code, Cursor, and other local IDE integrations):

```bash
cd pr0ta_platform/backend
python mcp_server.py
```

**SSE** (legacy remote/testing):

```bash
python mcp_server.py --sse
```

**Streamable HTTP** (local HTTP testing):

```bash
python mcp_server.py --streamable-http
```

### Claude Code Configuration (Local Stdio Fallback)

Add the PR0TA MCP server to `.claude/mcp.json` at the project root:

```json
{
  "mcpServers": {
    "pr0ta": {
      "command": "python",
      "args": ["pr0ta_platform/backend/mcp_server.py"],
      "cwd": "/path/to/script2screen"
    }
  }
}
```

With a virtual environment:

```json
{
  "mcpServers": {
    "pr0ta": {
      "command": "/path/to/script2screen/venv/bin/python",
      "args": ["pr0ta_platform/backend/mcp_server.py"],
      "cwd": "/path/to/script2screen"
    }
  }
}
```

### Cursor Configuration (Local Stdio Fallback)

**Project-level (recommended)** — `.cursor/mcp.json` in the repo root:

```json
{
  "mcpServers": {
    "pr0ta": {
      "command": "python3",
      "args": ["pr0ta_platform/backend/mcp_server.py"],
      "env": { "PYTHONPATH": "." }
    }
  }
}
```

Point `command` at your venv Python if using one. Restart Cursor after changing MCP config.

---

## Remote MCP Connectors (OAuth)

PR0TA exposes a remote MCP surface for Codex, ChatGPT, Claude-style connectors, Cursor-style clients, and other MCP hosts.

### Production URLs

- **Streamable HTTP:** `https://app.pr0ta.com/api/mcp/mcp`
- **OAuth metadata:** `https://app.pr0ta.com/api/mcp/.well-known/oauth-authorization-server`
- **Protected resource metadata:** `https://app.pr0ta.com/api/mcp/.well-known/oauth-protected-resource/api/mcp/mcp`
- **Root metadata aliases for RFC 9728 clients:** `https://app.pr0ta.com/.well-known/oauth-authorization-server/api/mcp`, `https://app.pr0ta.com/.well-known/oauth-authorization-server/api/mcp/mcp`, and `https://app.pr0ta.com/.well-known/oauth-protected-resource/api/mcp/mcp`

### Auth Model

- Remote connectors authenticate through PR0TA MCP OAuth.
- Codex-style public PKCE clients use `token_endpoint_auth_method: "none"`.
- Users log in with their normal PR0TA account on the consent page.
- Connector tokens are user-scoped and enforce: active account, verified email, admin approval, billing/account lock checks.

### ChatGPT Setup

1. Enable ChatGPT Developer Mode / connectors.
2. Add a custom MCP connector with URL `https://app.pr0ta.com/api/mcp/mcp`.
3. Complete the PR0TA OAuth authorization flow when prompted.

### Claude Setup (Remote)

1. Add a custom MCP connector with URL `https://app.pr0ta.com/api/mcp/mcp`.
2. Complete the PR0TA OAuth authorization flow.

For Claude Code local development, prefer the stdio setup above. For normal agent use, prefer the remote connector.

### Local vs Remote Auth

- Local `stdio` clients: use `access_token` tool arguments or `PR0TA_MCP_ACCESS_TOKEN` env var.
- Remote connectors: use MCP OAuth bearer auth, not tool-level `access_token` arguments.

---

## Environment Requirements

The MCP server requires the same environment variables as the main backend:

```bash
OPENROUTER_API_KEY=<your-key>       # Required for factory-default internal agents
# GEMINI_KEY or BytePlus credentials are required when those providers are selected.
DATABASE_URL=<your-database-url>    # Required for project listing
```

---

## Internal Agent Integration

When tools are enabled for a role, the agent chat function:

1. Builds a slim context (project summary, scene index, character names) instead of the full context blob.
2. Converts tool definitions through the selected runtime's Gemini or OpenAI-compatible adapter.
3. Runs a multi-round function-calling loop (up to 5 rounds) until the model returns a text response.
4. Parses the final text response as JSON.

### Enabling/Disabling Tools

Tools are enabled by default for all core roles. Override per-project via `crew_config.json`:

```json
{
  "agent_tools": {
    "enabled": false,
    "roles_with_tools": []
  }
}
```

When `agent_tools.enabled` is `false`, the system falls back to the existing full context blob flow with zero behavioral change.

---

## Adding New Tools

1. **Define** — Add a `ToolDefinition` entry to `TOOL_CATALOG` in `registry.py` with `allowed_roles`.
2. **Implement** — Add a handler function in `implementations.py` and register it in `TOOL_HANDLERS`.
3. **Done** — The new tool is automatically available to internal agents (via `get_tools_for_role()`) and MCP clients (via `register_tools()` in the MCP bridge). No changes needed in the MCP server, agent chat service, or adapters.

---

## Troubleshooting

- **MCP server won't start:** Check Python path, install `mcp` SDK, verify `.env` for database and API keys.
- **Tools return empty results:** Verify `project_id` via `list_projects`. Check that the Producer/Director/Script Supervisor reads have been run — tools wrap existing services.
- **Function calling not working (internal agents):** Verify `agent_tools.enabled` is `true`, the role is in `roles_with_tools`, the provider is BytePlus, Google, or OpenRouter, and the selected catalog model advertises tool support.
- **MCP tool calls failing:** All project-scoped MCP tools require `project_id`. `create_project` and `list_projects` are project-independent; internal project tools get the ID from the execution context, while external MCP calls need it explicitly.
