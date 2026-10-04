# PR0TA MCP Server

One tool registry serves both external MCP clients (Claude, Codex, ChatGPT,
Cursor, and other remote-MCP hosts) and PR0TA's in-app agents. A tool is defined
once, so the same name, schema, access checks, credits, and durable tasks apply
wherever it is called.

**Finding tools.** Call `prep_production_capabilities` for the page-to-tool map
(which tools serve Development, Prep, Production, and Post pages). The complete
generated catalog, with every tool's arguments, is `reference/mcp-tools.md`.
Your MCP client's tool listing has the full JSON schemas.

## Connecting

### Packaged setup

The Codex and Claude distributions bundle the remote connector; the universal
package carries the same configuration for other remote-MCP hosts:

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

After installing or updating, restart or reload the host if it keeps its
original tool inventory. The user authorizes PR0TA through the host's remote
MCP OAuth flow: the host opens or prints a PR0TA authorization URL, the user
signs in with their normal PR0TA account, and the host receives a user-scoped
token.

### Connect canary

Start a fresh session when the host requires it, then call `list_projects`. If
it returns the user's projects, the connection works. If PR0TA tools are not
callable, reconnect `https://app.pr0ta.com/api/mcp/mcp` with the host-specific
helper or instructions bundled with the distribution before falling back to
REST.

### Manual connector setup

- **ChatGPT:** enable Developer Mode / connectors, add a custom MCP connector
  with URL `https://app.pr0ta.com/api/mcp/mcp`, and complete PR0TA's OAuth.
- **Claude:** add a custom connector with URL
  `https://app.pr0ta.com/api/mcp/mcp` and complete PR0TA's OAuth.
- **Other hosts:** any client that supports remote Streamable HTTP MCP with
  OAuth.

### OAuth

- Streamable HTTP endpoint: `https://app.pr0ta.com/api/mcp/mcp`
- Authorization server metadata:
  `https://app.pr0ta.com/api/mcp/.well-known/oauth-authorization-server`
- Protected resource metadata:
  `https://app.pr0ta.com/api/mcp/.well-known/oauth-protected-resource/api/mcp/mcp`
- Root aliases for RFC 9728 clients:
  `https://app.pr0ta.com/.well-known/oauth-authorization-server/api/mcp`,
  `https://app.pr0ta.com/.well-known/oauth-authorization-server/api/mcp/mcp`,
  and `https://app.pr0ta.com/.well-known/oauth-protected-resource/api/mcp/mcp`
- Public PKCE clients (Codex-style) use `token_endpoint_auth_method: "none"`.
- Tokens are user-scoped and require an active account, verified email, admin
  approval, and an unlocked billing account.

### Troubleshooting

- **Host cannot discover OAuth:** check that the live authorization metadata
  lists `none` in `token_endpoint_auth_methods_supported`.
- **Host lists PR0TA tools but the model cannot call them:** the server setup
  succeeded; the fault is the host's tool admission. Do not replace MCP with
  PAT, REST, or browser automation for that case.
- **A tool is missing from the host's inventory:** refresh MCP discovery (for
  Codex, rerun the distribution's connection helper to refresh its enabled tool
  list) and start a fresh session.
- **Tools return empty results:** verify `project_id` with `list_projects`, and
  check that the Prep reads the tool wraps have been run.

## Compatibility rules

- Tool names use underscores, not dotted names.
- Every project-scoped tool requires `project_id`.
- `create_project` and `list_projects` are the project-independent MCP tools;
  they, `get_project_metadata`, `get_project_development_context`,
  `list_project_assets`, `get_workspace_snapshot` and the `operator_mission_*`
  tools exist only for MCP clients.
- `app_navigate` is client-only and is not published through MCP. External
  clients open returned app paths in their own browser.
- Long-running tools return task IDs. Wait with `tasks_get` (or a completion
  subscription); a submit never implies completion.
- Errors are structured: `error`, `error_reason`, `error_detail`, validation
  messages, and retry or fail-fast hints when available.
- File bytes move through upload and download handoffs, never inside MCP
  payloads. After a PUT to a signed upload URL, call `assets_upload_finalize`,
  which verifies existence and any declared size or SHA-256 before marking the
  asset ready, and confirm it returns `ready`. An upload you never finalize is
  confirmed by PR0TA within a few minutes; a probe result is not a ready
  asset.
