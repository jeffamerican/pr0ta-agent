# Hybrid sequences in Post

Use Post → Hybrid Production (`/hybrid?project=…`) for an edited sequence. The
single-shot editor and existing camera/set handoffs remain available. Sequence
records are shared by the UI, Operator, and MCP; do not keep a private parallel
shot ledger. Native NLE interchange is not implemented here: import an edited
project video, or use an independently prepared source and explicit frame cuts.

## Analyze and review

1. Read approved project/set/appearance context, then call
   `hybrid_sequences_create(request: {label, source_asset_id, threshold: 0.3})`.
   The source must be a ready project video. This starts non-generative media
   analysis. Read `hybrid_sequences_get(sequence_id)` until `active_task_id` is
   null; inspect `status` and `error`. Analysis failure is not an empty sequence.
2. Inspect the source and sampled contact sheets. Analysis proposes hard cuts and
   visual coverage groups; these are not calibrated camera solves or semantic
   continuity guarantees. Flashes, occlusions, pans, and similar actor poses can
   mislead either proposal. Review start, middle, and end of moving shots.
3. Correct the manifest with `hybrid_sequences_update(sequence_id, request:
   {expected_revision, changes: {label, occurrences, coverage, cuts_reviewed}})`.
   Occurrences cover `[0,total_frames)` contiguously, using integer, end-exclusive
   frame ranges and the returned rational `fps_num/fps_den`. No gaps, overlaps,
   silently dropped frames, or frame-rate reinterpretation are allowed.
4. Name coverage setups and set their `representative_id`. Assign each occurrence
   its `coverage_id` and `continuity_state` (for example, Door closed / Door open).
   Reverse coverage normally needs its own plate. A tighter lens or translated
   camera can share a setup but still need a separately authored background.
   Split/merge or reassign groups as necessary; set `cuts_reviewed: true` only
   after reviewing both cut boundaries and proposed coverage.
5. Flattened dissolves contain mixed source shots. Isolate those ranges with
   `treatment: "source"`, or obtain clean footage. Do not invent handles or claim
   transition reconstruction. A moving camera remains one uninterrupted shot;
   do not segment it merely because the framing changes.

## Prepare and establish continuity

Call `hybrid_sequences_job(sequence_id, request: {expected_revision,
 action: "prepare"})`. Poll the sequence. Each processable occurrence receives
its own materialized video asset and `shot_id`. The service leaves source-only
transition ranges untouched. Provider-sized chunks stay inside these individual
shots; never send the whole cut sequence into SwitchX's continuous reference chain.

Open a representative shot using its existing Hybrid Studio deep link and author
its angle-matched photographic background. Use the canonical environment for
geometry, approved plates for appearance, and world-space lighting direction for
reverse angles. Prepare any required per-shot matte or structure capture.

`hybrid_sequences_apply_setup` takes `expected_revision`, `coverage_id`,
`representative_revision`, explicit `occurrence_ids`, and `shot_revisions` keyed
by shot ID. It copies background/environment references, prompt, model, operation,
and settings to selected matching-continuity members atomically. It preserves each
camera and source, but clears masks/guides and current output selections. Rebuild
these for each member before generation. This operation is an explicit overwrite
of the selected members' setup: omit shot-specific exceptions. It does not modify
canonical sets or pretend to repaint other viewpoints after one inpaint.

## Generate and approve

Generate the representative using `hybrid_shot_generate` and review the actual
result. On explicit user approval, call `hybrid_sequences_approve(sequence_id,
request: {expected_revision, occurrence_id, shot_revision, asset_id})`. Only a
ready result from that current shot revision can be approved. Completion alone
never supplies approval.

Once the representative is approved, call `hybrid_sequences_generate` with
`request: {expected_revision, coverage_id, idempotency_key}`. This spends credits:
obtain generation authority first. It preflights every remaining applicable shot,
pins their revisions in a persisted batch, and dispatches each independently.
Only the representative's continuity state is included. Other states need their
own representative pass. Distinct camera/framing exceptions should be generated
individually with their own authored references.

A batch can partially submit before a provider failure. Inspect `items` and
`error`. Reuse the exact batch key to resume; do not mint new keys for retries.
Exception: `error_code: "batch_invalidated"` means the saved plan no longer
matches the reviewed edit. Review the current shots and start a replacement
batch with a new key. Missing/null error codes, transport failures, and temporary
processing or cut-review blocks retain the original key for retry.
`batches` on the sequence preserves plans across sessions. Use per-shot runs and
`tasks_get` for completion; group completion does not approve individual outputs.
Approve reviewed shot results individually. A later shot edit makes its prior
approval stale and blocks strict assembly until the new revision is reviewed.

## Reassemble and review

Call `hybrid_sequences_job` with `action: "assemble"`. The service validates
selected videos against the exact source frame count, rate, and dimensions,
reassembles editorial order, and uses the original sequence audio. A mismatch is
an error, never an implicit retime. No quality compositing or camera tracking is
performed by the application.

Strict assembly requires current approved results for every processable shot.
For a work-in-progress review only, explicitly pass `source_fallback: true` to
retain source where approval is absent/stale. The resulting asset records those
fallback occurrence IDs. Source-only transitions remain source in either mode.
`review_asset_id` and `review_revision` identify the assembled revision.

Review repeated coverage side by side, then play the original edit order. Check
landmarks, background scale, world-space light, eyelines, faces/hair, contact
shadows, and exposure across cuts. Preserve source timing/audio and record approved
continuity decisions in project memory. Do not call the sequence approved merely
because all isolated shots passed.

## API parity and conflicts

REST base: `/api/v2/projects/{project_id}/hybrid-sequences`. List/create use the
base; get/PATCH use `/{sequence_id}`; POST actions are `/jobs`, `/setup`, `/approve`,
and `/batch`, with the same request objects used by the tools. On 409, reread and
reconcile; never replay a stale whole manifest. Generic updates cannot forge shot,
result, thumbnail, or approval links. Changing a cut detaches affected prepared
shots and approvals while preserving earlier assets and shot history.
