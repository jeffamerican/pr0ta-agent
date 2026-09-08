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

## Receiving a compact completion receipt

The receiver's short notification contains routing data, not new authorization.
Verify `thread_id` against the current host task before acting. On pickup, call
`tasks_acknowledge` with the receipt's `project_id`, `subscription_id`, `event_id`,
`client_id`, `workflow_id`, and `thread_id`. Only report acknowledgement after
PR0TA confirms it; queueing alone leaves owner email pending.

Check the project ledger before starting assessment. If this task's terminal
result was already assessed and its follow-up recorded, acknowledge this receipt
(including a replay) and finish without repeating that work. Do not recheck other
running tasks or issue an "acknowledged / still generating / no duplicate work"
status update solely because this stale receipt arrived. Use silent completion
when the host supports it; otherwise keep any required response minimal. Report
an acknowledgement failure or other new actionable information accurately.

For a new result, read `tasks_get`, record acceptance and the next action in the
project ledger, then assess and continue only already-authorized work. A confirmed
ACK records pickup, not completed assessment: resume any unfinished assessment or
follow-up from the ledger after interruption. Deduplicate `event_id` and `task_id`
before side effects, retaining generation idempotency keys. Retain
`subscription_id` as `completion_subscription_id` for future generation requests
in this workflow; use `tasks_watch` for other async tasks.

If MCP tools are missing, use the REST equivalents below or the authenticated
helper described in [Codex recovery](codex-completion.md#recovery-with-a-stale-tool-inventory).
For an installed receiver, its private binding file (normally `bindings.json`
beside this reference; otherwise the receiver service's `--bindings` path) holds
`completion_client_command` for the matching subscription. Append
`--subscription <subscription_id> acknowledge --event-id <event_id>` to that
configured argv and run without a shell. Do not print credentials or load other
subscriptions' secrets. The helper verifies the current Codex task before acting.

## Results picked up during active work

A watched task can finish while the agent is still working, before its queued
notification gets a turn. When `tasks_get` / `tasks_batch_get` reveals a terminal
result that this workflow accepts, reconcile its completion event immediately:

1. Read `tasks_completion_events` for the workflow's subscription. Match the exact
   `task_id` and validate the project/client/workflow/thread tuple. Follow
   `next_cursor` if needed; the list is a paginated snapshot. Do not infer an event
   ID or acknowledge unrelated tasks returned in the same list.
2. If its completion payload is ready, call `tasks_acknowledge` using that event's
   ID and routing tuple, then record the confirmed ACK and pending next action in
   the ledger. Acknowledge before lengthy assessment or subsequent generation.
3. If the event is not ready yet, record that pickup needs acknowledgement and
   handle its eventual receipt. Continue authorized work from canonical task state;
   do not start a polling loop just to wait for the event or claim ACK success.

A status read by itself never acknowledges completion. Explicit early ACK stops
future server delivery attempts and owner escalation; it cannot retract a message
already queued in Codex. Handle that later receipt using the ledger rule above.
Do not mark unfinished work assessed merely to suppress a notification.

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