- Use `voices_list` before TTS when the user has not named an exact voice, and
  copy the returned `selection` fields into `generation_submit`.
- Project memory: `SKILL.md` → "Project memory" owns the contract
  (`memory_context_pack` arguments, what `memory_record_decision` requires).
  A decision becomes Current only from a signed Operator approval or a
  verified user confirmation; a missing reference returns
  `confirmation_required` and `created: false`, so do not retry blindly or
  claim the Bible changed. Confirmation references:
  - After the user approves in PR0TA chat, call `memory_get_confirmation` and
    pass its `persisted-agent-chat-message-id` unchanged as
    `user_confirmation_ref`. Quoted approval prose is not an ID.
  - From an elicitation-capable MCP client, call `memory_request_confirmation`
    and pass its short-lived signed reference unchanged with the same
    `approved_asset_id`, `semantic_key`, and decision.
  - An actor-attributed `approved` or `approved_with_notes` event from
    `get_review_annotations` also works when it is still that submission's
    active decision, the call passes the event's exact `approved_asset_id`, and
    the key is an asset, reference, selection, or approval facet. The Current
    claim derives from the approved asset and key, not agent-written text.

## Prompt orchestration contract

`agent_chat_orchestrate_prompt` and typed `agent_chat_send` requests end at one
Cinematographer boundary. Poll with `tasks_get` and branch on `result.type`:

- `type: "generation_package"`: the final prompt, ordered multimodal reference
  plan, validated technical settings, prompt character count, and stage lineage.
  Generate only from this.
- `type: "prompt_assessment"`: designed-world or reference-design orchestration
  stopped for explicit review. Inspect `prompt_assessment.status`
  (`needs_clarification` or `has_problems`),
  do not assume `final_prompt` exists, and do not generate. The compiler does not call departments again for
  clarification.


The boundary repairs one invalid agent result, then fails with
`AGENT_RESULT_CONTRACT_VIOLATION`. Orchestration is a single pass: each
department resolves from the project's Settings → Agents configuration, gets
one structured call, and may get one retry of that same runtime or one focused
repair call. Exhausted attempts set `resume_safe: false` and omit
`retry_token`; `tasks_get.error.details.target_generation` states whether the
target provider was submitted and charged. `timeout_seconds` is a per-department
latency target, not a workflow deadline. Supply `target.max_characters` only to
assert an explicit endpoint limit.

**Designed-world references.** For guided stylized designed-world generation,
call `agent_chat_orchestrate_prompt` with
`prompt_profile: "designed_world_reference_image"`. Pass `guidance_package` with
exactly one neutral `flat_structural` pass and one `depth_normalized` pass
sharing package ID, resolution, and camera/frame identity; both are mandatory,
and depth needs finite visible-pixel percentile metadata and a passing histogram
check. Put the approved `appearance` reference and the required character,
styling, and prop authorities in `references`.
The Storyboarder must select or exclude every candidate reference explicitly. Provider order is flat, depth,
appearance, continuity. The older `semantic_asset_id` plus `appearance` pair
still works. Inspect `generation_receipt` for selected and excluded references,
normalization, QC, and provider order. Workflow: `pr0ta-prompting` →
`reference/designed-world-reference-image.md`.

**Net-new references.** The profiles
`prompt_profile: "character_reference_design"`, `"prop_reference_design"`, and
`"wardrobe_reference_design"` accept zero `references` and run the configured
department chain; departments with nothing to add return
`referenceDesignStatus: "not_applicable"`. Require a `generation_package` whose
`approval_status` is `candidate`, and call `generation_submit` only after the
user approves. Workflow: `pr0ta-prompting` →
`reference/reference-design-bootstrap.md`.

**Prompt-only packages.** `agent_chat_send` with `generation_mode:
"prompt_only"` freezes project context before the first department call.
Choosing Director, Storyboarder, or Cinematographer as the entry role runs the
full configured chain through the Cinematographer.

## Tool contracts worth knowing

- **`models_get_defaults`** resolves a catalog alias or provider ID and returns
  `requested_model_id`, `resolved_model_id`, the parameter schema, and, for
  models unified generation accepts, `request_defaults` that can seed a
  `generation_submit` request. Image parameters the schema advertises are
  forwarded or rejected before provider dispatch.
