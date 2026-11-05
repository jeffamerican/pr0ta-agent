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

## Assemble sequence-source Omni Reference chunks

For the [sequence-source Omni Reference workflow](route-selection.md#sequence-source-omni-reference), keep each contiguous source chunk's existing cuts. Do not materialize every occurrence as a new generated shot merely to use the per-shot workflow below. Track each chunk's original integer frame range and rational frame rate, and finish its accepted native draft through `pr0ta-video/reference/draft-to-final.md` before final delivery.

Before each submission, follow [Angle reference memory](#angle-reference-memory):
inspect the incoming coverage, retrieve both references for returning angles, and
retain the previous accepted video chunk as the separate continuity input within
the selected reference route's verified limits.

Place accepted chunks on the shared timeline using that source-frame mapping and the measured delivered media, retaining the original continuous recorded soundtrack. `video_chunks_assemble` can assemble chunks when its documented provenance/join contract applies (`pr0ta-video/SKILL.md`, "Duration and Shape"); inspect every join report. Independent contiguous source chunks do not imply a repeated opening: do not invent overlap trims, chain performance from a previous reverse, drop frames, or retime a mismatched output to conceal a shortfall. Surface any mismatch for the user's decision. Use the cut's native draft-finish approval path when drafts already occupy that cut, without also submitting individual finishes.

## Angle reference memory

For long hybrid sequences, keep two stills per established angle alongside the
previous accepted video chunk. A wide returning minutes after close-up coverage
needs its own set reference; the immediately preceding reverse cannot supply it.
This is an agent-managed workflow using existing frame and asset tools, not an
automatic sequence-service feature or a new API field.

**Identify the setup.** Scope each entry by project, sequence/scene, location,
coverage setup and continuity state. Record camera position/viewing direction,
framing or lens where known, and distinguishing landmarks; "wide" alone is not
an angle identity. Review proposed coverage matches visually. Reverses and
materially different viewpoints need their own entries. A deliberate change of
lighting, set dressing or location starts a new state, rather than overwriting
the old one. A moving shot remains one shot; an endpoint is only a reference for
the view it actually shows.

| Reference | Authority and update rule |
|---|---|
| Approved angle anchor | Fixed approved angle-matched plate or clear frame of an accepted hybridized result. Holds established geography, materials, lighting and style. Keep it until an explicit approved change; generated drift never replaces it. |
| Latest usable frame | Last clear frame of that angle/state in an accepted hybridized result. Carries its most recent visible appearance and compatible prop state. Replace this pointer only after the later result is reviewed and accepted. |
| Previous video chunk | Previous accepted hybridized chunk, or a short tail within the route's limits. Carries recent motion, visual rhythm and atmosphere across the join; it supplies no new action, dialogue, cuts or duration. |

**Before generating a chunk:**

1. Inspect all source shots in the incoming chunk, including brief returns and
   internal cuts. Match each returning angle to its setup and current state.
   Retrieve both its approved anchor and latest usable frame, even after minutes
   off-screen. If they are the same asset, attach it once and explain both roles.
   For a new angle, use approved set/appearance references and establish its
   anchor from an approved plate or accepted result; do not invent a match.
2. Submit through `generation_submit` with `generator: "video"`, `mode:
   "ref_to_vid"` and, for Seedance 2.5 Omni, `parameters.omni_reference_task_type:
   "reference"`. Do not send this packet through a Hybrid Studio edit operation.
   Attach the incoming source video, matching stills and, when one exists, the
   previous accepted video chunk (a bounded tail when necessary). Check live
   image/video counts and aggregate duration limits for the complete request. If the
   packet does not fit, shorten the continuity tail or use smaller contiguous
   source chunks without changing the edit. Surface unresolved limits rather
   than silently dropping an anchor or claiming an unattached reference.
   Preserve the requested multi-angle continuity coverage when budgeting a tail;
   allocate it before splitting incoming source, and strip only that derivative's
   audio. Read [reference packet checks](hybrid-reference-checks.md) for measured
   budgets, audio-stream verification and explicit coverage criteria.
3. Bind every attachment using the model's syntax and final attachment order.
   The incoming source owns current performance, blocking, camera, framing,
   timing and cuts. Name the angle and incoming shot/time range each still
   serves. The anchor owns the established environment; the latest frame adds
   only compatible recent state. Neither still imposes old actor poses or
   blocking. The previous video is continuity context, never footage to replay
   or prepend. Keep recorded dialogue/audio authoritative in Post. Read
   `pr0ta-prompting` → "Reference Binding Is a Submission Contract".
   For requested relighting, weather or element changes, explicitly name what
   the source lacks and the visible target (`route-selection.md` → "Explicit
   source-to-target changes"). Old angle references must not reinforce the source's
   deficient appearance or block an approved new continuity state.

**After reviewing and accepting the output:**

- Extract the last usable frame of **every angle occurrence** inside the chunk,
  just before its cut, not just the chunk's final frame. Use
  `post_frames_get(asset_id: <accepted output>, frames: [<frame index>], detail:
  "native")` for clean registered image assets; inspect the returned frames for
  errors. Choose an earlier clear frame within the same occurrence if the end
  is blurred, occluded, faded or a mixed transition. If none is usable, retain
  the existing reference. Use actual output frame indices after checking its
  mapping to the source; never assume identical timing from requested duration.
- Process occurrences chronologically: when the same angle returns several
  times, its last accepted usable occurrence becomes the latest pointer. Keep
  the anchor fixed, retain previous asset IDs for recovery, and record the
  output asset/revision, occurrence, frame index/timebase and reference roles.
  Completion alone, a rejected take, or an unresolved QC flag does not authorize
  updating references. Never use a future occurrence to guide an earlier chunk.
- Compare returning coverage against both stills and the source, then play the
  join. Check set geography, world-space light, props, faces and performance;
  explicitly check that the continuity video did not replay earlier gestures
  or dialogue. Resolve conflicting state against approved context and current
  source action, not by averaging references. Finish an accepted native draft
  through its native finish path without swapping its reference packet.

Keep references as project assets and record their roles/provenance in shared
asset notes and project memory so another agent can resume. The sequence manifest
remains the authority for cuts, coverage and states; do not add unsupported
fields or create a competing shot ledger.

Maintain a temporary frame folder with an index of the shared asset IDs and
setup/state keys. Keep the anchor and latest frame separately; replace the latest
file only after saving its new asset/provenance. This is a disposable cache of
shared records. Remove local copies after handoff/completion once shared assets
and decisions are verified; keep the approved project references.

**Route limits remain real.** This multi-video packet belongs to Omni Reference
sequence hybridization, not dedicated video-edit or Omni `edit` operations.
Those keep the source as their only video and use the angle stills where their
schemas allow; retain the previous chunk in the working collection without
attaching it as a second video. SwitchX accepts one look image: use the
appropriate approved angle plate, check against the latest frame, and retain its
existing continuous-shot reference chain. Do not send cuts or a multi-reference
packet into that chain. Explain an input limitation without changing the user's
chosen route.

## Prepare and establish per-shot continuity

Call `hybrid_sequences_job(sequence_id, request: {expected_revision,
 action: "prepare"})`. Poll the sequence. Each processable occurrence receives
its own materialized video asset and `shot_id`. The service leaves source-only
transition ranges untouched. Provider-sized chunks stay inside these individual
shots; never send the whole cut sequence into SwitchX's continuous reference chain.

Open a representative shot using its existing Hybrid Studio deep link and author
its angle-matched photographic background. Use the canonical environment for
geometry and approved plates for appearance. Every angle, reverses included,
must agree on light direction in world space, eyelines and prop placement.
Prepare any required per-shot matte or structure capture.

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

## Recheck missed cuts

Automatic cut ranges are proposals, not verified shots. Inspect source frames at
angle changes, including reverses that a low-contrast detector may miss. Before
shots are prepared, rerun `hybrid_sequences_job` on the same sequence with
`request: {"expected_revision": <current revision>, "action": "analyze", "threshold": 0.15}`.
The threshold accepts 0.05–0.9; lowering it proposes more boundaries and may also
find flashes or camera motion. Reanalysis resets cut review. Once shots are
prepared, adjust occurrence ranges explicitly so their existing work is retained.
Review exact source frames around each boundary before marking cuts reviewed.
