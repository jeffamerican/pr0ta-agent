# Asset Management

MCP: `assets_list`, `assets_get_download_link` (or `assets_get_download_links` for many), `assets_upload_start`, `assets_upload_batch_start`, `assets_upload_finalize`, `assets_annotations_update`, `assets_trim`. The REST routes below need a bearer token or, for downloads and thumbnails, a scoped `asset_token` URL.

## Listing and Reading Assets

### List Project Assets

```
GET /api/v2/projects/{project_id}/assets
```

Supported filters: `offset`, `limit`, `kind`, `type`, `category`, `source`, `subject`, `origin_system`, `ingest_channel`, `external_project_id`, `is_imported`, `music_only`, `folder_path`, `recursive`, `sort`, `sort_by=scene_shot_take`, `q`, `task_id`, `created_after`, `created_before`

**Important:** Response uses nested shape:
```json
{
  "assets": [
    {
      "asset": {
        "id": "c4f3bdf3-472a-4d6a-ad08-ea3872b8ed0c",
        "kind": "video",
        "category": "generated"
      },
      "download": {
        "url": "/api/v2/projects/project-1/assets/c4f3bdf3.../download"
      }
    }
  ]
}
```

Read the asset ID from `.assets[i].asset.id`, not `.assets[i].id`.

**Note on asset metadata:** Asset objects from the listing endpoint may return empty `prompt`, `model`, and `params` fields. To retrieve the original generation parameters for an asset, query the task metadata instead: `GET /api/tasks/{task_id}` → `metadata.provider_request.parameters`.

### ⚠️ Asset Listing Pagination — Always Iterate to Exhaustion

**Do not assume page 1 is exhaustive.** The listing paginates; a project with more assets than one page spans several, and an asset missing from page 1 may be on page 2.

**Canonical pagination contract for the project-scoped API:** offset-based with `next_offset`.

```
GET /api/v2/projects/{project_id}/assets?offset=0&limit=100
```

Response shape:

```json
{
  "assets": [ ... ],
  "next_offset": 100,
  "total": 247
}
```

- `assets` — the page of results
- `next_offset` — offset to pass on the next request; **`null` when the listing is exhausted**
- `total` — total count of assets matching the filters (useful for progress reporting)

**Rule:** When searching for a known asset ID or name, iterate until `next_offset` is `null` (or the returned page is empty) before concluding the asset doesn't exist. MCP `assets_list` pages the same way (`offset`, `limit`) and filters by `task_id`, `kind`, `category`, `reference_type`, `subject`, `q`, and more. It returns compact summaries with `next_offset` and `total` unless you pass `compact: false`; `total` is `null` only for a `browser_category` filter with more pages to go.

```python
import subprocess, json

def list_all_assets(project_id: str, pat: str, kind: str | None = None) -> list[dict]:
    """Iterate every page of the project-scoped asset listing until exhausted."""
    all_assets: list[dict] = []
    offset, limit = 0, 100
    while True:
        params = f"offset={offset}&limit={limit}" + (f"&kind={kind}" if kind else "")
        url = f"https://app.pr0ta.com/api/v2/projects/{project_id}/assets?{params}"
        resp = json.loads(subprocess.run(
            ["curl", "-sSL", "--fail", url, "-H", f"Authorization: Bearer {pat}"],
            check=True, capture_output=True, text=True,
        ).stdout)
        all_assets.extend(resp.get("assets", []))
        next_offset = resp.get("next_offset")
        if next_offset is None:
            break
        offset = next_offset
    return all_assets

def find_asset_by_name(project_id: str, pat: str, name: str) -> dict | None:
    for wrapper in list_all_assets(project_id, pat):
        a = wrapper.get("asset", {})
        if a.get("name") == name or a.get("display_name") == name:
            return a
    return None  # truly not in the project
```

**Tip:** For productions with many assets, keep a local `assets.json` map (see the `pr0ta` hub skill) so you do not re-iterate the listing for every lookup.

### Get One Asset

```
GET /api/v2/projects/{project_id}/assets/{asset_id}
```

Returns the canonical `AssetRead` object directly. The asset must belong to the project, and normal project authorization applies.

### Download Asset

```
GET /api/v2/projects/{project_id}/assets/{asset_id}/download
GET /api/v2/projects/{project_id}/assets/{asset_id}/download-link
```

