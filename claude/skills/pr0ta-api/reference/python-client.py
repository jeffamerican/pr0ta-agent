#!/usr/bin/env python3
"""
PR0TA Minimal Python REST Client
================================

A starting point for Python automation against the PR0TA REST API. Agents
with the PR0TA MCP connector should prefer its tools; use this for standalone
scripts.

Core functions:
  - preferred_model()     GET /api/v2/models/preferred for one modality
  - submit_generation()   unified /generate; resolves the model when not given
  - poll_task()           project-scoped polling; raises on failure
  - download_asset()      curl download with status and size checks
  - upload_images()       multipart image upload into a project
  - list_assets()         offset/next_offset asset paging

Setup:
  pip install requests
  export PR0TA_PAT="pat_..."
  export PR0TA_PROJECT_ID="your-project-uuid-or-slug"
  python python-client.py                  # one image with the preferred model
  python python-client.py MODEL_ID [...]   # compare explicit model ids

Model choice belongs to the platform: the user's Settings -> Tools default,
else the admin's pinned model for the modality. When nothing resolves, pick a
model from GET /api/v2/models (or MCP models_list with modality=...) and pass
it explicitly.

Rate limits are per user per minute by tier (see the pr0ta-api skill); this
client polls every 2 seconds and does not retry validation errors.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

import requests  # pip install requests

BASE_URL = "https://app.pr0ta.com"
TERMINAL_STATUSES = {"succeeded", "completed", "failed", "error", "cancelled", "canceled"}


class PR0TAError(RuntimeError):
    pass


def _pat() -> str:
    try:
        return os.environ["PR0TA_PAT"]
    except KeyError as exc:
        raise PR0TAError("Set PR0TA_PAT to a personal access token (pat_...)") from exc


def _headers(json_body: bool = True) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {_pat()}"}
    if json_body:
        headers["Content-Type"] = "application/json"
    return headers


def preferred_model(modality: str) -> str | None:
    """Return the model id PR0TA resolves for ``modality``, or None when nothing is set or pinned.

    Modality keys include image_model, image_edit_model, reference_to_video_model,
    video_model, video_edit_model, video_extend_model, dialogue_model,
    music_model, and sfx_model.
    """
    r = requests.get(
        f"{BASE_URL}/api/v2/models/preferred",
        headers=_headers(json_body=False),
        params={"modality": modality},
        timeout=30,
    )
    if r.status_code == 400:
        raise PR0TAError(f"Unknown modality {modality!r}: {r.text}")
    r.raise_for_status()
    entry = (r.json().get("modalities") or {}).get(modality) or {}
    return entry.get("model_id")


def submit_generation(
    project_id: str,
    payload: dict[str, Any],
    *,
    modality: str | None = None,
    idempotency_key: str | None = None,
) -> str:
    """Submit one unified generation request and return its task_id.

    ``payload["model"]`` wins when present. Otherwise ``modality`` is resolved
    with preferred_model(); a request with neither is rejected here rather than
    left for the server to guess. Reuse the same ``idempotency_key`` when
    retrying one logical generation after a timeout.
    """
    body = dict(payload)
    if not body.get("model"):
        if not modality:
            raise PR0TAError("Pass payload['model'] or a modality to resolve it from.")
        model = preferred_model(modality)
        if not model:
            raise PR0TAError(
                f"No model is set or pinned for {modality}. Choose one from "
                f"GET /api/v2/models and pass it as payload['model']."
            )
        body["model"] = model
    body.setdefault("idempotency_key", idempotency_key or f"client-{uuid.uuid4()}")

    r = requests.post(
        f"{BASE_URL}/api/v2/projects/{project_id}/generate",
        headers=_headers(),
        json=body,
        timeout=60,
    )
    data = r.json() if r.content else {}
    if r.status_code >= 400:
        detail = data.get("detail") if isinstance(data, dict) else data
        raise PR0TAError(
            f"Generation rejected (HTTP {r.status_code}): {json.dumps(detail, indent=2)}\n"
            f"Payload: {json.dumps(body, indent=2)}"
        )
    task_id = data.get("task_id")
    if not task_id:
        raise PR0TAError(f"No task_id in response: {json.dumps(data, indent=2)}")
    return task_id


def poll_task(project_id: str, task_id: str, *, timeout_s: int = 1200, interval_s: float = 2.0) -> dict[str, Any]:
    """Poll until the task is terminal. Returns the task; raises on failure or timeout.

    Read outputs from ``task["result"]`` (asset_id, asset_ids, download_url).
    Stalled tasks are not recovered by PR0TA: if ``progress`` stops moving for
    several minutes, cancel with POST .../tasks/{task_id}/cancel and decide
    whether to resubmit.
    """
    url = f"{BASE_URL}/api/v2/projects/{project_id}/tasks/{task_id}"
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        r = requests.get(url, headers=_headers(json_body=False), timeout=30)
        r.raise_for_status()
        task = r.json()
        status = task.get("status")
        if status in TERMINAL_STATUSES:
            if status in {"failed", "error"}:
                raise PR0TAError(
                    f"Task {task_id} failed ({task.get('error_reason', 'unknown')}): "
                    f"{task.get('error', 'no message')}\n"
                    f"error_detail: {json.dumps(task.get('error_detail') or {}, indent=2)}"
                )
            return task
        time.sleep(interval_s)
    raise PR0TAError(f"Task {task_id} did not finish within {timeout_s}s")


def download_asset(project_id: str, asset_id: str, out_path: Path, *, attempts: int = 5) -> Path:
    """Download an asset with curl and verify it.

    curl is used because PR0TA's CDN can reject Python urllib's default user
    agent. A just-finished asset may answer 202 "materializing"; that is
    retried after a short wait. The file must come back as HTTP 200 and be
    larger than zero bytes.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    url = f"{BASE_URL}/api/v2/projects/{project_id}/assets/{asset_id}/download"
    status = ""
    for _ in range(attempts):
        result = subprocess.run(
            ["curl", "-sSL", "-o", str(out_path), "-w", "%{http_code}",
             "-H", f"Authorization: Bearer {_pat()}", url],
            check=True, capture_output=True, text=True,
        )
        status = result.stdout.strip()
        if status == "200" and out_path.stat().st_size > 0:
            return out_path
        if status != "202":
            break
        time.sleep(2)
    raise PR0TAError(f"Download of asset {asset_id} failed (HTTP {status}); request a fresh link and retry")


