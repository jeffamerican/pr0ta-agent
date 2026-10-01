---
name: pr0ta-timeline
description: "PR0TA post-production timeline: sequences and tracks, clip editing, Ken Burns, audio mix and ducking, transitions, frame-accurate cuts, marks, 3-point edits, trims, link groups, snapshots, preview, render diagnostics, source shortfalls and fitToFill, narration materialization, and final export. Read when assembling, editing, mixing, previewing, or exporting a cut."
---

# Post-Production Timeline

The post-production timeline is PR0TA's editing surface. It is persistent, shared state: agents edit it through tools and the API, and the user opens the same sequence in the browser to scrub, reorder, trim, and approve. Every edit persists; a one-shot fix is one call, not a rebuild. Assemble, mix, preview, and render here. If the timeline lacks something a production needs, report it (`bug_report_create`) rather than building a parallel local pipeline.

This is **not** the narration timeline. The narration timeline is a transcript-anchored cut list (`pr0ta-sync`); once its cuts verify, you materialize them into a post-production sequence and edit here.

This skill owns the workflow. Field-level contracts live in `pr0ta-api` → `reference/timeline-api.md`, `reference/editorial-primitives.md`, `reference/asset-tags-and-analysis.md`, and `reference/source-shortfalls-and-fit-to-fill.md`. Editorial judgment (what to cut, when it ships) lives in `pr0ta-editorial`.

Before assembly or a major pass, call `memory_context_pack` with a `task_intent` and the sequence, scene, or task `scope`; use approved memory for continuity, client notes, style, pacing, and asset decisions, and surface conflicts before mutating the timeline. After a meaningful edit decision, accepted fix, snapshot rationale, or review conclusion, record it with `memory_record_decision` or `memory_record_note`.

## Tools and Routes

| Job | MCP tool | REST (post-production prefix) |
|---|---|---|
| Read a sequence | `post_sequence_get` | `GET /timeline?sequence_id=`, `GET /timeline/state`, `GET /timeline/clips` |
| Save or patch a sequence | `post_sequence_save` (`merge_existing: true` patches) | `POST /timeline?sequence_id=`, `PATCH /timeline` |
| Preview render of a range | `post_render_start` (`render_request` with `from`, `to`) | `POST /render`, `GET /preview?from=&to=` |
| Final master | `post_export_start` | `POST /export` |
| Mix prediction and metering | `audio_analyze`, `audio_meter` | `GET /audio/analyze`, `GET /audio/meter`, `GET /preview/audio` |
| Poll a render | `tasks_get` | `GET /render/{task_id}/status` |
| Narration cuts into Post | `narration_materialize_to_post` | `POST /api/v2/projects/{project_id}/narration-timeline/materialize-to-post-production` |

Relative REST paths in this skill sit under the post-production prefix, as in `GET /api/post-production/{project_id}/timeline/state`. Tracks, clip CRUD, marks, 3-point edits, trims, link groups, snapshots, history, and timeline analysis are REST routes on that prefix (listed in the sections below).

**Editing through the MCP tools.** Clip CRUD, tracks, marks, 3-point edits, trims, link groups and snapshots are REST routes; the MCP tools save whole sequences. With MCP tools only, edit safely:

1. Keep a restore point: save the sequence you read to a backup `sequence_id` with `post_sequence_save` (REST clients use `POST /timeline/snapshot`).
2. Call `post_sequence_get` immediately before `post_sequence_save`, never from an earlier read. A save that carries an older `version` than the stored one fails with `409` (stale); read again and reapply.
3. Change only the clips you mean to change and send everything else exactly as you read it. This is the one exception to the rule below about rewriting `tracks[]`, and it holds only because the read is fresh.


REST clients use the clip and track routes for targeted edits and the MCP tools for reads, whole-sequence saves, renders and exports. The user opens the same sequence at `https://app.pr0ta.com/timeline?sequence_id={sequence_id}`.

**From the Production Queue.** Scripted shots are generated in the Production Queue (`pr0ta-prep` → "Production Queue"), and selected takes do not reach a sequence on their own. The First Cut (Timeline toolbar; REST `POST /api/editor/{project_id}/auto-assemble-async`, a task whose `result_refs.sequence_id` is the new sequence) assembles one from each Queue item's selected take; otherwise place each selected take's asset as a clip (Clips below).

## Core Rules

