"""Unit tests for the public distribution updater."""

from __future__ import annotations

import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.sync_from_pr0ta import (
    safe_target,
    update_codex_metadata,
    version_key,
    write_archive,
)


class SyncFromPr0taTests(unittest.TestCase):
    def test_version_comparison_key(self) -> None:
        self.assertGreater(version_key("1.19.1513"), version_key("1.19.1512"))

    def test_source_target_cannot_escape_destination(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.assertEqual(
                safe_target(root, "pr0ta", "reference/api.md"),
                root.resolve() / "pr0ta" / "reference" / "api.md",
            )
            with self.assertRaises(ValueError):
                safe_target(root, "pr0ta", "../../private.txt")

    def test_codex_metadata_uses_public_distribution(self) -> None:
        payload = {"interface": {}}
        update_codex_metadata(payload, "5.22.0", "abc123")

        self.assertEqual(payload["version"], "5.22.0+codex.abc123")
        self.assertEqual(payload["repository"], "https://github.com/jeffamerican/pr0ta-agent")
        self.assertIn("protafilmmaker.com", payload["interface"]["websiteURL"])

    def test_archives_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            source.mkdir()
            (source / "manifest.json").write_text(json.dumps({"ok": True}))
            first = root / "first.zip"
            second = root / "second.zip"

            write_archive(first, source)
            write_archive(second, source)

            self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_archive_preserves_executable_scripts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            source.mkdir()
            helper = source / "connect.sh"
            helper.write_text("#!/bin/sh\n")
            helper.chmod(0o755)
            archive_path = root / "package.zip"

            write_archive(archive_path, source)

            with zipfile.ZipFile(archive_path) as archive:
                mode = archive.getinfo("connect.sh").external_attr >> 16
            self.assertEqual(mode, 0o755)


if __name__ == "__main__":
    unittest.main()
