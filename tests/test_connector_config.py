"""Regressions for complete, reproducible Codex connector admission."""

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
