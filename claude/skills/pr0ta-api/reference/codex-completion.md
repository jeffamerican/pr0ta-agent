# Codex completion receiver

The bundled `completion-receiver.py` and `codex_completion_adapter.py` support
Codex installations with `codex queue --thread <UUID> --message <TEXT>`.
Check the installed CLI with `codex queue --help`; older installations may lack
this command. Use the executable belonging to the same Codex installation and
user profile as the target task. Never use `--last`, a task name, or `exec resume`
as an implicit replacement for routing to the active desktop task.

## Configure once per machine, bind each workflow

1. Keep both Python files together in a persistent, user-private service directory.
   Check `tasks_subscribe`, `tasks_watch`, `tasks_completion_events`,
   `tasks_acknowledge`, and `tasks_unsubscribe` are exposed by the host. An older
   `enabled_tools` allowlist can hide them even after a skill update. Add these
   five names to that server's existing allowlist, preserving other tools, then
   reload the connection. Authenticated REST equivalents are in `task-completion.md`.
2. Run one receiver worker against a persistent SQLite inbox. Expose only its
   `/completion` route through stable public HTTPS (for example a dedicated
   Cloudflare Tunnel). Do not expose Codex itself. A temporary tunnel URL is a
   diagnostic option, not durable setup: subscriptions bind immutable URLs.
3. Register `tasks_subscribe` for the exact project, workflow, and Codex task UUID.
   Use a random signing secret held in the receiver's private environment. Start
   with `task_ids: []`, save the returned subscription binding below, and restart
   the receiver to load it before watching existing tasks or submitting new work.
4. Bind new generation requests with `completion_subscription_id`; use `tasks_watch`
   for already-submitted jobs and other async tools. Preserve the subscription in
   the workflow ledger. Separate projects/tasks get separate bindings and secrets.
5. Verify real completion delivery, exact-task pickup, and a committed PR0TA ACK.
   A receiver HTTP 200 or CLI queue receipt alone does not prove agent pickup.
   Only after this succeeds should an obsolete polling automation be disabled.

Example binding, keyed by the subscription ID returned by PR0TA:

```json
{
  "cs_returned_id": {
    "host": "codex",
    "codex_command": ["/absolute/path/to/codex"],
    "project_id": "project-uuid",
    "client_id": "codex-this-machine",
    "workflow_id": "this-production-workflow",
    "thread_id": "exact-codex-task-uuid",
    "secret_env": "PR0TA_COMPLETION_SECRET"
  }
}
```

```bash
python completion-receiver.py --bindings bindings.json --database inbox.sqlite
```

Use the OS service manager to restart both receiver and tunnel after failure and
login. Keep the service files, environment secrets, and inbox accessible only to
their owner. Configure executable paths explicitly; service-manager PATH differs
from the interactive terminal. Multiple workflows share the service, not routing
identities. Existing bindings must be preserved when adding a workflow.

## Pickup and outage behavior

The adapter validates the task UUID, queues a message with the immutable routing
receipt, and returns **queued**, not **handled**. The receiver records the queued
state and never acknowledges it on the agent's behalf. This mode needs no PR0TA
API token in the receiver. The task receiving the message calls `tasks_acknowledge`
using its authenticated PR0TA connection, then reads canonical task state and
continues already-authorized work. If acknowledgement is unavailable, report that
failure accurately; owner fallback remains active.

Normal webhook replays and receiver restarts do not queue a second message.
A crash after Codex accepts a message but before the local inbox commits can
repeat the handoff. The receiving task must deduplicate event/task IDs and retain
generation idempotency keys; queue delivery is not exactly once.

If the machine sleeps, loses connectivity, or the agent never processes the queued
message, no ACK is sent. PR0TA retains the completion and sends the owner email
after the configured grace. A locked screen alone does not establish agent failure.
On recovery, reconcile outstanding events using `tasks_completion_events` and
acknowledge actual pickup, including duplicates. Disabling a subscription stops
pending delivery and escalation; deleting a queued host message alone does not.

## Recovery with a stale tool inventory

`completion_client.py` provides `events`, `watch --task-id <id>` (repeatable), and
`acknowledge --event-id <id>` through the same REST API. It requires `requests`
and refuses calls unless `CODEX_THREAD_ID` matches the private binding. Use a PAT
from `PR0TA_PAT`, or explicitly opt into `--codex-oauth` for an installation using
Codex's file-backed PR0TA OAuth store. This mode reads the host's current token;
it never rotates credentials. If expired, first make a PR0TA MCP call to let the
host refresh its connection, then retry. Keyring-only installations should use
MCP or a PAT instead.

```bash
python completion_client.py --bindings bindings.json --subscription cs_returned_id \
  --codex-oauth acknowledge --event-id ce_returned_id
```

An optional `completion_client_command` argv in a Codex binding can point to this
script with an absolute Python path, `--bindings` path, and `--codex-oauth` (or
`--token-env`). The adapter includes a ready-to-run acknowledgement argv in the
queued message. The agent executes it on pickup; the receiver does not. Keep all
three Python files together when distributing the recovery option.
