"""Regressions for complete, reproducible Codex connector admission."""

import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from scripts.connector_config import CodexConnectorConfig
from scripts import sync_from_pr0ta


class ConnectorConfigTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.plugin = self.root / "plugins/pr0ta"
        (self.plugin / "scripts").mkdir(parents=True)
        self.profile = sorted(CodexConnectorConfig.REQUIRED_TOOLS)
        self.write_profile(self.profile)
        self.config = {"mcpServers": {"pr0ta": {
            "type": "http", "url": "https://app.pr0ta.com/api/mcp/mcp",
            "scopes": ["mcp"], "oauth_resource": "https://app.pr0ta.com/api/mcp/mcp",
            "enabled_tools": ["list_projects"],
        }}}
        self.write_config()

    def write_profile(self, names):
        (self.plugin / "scripts/prep-production-tools.json").write_text(json.dumps(names))

    def write_config(self):
        (self.plugin / ".mcp.json").write_text(json.dumps(self.config))

    def test_build_repairs_stale_allowlist_and_packages_exact_profile(self):
        with patch.object(sync_from_pr0ta, "ROOT", self.root):
            sync_from_pr0ta.build_archives()
        with zipfile.ZipFile(self.root / "dist/pr0ta-codex-plugin.zip") as archive:
            connector = json.loads(archive.read("pr0ta/.mcp.json"))["mcpServers"]["pr0ta"]
        self.assertEqual(connector["enabled_tools"], self.profile)
        for field in ("type", "url", "scopes", "oauth_resource"):
            self.assertEqual(connector[field], self.config["mcpServers"]["pr0ta"][field])

    def test_incomplete_profile_prevents_archive_build(self):
        self.write_profile(["list_projects"])
        with patch.object(sync_from_pr0ta, "ROOT", self.root):
            with self.assertRaisesRegex(ValueError, "omits production tools"):
                sync_from_pr0ta.build_archives()
        self.assertFalse((self.root / "dist").exists())

    def test_missing_completion_tool_prevents_publishing_an_unusable_connector(self):
        for name in ("tasks_subscribe", "tasks_watch", "tasks_completion_events",
                     "tasks_acknowledge", "tasks_unsubscribe"):
            with self.subTest(tool=name):
                self.write_profile([tool for tool in self.profile if tool != name])
                with self.assertRaisesRegex(ValueError, name):
                    CodexConnectorConfig(self.plugin).synchronize()

    def test_duplicate_and_malformed_profiles_are_rejected(self):
        for profile in (self.profile + self.profile, {}, [None]):
            with self.subTest(profile=profile):
                self.write_profile(profile)
                with self.assertRaises(ValueError):
                    CodexConnectorConfig(self.plugin).synchronize()

    def test_explicit_blocks_are_not_silently_overridden(self):
        self.config["mcpServers"]["pr0ta"]["disabled_tools"] = ["post_render_start"]
        self.write_config()
        with self.assertRaisesRegex(ValueError, "blocks tools"):
            CodexConnectorConfig(self.plugin).synchronize()

    def test_repeated_sync_is_stable(self):
        connector = CodexConnectorConfig(self.plugin)
        connector.synchronize()
        first = (self.plugin / ".mcp.json").read_bytes()
        connector.synchronize()
        self.assertEqual(first, (self.plugin / ".mcp.json").read_bytes())

    @staticmethod
    def manifest(profile):
        return {"skills_version": "6.24.2", "source_revision": "v6.24.2", "bundle_sha256": "a" * 64,
                "skills": [], "mcp_connector_tools": profile,
                "mcp_connector_tools_sha256": hashlib.sha256(json.dumps(profile).encode()).hexdigest()}

    def test_live_profile_admits_new_tools_and_preserves_oauth(self):
        profile = sorted(self.profile + ["review_note_status", "future_production_tool"])
        live = CodexConnectorConfig.from_manifest(self.manifest(profile))
        CodexConnectorConfig(self.plugin).synchronize(live)
        actual = json.loads((self.plugin / ".mcp.json").read_text())["mcpServers"]["pr0ta"]
        self.assertEqual(actual["enabled_tools"], profile)
        self.assertEqual(json.loads((self.plugin / "scripts/prep-production-tools.json").read_text()), profile)
        for field in ("type", "url", "scopes", "oauth_resource"):
            self.assertEqual(actual[field], self.config["mcpServers"]["pr0ta"][field])

    def test_missing_or_tampered_manifest_cannot_fall_back_to_stale_profile(self):
        original = (self.plugin / ".mcp.json").read_bytes()
        manifest = self.manifest(self.profile)
        invalid = [{}, {**manifest, "mcp_connector_tools": self.profile + ["review_note_status"]},
                   {**manifest, "mcp_connector_tools_sha256": "0" * 64}]
        for source in invalid:
            with self.subTest(source=source):
                with self.assertRaises(ValueError):
                    CodexConnectorConfig.from_manifest(source)
        self.assertEqual((self.plugin / ".mcp.json").read_bytes(), original)

    def test_new_live_tools_cannot_override_explicit_blocks(self):
        original = (self.plugin / "scripts/prep-production-tools.json").read_bytes()
        self.config["mcpServers"]["pr0ta"]["disabled_tools"] = ["review_note_status"]
        self.write_config()
        live = CodexConnectorConfig.from_manifest(self.manifest(self.profile + ["review_note_status"]))
        with self.assertRaisesRegex(ValueError, "blocks tools"):
            CodexConnectorConfig(self.plugin).synchronize(live)
        self.assertEqual((self.plugin / "scripts/prep-production-tools.json").read_bytes(), original)

    def test_unchanged_skill_release_repairs_and_versions_the_connector_once(self):
        manifest = self.manifest(sorted(self.profile + ["review_note_status"]))
        for path in (self.plugin / ".codex-plugin/plugin.json", self.root / "claude/.claude-plugin/plugin.json"):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"version": "6.24.2", "interface": {}}))
        (self.root / "release-manifest.json").write_text(json.dumps(manifest))
        with patch.object(sync_from_pr0ta, "ROOT", self.root), \
             patch.object(sync_from_pr0ta, "fetch_json", return_value=manifest), \
             patch.object(sync_from_pr0ta, "platform_is_compatible", return_value=True), \
             patch.object(sync_from_pr0ta, "stage_skills") as stage:
            self.assertTrue(sync_from_pr0ta.sync())
            first = json.loads((self.plugin / ".codex-plugin/plugin.json").read_text())["version"]
            self.assertNotEqual(first, "6.24.2")
            with zipfile.ZipFile(self.root / "dist/pr0ta-codex-plugin.zip") as archive:
                connector = json.loads(archive.read("pr0ta/.mcp.json"))["mcpServers"]["pr0ta"]
                self.assertEqual(connector["enabled_tools"], manifest["mcp_connector_tools"])
            self.assertFalse(sync_from_pr0ta.sync())
            manifest.update(self.manifest(sorted(manifest["mcp_connector_tools"] + ["another_future_tool"])))
            self.assertTrue(sync_from_pr0ta.sync())
            self.assertNotEqual(json.loads((self.plugin / ".codex-plugin/plugin.json").read_text())["version"], first)
            stage.assert_not_called()
