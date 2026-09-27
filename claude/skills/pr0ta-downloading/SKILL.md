---
name: pr0ta-downloading
description: "PR0TA asset download and export guide: download links, fetching and verifying bytes, bulk export, and tracing a file back to the prompt and model that made it. Read when downloading generated images, videos, or audio, exporting many assets, or tracking asset provenance."
---

# Downloading and Exporting Assets

A finished generation task names its outputs in `result.asset_id` and
`result.asset_ids` (`pr0ta-api` → "Task lifecycle"). To get the file, ask PR0TA
for a download link, then fetch the bytes from it.

## Download links

Call `assets_get_download_link` with the project and asset:

```json
{
  "project_id": "project-uuid-or-slug",
  "asset_id": "asset-uuid"
}
```

It returns an absolute, scoped URL for the asset that works without further
auth for a short time. For many assets, `assets_get_download_links` takes
`asset_ids` and returns one link each. Pass `as_attachment: true` for download
headers. `artifact` selects a secondary file where an asset has one (for
example a Marble world's SPZ, collider, or panorama). Find asset IDs with
`assets_list` (filter by `task_id`, `kind`, `category`, and more).


## Fetching the bytes

Fetch with `curl`:

```bash
curl -sSL --fail -o shot_03.mp4 "<url from assets_get_download_link>"
```

Project assets are private. Without a link, download directly with a bearer
token (PAT):

```bash
curl -sSL --fail "https://app.pr0ta.com/api/v2/projects/{project_id}/assets/{asset_id}/download" \
  -H "Authorization: Bearer $PR0TA_PAT" \
  -o shot_03.mp4
```

Direct REST downloads need that bearer token or a scoped `asset_token` URL from
an authenticated PR0TA handoff. Do not retry a bare project-asset URL after
HTTP 401. Add `?size=thumbnail` for a small variant.

From Python, run `curl` through `subprocess`. PR0TA's CDN can reject Python's
`urllib` with 403 because of its default user agent; `curl` passes.

```python
import subprocess
from pathlib import Path

def download(url: str, out_path: Path, pat: str | None = None) -> Path:
    cmd = ["curl", "-sSL", "--fail", "-o", str(out_path), "-w", "%{http_code}", url]
    if pat:
        cmd += ["-H", f"Authorization: Bearer {pat}"]
    status = subprocess.run(cmd, check=True, capture_output=True, text=True).stdout.strip()
    if status != "200" or out_path.stat().st_size == 0:
        raise RuntimeError(f"download not ready (HTTP {status}); retry or request a new link")
    return out_path
```

### Robustness

Check every file: HTTP status 200 and size greater than zero. A just-finished
asset can answer `202` with `{"status": "materializing"}` and `Retry-After`;
wait and fetch again (with `curl -o`, that small JSON body lands in your file,
so the status check matters). If a download link fails or has expired, request
a new one with `assets_get_download_link` instead of retrying the old URL.

## Bulk export

1. Collect the asset IDs: from your task results, or page through
   `assets_list` (REST `GET /api/v2/projects/{project_id}/assets`, iterating
   `offset` until `next_offset` is `null`).
2. Request links in batches with `assets_get_download_links`.
3. Fetch each file, check it as above, and name it from your ledger (next
   section) instead of the opaque asset ID.

REST routes for scripts:

| Route | Returns |
| --- | --- |
| `GET /api/v2/projects/{project_id}/assets` | Asset listing; `offset`, `limit`, `kind`, `category`, `source`, `task_id`, `sort`, `include_download`, `folder_path`, `recursive` |
| `GET /api/v2/projects/{project_id}/assets/{asset_id}/download-link` | A scoped download URL; `?as_attachment=true` |
| `GET /api/v2/projects/{project_id}/assets/{asset_id}/download` | The bytes |
| `GET /api/v2/projects/{project_id}/assets/{asset_id}/metadata` | Metadata including `generation_context` |
| `GET /api/v2/projects/{project_id}/assets/facets` | Facet counts for browsing |

Listing shape, paging, and uploads: `pr0ta-api` →
`reference/asset-management.md`. A Python client with a download helper:
`pr0ta-api` → `reference/python-client.py`.

## Provenance

Downloaded files have opaque names. Keep the answer to "which prompt made this
file?" one lookup away.

**Local `assets.json` ledger.** The `pr0ta` hub defines one production ledger
per job. It maps readable shot keys (`img_title`, `vid_newsroom_01`) to
`pr0ta_asset_id`, `local_path`, `source_prompt`, `model`, `used_in_shots`, and
editorial notes. Append to it right after each successful generation, not in a
batch at the end. It is the file you assemble the cut from and ship with the
export. Keep only this one local ledger.

**`generation_context` from PR0TA.** The asset's metadata
(`GET /api/v2/projects/{project_id}/assets/{asset_id}/metadata`) has a
`generation_context` block with `prompt`, `model`, `negative_prompt`, `seed`,
`task_id`, `submitted_at`, `completed_at`, and `status` when recoverable. Use it
whenever a ledger is missing or stale: any asset whose ID you know can be traced
back to the job that produced it.
