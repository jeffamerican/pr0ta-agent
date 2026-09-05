"""Keep the packaged Codex connector aligned with its connection helper."""

import json
from pathlib import Path


class CodexConnectorConfig:
    REQUIRED_TOOLS = {
        "create_project", "list_projects", "generation_submit", "tasks_get",
        "post_sequence_get", "post_sequence_save", "post_render_start",
        "post_export_start", "assets_get_download_link", "review_submit_assets",
        "transcription_start", "transcription_get", "blender_job_submit",
        "world_generation_submit", "set_environment_collider_materialize",
    }

    def __init__(self, plugin: Path):
        self.plugin = plugin

    def synchronize(self) -> None:
        profile = json.loads(
            (self.plugin / "scripts/prep-production-tools.json").read_text()
        )
        if not isinstance(profile, list) or not all(
            isinstance(name, str) and name for name in profile
        ):
            raise ValueError("Codex tool profile must be a list of tool names")
        if len(profile) != len(set(profile)):
            raise ValueError("Codex tool profile contains duplicate names")
        missing = sorted(self.REQUIRED_TOOLS - set(profile))
        if missing:
            raise ValueError(f"Codex tool profile omits production tools: {missing}")
        path = self.plugin / ".mcp.json"
        payload = json.loads(path.read_text())
        connector = payload["mcpServers"]["pr0ta"]
        if set(connector.get("disabled_tools", [])) & set(profile):
            raise ValueError("Codex connector blocks tools required by its profile")
        connector["enabled_tools"] = profile
        path.write_text(json.dumps(payload, indent=2) + "\n")
