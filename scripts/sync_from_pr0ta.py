"""Regenerate every public PR0TA skill distribution from the live manifest."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath
from collections.abc import Callable
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_URL = os.getenv(
    "PR0TA_SKILLS_MANIFEST_URL",
    "https://app.pr0ta.com/api/skills/manifest",
)
PLATFORM_VERSION_URL = "https://app.pr0ta.com/api/system-status/version"
SOURCE_BASE_URL = "https://app.pr0ta.com/api/skills/source"
SKILL_DESTINATIONS = (
    ROOT / "plugins" / "pr0ta" / "skills",
    ROOT / "claude" / "skills",
    ROOT / "universal" / "skills",
)


def fetch_json(url: str) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            payload = json.load(response)
    except (OSError, urllib.error.HTTPError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Could not read PR0TA release source: {url}") from error
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object from PR0TA release source: {url}")
    return payload


def fetch_document(skill: str, document: dict[str, str]) -> bytes:
    path = document["path"]
    url = "/".join(
        (
            SOURCE_BASE_URL,
            urllib.parse.quote(skill, safe=""),
            urllib.parse.quote(path, safe="/"),
        )
    )
    with urllib.request.urlopen(url, timeout=30) as response:
        content = response.read()
    digest = hashlib.sha256(content).hexdigest()
    if digest != document["sha256"]:
        raise ValueError(f"Digest mismatch for {skill}/{path}")
    return content


def version_key(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split(".") if part.isdigit())


def platform_is_compatible(manifest: dict[str, Any]) -> bool:
    platform = fetch_json(PLATFORM_VERSION_URL)
    if not platform:
        return False
    return version_key(platform.get("version", "0")) >= version_key(
        manifest.get("minimum_platform_version", "0")
    )


def stage_skills(manifest: dict[str, Any], destination: Path) -> None:
    for skill in manifest["skills"]:
        name = skill["name"]
        for document in skill["documents"]:
            target = safe_target(destination, name, document["path"])
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(fetch_document(name, document))


def safe_target(destination: Path, skill: str, document: str) -> Path:
    relative = PurePosixPath(skill) / PurePosixPath(document)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"Unsafe skill source path: {relative}")
    target = (destination / Path(*relative.parts)).resolve()
    if not target.is_relative_to(destination.resolve()):
        raise ValueError(f"Unsafe skill source path: {relative}")
    return target


def replace_skill_trees(source: Path) -> None:
    # Canonical skill prose is intentionally host-neutral. Host-specific MCP
    # helpers and manifests live alongside (not inside) these skill trees and
    # remain untouched by this replacement.
    for destination in SKILL_DESTINATIONS:
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(source, destination)


def update_json(path: Path, mutate: Callable[[dict[str, Any]], None]) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    mutate(payload)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def update_metadata(manifest: dict[str, Any]) -> None:
    version = manifest["skills_version"]
    revision = manifest.get("source_revision", "unknown")[:12]
    update_json(
        ROOT / "plugins/pr0ta/.codex-plugin/plugin.json",
        lambda payload: update_codex_metadata(payload, version, revision),
    )
    update_json(
        ROOT / "claude/.claude-plugin/plugin.json",
        lambda payload: payload.update({"version": version}),
    )


def update_codex_metadata(
    payload: dict[str, Any],
    version: str,
    revision: str,
) -> None:
    homepage = "https://www.protafilmmaker.com/downloads/skills/"
    repository = "https://github.com/jeffamerican/pr0ta-agent"
    payload.update(
        {
            "version": f"{version}+codex.{revision}",
            "homepage": homepage,
            "repository": repository,
        }
    )
    interface = payload.setdefault("interface", {})
    interface["websiteURL"] = homepage
    interface["privacyPolicyURL"] = f"{repository}/blob/main/PRIVACY-POLICY.md"


def write_archive(path: Path, source: Path, prefix: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for item in sorted(source.rglob("*")):
            if not item.is_file():
                continue
            relative = item.relative_to(source).as_posix()
            name = f"{prefix}/{relative}" if prefix else relative
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            mode = 0o755 if item.stat().st_mode & 0o111 else 0o644
            info.external_attr = mode << 16
            archive.writestr(info, item.read_bytes(), compress_type=zipfile.ZIP_DEFLATED)


def build_archives() -> None:
    destination = ROOT / "dist"
    write_archive(destination / "pr0ta.plugin", ROOT / "claude", "pr0ta")
    write_archive(destination / "pr0ta-skills.zip", ROOT / "universal")
    write_archive(destination / "pr0ta-codex-plugin.zip", ROOT / "plugins/pr0ta", "pr0ta")


def read_current_manifest() -> dict[str, Any]:
    path = ROOT / "release-manifest.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def sync() -> bool:
    manifest = fetch_json(MANIFEST_URL)
    if not platform_is_compatible(manifest):
        print("PR0TA platform has not reached the manifest's minimum version")
        build_archives()
        return False
    current = read_current_manifest()
    fields = ("skills_version", "bundle_sha256")
    changed = any(current.get(field) != manifest.get(field) for field in fields)
    if changed:
        with tempfile.TemporaryDirectory() as temporary:
            staged = Path(temporary) / "skills"
            stage_skills(manifest, staged)
            replace_skill_trees(staged)
        update_metadata(manifest)
        (ROOT / "release-manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n",
            encoding="utf-8",
        )
    build_archives()
    print("updated" if changed else "current")
    return changed


if __name__ == "__main__":
    sync()