`/download` returns the bytes for every asset type and needs project
authorization (bearer token or a scoped `asset_token` URL). A just-finished
task can precede object-store visibility: the route then returns `202`,
`Retry-After: 2`, and `{"status":"materializing"}`; retry the same URL after
the delay. `/download-link` (MCP `assets_get_download_link`) returns a
short-lived scoped URL; add `?as_attachment=true` for download headers.
Fetching bytes, verifying them, and bulk export: `pr0ta-downloading`.

### Get Asset Metadata and Thumbnail

```
GET /api/v2/projects/{project_id}/assets/{asset_id}/metadata
GET /api/v2/projects/{project_id}/assets/{asset_id}/thumbnail
```

Metadata includes `generation_context` (`prompt`, `model`, `negative_prompt`,
`seed`, `task_id`, `submitted_at`, `completed_at`, `status` when recoverable),
so any asset can be traced back to the job that produced it.

### Trim an Asset

```
POST /api/assets/{project}/trim
{"asset_id": "...", "asset_type": "audio" | "video", "in_point": 12.0, "out_point": 48.5,
 "idempotency_key"?: "...", "background"?: false}
```

MCP: `assets_trim`. A short trim answers `200 {success, asset}` with the new
asset. A trim estimated to take over ~60 s (long slices, 4K, HEVC/VP9), or one
sent with `background: true`, answers `202 {success, async: true, task_id,
status, deduplicated, idempotency_key, estimated_seconds, poll}`: poll
`GET /api/tasks/{task_id}` (MCP `tasks_get`) until it succeeds, then read
`result_refs.asset_id`. A retry of the same trim (same asset, points and
labels), or with the same `Idempotency-Key` header / `idempotency_key`, joins
the existing task (`deduplicated: true`) instead of trimming twice; a failed
attempt never blocks a retry.

### MCP Signed Upload Lifecycle

Use `assets_upload_start` or `assets_upload_batch_start` to create upload handoffs, then PUT bytes to each returned signed URL. For a single upload, supply a stable `idempotency_key` and reuse it after any ambiguous timeout; PR0TA returns the same placeholder instead of creating a duplicate. Supplying `checksum_sha256` at start binds that digest to finalization. After each PUT succeeds, call `assets_upload_finalize` and check that it returns `status: "ready"`.

Asset MCP timeouts return `retryable: true` with a `retry_token` (the upload-start token is the idempotency key). Retry unchanged requests with that token. `assets_list` uses a short database deadline, and `assets_get_download_link` returns a scoped proxy handoff without waiting for object-store signing.

Finalize each uploaded asset:

```json
{
  "tool": "assets_upload_finalize",
  "project_id": "project-id",
  "asset_id": "asset-id",
  "byte_size": 123456,
  "duration_ms": 12000
}
```

The start tools only create placeholders and signed upload URLs. Until `assets_upload_finalize` succeeds, uploaded assets remain in `uploading` status and may be absent from filtered `assets_list` results, normal project asset lists, and Asset Browser selectors. If you never call it, PR0TA finds the uploaded object and finalizes the asset within a few minutes; an asset whose object never arrives is marked failed once its upload URL has expired. `assets_probe` measuring a file does not mean the asset is ready. Finalize verifies object existence and any declared byte size/SHA-256 before transitioning the record to `ready`; integrity failures leave it non-ready. Successful finalization applies metadata/category/labels/folder updates and runs post-upload processing for media metadata and thumbnails.

---

## Batch Workflow Pattern

For multi-shot productions, avoid one polling loop per task.

1. Submit each generation with a stable `idempotency_key` and immediately
   persist `{scene_key, shot_key, task_id}` in your orchestration state.
2. Poll the tasks together with `tasks_batch_get` on a shared cadence, or read
   `GET /api/v2/projects/{project_id}/events` (page with `cursor`; `limit`
   defaults to and caps at 200) to learn which finished, then confirm each with
   the task. Task status is authoritative.
3. Attach `result.asset_id` / `result.asset_ids` back to your scene or shot
   keys.
4. For audits, list with `task_id=...`, `kind=video`, or
   `created_after` / `created_before` to separate the current run from earlier
   batches.

Minimal orchestration state example:
```json
{
  "scene_012_shot_03": {
    "task_id": "task_xyz123",
    "generator": "video",
    "mode": "ref_to_vid",
    "requested_asset_ids": ["c4f3bdf3-472a-4d6a-ad08-ea3872b8ed0c"],
    "completed_asset_id": null
  }
}
```

---
