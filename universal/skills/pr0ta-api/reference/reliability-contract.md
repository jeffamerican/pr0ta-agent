# Client Reliability Contract

> Detailed state machine, polling policy, fallback chain, and reference implementation for reliable PR0TA generation clients. Extracted from `pr0ta-api/SKILL.md` — read this when you are building or reviewing the wrapper layer that drives `/generate` end-to-end.

For robust automation, all generation calls should go through a single wrapper that implements the full state machine, polling policy, and fallback chain below. Do **not** rely on a single signal (events-only, task-only, or task_id-filter-only).

### State Machine

```
submitted -> waiting_task -> waiting_asset_fallback -> downloading -> succeeded
```

Failure paths:
- `waiting_task -> failed` (task terminal failure — check `error_reason`)
- `waiting_task -> canceled` (stalled task canceled via `POST /api/v2/projects/{id}/tasks/{task_id}/cancel`)
- `waiting_asset_fallback -> failed` (timeout + no matching asset)
- `downloading -> ambiguous` (asset found but bytes unavailable after retries)

**Note:** The backend normalizes both `canceled` and `cancelled` — handle both spellings in terminal status checks.

For every generation request, store: `task_id`, `project_id`, `submitted_at`, `prompt_hash`, `generator`.

### Polling Policy

- **Task poll interval:** `2s` with jitter (`+/- 300ms`)
- **Task poll max window:**
  - image: `120s`
  - video: `1200s` (20 minutes — long generations on busy days)
  - audio: `180s`
- **Asset fallback interval:** `3s` with jitter
- **Asset fallback window:**
  - image: `120s`
  - video: `600s`
  - audio: `120s`
- **Retries:** exponential backoff `2s, 4s, 8s, 16s` (cap 4 attempts) for transient `5xx/429/network`.

### Asset Correlation Rules

When correlating request → asset, use this priority order:

1. `assets?task_id={task_id}` — if non-empty, take newest by `created_at`
2. Filtered listing by kind (`?kind=image|video|audio`) and match:
   - exact `labels.prompt_hash` (if client wrote one), else
   - normalized prompt equality, else
   - `created_at` within `[submitted_at - 10s, submitted_at + max_window]`
3. If multiple candidates, score and pick highest:
   - same model: +3
   - prompt exact match: +3
   - nearest `created_at`: +2
   - matching aspect/duration hints: +1

### Download Fallback Rules (Video-Critical)

When asset is resolved:

1. Try authenticated `GET /api/v2/projects/{project_id}/assets/{asset_id}/download`, or use the scoped URL returned by `assets_get_download_link`
2. Validate bytes (`content-length > 0` OR body length > 0)
3. If zero-byte/invalid: fetch asset metadata, use authenticated `storage_uri` path. **Important:** The `storage_uri` path involves a redirect — always use `curl -L` (follow redirects) or equivalent.
4. If still invalid after retries: mark `ambiguous` and quarantine for replay

For MCP upload starts, create a stable `idempotency_key` before the first call and reuse it unchanged after a typed timeout. Do not invent a new key during recovery. Asset list and download-handoff timeout responses include `retryable: true` and a deterministic `retry_token`.

### Completion Signal Hierarchy

1. **Primary: Task polling** — `GET /api/v2/projects/{project_id}/tasks/{task_id}` (preferred) or `GET /api/tasks/{task_id}` (also valid). This is the authoritative completion signal. Poll at 2s intervals.
2. **Secondary: Events** — `GET /events` is acceleration only. Events may short-circuit task polling, but never mark a job succeeded/failed from events alone.
3. **Tertiary: Asset correlation** — `GET /assets?task_id=` as a fallback. Assume failures are metadata-population bugs, not a missing route. Keep the correlation scoring fallback (model +3, prompt +3, nearest created_at +2).
4. **Cancel stalls** — `POST /api/v2/projects/{project_id}/tasks/{task_id}/cancel` (preferred) or `POST /api/tasks/{task_id}/cancel` for stuck tasks before resubmitting.

### Async Provider Errors

A 200 on `POST /generate` does **not** mean the generation will succeed — it means the task was created and dispatched. Provider failures (insufficient credits, model unavailable, rate limits) happen asynchronously and surface only when the task reaches `status: "failed"`. The task will include:

- `error` — human-readable message (e.g. `"Insufficient credits"`)
- `error_reason` — machine-readable category (`provider_error`, `provider_timeout`, `invalid_parameters`)
- `error_detail` — full provider payload for diagnosis