def upload_images(
    project_id: str,
    paths: list[str | Path],
    *,
    category: str = "imported",
    subject: str | None = None,
    labels: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Upload local images; returns the created assets. Their ids work in generation payloads."""
    data: dict[str, str] = {"category": category}
    if subject:
        data["subject"] = subject
    if labels:
        data["labels"] = json.dumps(labels)
    handles = [open(p, "rb") for p in paths]
    try:
        files = [("files", (Path(p).name, h)) for p, h in zip(paths, handles)]  # field name is "files"
        r = requests.post(
            f"{BASE_URL}/api/v2/projects/{project_id}/assets/upload",
            headers=_headers(json_body=False), files=files, data=data, timeout=120,
        )
    finally:
        for h in handles:
            h.close()
    r.raise_for_status()
    return r.json().get("assets", [])


def list_assets(project_id: str, *, kind: str | None = None, task_id: str | None = None) -> list[dict[str, Any]]:
    """List every asset, following offset/next_offset until it is null.

    Each item is the listing's wrapper; the asset id is item["asset"]["id"].
    """
    params: dict[str, Any] = {"limit": 100, "offset": 0}
    if kind:
        params["kind"] = kind
    if task_id:
        params["task_id"] = task_id
    out: list[dict[str, Any]] = []
    while True:
        r = requests.get(
            f"{BASE_URL}/api/v2/projects/{project_id}/assets",
            headers=_headers(json_body=False), params=params, timeout=30,
        )
        r.raise_for_status()
        body = r.json()
        out.extend(body.get("assets", []))
        if body.get("next_offset") is None:
            return out
        params["offset"] = body["next_offset"]


# Example: one prompt on the preferred image model, or a side-by-side of the
# model ids given on the command line. For many payloads in one request, the
# batch route POST /api/v2/projects/{project_id}/generate/batch takes up to 10.
if __name__ == "__main__":
    project = os.environ["PR0TA_PROJECT_ID"]
    prompt = (
        "Flat vector poster on deep navy. Line 1 (small white caps): EXAMPLE HEADER. "
        "Line 2 (huge bold amber-gold): EXAMPLE TITLE. No other text."
    )
    candidates: list[str | None] = list(sys.argv[1:]) or [None]

    tasks: dict[str, str] = {}
    for model_id in candidates:
        request: dict[str, Any] = {
            "generator": "image",
            "mode": "txt_to_img",
            "prompt": prompt,
            "aspect_ratio": "9:16",
        }
        if model_id:
            request["model"] = model_id
        label = model_id or "preferred"
        try:
            tasks[label] = submit_generation(project, request, modality="image_model")
        except PR0TAError as exc:
            print(f"[WARN] {label}: {exc}")

    for label, task_id in tasks.items():
        finished = poll_task(project, task_id)
        asset_id = (finished.get("result") or {}).get("asset_id")
        if asset_id:
            safe = label.replace("/", "_")
            print(download_asset(project, asset_id, Path(f"out/{safe}.png")))
