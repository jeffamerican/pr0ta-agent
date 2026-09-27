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

Draft when the resolved model offers it and any of these hold:

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
- Use an `idempotency_key` so a retried finish is not billed twice.

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
