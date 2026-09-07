"""Durable webhook receiver. Put behind HTTPS; configure an explicit host adapter.

Run: python completion-receiver.py --bindings bindings.json --database inbox.sqlite
Bindings are keyed by subscription_id and contain project_id, client_id,
workflow_id, thread_id, secret_env, token_env, and resume_command (an argv list).
The configured command receives the event on stdin. Exit zero ONLY after the
exact thread has durably accepted responsibility; use event_id for deduplication.
"""

import argparse
from contextlib import contextmanager
import hashlib
import hmac
import json
import logging
import os
import sqlite3
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen


class CompletionReceiver:
    def __init__(self, database, bindings, *, clock=time.time, resume=None, acknowledge=None):
        self.database, self.bindings, self.clock = database, bindings, clock
        self.resume = resume or self._resume
        self.acknowledge = acknowledge or self._acknowledge
        with self.connect() as connection:
            connection.execute("""CREATE TABLE IF NOT EXISTS inbox (
                event_id TEXT PRIMARY KEY, payload TEXT NOT NULL,
                handled INTEGER NOT NULL DEFAULT 0, acknowledged INTEGER NOT NULL DEFAULT 0,
                next_attempt REAL NOT NULL DEFAULT 0
            )""")

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.database, timeout=30)
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def accept(self, body, headers):
        payload = json.loads(body)
        binding = self.bindings[payload["subscription_id"]]
        timestamp = headers["X-Pr0ta-Timestamp"]
        if abs(self.clock() - int(timestamp)) > 300:
            raise ValueError("Expired signature")
        secret = os.environ[binding["secret_env"]]
        expected = "sha256=" + hmac.new(secret.encode(), timestamp.encode() + b"." + body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, headers["X-Pr0ta-Signature"]):
            raise ValueError("Invalid signature")
        if any(payload.get(key) != binding[key] for key in ("project_id", "client_id", "workflow_id", "thread_id")):
            raise ValueError("Wrong conversation")
        if headers["X-Pr0ta-Event-Id"] != payload["event_id"] or payload.get("schema_version") != 1:
            raise ValueError("Invalid event")
        canonical = json.dumps(payload, sort_keys=True)
        with self.connect() as connection:
            connection.execute("INSERT OR IGNORE INTO inbox(event_id,payload) VALUES (?,?)", (payload["event_id"], canonical))
            stored = connection.execute("SELECT payload FROM inbox WHERE event_id=?", (payload["event_id"],)).fetchone()[0]
            if stored != canonical:
                raise ValueError("Conflicting event replay")

    def drain_once(self):
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT event_id,payload,handled FROM inbox WHERE acknowledged=0 AND next_attempt<=? LIMIT 100",
                (self.clock(),),
            ).fetchall()
        for event_id, raw, handled in rows:
            payload = json.loads(raw)
            try:
                binding = self.bindings[payload["subscription_id"]]
                if not handled:
                    self.resume(binding, payload)
                    self._update(event_id, handled=1)
                self.acknowledge(binding, payload)
                self._update(event_id, acknowledged=1)
            except Exception:
                self._update(event_id, next_attempt=self.clock() + 30)

    def _update(self, event_id, **fields):
        allowed = {"handled", "acknowledged", "next_attempt"}
        if not set(fields) <= allowed:
            raise ValueError("Invalid state field")
        assignments = ",".join(f"{key}=?" for key in fields)
        with self.connect() as connection:
            connection.execute(f"UPDATE inbox SET {assignments} WHERE event_id=?", (*fields.values(), event_id))

    @staticmethod
    def _resume(binding, payload):
        command = binding["resume_command"]
        if not isinstance(command, list) or not command or not all(isinstance(arg, str) for arg in command):
            raise ValueError("Configure resume_command as an argv list")
        # A command from local configuration, never from a webhook. No shell.
        subprocess.run(command, input=json.dumps(payload), text=True, check=True, timeout=30)

    @staticmethod
    def _acknowledge(binding, payload):
        from urllib.parse import quote
        parts = [quote(payload[key], safe="") for key in ("project_id", "subscription_id", "event_id")]
        url = f"https://app.pr0ta.com/api/v2/projects/{parts[0]}/completion-subscriptions/{parts[1]}/events/{parts[2]}/acknowledge"
        body = json.dumps({key: binding[key] for key in ("client_id", "workflow_id", "thread_id")}).encode()
        request = Request(url, data=body, headers={
            "Authorization": "Bearer " + os.environ[binding["token_env"]], "Content-Type": "application/json",
        })
        with urlopen(request, timeout=15) as response:
            if response.status != 200:
                raise ValueError("Acknowledgement failed")


class ReceiverServer:
    def __init__(self, receiver, host, port):
        self.receiver = receiver
        self.stop = threading.Event()
        self.server = ThreadingHTTPServer((host, port), self._handler(receiver))

    @staticmethod
    def _handler(receiver):
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                    if self.path != "/completion" or not 0 < length <= 65536:
                        raise ValueError("Invalid request")
                    self.connection.settimeout(10)
                    receiver.accept(self.rfile.read(length), self.headers)
                except Exception:
                    self.send_response(400)
                else:
                    # A receipt only: the separate worker must hand it to the agent.
                    self.send_response(200)
                self.end_headers()

            def log_message(self, *args):
                pass
        return Handler

    def run(self):
        worker = threading.Thread(target=self._work, daemon=True)
        worker.start()
        try:
            self.server.serve_forever()
        finally:
            self.stop.set()
            self.server.server_close()
            worker.join(timeout=50)

    def _work(self):
        while not self.stop.is_set():
            try:
                self.receiver.drain_once()
            except Exception:
                logging.getLogger(__name__).exception("Completion inbox unavailable; retrying")
            self.stop.wait(2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bindings", required=True)
    parser.add_argument("--database", required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    arguments = parser.parse_args()
    with open(arguments.bindings) as stream:
        receiver = CompletionReceiver(arguments.database, json.load(stream))
    ReceiverServer(receiver, arguments.host, arguments.port).run()
