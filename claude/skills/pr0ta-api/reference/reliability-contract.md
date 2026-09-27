# Client Reliability Contract

State machine, polling policy, stall handling, and error handling for anything
that drives generation end to end. The task is the authoritative record at
every step.

### State Machine

```
submitted -> waiting_task -> downloading -> succeeded
```

Failure paths:
- `submitted -> rejected`: the submit returned `4xx` (fix the payload; see
  `SKILL.md` → "Errors")
- `waiting_task -> failed`: terminal task failure; check `error_reason`
- `waiting_task -> cancelled`: a stalled task you cancelled with `tasks_cancel`
  or `POST /api/v2/projects/{project_id}/tasks/{task_id}/cancel`
- `downloading -> ambiguous`: the asset exists but its bytes could not be
  fetched after retries

Terminal status arrives as `cancelled` or `canceled`; handle both.

For every generation, store `task_id`, `project_id`, `idempotency_key`,
`submitted_at`, `model`, and `generator`.

### Polling Policy

- **Task poll interval:** 2 seconds or slower, with jitter (±300 ms). For
  several tasks, poll them together with `tasks_batch_get`.
- **Maximum wait before treating a task as dead:**
  - image: 120 s
  - video: 1200 s (20 minutes)
  - audio: 180 s
- **Transport retries:** exponential backoff 2 s, 4 s, 8 s, 16 s (at most 4
  attempts) for `5xx`, `429` (honor `Retry-After`), and network errors.
- Keep the whole client inside the per-minute rate limit in `SKILL.md` →
  "Rate limits and concurrency"; polling counts toward it.

### Completion Signals

1. **Task state** (`tasks_get`, `tasks_batch_get`, or
   `GET /api/v2/projects/{project_id}/tasks/{task_id}`) decides success or
   failure.
2. **Completion subscriptions** and the **event feed**
   (`GET /api/v2/projects/{project_id}/events`) tell you when to look. Never mark
   a job succeeded or failed from an event alone.
3. **Assets.** A succeeded generation task carries `result.asset_id` and
   `result.asset_ids`. If one does not, report it with `bug_report_create`;
   `assets_list` with `task_id` finds the output meanwhile.

### Downloads

Fetch bytes as `pr0ta-downloading` describes. Verify the file is larger than
zero bytes. A `202` with `{"status":"materializing"}` means retry the same URL
after `Retry-After`. If a scoped link has expired or fails, request a new one
with `assets_get_download_link` rather than reusing the old URL.

For MCP upload starts, create a stable `idempotency_key` before the first call
and reuse it unchanged after a typed timeout. Asset list and download-handoff
timeouts return `retryable: true` and a deterministic `retry_token`.

### Async Provider Errors

A 200 on `POST /generate` means the task was created and dispatched, not that
the generation will succeed. Provider failures (insufficient credits, model
unavailable, provider rate limits) surface only when the task reaches
`status: "failed"`, with:

- `error`: human-readable message
- `error_reason`: `provider_error`, `provider_timeout`, or `invalid_parameters`
- `error_detail`: the provider payload for diagnosis

Retry by `error_reason`:
- `provider_timeout`: retry once (transient)
- `provider_error` with `error_detail.code: 402`: do not retry; the provider
  account needs credits
- `provider_error` with other codes: inspect `error_detail`; may be transient
- `invalid_parameters`: do not retry; fix the payload

### Dead Task Detection and Resubmission

Video tasks can stall, often at 80–95% progress, and never finish. PR0TA polls
providers to pick up results whose webhooks were late, but it never cancels or
resubmits a job the provider has stalled.
There is no automatic stall recovery or auto-retry; the client owns stall handling: detect stalled tasks, cancel them, and decide whether to resubmit.

**Detection:**
- The same `progress` value for more than 3 minutes: stalled.
- Running longer than the maximum wait with no terminal status: dead.
- `failed`: follow the `error_reason` rules above.

**Resubmission:**
1. Log the stalled `task_id` and its last `progress`.
2. Cancel it (`tasks_cancel`).
3. Resubmit the same request once, with a new `idempotency_key` (a new
   attempt, not a retry of the old submission).
4. If that stalls too, try a simpler prompt (shorter, fewer references), or,
   with the user's agreement, another model for the modality from
   `models_list(modality=...)`.
5. After three failed attempts on the same shot, flag it for the user; the
   prompt and reference combination may not suit the model.

**Concurrency:** at most 5 video, 10 image, and 3 audio submissions in flight
per project (`SKILL.md` → "Rate limits and concurrency"). More does not finish
sooner and raises stall rates.

### Client Logging

Log one structured record per request with at least:

- `request_id` (client UUID), `task_id`, `project_id`, `idempotency_key`
- `generator`, `model`, `prompt_hash`
- `submitted_at`, `first_terminal_at`
- `attempt_count`, `final_status`
- `error_class` (`provider_error | transport_error | timeout | download_failed | unknown`)

### Reference Implementation

```ts
async function runReliableGeneration(req: GenRequest): Promise<GenResult> {
  const ctx = initContext(req); // request_id, idempotency_key, submitted_at
  const { task_id } = await submitGeneration(req, ctx.idempotency_key);
  ctx.task_id = task_id;

  const task = await pollTaskUntilTerminal(ctx); // cancels and returns "stalled" on a stall
  if (task.status === "failed") return fail("provider_error", task.error);
  if (task.status !== "succeeded") return fail("timeout", task.status);

  const assetId = task.result?.asset_id;
  if (!assetId) return fail("unknown", "succeeded task without result.asset_id");

  const file = await downloadAsset(ctx.project_id, assetId); // fresh link, retries 202
  if (!file || file.bytes <= 0) return ambiguous("download_failed", { asset_id: assetId });

  return succeed({ task_id, asset_id: assetId, file });
}
```

Route every generation through one wrapper like this, and count outcomes so
reliability can be tracked over time. `python-client.py` is a smaller Python
starting point.
