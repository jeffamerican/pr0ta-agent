# Completion notifications and owner fallback

Use completion subscriptions when a dependent workflow needs to resume after a
generation. A host receiver is required: skill text alone cannot wake a stopped
conversation. Without a configured receiver and host-resume integration, use
`tasks_get` / `tasks_batch_get`; do not claim push delivery is active.

For Codex, read [Codex receiver setup](codex-completion.md). A built-in adapter
uses `codex queue --thread <UUID>`; it does not require writing a resume command.
When asked to configure push delivery, perform that setup within the user's
authorized scope. A scheduled polling automation is a different mechanism;
do not substitute it and report webhook setup complete.

## Register the exact conversation

Call `tasks_subscribe` with `project_id` and `request`:

```json
{
  "client_id": "my-agent-host",
  "workflow_id": "scene-12-continuity-run-1",
  "thread_id": "host-conversation-id",
  "webhook_url": "https://my-receiver.example/completion",
  "webhook_secret": "a-random-secret-of-at-least-32-characters",
  "grace_seconds": 600,
  "task_ids": []
}
```

Provision a cryptographically random secret through the integration's secret
store. The destination must resolve to public HTTPS on port 443. Project edit
access is required. The subscription belongs to the authenticated user and this
immutable client/workflow/thread tuple; never use a current/global thread as the
destination. Identical registration retries return the same subscription.
Different settings for the same tuple return 409; use a new workflow ID.

Pass the returned `id` as `completion_subscription_id` on each `generation_submit`
request or item of `generation_batch_submit`. The public task annotation is
persisted and recovered by the notification worker. Preserve the subscription ID
when retrying an idempotent generation submission.

For other asynchronous tools or existing tasks, call `tasks_watch` with
`subscription_id` and `task_ids`. Registering after completion is safe: the worker
reads durable task state and catches up. Each task/subscription pair has one stable
event ID. Always retain generation receipts; subscriptions do not replace
submission idempotency or recovery after an interrupted provider submission.

## Delivery and handled acknowledgement

Events contain `schema_version`, `event_id`, `subscription_id`, `project_id`,
`task_id`, `task_type`, `client_id`, `workflow_id`, `thread_id`, `status`,
`asset_ids`, `task_url`, `completed_at`, `occurred_at`, and failure `error`.
Event names are `task.succeeded`, `task.failed`, and `task.cancelled`.
Success waits for persisted result references and referenced assets to be ready.
Obtain fresh delivery URLs through the asset API using the durable asset IDs.

1. Verify the signature and routing tuple, durably store the event, then return 2xx.
2. Hand the event to the exact bound conversation, deduplicating by `event_id`.
3. When that agent accepts responsibility, call `tasks_acknowledge` with
   `subscription_id`, `event_id`, `client_id`, `workflow_id`, and `thread_id`, under
   the same authenticated user/project.
4. Read the canonical task with `tasks_get`, assess its output, and continue only
   already-authorized work. Acknowledgement is not creative approval, asset
   selection, or authorization for additional paid work.

Do not acknowledge merely because a receiver stored the event. Do not wait until
a lengthy assessment finishes to acknowledge an accepted handoff.

Delivery retries until handled acknowledgement or subscription disablement. Delays
start at 60 seconds and back off to one hour. Retries keep the same event ID/body.
Treat delivery as at least once. `tasks_completion_events` supports recovery;
its cursor paginates one snapshot, not an incremental stream. Start without a
cursor on reconnection to include changed receipt states. Reading never acknowledges.

`tasks_unsubscribe` disables future delivery and pending escalation. A network
request already started may finish. Lost project access or account deactivation
also prevents further delivery.

## Owner email is an exception

The default grace period is 10 minutes from recording usable completion (range:
60 seconds to 24 hours). If the agent acknowledges before email dispatch, no email
is sent, including when the agent recovered through the API after webhook failure.

Otherwise PR0TA emails the current project owner's database email address with
project, task outcomes, and result links. No caller-supplied email is accepted.
Overdue events are grouped by project, up to 100 per email, with at least 15 minutes
between successful project emails. Each event is emailed once after confirmed SMTP
success; webhook retries continue. The message does not guess why the agent is away.

SMTP failures retry. A crash after SMTP acceptance but before database commit can
cause a duplicate on recovery. Routine retries and concurrent workers use durable
state and locks; this is not an exactly-once SMTP guarantee.

## Signature

Headers: `X-Pr0ta-Event`, `X-Pr0ta-Event-Id`, `X-Pr0ta-Timestamp` (Unix seconds),
and `X-Pr0ta-Signature` (`sha256=<hex>`). Compute HMAC-SHA256 with the subscription
secret over `<timestamp>.<raw HTTP body>` bytes. Compare in constant time, reject
timestamps outside your clock-skew window (the example uses five minutes), check
the complete routing tuple, and deduplicate `event_id`. Each retry has a fresh
signed timestamp. Legacy generation webhooks use a different signature contract.

## Receiver example

`completion-receiver.py` provides HTTPS-proxied intake and a durable SQLite inbox.
Run one worker per database, on persistent storage. The binding file is keyed by
the returned subscription ID:

```json
{
  "cs_returned_id": {
    "project_id": "project-uuid",
    "client_id": "my-agent-host",
    "workflow_id": "scene-12-continuity-run-1",
    "thread_id": "host-conversation-id",
    "secret_env": "PR0TA_COMPLETION_SECRET",
    "token_env": "PR0TA_PAT",
    "resume_command": ["/absolute/path/to/my-host-resume-adapter"]
  }
}
```

The adapter receives the event JSON on stdin and returns zero only after that
conversation durably accepts responsibility. If the host merely queues a message,
defer acknowledgement until pickup is confirmed. Deduplicate handoffs using
`event_id`, including a crash after host acceptance. Adapter failures leave the
event unacknowledged, allowing owner escalation.

There is no universal Codex/Claude/other-host resume command: configure the host's
supported mechanism explicitly. Never infer a thread from its project.

```bash
python completion-receiver.py --bindings bindings.json --database inbox.sqlite
```

Protect the binding file and environment secrets. The example listens on loopback
port 8765 at `/completion`; put it behind public HTTPS. It invokes only configured
argv, without a shell, and never executes commands from webhook payloads.

## REST equivalents

Base: `/api/v2/projects/{project_id}/completion-subscriptions`

| Operation | Route |
| --- | --- |
| Register | `POST {base}` with registration body |
| Watch | `POST {base}/{subscription_id}/tasks` with `task_ids` |
| Read | `GET {base}/{subscription_id}/events?cursor=...&limit=100` |
| Acknowledge | `POST {base}/{subscription_id}/events/{event_id}/acknowledge` with routing tuple |
| Disable | `DELETE {base}/{subscription_id}` |

Authenticate with PR0TA OAuth/PAT. Another project member cannot read or acknowledge
a subscription they did not create.
