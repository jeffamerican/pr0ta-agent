# Batch Generation and the Event Feed

## Batch Generation

Submit several generation requests in one call. MCP: `generation_batch_submit`
with `{project_id, requests: [...]}`.

### Submit Batch (Auth Required)

```
POST /api/v2/projects/{project_id}/generate/batch
```

Request:
```json
{
  "requests": [
    { "generator": "image", "mode": "txt_to_img", "model": "<model_id from models_preferred>", "prompt": "...", "idempotency_key": "shot-01-v1" },
    { "generator": "image", "mode": "txt_to_img", "model": "<model_id from models_preferred>", "prompt": "...", "idempotency_key": "shot-02-v1" }
  ]
}
```

**All parameters go at the top level of each request object.** Each item has
the same flat shape as a single `POST /generate` request. Nesting them inside a
`"params"` object fails with errors such as `"prompt is required"`.

```json
// Correct: flat
{ "generator": "video", "mode": "ref_to_vid", "model": "<model_id>", "prompt": "...", "duration": 10 }

// Wrong: nested params object
{ "generator": "video", "mode": "ref_to_vid", "params": { "model": "<model_id>", "prompt": "...", "duration": 10 } }
```

**Guardrails:**
- At most 10 requests per batch; more returns `413`.
- An empty `requests` array returns `400`.
- Every item is validated before any is submitted; items are then submitted one
  by one, so an early item can be accepted before a later one fails.
- An `Idempotency-Key` header is the batch key; PR0TA derives one key per item
  from it. An item's own `idempotency_key` takes precedence.
- `completion_subscription_id` can be set on each item.

Response:
```json
{
  "tasks": [
    { "index": 0, "task_id": "task_x", "status": "queued", "estimated_seconds": null, "credits_cost": null }
  ],
  "total_credits_cost": null
}
```

**Batch or loop.** Use the batch route for N distinct payloads you want queued in
one round-trip. Use separate submissions when retries, cancels, or later
requests depend on earlier results.

---

## Generation Event Feed

```
GET /api/v2/projects/{project_id}/events
```

Returns terminal generation events for the project, newest first. The feed
tells a batch poller which tasks finished; the task itself stays the
authoritative record, so confirm each event with `tasks_get` or
`tasks_batch_get` before acting on it. For wake-ups without polling, use a
completion subscription (`SKILL.md` → "Completion subscriptions").

**Query parameters:**
- `since`: ISO timestamp; only events after this time
- `status`: `succeeded` or `failed`
- `generator`: `image`, `video`, `audio`, `music`, ...
- `task_id`: one task
- `limit`: events per page (default and maximum 200)
- `cursor`: from the previous response; page while `has_more` is true

**Example response:**
```json
{
  "events": [
    {
      "id": "evt_abc123",
      "event": "generation.succeeded",
      "task_id": "task_xyz123",
      "project_id": "project-1",
      "generator": "video",
      "mode": "ref_to_vid",
      "model": "<model_id>",
      "status": "succeeded",
      "asset_id": "asset_abc123",
      "asset_ids": ["asset_abc123"],
      "download_url": "/api/v2/projects/project-1/assets/asset_abc123/download",
      "created_at": "2026-03-30T14:22:03Z"
    }
  ],
  "cursor": "opaque-cursor",
  "has_more": false
}
```

**Useful filters:**
- `generator=video&status=succeeded`: completed videos only
- `generator=audio`: narration and TTS completions
- `task_id=$TASK_ID`: one job
- `cursor=$CURSOR`: a long feed page by page

For mixed image/video/audio/music batches, filter by `generator` rather than
scanning one mixed feed.

### Wait strategy

Typical time before the first check:
- Image: 15 seconds
- Video: 60 seconds, then every 30 seconds
- Audio: 10 seconds
- Music: 20 seconds
