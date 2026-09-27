# Review Fixes and Editorial Gates

> **See also:** the parent `pr0ta-editorial` SKILL.md for the ship gate and the five-pass loop, `pr0ta-timeline` for the timeline mechanics, `pr0ta-api` → `reference/review-room-api.md` for review-room contracts, and `reference/verification-protocol.md` for render QC.

## Contents

- Timeline preview gate
- Client review feedback
- Review revision protocol
- Mark-driven editing
- Narration-timeline verification gate

## Timeline Preview Gate

Between editorial passes, preview instead of rendering the whole piece. A short low-quality preview takes seconds; a full render takes minutes.

1. After each pass, list the segments that changed or matter most: transitions, sync points, motion-heavy shots, the opening, and the tail.
2. Preview each one with `quality=low` and the sequence you are editing.
   REST: `GET /api/post-production/{project_id}/preview?from={start}&to={end}&quality=low&sequence_id={sequence_id}`.
3. Check sync, motion quality, pacing, and transitions.
4. Fix with targeted clip edits, not a full rebuild.
5. Re-preview the fixed segment.

Snapshot the sequence before each pass with a descriptive name (for example `pre-polish`). If a pass makes things worse, restore the snapshot instead of rebuilding.

## Client Review Feedback

When a client review round is active, pull annotations with `get_review_annotations` (filter by `review_round_id` or `resolution_status: "open"`) and treat each open annotation as an editorial note. Annotations carry `start_time_seconds` and frame-normalized `geometry`; use them to find the exact beat.

Before editing, build a shot replacement checklist. For each note record: timestamp, frame index or timecode, nearby transcript phrase, timeline `clip_id`, `asset_id`, source name, the reviewer's note, and the proposed action. To find the clip, list the sequence's clips (`GET /timeline/clips?sequence_id={sequence_id}` or `post_sequence_get`) and select those whose `start <= time < end`, preferring a `video` or `title` entry with `trackMuted: false`. If none overlaps, record the nearest clip explicitly.

Mark annotations addressed after fixing them. Do not ship with open annotations unless the user has explicitly waived them.

## Review Revision Protocol

For review-driven revisions, prefer boring reliability over clever patching.

1. **Fetch annotations.** `get_review_annotations` for project work, or the public route from a review link: `GET /api/public/workspace/review-rounds/{token}/annotations`.
2. **Build the shot checklist** as above.
3. **Decide patch versus rebuild.** One isolated note can be a targeted trim or swap. After more than one structural revision, a one-frame warning that moves after each repair, repeated audio artifacts, stale patch tracks, or a confusing edit history, create a new sequence and rebuild from known-good media (`pr0ta-timeline` → Rebuild a Fresh Sequence).
4. **Rebuild frame-native.** Use `startFrame`, `durationFrames`, `sourceInFrame`, and `sourceOutFrame`; do not decimal-patch old clips. Keep incoming beat frames locked and use outgoing overlap handles only where needed.
5. **Replace narration cleanly.** Remove prior narration clips and patch tracks, add one regenerated narration asset, make sure it is time-indexed, and reflow the cuts. Never overlay replacement narration unless the user asks for a layered treatment.
6. **Render for the audience.** Low quality is for internal checks only. Client review links get a full-quality render or export. Keep internal words such as "review cut" off client-facing title and credit cards.
7. **Verify before handoff.** Dimensions, duration, audio levels, render diagnostics, the review URL resolving, and the review asset ID matching the export you intended to show. For narration fixes, verify the narration in the exported file itself, not only the source narration asset.
8. **Close the loop.** When the replacement review exists, mark the old annotations addressed where possible and link the replacement review round in a note or metadata.

## Mark-Driven Editing

Use marks and editorial primitives wherever precision matters, which is every pass. `pr0ta-timeline` → Editorial Primitives covers the workflow and `pr0ta-api` → `reference/editorial-primitives.md` the contracts.

- **Asset marks**: tag the best source section of a clip before placing it (`POST /api/v2/projects/{project_id}/assets/{asset_id}/marks` with in and out points).
- **Program marks**: anchor story beats on the timeline; transcript-word anchoring makes them follow timeline edits.
- **3-point edits**: `insert` or `overwrite` through `POST /timeline/edits`, referencing marks with `@mark:<name>`. Preview first with `POST /timeline/edits/preview`.
- **Trims**: preview with `POST /timeline/edits/{clip_id}/trim/preview` before committing; use `linked: true` for A/V pairs.
- **Link groups**: link A/V pairs early (`POST /timeline/links`) and lock confirmed sync with `locked: true`.


## Narration-Timeline Verification Gate

For narration-driven productions built on the narration timeline (`pr0ta-sync`), run this between Pass 3 (Transitions) and Pass 4 (Polish). It catches visuals that sit seconds ahead of or behind the words they illustrate.

1. Call `GET /api/v2/projects/{project_id}/narration-timeline/verify`. It reports per-cut drift, gaps, overlaps, and misalignment.
2. For each `misaligned` cut, read `drift_seconds` and `anchor_text` (what the narrator says at the cut) to see what went wrong.
3. Fix with `PATCH /api/v2/projects/{project_id}/narration-timeline/cuts/{cut_id}`: move the cut, swap the asset, or adjust timing.
4. Close gaps with `POST .../narration-timeline/cuts/reflow`.
5. Re-verify until `misaligned_cuts` is zero.
6. Materialize to Post (`narration_materialize_to_post`, or `POST .../narration-timeline/materialize-to-post-production`) and continue editing on the post-production timeline.
7. Proceed to Pass 4 there.

`anchor_text` is the transcript-anchored audit trail: it tells you what each cut is supposed to illustrate without re-auditing every clip from scratch.