- **Motion.** Text motion uses `generator=motion`, `mode=text_to_motion`, the
  model from `models_preferred(modality: "humanoid_motion_model")`, and a short
  body-geometry prompt. The Hunyuan motion route (`fal-ai/hunyuan-motion`, the only text-to-motion route) takes optional `duration`
  (0.5–12), `guidance_scale` (1–10), `seed`, and `output_format` (`fbx` or
  `dict`). Read `pr0ta-prompting` → "Motion Prompting Is an Exception" before
  writing the prompt.
- **Cast visibility.** `cast_list_get` also shows explicitly named image assets
  tagged `reference_type: "character_reference"` with category `portrait` or
  `character_sheet` as unselected cast members. Give a consistent `subject` or
  `character_name`; visibility is not portrait approval. `cast_list_save` writes
  the Casting metadata and cast CSV together.
- **Storyboard sequences.** Saved sequences are authoritative for grouping,
  title, duration, marked prompts, selected reference sheets, and the ordered
  reference package. `storyboard_sequences_save` keeps records a partial upsert
  omits unless their scene is in `replace_scene_numbers`. Prompt markers are
  `storyboardSheetPrompt`, `seedancePrompt`, `omniReferencePrompt`, and
  `motionContinuityPrompt`; unknown markers fail with `422`. For Seedance
  storyboard control: `storyboard_chunks_list` →
  `storyboard_reference_sheet_generate` → `tasks_get` →
  `storyboard_reference_sheets_list`.
- **Production context.** `production_context_get` composes breakdown, casting,
  set, prop, look, and approved reference context for a scene or shot before
  generation.
- **Worlds.** `world_generation_submit` takes `mode` `text_to_world`,
  `image_to_world`, or `video_to_world`, and `world_model` from the Marble
  models the tool lists. Image mode accepts one image, an explicit panorama
  (`is_pano: true`), or 2–8 `multi_image_inputs`; a depth-guided set adds
  `depth_pano_url` or `depth_pano_media_asset_id` (EXR metric, or PNG with
  `depth_z_min`/`depth_z_max`). Set Designer requests pass `set_environment_id`
  so the world attaches to its set. Fetch SPZ, collider, or panorama files with
  `assets_get_download_link.artifact`. Workflow: `pr0ta-prompting` →
  `reference/marble-world-generation.md`.
- **Hybrid plates.** `set_environment_collider_materialize` (`environment_id`,
  `world_asset_id`) stores a Marble world's collider mesh as the environment's
  Blender source, and `blender_job_submit` accepts
  `request.source_world_asset_id` to render structure passes from it. Workflow:
  `pr0ta-hybrid`.
- **Trim, analysis, reports.** `assets_trim` (`asset_id`, `asset_type` `audio`
  or `video`, `in_point`, `out_point` in seconds) needs editor access. A short
  trim returns the new `asset.id` directly. One estimated past ~60 s (or sent
  with `background: true`) returns `{async: true, task_id, status,
  idempotency_key}`: poll `tasks_get` until it succeeds and read
  `result_refs.asset_id`. Retrying the same trim, or passing the same
  `idempotency_key`, joins that task instead of trimming twice. `music_analyze` returns an analysis
  task. `bug_report_create` returns `bug_report.id`.
- **Screenplay reads.** `get_screenplay_text` pages with `scene_number`,
  `offset`, `limit`, and `next_offset`. By default it returns the latest
  published revision with Fountain notes removed (`not_published` before the
  first publish); `working_draft: true` returns the working draft. Read the
  draft before revising or saving it, and save the complete current draft,
  never published text over a newer draft (`pr0ta-development`).

## Pending Operator action handoff

A succeeded agent-chat task can contain `proposedOperatorActions` awaiting
approval; it is not an analysis result. Each signed action includes
`execution_handoff` with the authenticated REST path, the exact request body,
and confirmation instructions. Present the arguments, risk, estimate, and
confirmation reason, and disclose unverified cost. Get the user's confirmation
before using the single-use, expiring token. The server still checks project
editor access, role, arguments, conversation epoch, and replay. A direct
resubmission is a separate paid request, not approval of the pending action.
Poll the returned analysis task before reporting QC findings.

## PR0TA's in-app agents

Inside PR0TA, department agents and the Operator call the same registry tools
through their configured model runtimes; the registry enforces which roles may
call each tool. The Operator runs durable missions on PR0TA's agent harness or,
when the project selects it in Settings → Agents, the Managed Codex runtime.
External agents reach it through the `operator_mission_*` tools (see
`SKILL.md` → "Operator missions" and `pr0ta-operator`).