- **Name the sequence every time.** Tools and routes default to `timeline_v2`. Record the `sequence_id` you are editing and pass it to every read, write, render, export, and review submission, or you will render a stale default.
- **One track is one linear lane.** Concurrent audio (narration under music) goes on separate audio tracks. Overlapping clips on one track are invalid and the renderer rejects them.
- **Create tracks before clips**, one at a time with `POST /timeline/tracks`. Do not rewrite the whole `tracks[]` array through `PATCH /timeline`; a stale payload can restore deleted clips. With MCP tools only, follow "Editing through the MCP tools" above.
- **`POST /timeline/clips` always creates.** It never upserts: running the same edit logic twice doubles your clips. Read the clip list first; change a clip with `PATCH /timeline/clips/{clip_id}`; replace one by deleting it and adding the new clip.
- **Seconds are canonical; frames are exact.** `start` and `duration` are seconds (the `_ms` fields are the same values in milliseconds). For picture cuts that matter, use frame-native fields (see Frame-Accurate Picture Cuts).
- **Snapshot before every major pass**, user review, or many-clip change.
- **Read state after the user edits.** They may have reordered, trimmed, or swapped clips; read the sequence before your next write.
- **Respect the edit lock.** A user can hold an advisory lock on a sequence. Writes then fail with `409 timeline_locked` unless they carry the lock token (`X-Timeline-Lock-Token` header, or `lock_token` on `post_sequence_save`). Do not take the lock from a user who is editing; ask. Lock routes: `GET /timeline/lock`, `POST /timeline/lock/acquire`, `/heartbeat`, `/release`.

## Sequences and Tracks

**Sequence settings come first.** Set width, height, and frame rate before adding clips: 1920×1080 at 30 fps for HD, 1080×1920 at 30 fps for vertical social, 3840×2160 at 24 fps for 4K cinematic. The timeline normalizes every clip to the sequence's size and frame rate at render, so no manual scaling is needed. Plate-based hybrid clips should match the sequence frame rate rather than be retimed (`pr0ta-hybrid`).

`POST /sequences` creates a named empty sequence (`sequence_id`, `name`, `sequence` dimensions). It does not copy another sequence or accept tracks. `POST /sequences/{sequence_id}/duplicate` copies one with its clips. `GET /sequences` lists them.

**Standard track layout:**

| Track ID | Type | Purpose |
|---|---|---|
| `video` | video | Picture |
| `dialogue` | audio | Narration and dialogue |
| `music` | audio | Score and beds |
| `sfx` | audio | Effects and foley |
| `titles` | title | Title cards and lower thirds |

`POST /timeline/tracks?sequence_id=` with `{"id": "dialogue", "type": "audio", "label": "Dialogue", "position": 2}` creates an empty track (`position` optional; appended when omitted). Tracks also answer to NLE aliases (`V1`, `A1`, `A2`); `GET /timeline/tracks` returns the alias map. Use raw IDs in requests and aliases when talking to the user.

### Rebuild a Fresh Sequence

Mutate the current sequence for normal iteration. Rebuild into a new `sequence_id` when patch state accumulates: more than one structural review revision, a one-frame or media-gap warning that moves after each repair, audio patches that create artifacts twice, or orphan patch tracks, stale narration, muted keyframe remnants, or duplicate shot families.

1. `POST /sequences` with a new `sequence_id` and the dimensions.
2. Save the complete intended payload to it (`post_sequence_save` or `POST /timeline?sequence_id={new_id}`): tracks, `audioMix`, and `metadata` such as `{"reason": "review-rebuild", "sourceSequenceId": "timeline_v2"}`. To keep settings, read the source sequence first and copy only what you intend.
3. Rebuild clips frame-native from the authoritative beat or cut list and known-good media: one primary picture track, one narration track, one music track, and extra tracks only for a specific purpose.
4. Render, export, and submit for review with the new `sequence_id`.

`reference/repairs-and-diagnostics.md` has the full repair and rebuild procedure.

## Clips

| Route (with `?sequence_id=`) | Purpose |
|---|---|
| `POST /timeline/clips` | Create a clip with placement |
| `PATCH /timeline/clips/{clip_id}` | Update properties, move to another track |
| `DELETE /timeline/clips/{clip_id}?ripple=true` | Delete; `ripple=true` closes the gap on that track |
| `POST /timeline/clips/reorder` | Batch placement and start changes |

Create payload: clip fields under `clip`, placement under `placement`:

```json
{
  "clip": { "assetId": "asset_123", "start": 0, "duration": 2.5, "kenBurns": { "preset": "push_in" } },
  "placement": { "track_id": "video", "position": 0 }
}
```

Use `track_id` in `placement`. Sequence duration is derived from the last clip's end; you never set it. Check each clip's native duration before placing it: a slot longer than the media leaves a real gap (see Source Shortfalls).

## Ken Burns as a Clip Property

Set `kenBurns` on create or `PATCH`; the renderer computes the motion at export. You never write zoompan expressions.

- **Presets:** `push_in` (emphasis), `pull_back` (reveal), `drift_left` and `drift_right` (lateral movement), `hold` (static). An unrecognized preset renders as `hold`, so use only these names.
- **Custom:** `{"kenBurns": {"start_zoom": 1.0, "end_zoom": 1.15, "pan": [0, 0]}}`, with `pan` values from −1 to 1.

Alternate directions across adjacent stills (`push_in` then `pull_back`); repeating one direction reads as monotonous.

## Audio Mix

Timeline-level mix lives in `audioMix`, set by saving or patching the sequence:

```json
{
  "audioMix": {
    "ducking": [
      { "sourceTrack": "music", "keyTrack": "dialogue", "duckedGain": 0.35, "attackMs": 300, "releaseMs": 500 }
    ],
    "narrationOffsetMs": 1500
  }
}
```

- `ducking` is an **array of rules**, one per relationship (music under dialogue, SFX under narration). Ducking renders as gain automation on the ducked clips, not a sidechain compressor.
- `duckedGain` is the fraction of nominal volume while the key track plays: `1.0` no ducking, `0.5` ≈ −6 dB, `0.0` mute. Send camelCase fields.
- **`volumeKeyframes`** give manual level moves. On a track (`PATCH /timeline/tracks/{track_id}`), times are program time: lower the bed from 20s to 35s. On a clip (`PATCH /timeline/clips/{clip_id}`), times are clip-relative: fade a music clip in. Each keyframe has `time`, `value` (linear gain, `1.0` unchanged) or `db`, and optional `interpolation` (`linear` or `hold`). Track and clip gains multiply; ducking merges its keyframes with yours.

`pr0ta-api` → `reference/timeline-api.md` → "Audio Mix Properties" and "Audio Level Keyframes" hold the full field contract and aliases.

## Transitions

A transition is an object on the clip it belongs to, with `duration` in seconds:

```json
{ "transition": { "type": "dissolve", "duration": 0.5 } }
```

| `type` | Effect |
|---|---|
| `dissolve`, `crossfade`, `wipe` | From the previous clip into this one. Set it on the **incoming** clip. Applies only between adjacent clips on the same track (touching, or within 0.1s). |
| `fade-up` | This clip opens from black. |
| `fade-out`, `fade-to-black` | This clip closes to black. |

- `duration`: seconds, above 0 and at most 10 (longer values are capped at 10). Send a number. If it is missing or unreadable, the transition gets 0.5s.
- `easing` (optional): `linear`, `ease-in`, `ease-out`, or `ease-in-out`. It shapes the editor preview only; renders ramp linearly.
- A cut has no transition: omit the field, or send `"transition": null` in a clip update to remove one.
- Always send the object. A bare name such as `"dissolve"` is saved as that type at 0.5s; `"cut"`, `"none"`, the ambiguous `"fade"`, and unrecognized names are saved as a cut.

This covers common editorial cases; it is not a full transition engine. If the viewer notices the transition, it is probably in the way (`pr0ta-editorial`).

## Frame-Accurate Picture Cuts

PR0TA normalizes picture clips to `[startFrame, endFrame)` on save and render and derives seconds from the sequence frame rate. Treat video and title edits as frame intervals, not decimal guesses.

- Use `startFrame`, `durationFrames`, `sourceInFrame`, and `sourceOutFrame` for frame-critical edits and repairs.
- A 1–2 frame gap or overlap on one track is drift. Keep the incoming cut frame and adjust the outgoing side.
- On beat-aligned edits, never pull an incoming cut earlier unless the user asks for a timing change. Cover boundary artifacts with an outgoing tail handle of about 4–8 frames under the beat-locked incoming shot.
- Never fix a render-boundary defect by holding the last frame. Trim, retime deliberately, extend or regenerate the source, add a tail handle, or replace the shot.
- After a repair, read the clips back and confirm `startFrame`, `endFrame`, `endFrameInclusive`, and `durationFrames`.

