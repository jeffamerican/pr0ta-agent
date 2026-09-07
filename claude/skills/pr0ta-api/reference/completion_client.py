"""Authenticated completion recovery for hosts whose MCP tool inventory is stale.

Requires requests. Prefer MCP tools when available. No token is printed or stored.
"""

import argparse
import json
import os
from pathlib import Path
import time
from urllib.parse import quote

import requests


class CompletionClient:
    def __init__(self, binding, subscription_id, token, session=None):
        self.binding = binding
        self.session = session or requests.Session()
        self.headers = {"Authorization": "Bearer " + token}
        parts = [quote(value, safe="") for value in (binding["project_id"], subscription_id)]
        self.base = f"https://app.pr0ta.com/api/v2/projects/{parts[0]}/completion-subscriptions/{parts[1]}"

    def execute(self, operation, *, event_id=None, task_ids=None):
        if os.environ.get("CODEX_THREAD_ID") != self.binding["thread_id"]:
            raise ValueError("Run completion recovery inside the bound Codex task")
        if operation == "acknowledge":
            if not event_id:
                raise ValueError("event_id is required")
            route = f"/events/{quote(event_id, safe='')}/acknowledge"
            body = {key: self.binding[key] for key in ("client_id", "workflow_id", "thread_id")}
            return self._request("POST", route, body)
        if operation == "watch":
            if not task_ids:
                raise ValueError("task_ids are required")
            return self._request("POST", "/tasks", {"task_ids": task_ids})
        if operation == "events":
            return self._request("GET", "/events")
        raise ValueError("Unsupported completion operation")

    def _request(self, method, route, body=None):
        response = self.session.request(method, self.base + route, json=body,
                                        headers=self.headers, timeout=30, allow_redirects=False)
        if not 200 <= response.status_code < 300:
            raise RuntimeError(f"PR0TA completion request failed (HTTP {response.status_code})")
        return response.json()


class CompletionCredentials:
    @staticmethod
    def load(token_env, codex_oauth):
        if not codex_oauth:
            return os.environ[token_env]
        # Explicit opt-in to Codex's existing file-backed OAuth store. Never refresh
        # or rewrite it here: the host owns refresh-token rotation and locking.
        root = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
        records = json.loads((root / ".credentials.json").read_text())
        matches = [record for record in records.values() if isinstance(record, dict)
                   and record.get("server_url") == "https://app.pr0ta.com/api/mcp/mcp"]
        if len(matches) != 1 or matches[0].get("expires_at", 0) <= time.time() * 1000:
            raise ValueError("Refresh the PR0TA MCP connection, or use a PAT; no current unique OAuth credential")
        return matches[0]["access_token"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bindings", required=True)
    parser.add_argument("--subscription", required=True)
    parser.add_argument("--token-env", default="PR0TA_PAT")
    parser.add_argument("--codex-oauth", action="store_true")
    parser.add_argument("operation", choices=["acknowledge", "watch", "events"])
    parser.add_argument("--event-id")
    parser.add_argument("--task-id", action="append")
    args = parser.parse_args()
    binding = json.loads(Path(args.bindings).read_text())[args.subscription]
    token = CompletionCredentials.load(args.token_env, args.codex_oauth)
    result = CompletionClient(binding, args.subscription, token).execute(
        args.operation, event_id=args.event_id, task_ids=args.task_id)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