**Retry guidance by `error_reason`:**
- `provider_timeout` → retry (transient)
- `provider_error` + `error_detail.code: 402` → do **not** retry; fix provider account credits first
- `provider_error` + other codes → inspect `error_detail`, may be transient
- `invalid_parameters` → do not retry; fix the payload

### Voice Discovery

Before TTS workflows: call MCP `voices_list` when the user has not provided an exact voice, or REST `GET /api/v2/projects/{project_id}/voices/browser` when MCP is unavailable. Use `provider`, `search`, `page_size`, `include_live`, and `include_custom` to browse/search. Copy the selected voice's `selection` fields into generation. On `404 voice_id` errors, refresh with `voices_list`. Do not gate on `supports_v3` metadata -- use try-and-fallback (attempt `eleven_v3`, fall back to `eleven_multilingual_v2`).

### Dead Task Detection and Resubmission

Video tasks can stall at 80-95% progress and never complete. There is no automatic stall recovery or auto-retry. **You must detect stalled tasks, cancel them through REST or MCP `tasks_cancel`, and decide whether to resubmit.**

**Detection rules:**
- If a video task has been at the same `progress` value for **>3 minutes** with no change, treat it as stalled
- If a video task has been in `processing` state for longer than the max window (20 minutes) with no terminal status, treat it as dead
- If a task reaches `failed` status, check `error_reason` — `provider_timeout` is worth retrying, `invalid_parameters` is not

**Resubmission strategy:**
1. Log the stalled `task_id` and its last known `progress` for debugging
2. **Cancel the stuck task:** `POST /api/tasks/{task_id}/cancel`
3. Resubmit the identical generation request (same prompt, model, references)
4. If the retry also stalls, cancel and try simplifying the prompt (shorter, fewer references)
5. After 3 failed attempts on the same shot, flag it for manual review — the prompt or reference combination may be incompatible with the model

**Concurrency guidance:**
- Safe to run **5-7 video tasks in parallel** without obvious throttling
- Above ~8-10 concurrent tasks, some providers may silently queue or deprioritize — monitor for increased stall rates
- Image tasks can be parallelized more aggressively (10-15 concurrent)
- Audio/music tasks are fast — serial or low parallelism (3-5) is fine

### Client Logging

Log one structured record per request with at minimum:

- `request_id` (client-generated UUID), `task_id`, `project_id`
- `generator`, `model`, `prompt_hash`
- `submitted_at`, `first_terminal_at`
- `resolution_path` (`task | task_id_assets | asset_fallback`)
- `download_path` (`download_endpoint | storage_uri`)
- `attempt_count`, `final_status`
- `error_class` (`provider_error | transport_error | reconciliation_timeout | download_zero_byte | unknown`)

### Reference Implementation

```ts
async function runReliableGeneration(req: GenRequest): Promise<GenResult> {
  const ctx = initContext(req); // request_id, prompt_hash, submitted_at
  const { task_id } = await submitGeneration(req);
  ctx.task_id = task_id;

  const taskResult = await pollTaskUntilTimeout(ctx);
  if (taskResult.terminal === "failed") return fail("provider_error", taskResult.error);

  let asset = taskResult.asset ?? await resolveByTaskId(ctx);
  if (!asset) asset = await resolveByAssetFallback(ctx);
  if (!asset) return fail("reconciliation_timeout", "No asset correlated within timeout");

  let file = await tryProjectDownload(asset, ctx);
  if (!file || file.bytes <= 0) file = await tryStorageUriDownload(asset, ctx);
  if (!file || file.bytes <= 0) return ambiguous("download_zero_byte", { asset_id: asset.id });

  return succeed({ task_id, asset_id: asset.id, file });
}
```

### Acceptance Tests

1. Image job where task remains `queued` but asset appears → wrapper returns `succeeded`
2. Video job where `/download` returns zero bytes but `storage_uri` works → wrapper returns `succeeded`
3. `assets?task_id=` empty but prompt/time fallback finds output → wrapper returns `succeeded`
4. Complete timeout with no task terminal + no asset → wrapper returns `failed` with `reconciliation_timeout`
5. Voice list call unavailable → wrapper retries, then fails with clear `voice_discovery_error`

### Implementation Notes

- Keep this wrapper in one module and route all generation calls through it
- Expose counters/metrics so reliability can be tracked over time
- Do not remove fallbacks until platform telemetry shows sustained stability

For mixed image/video/audio/music batches, split event polling by `generator` where practical rather than scanning one mixed stream.
