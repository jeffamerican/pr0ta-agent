---
name: pr0ta-operator
description: "Hand work to PR0TA's own Operator as a durable mission: long or many-step production goals (draft a screenplay from beats, prep a set of scenes, storyboard an act, generate and review a batch) that run inside the app with its permissions, credit budget, and approval stops. Read when delegating, running work unattended, or waiting on a mission."
---

# PR0TA Operator missions

PR0TA runs its own production agent, the Operator. A mission is a goal the
Operator works on durably inside the app: it plans, calls PR0TA's tools, waits
on tasks, delegates to department specialists, and stops when it needs the
user. It runs under the project's Operator permissions and credit limits, and
survives disconnects and restarts.

## When to delegate

Drive the tools yourself when the work is short and interactive: a few
generations, one scene, a conversation with the user about choices.

Start a mission when the goal is long, many-step, or should keep going without
you: drafting a screenplay from an approved beat sheet, prepping or
storyboarding a range of scenes, generating and curating a batch of shots.
The Operator has the app's tools except the chat-to-department ones, which it
replaces with its own delegation to department specialists; it also has the
project's memory and the owner's permission policy. You get a receipt when it
stops.

Do not start a mission to make a decision that belongs to the user. Missions
stop for approvals under the project's policy.

## Starting

`operator_mission_start(objective, title?, scene_numbers?, character?,
shot_number?, client_id?, completion_subscription_id?)` returns `mission_id`
and `receipt_task_id`.

- Write the objective as a brief: the outcome, the scope, what "done" means,
  and what to leave alone. Scope it with `scene_numbers`, `character` or
  `shot_number` when the work is bounded.
- Pass a stable `client_id` (your own idempotency key). A retry with the same
  key and the same title, objective and scope returns the same mission instead
  of starting another; the same key with a different title, objective or scope
  fails with `409`.

## Waiting: receipts

Every command that sets the mission working (start, send, resume, review)
returns a `receipt_task_id`. The receipt is an ordinary task that settles when
the mission next stops: done, idle (finished this turn, waiting for a follow-up),
review (an action or draft awaits approval), attention (an action's outcome is
uncertain), paused, failed, or cancelled. Wait on it like any task: poll
`tasks_get(receipt_task_id)` with backoff, or pass a `completion_subscription_id`
(from `tasks_subscribe`) when starting or sending, and your webhook fires when
it settles. The settled receipt's `result_refs` carry `mission_id`,
`mission_status`, `summary`, and an event `cursor`. A receipt still open 7 days
after it was issued expires as `failed` ("Receipt expired"); read the mission with
`operator_mission_get` instead of waiting on it.

## Reading

`operator_mission_get(mission_id, after?)` returns the mission: status, summary,
checkpoint (plan and draft artifacts), effects (actions it took or holds for
review), usage, and events after `after`: at most 200 per call, with
`has_more` true when more remain. Pass the returned `cursor` as `after` to read
the rest or only what is new. `operator_missions_list` lists your missions in
the project.

## Steering

`operator_mission_send(mission_id, text, mode?)`: `steer` changes the current
work, `follow_up` queues the next request after it. Each send returns a new
receipt.

`operator_mission_control(mission_id, action)`: `pause`, `resume`, `cancel`,
`archive`, `unarchive`. Resume returns a receipt.

## Approvals

A mission in `review` holds actions for approval: effects with status
`pending` in `operator_mission_get`. The project's Operator policy put them
there (credit spends, changes to shared work). Show the user what is held and
why; `operator_mission_review(mission_id, effect_id, decision)` approves or
rejects one, and only on the user's explicit decision. Draft artifacts marked
`requires_review` and actions in `attention` are resolved in the app (the
Operator page) by the user.

## Quality control

Every take a mission generates is reviewed automatically before the mission
continues, free of credits; the verdict is in the dependency results of its
checkpoint. The Operator regenerates a `fixable` take with the review's revised
prompt, at most twice per shot. A `fail` verdict, or a third failed attempt at
the same shot, saves a draft titled `QC: scene N shot M` with the takes as
evidence and puts the mission in `review`. Show the user that draft; they
answer it in the app (keep the best take, or give a direction).

## Costs and limits

The mission spends credits under the project's Operator policy and its own
allowance. Its `usage` in `operator_mission_get` reports what it spent. The
user changes permissions and allowances in the app.

