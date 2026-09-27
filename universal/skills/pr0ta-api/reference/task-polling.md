# Task Polling — Reference

Full polling contract: routes, in-progress / succeeded / failed response shapes, the error-reason taxonomy, cancellation, and the `result` vs `result_refs` canonical contract.

## Task Status and Polling Fallback

**Task status is authoritative.** Poll until a terminal state. MCP: `tasks_get` for one task, `tasks_batch_get` for several.

With a configured completion subscription, await the notification, acknowledge actual pickup, and read `tasks_get` to reconcile its result; see [completion notifications](task-completion.md). If a subscribed task finishes during active work and you accept its result through a status read, reconcile and acknowledge its completion event now; follow [active-work pickup](task-completion.md#results-picked-up-during-active-work).

### Get Task Status

```
GET /api/v2/projects/{project_id}/tasks/{task_id}
```

Use the project-scoped route so the project is explicit; the unscoped `GET /api/tasks/{task_id}` returns the same task object.

### Async Provider Errors

When a generation reaches the provider but fails there (e.g. insufficient provider credits, model unavailable), the task will reach `status: "failed"` with:

- `error` — human-readable message (e.g. `"Insufficient credits"`)
- `error_detail` — full provider payload for diagnosis

These failures are **asynchronous** — the initial `POST /generate` returns 200 + `task_id` + `"running"` before the provider rejects the job. Completion subscriptions report failures as well as success. Read the terminal task for details; never assume a 200 on submission means the generation will succeed.

Example in-progress response:
```json
{
  "id": "task_xyz123",
  "type": "video_generation",
  "project_id": "project-1",
  "status": "running",
  "progress": 42,
  "message": "Generation submitted, waiting for webhook",
  "created_at": "2026-04-03T14:20:00Z",
  "submitted_at": "2026-04-03T14:20:01Z",
  "result_refs": {},
  "metadata": {
    "unified_generation": {
      "generator": "video",
      "mode": "ref_to_vid"
    }
  }
}
```

Example completed response:
```json
{
  "id": "task_xyz123",
  "type": "video_generation",
  "project_id": "project-1",
  "status": "succeeded",
  "progress": 100,
  "message": "Generation completed",
  "created_at": "2026-04-03T14:20:00Z",
  "submitted_at": "2026-04-03T14:20:01Z",
  "result_refs": {
    "asset_id": "asset_abc123",
    "type": "video",
    "download_url": "/api/v2/projects/project-1/assets/asset_abc123/download"
  },
  "result": {
    "type": "video",
    "asset_id": "asset_abc123",
    "asset_ids": ["asset_abc123"],
    "download_url": "/api/v2/projects/project-1/assets/asset_abc123/download",
    "urls": ["/api/v2/projects/project-1/assets/asset_abc123/download"]
  }
}
```

Example failed response (async provider error):
```json
{
  "id": "task_xyz123",
  "status": "failed",
  "progress": 0,
  "error": "Insufficient credits",
  "error_reason": "provider_error",
  "error_detail": { "provider": "muapi", "message": "Insufficient credits", "code": 402 },
  "created_at": "2026-04-06T03:00:00Z",
  "submitted_at": "2026-04-06T03:00:01Z"
}
```

Example failed response (provider timeout):
```json
{
  "id": "task_xyz123",
  "status": "failed",
  "progress": 95,
  "error": "Provider generation timeout",
  "error_reason": "provider_timeout",
  "created_at": "2026-04-03T14:20:00Z",
  "submitted_at": "2026-04-03T14:20:01Z"
}
```

**Task response fields:**
- `created_at` — when the task was created
- `submitted_at` — when it was submitted to the provider
- `error` — human-readable error message (present when `status=failed`)
- `error_reason` — machine-readable error category (present when `status=failed`)
- `error_detail` — full provider payload for diagnosis (present on async provider failures)

Use `created_at` for timing calculations in the reliability contract. Use `error_reason` to decide whether a failed task is worth retrying:
- `provider_timeout` → retry (transient)
- `provider_error` + `error_detail.code: 402` → do **not** retry; fix provider account credits first
- `invalid_parameters` → do not retry; fix the payload

**`result` is the canonical media contract.** `result_refs` is the raw record the task wrote, and `result` is derived from it. Read asset information for generation tasks from `result`; its canonical shape is:

```json
{
  "result": {
    "type": "video",
    "asset_id": "asset-uuid",
    "asset_ids": ["asset-uuid"],
    "download_url": "/api/v2/projects/{project_id}/assets/{asset_id}/download",
    "urls": ["/api/v2/projects/{project_id}/assets/{asset_id}/download"],
    "variant_count": 1
  }
}
```

- `result.asset_id` — primary single-output identifier
- `result.asset_ids` — complete list of asset-backed outputs
- `result.download_url` — primary retrieval URL
- `result_refs` — the task's own payload. The media envelope keeps only the fields above, so anything task-specific is read from `result_refs`: drafted screenplay scenes (`scenes`, `failed`, `notReached`), Operator mission receipts (`mission_id`, `mission_status`, `summary`, `cursor`), trained Seedance character tokens (`character_id`), SwitchX alphas (`alpha_asset_id`, `source_asset_id`), BiRefNet mattes (`matte_asset_id`, `plate_asset_id`), and assembled timelines (`timeline`, `sequence_id`). Tasks whose contract is a passthrough (agent chat, generation packages) copy `result_refs` into `result` unchanged.

A succeeded generation task always carries `result.asset_id`. If one does not, report it with `bug_report_create`; meanwhile `assets_list` with `task_id` finds the output.

### Cancel a Stuck Task

MCP `tasks_cancel`, or:

```
POST /api/v2/projects/{project_id}/tasks/{task_id}/cancel
```

The unscoped `POST /api/tasks/{task_id}/cancel` also exists.

Cancels a running or stalled task. Use this when a video task has been stuck at the same `progress` for >3 minutes, or has exceeded the max polling window (20 min for video).

The backend normalizes both `canceled` and `cancelled` terminal states — completion side-effects are reliable for cancelled tasks.

**After a stall:** cancel, then resubmit the same request once (with a new `idempotency_key`, since it is a new attempt). If it stalls again, tell the user and choose another model for the modality with `models_list(modality=...)` only with their agreement. Replacing motion with a still is a creative decision for the user, not a recovery step. The full stall policy is in `reliability-contract.md`.

---