## Editorial Primitives

Marks, 3-point edits, trims, and link groups give NLE precision. `pr0ta-api` → `reference/editorial-primitives.md` has every shape.

- **Asset marks** (`POST /api/v2/projects/{project_id}/assets/{asset_id}/marks`): in and out points on source media. Mark the best section before placing a clip.
- **Program marks** (`POST /timeline/marks`): story anchors on the timeline, absolute or anchored to a transcript word; anchored marks follow the word when clips move. Send `clipId` (and `assetId`) when the same dialogue asset appears more than once. Give marks a `label` and `description` that say what they are for ("Credits In" / "Credits begin here").
- **3-point edits** (`POST /timeline/edits`, preview first with `POST /timeline/edits/preview`): give three of source in/out and program in/out and PR0TA computes the fourth. Modes `insert` (ripples downstream) and `overwrite`; reference marks as `@mark:<name>`; `affectedTracks` extends the edit to other tracks.
- **Trims** (`POST /timeline/edits/{clip_id}/trim`, preview with `.../trim/preview`): modes `ripple`, `roll`, `slip`, `slide`; `linked: true` trims linked companions; only `ripple` accepts `affectedTracks`.
- **Link groups** (`POST /timeline/links`, `GET /timeline/links`): persisted A/V relationships. Link picture and sound as soon as they are placed together; moves and trims on one member propagate. Lock the group (`PATCH /timeline/links/{link_group_id}` with `locked: true`) once sync is confirmed; a locked group rejects every mutation of its members. Clip update, delete, and reorder accept `linked: true`.

Prefer marks to hard-coded seconds, which break when clips move. Preview before committing whenever you reason from marks.

### Source Shortfalls and fitToFill

When the source is shorter than the requested program range, PR0TA inserts only the available media and leaves a real gap: no freeze padding, no silent stretch. The edit response carries a `source_shortfall` warning (`requestedDuration`, `insertedDuration`, `shortfallDuration`, `gapStart`, `gapEnd`). Surface it and decide: a longer take, a companion shot, different media over the gap, or `fitToFill: true` to retime the source to the range (it writes `speed`; below 1.0 is slow motion). Use `fitToFill` only as a deliberate visible choice (`pr0ta-editorial` limits it to cinematic B-roll). Before render, confirm the clip shows `fitToFill`, `speed`, `sourceSpan`, `programDuration`, and `effectivePlaybackDuration`, and that the effective duration covers the program duration.

## Snapshots

| Route (with `?sequence_id=`) | Purpose |
|---|---|
| `POST /timeline/snapshot` | Create or replace a named snapshot (`{"name": "pre-polish"}`) |
| `GET /timeline/snapshots` | List snapshots |
| `POST /timeline/snapshot/{name}/restore` | Restore into the sequence |
| `GET /timeline/snapshot/{name}/diff` | Added, removed, and modified clips versus now |
| `GET /timeline/history` | Recent saves and mutations, newest first |

If a pass makes things worse, restore the snapshot instead of rebuilding.

## Preview, Mix Checks, and Render

Check cheapest first:

1. **`audio_analyze`** (`GET /audio/analyze`): predicted levels, ducking impact, and each segment's `render_gain_envelope`, with no render. Is narration far louder than music? Did ducking bury a track?
2. **`audio_meter`** (`GET /audio/meter`): actual integrated LUFS, loudness range, true peak, and short-term LUFS through the render path, for short windows. Use it for loudness targets.
3. **`GET /preview/audio`**: a `.wav` of the mix to listen to; `tracks=dialogue,music` solos tracks (all audio checks accept a track filter).
4. **`GET /preview`** or a range render: picture and sound, only when you need to see it. Omitted `quality` renders full sequence resolution; `quality=low` (or `preview`) renders at half size for fast checks.

Music must stay audible in narration gaps: after any render with music automation, meter or listen to at least one narration-quiet window. If the mix goes silent where the bed should play, the render failed.

`POST /render` (`post_render_start`) is the preview render. It loads the saved sequence; send control fields only (`from`, `to`, `resolution`, `width`, `height`, `format`), not timeline JSON. A sequence with no clips returns 400.

## Analyze Before Render

Call `GET /timeline/analysis?sequence_id=` before any render or export. It reports gaps, overlaps, reused media, source shortfalls, frame coverage, and `trackCoverage`, with counts under `summary`:

- Unintended gaps on primary tracks: fix them. `trackCoverage` separates critical gaps from empty overlay lanes.
- Reused visual media (`reusedMediaCount`): fix unless it is a stated motif.
- `sourceShortfallCount > 0`: present the affected clips and resolve each (see Source Shortfalls).
- For retimed clips, confirm `effectivePlaybackDuration >= programDuration` within a frame.

`GET /timeline/debug-report` adds render-risk diagnostics. Render and export results carry `timelineMediaGaps[]` (program frames with no media) and `renderedPixelGaps[]` (transparent or checkerboard frames after render). Each is a hard review item: classify it and repair by its `startFrame`/`endFrame`, never by loose timestamp and never by clearing it on a black-frame check alone. `reference/repairs-and-diagnostics.md` has the adjudication procedure.

## Narration Materialization

Narration-driven pieces (documentary, explainer, anything cut to a transcript) are built and verified in the narration timeline (`pr0ta-sync`), then materialized with `narration_materialize_to_post`. The response includes `timeline`, `clip_count`, and `sequence_name`. The materializer keeps cut order, resolves assets to stable URLs, gives clips stable IDs, keeps transcript-anchor provenance under `metadataOverrides.origin`, converts narration motion to `kenBurns` and supported transitions to clip transitions, adds narration and music clips when those layers exist, and writes the narration offset and ducking intent into `audioMix`. After that, all editing happens here.

## Standard Production Workflow

1. **Generate** images, video, narration, and music: scripted shots in the Production Queue (`pr0ta-prep`), ad-hoc shots with `pr0ta-image`, `pr0ta-video`, `pr0ta-audio`, `pr0ta-music`.
2. **Set the sequence** size and frame rate, then **create tracks**: at least `video`, `dialogue`, `music`; `sfx` and `titles` as needed.
3. **Build the edit.** Narration-driven: verify in the narration timeline, then materialize. Otherwise add clips with placement and Ken Burns, narration on `dialogue`, music on `music`.
4. **Configure audio**: ducking rules, narration offset, clip and track levels, `volumeKeyframes` for manual moves.
5. **Check the mix** with the escalation above.
6. **Mark key points**: program marks on concept words, beat changes, and section boundaries; asset marks on best source sections.
7. **Analyze before render.**
8. **Snapshot** (`agent-pass-1`).
9. **Hand off**: tell the user the sequence is ready and which `sequence_id` to open. They scrub, reorder, trim, and swap directly.
10. **Read back and address notes** with targeted clip edits, not a full rebuild.
11. **Rebuild when patch state accumulates** (Rebuild a Fresh Sequence). Replacing narration means removing the old narration clips, patch tracks, and stale automation, adding one regenerated narration asset, making sure it is time-indexed, and reflowing the cuts; never layer a replacement over the old one unless asked.
12. **Final export** when the cut passes the ship gate.

## Final Export

`post_export_start` (`POST /export`) renders the locked master from the saved sequence; inline timeline payloads are rejected. Use it only when the cut passes `pr0ta-editorial`'s seven-criteria ship gate and render verification; use preview renders during iteration. Record the `sequence_id`, render or export task ID, and export asset ID together. Client review links get a full-quality export, never a low-quality preview; after submitting for review, confirm the review asset ID is the export you meant to show and record the review round and URL with it. `POST /export-fcpxml` exports the edit as FCPXML for another NLE.

## Collaborative Model

| Actor | Works via | Does |
|---|---|---|
| Agent | Tools and API | Generates, places, sets motion and mix, previews, verifies |
| User | Browser Timeline | Scrubs, reorders, trims, swaps, adjusts pacing, approves |
| Agent, round 2 | Tools and API | Reads the user's changes, addresses remaining notes, re-renders only what changed |

The agent's job is editorial judgment (what goes where, what motion, what pacing), not mechanical assembly.

## Tips

- Use `audio_analyze` before rendering; escalate to an audio preview, then a picture preview, only as needed.
- Preview segments; render the full piece only for verification and delivery.
- Presets cover most Ken Burns needs; use custom zoom and pan only for a specific range.
- Link A/V pairs early and lock them once sync is confirmed.
- Preview 3-point edits and trims before committing, especially when working from marks.
- Every `source_shortfall`, `timelineMediaGaps[]`, and `renderedPixelGaps[]` entry gets a decision and a recorded repair.
