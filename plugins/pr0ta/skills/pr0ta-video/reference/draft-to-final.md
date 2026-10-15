# Draft to Final

Some video models can render a cheap **draft** first and then **finish** that exact draft at full quality. The final keeps the draft's composition, motion, prompt, references, seed, duration and aspect ratio; only the resolution goes up. Use drafts to iterate on prompts and references at a fraction of the final cost, and pay the full rate only for shots someone has approved.

## Does the resolved model offer drafts?

Resolve the model the usual way (`models_preferred` for the shot's modality), then call `models_get_defaults` with that model id. If the response has a `draft_mode` block, the model supports drafts:

```json
"draft_mode": {
  "draft_resolution": "480p",
  "final_resolution": "1080p",
  "expires_after_days": 7,
  "unsupported_tasks": ["edit", "extend"],
  "draft_request": {"draft": true},
  "finalize_request": {"generator": "video", "mode": "finalize_draft", "draft_asset_id": "<draft video asset id>"}
}
```

No `draft_mode` block means no drafts: generate normally. Never send `draft: true` to a model without the block; the request is rejected with a 400.

## When to draft

Drafting is the default way to explore. On a model that offers drafts, draft first whenever any of these hold (the Video editor's Draft toggle likewise starts on for every draft-capable model, and the Production Queue drafts first on them):

- The shot is new, or its prompt or references changed since the last approved take.
- You expect more than one attempt (blocking, camera move, performance, continuity with neighbouring shots).
- The user wants to see options before spending on finals.

Generate the final directly, without a draft, when the shot is already approved in substance and one attempt will do, or when the task is a video **edit** or **extend** (drafts do not cover those).

Rule of thumb: a draft plus its final costs a little more than a single direct final, so drafting pays off as soon as a shot takes two or more attempts.

## Step 1: generate the draft

Send the normal generation request with `draft: true`. Everything else is the same as a normal request: prompt, references, duration, aspect ratio, seed.

```json
{
  "generator": "video",
  "mode": "ref_to_vid",
  "model": "<resolved model id>",
  "prompt": "...",
  "reference_image_asset_ids": ["..."],
  "duration": 5,
  "aspect_ratio": "16:9",
  "draft": true
}
```

- The platform renders at the model's `draft_resolution` (480p) regardless of any `resolution` you send.
- The resulting video asset is labelled `draft: true`, tagged `DRAFT`, and carries `draft_expires_at` (ISO time).
- Get the draft's asset id from the finished task's `result_refs.asset_id` (`tasks_get`).

## Step 2: review the draft

Treat a draft as a proposal, not a deliverable.

- Show it to the user, or check it against the shot's intent: framing, blocking, continuity with adjacent shots, performance, the reference identities.
- If it is wrong, change the prompt or references and make a **new draft**. Do not finish a draft you would not ship.
- Never finish a draft the user has not accepted when the user asked to review takes.
- Drafts are low resolution: judge composition, motion and performance, not fine texture or text legibility.

## Step 3: finish the approved draft

```json
{
  "generator": "video",
  "mode": "finalize_draft",
  "draft_asset_id": "<approved draft asset id>"
}
```

- Send nothing else about the shot. The final reuses the draft's model, prompt, references, seed, duration and aspect ratio. Sending `prompt`, `duration`, `aspect_ratio`, `seed`, `resolution` or any reference field is rejected with a 400. To change any of them, make a new draft.
- `model` is optional; if present it must match the draft's model.
- `output_format` may be set when the model's schema offers it (for example `mov`).
- The final renders at the model's `final_resolution` (1080p) and is labelled `finalized_from_draft_asset_id`.
- A draft is finished once, whichever path asks. A second finish request joins the one under way: its task comes back with `deduplicated: true` and `draft_finish: "rendering"`. If the final already exists, the response is `draft_finish: "finished"` with its `final_asset_id`. Neither is billed again.

## Finishing the cut

Drafts are for iterating; what ships is finished. Only the drafts that play in the final cut are finished; alternates and outtakes stay drafts.

- The project setting **Finish drafts at full quality** (Settings → General) is on by default; a mission can override it in its settings drawer. `post_drafts_list` reports it as `finish_drafts`.
- Before you present a cut as final, call `post_drafts_list(sequence_id)`. Each draft clip has a `state`: `to_finish` (with its `credits`), `rendering`, `finished` (a final exists but the cut still plays the draft) or `expired`. `credits` is the price of finishing every `to_finish` draft. `slow_motion` lists clips whose slow motion was made from a draft and is made again from its final, each with its price; `total_credits` is both together.
- Setting on, drafts remain: ask once for the whole cut. In a mission, save a checkpoint draft with `requires_review: true` and `finishes_drafts_in_sequence` set to the sequence id. The server lists and prices the drafts and titles the card "Finish N drafts at 1080p — X credits"; approving it finishes them and swaps each final into the cut in place. Its outcome is on the card as `finish_drafts_result`. Do not also call `post_drafts_finish`.
- Outside a mission, show the price and, once the user accepts, call `post_drafts_finish(sequence_id, confirm_credits)` with `total_credits`. Without `confirm_credits` at or above it, nothing runs and the quote comes back. The call returns once the finishes are submitted; finals already made are swapped in right after. Inside a mission the tool refuses: the card is the approval.
- Setting off: present the cut with the drafts it still plays listed. To have them finished, the user turns the setting on (for one mission, in its settings drawer).
- The swap keeps each clip's timing, in and out points, links and an approved cut's approval. Finals swap in as each render finishes. While the cut is open in the editor, the swap waits until it closes.
- The clip's production audio switches to the final's audio; the audio clip keeps its timing, in and out points, gain and links. Audio the user replaced stays. If the final's audio cannot be extracted yet, the draft's audio plays until it can (retried, the reason in the swap result).
- Slow motion made from the draft is made again from the final. Its price is in the card's or quote's total, and it is billed to the person who approved it, never above that price. It attaches when ready and the cut stays approved; if the cut is open in the editor then, it attaches once the editor closes. The swap result lists it under `slow_motion`.
- Drafts on hidden tracks are not in the cut.
- A draft already finished (by the Production Queue's Finish button, the Video editor or the expiry finish below) is swapped in without paying again.
- Expired drafts cannot be finished: make a new draft of that shot and replace the clip.

**Before expiry.** With the project setting on, the take selected for a shot in the Production Queue is finished automatically about a day before its draft expires, so its 1080p version is never lost. This follows the project setting only: a mission that keeps its drafts does not stop it. The person who made the draft is billed while still on the project, otherwise the project owner. A finish that cannot start or render (credits, provider) shows once as a failed task and is retried every few hours until the draft expires.

## Limits and errors

| Situation | Result |
|---|---|
| Model has no `draft_mode` | 400 on `draft: true`; generate normally |
| Draft of an edit or extend task | 400; generate without `draft` |
| Finish request resends shot fields | 400 naming the fields |
| Draft asset in another project or deleted | 404 |
| Asset is not a draft | 409 |
| Draft older than 7 days (`draft_expires_at` passed) | 410; make a new draft with the same prompt and references |

- The final is always the model's `final_resolution`; a draft cannot be finished at a different resolution. For other resolutions, generate directly.
- A draft can only be finished by the account that made it, within 7 days.
- The final matches the draft closely but is a new render: re-check it before delivery, especially faces and fine detail that 480p could not show.

## Costs

Pricing is per model; check the estimate the platform returns. As an order of magnitude, a draft costs the model's 480p rate and the final its 1080p rate for the same duration, so a 480p draft is roughly a fifth of the final's cost. Iterate at draft cost; spend the final rate once per approved shot.

## REST equivalents

The same requests go to `POST /api/v2/projects/{project_id}/generate`. The draft capability is also listed per model in `GET /api/v2/models` as `draft_mode`.
