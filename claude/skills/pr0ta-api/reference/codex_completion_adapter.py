"""Queue verified completion receipts to an exact Codex task; never acknowledge pickup."""

import json
from pathlib import Path
import re
import subprocess
from uuid import UUID


class CodexCompletionAdapter:
    """Use the installed CLI's queue interface without changing task permissions."""

    def __init__(self, command=None, runner=subprocess.run):
        self.command = command or ["codex"]
        self.runner = runner
        if not isinstance(self.command, list) or not self.command or not all(
            isinstance(arg, str) and arg for arg in self.command
        ):
            raise ValueError("codex_command must be a nonempty argv list")

    def deliver(self, binding, event):
        thread_id = binding["thread_id"]
        if str(UUID(thread_id)) != thread_id:
            raise ValueError("Codex routing requires an exact task UUID, not a name")
        for key in ("project_id", "client_id", "workflow_id", "thread_id"):
            if event.get(key) != binding[key]:
                raise ValueError("Wrong conversation")
        result = self.runner(
            [*self.command, "queue", "--thread", thread_id, "--message", self.message(event, binding)],
            capture_output=True, text=True, timeout=25, check=True,
        )
        # Fail closed on unsupported CLI versions, including a zero-exit usage response.
        receipt = re.search(r"Queued message ([0-9a-f-]{36}) for thread ([0-9a-f-]{36})\.", result.stdout)
        if receipt is None or receipt.group(2) != thread_id:
            raise RuntimeError("Codex did not confirm an exact-task queue receipt")
        return False  # Queued is not handled. The receiving agent owns acknowledgement.

    @staticmethod
    def message(event, binding):
        receipt = {key: event[key] for key in (
            "event_id", "subscription_id", "project_id", "client_id", "workflow_id",
            "thread_id", "task_id", "status",
        )}
        guide = Path(__file__).resolve().with_name("task-completion.md")
        return (
            "PR0TA completion. Handle receipt using " + str(guide) + ".\n\n"
            + json.dumps(receipt, separators=(",", ":"), sort_keys=True)
        )
