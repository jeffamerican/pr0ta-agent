"""Keep the packaged Codex connector aligned with its connection helper."""

import hashlib
import json
from pathlib import Path


class CodexConnectorConfig:
    REQUIRED_TOOLS = {
        "create_project", "list_projects", "generation_submit", "tasks_get",
        "post_sequence_get", "post_sequence_save", "post_render_start",
        "post_export_start", "assets_get_download_link", "review_submit_assets",
        "transcription_start", "transcription_get", "blender_job_submit",
        "world_generation_submit", "set_environment_collider_materialize",
        "tasks_subscribe", "tasks_watch", "tasks_completion_events",
        "tasks_acknowledge", "tasks_unsubscribe",
    }

    def __init__(self, plugin: Path):
        self.plugin = plugin

    @classmethod
    def validate_profile(cls, profile) -> list[str]:
        if not isinstance(profile, list) or not all(
            isinstance(name, str) and name for name in profile
        ):
            raise ValueError("Codex tool profile must be a list of tool names")
        if len(profile) != len(set(profile)):
            raise ValueError("Codex tool profile contains duplicate names")
        missing = sorted(cls.REQUIRED_TOOLS - set(profile))
        if missing:
            raise ValueError(f"Codex tool profile omits production tools: {missing}")
        return profile

    @classmethod
    def from_manifest(cls, manifest) -> list[str]:
        profile = cls.validate_profile(manifest.get("mcp_connector_tools"))
        digest = hashlib.sha256(json.dumps(profile).encode()).hexdigest()
        if digest != manifest.get("mcp_connector_tools_sha256"):
            raise ValueError("Live Codex tool profile checksum mismatch")
        return profile

    def synchronize(self, profile=None) -> bool:
        profile_path = self.plugin / "scripts/prep-production-tools.json"
        profile = self.validate_profile(
            json.loads(profile_path.read_text()) if profile is None else profile
        )
        path = self.plugin / ".mcp.json"
        payload = json.loads(path.read_text())
        connector = payload["mcpServers"]["pr0ta"]
        if set(connector.get("disabled_tools", [])) & set(profile):
            raise ValueError("Codex connector blocks tools required by its profile")
        connector["enabled_tools"] = profile
        updates = {path: payload, profile_path: profile}
        changed = False
        for target, value in updates.items():
            content = json.dumps(value, indent=2) + "\n"
            if target.read_text() != content:
                target.write_text(content)
                changed = True
        return changed
