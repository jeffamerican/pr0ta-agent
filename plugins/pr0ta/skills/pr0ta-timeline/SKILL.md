---
name: pr0ta-timeline
description: "PR0TA post-production timeline: sequences and tracks, probing sources, framing with fit (contain, cover, stretch) and transforms, 16:9 to 9:16 reframing, text and caption clips, clip editing, Ken Burns, audio mix, linking picture to its sound, transitions, frame-accurate cuts, trims, snapshots, cut provenance and review status, the verification loop (low-quality render, frame contact sheets, loudness, analysis), and final export. Read when assembling, editing, mixing, checking, or exporting a cut."
---

# Post-Production Timeline

The post-production timeline is PR0TA's editing surface. It is persistent, shared state: agents edit it through tools and the API, and the user opens the same sequence in the browser to scrub, trim, review and approve. Assemble, frame, caption, mix, check and export here. If the timeline lacks something a production needs, report it (`bug_report_create`) rather than building a parallel local pipeline.

This is **not** the narration timeline (`pr0ta-sync`), a transcript-anchored cut list you materialize into a sequence once it verifies. Field contracts live in `pr0ta-api` → `reference/timeline-api.md`, `reference/editorial-primitives.md` and `reference/source-shortfalls-and-fit-to-fill.md`. Editorial judgment (what to cut, when it ships, vertical and short-form craft) lives in `pr0ta-editorial`.

Before a major pass, call `memory_context_pack` with a `task_intent` and the sequence `scope`; after a meaningful decision, record it with `memory_record_decision` or `memory_record_note`.

## Tools and Routes

| Job | MCP tool | REST (post-production prefix) |
|---|---|---|
| Measure sources | `assets_probe` | `POST /api/assets/{project_name}/media/probe-backfill` (whole project) |
| Read a sequence | `post_sequence_get` | `GET /timeline?sequence_id=`, `GET /timeline/clips` |
| Save or patch a sequence | `post_sequence_save` (`merge_existing: true` patches) | `POST /timeline?sequence_id=`, `PATCH /timeline` |
| Link picture and sound | `post_clips_link` | `POST /timeline/links` |
| Analyze and list problems | `post_sequence_analyze`, `post_sequence_debug_report` | `GET /timeline/analysis`, `GET /timeline/debug-report` |
| Look at frames | `post_frames_get` | |
| Is the latest render current? | `post_sequence_analyze` (`no_verification_render`) | `GET /timeline/verification?sequence_id=` |
| Approve, request changes, reopen | none: people only | `POST /timeline/review?sequence_id=` (signed-in user in the app) |
| Preview render | `post_render_start` (`from`, `to`, `quality`) | `POST /render`, `GET /preview?from=&to=&quality=low` |
| Mix prediction and loudness | `audio_analyze`, `audio_meter` | `GET /audio/analyze`, `GET /audio/meter`, `GET /preview/audio` |
| Final master | `post_export_start` | `POST /export` |
| Poll a render | `tasks_get` | `GET /render/{task_id}/status` |
| Cut a source into a new asset | `assets_trim` (a long one returns a `task_id` to poll) | |
| Smooth slow motion | `post_clip_slow_motion` | `POST /timeline/slow-motion`, `GET /timeline/slow-motion/quote` |
| Narration cuts into Post | `narration_materialize_to_post` | `POST /api/v2/projects/{project_id}/narration-timeline/materialize-to-post-production` |

Relative REST paths sit under the post-production prefix, as in `GET /api/post-production/{project_id}/timeline/clips`.

**Renders, frame grabs, probes and analysis are free.** They spend no credits, so a mission with a credit cap can run them; use them on every pass. `assets_probe` and `post_frames_get` save what they find (measurements on the asset, a contact-sheet image), so they need edit access and count as project edits.

**Editing through the MCP tools.** The MCP tools save whole sequences. Edit safely:

1. Keep a restore point: save the sequence you read to a backup `sequence_id` (REST clients use `POST /timeline/snapshot`).
2. Call `post_sequence_get` immediately before `post_sequence_save`, never from an earlier read, and send `baseVersion` set to the `version` it returned. A full replace of an existing sequence without `baseVersion` fails with `428 base_version_required`; one built on an older version fails with `409 stale_write` (both carry `current_version`): read again and reapply. A save to a deleted sequence fails with `410 sequence_deleted`. Creating a new sequence needs no base; `merge_existing: true` patches need none either.
3. Change only the clips you mean to change and send everything else exactly as you read it.

Every save answers with `validationWarnings`; its `deliveryWarnings` list names letterboxed sources, doubled audio, missing captions and same-source slices. Fix them before rendering.


REST clients use the clip and track routes for targeted edits and the MCP tools for reads, whole-sequence saves, checks, renders and exports. The user opens the same sequence at `https://app.pr0ta.com/timeline?sequence_id={sequence_id}`.

**From the Production Queue.** Selected takes do not reach a sequence on their own. The First Cut (Timeline toolbar; REST `POST /api/editor/{project_id}/auto-assemble-async`) assembles one; otherwise place each selected take as a clip.

## Core Rules

- **Name the sequence every time.** Tools default to `timeline_v2`. Pass the `sequence_id` you are editing to every read, write, check, render and export.
- **One track is one linear lane.** Concurrent audio goes on separate audio tracks; overlapping clips on one track are invalid.
- **Create tracks before clips** (`POST /timeline/tracks`). Never rewrite `tracks[]` from a stale read.
- **`POST /timeline/clips` always creates**, never upserts. Change a clip with `PATCH /timeline/clips/{clip_id}`.
- **Seconds are canonical; frames are exact.** Use frame-native fields for cuts that matter.
- **Snapshot before every major pass** and read the sequence again after the user edits.
- **Respect the edit lock.** A user editing holds the lock; writes then fail with `409 timeline_locked` unless they carry its token (`lock_token`). Do not take it from someone who is editing; ask.

## Sequences, Sources and Framing

**The sequence frame is the deliverable's shape.** Set width, height and frame rate first: 1920×1080 for 16:9, 1080×1920 for 9:16 Reels, Stories, TikTok and Shorts, 1080×1350 for 4:5 feeds, 3840×2160 at 24 fps for 4K.

**Probe every source before you cut it in.** `assets_probe` returns `width`, `height`, `aspect_ratio`, `orientation`, `fps`, `duration_seconds` and `has_audio`, and saves them on the asset; new uploads, generations, trims and renders are measured at registration. Clips carry the result as `sourceMedia` (`width`, `height`, `aspectRatio`, `fps`, `hasAudio`, `fitsSequence`, and for a trim `sourceAssetId` and `sourceInPoint`). `fitsSequence: false` means the source's shape differs from the frame.

**Nothing is reframed for you.** Each picture clip is fitted into the frame by `fit`, then `transform` applies on top:

| `fit` | Result when shapes differ |
|---|---|
| `contain` (absent means contain) | Whole source visible, bars where shapes differ. 16:9 in 9:16 fills only 32% of the frame. |
| `cover` | Fills the frame, crops the overflow, centered. |
| `stretch` | Distorts the source to the frame. Avoid. |

`transform` then moves the fitted picture: `scale` (a multiplier, never a percent: 1.0 = fitted size, clamped to 0.01–10), `positionX` and `positionY` (fractions of the frame width and height; `0.25` moves it a quarter frame right or down), `rotation`, `opacity`, with keyframes for moves. Ken Burns on stills composes with the fit.

**Reframing 16:9 into 9:16:** set `"fit": "cover"`, then keep the subject in the window with `transform.positionX`. Covered, the source is 3.16× the frame width, so `positionX` from about −1.08 to 1.08 pans from one edge of the source to the other (positive shows more of its left side). Check the framing with `post_frames_get` on the sequence, shot by shot. Analysis treats a mismatched source (shape more than 1% off the frame's) as `letterboxed_source` unless it is resolved: `fit` `cover` or `stretch`, or `transform.scale` at least 0.98 × the cover scale (3.16 for 16:9 in 9:16). A clip scaled below 1 or moved off centre is an overlay (picture-in-picture) and is never flagged. A wide with its subject at the edge, or two people at opposite edges, does not survive the crop: pick another shot or generate a vertical one (`pr0ta-video`).

### Rebuild a Fresh Sequence

Rebuild into a new `sequence_id` when patch state accumulates (more than one structural revision, gap warnings that move after each repair, orphan patch tracks, stale narration): `POST /sequences` with the dimensions, save the complete intended payload to it, rebuild clips frame-native from the authoritative cut list, then check and render with the new id. `reference/repairs-and-diagnostics.md` has the procedure.

## Clips

| Route (with `?sequence_id=`) | Purpose |
|---|---|
| `POST /timeline/clips` | Create a clip with placement |
| `PATCH /timeline/clips/{clip_id}` | Update properties, move to another track |
| `DELETE /timeline/clips/{clip_id}?ripple=true` | Delete; `ripple=true` closes the gap |
| `POST /timeline/clips/reorder` | Batch placement and start changes |

```json
{
  "clip": { "assetId": "asset_123", "start": 0, "duration": 2.5, "inPoint": 4.0, "fit": "cover",
            "transform": { "positionX": 0.3 } },
  "placement": { "track_id": "video", "position": 0 }
}
```

Sequence duration is derived from the last clip's end. Check each clip's native duration first: a slot longer than the media leaves a real gap (Source Shortfalls). Cut a long take into the range you need with `inPoint`/`outPoint`, or with `assets_trim` for a standalone asset; trims are frame-accurate, remember their source, and keep its alpha, bit depth and ProRes profile.

### Ken Burns as a Clip Property

Set `kenBurns` on create or `PATCH`; the renderer computes the motion. Presets: `push_in` (emphasis), `pull_back` (reveal), `drift_left` and `drift_right`, `hold`. Custom: `{"start_zoom": 1.0, "end_zoom": 1.15, "pan": [0, 0]}`, `pan` from −1 to 1. Alternate directions across adjacent stills; one direction repeated reads as monotonous.

## Text and Captions

Title-track clips with no asset are text clips: their `text` object is drawn in preview and burned in at render, and `role: "caption"` clips also export as an SRT sidecar.

```json
{ "id": "cap_01", "type": "title", "start": 0.4, "duration": 2.1,
  "text": { "content": "We built it in a weekend.", "role": "caption" } }
```

| Field | Values and defaults |
|---|---|
| `content` | Required; `\n` breaks lines |
| `role` | `title` (default), `caption`, `lower_third` |
| `position` | `top`, `center`, `bottom`, `lower_third`; caption → bottom, lower third → lower_third, title → center |
| `fontSizePct` | Percent of frame height: caption 4.5, lower third 4, title 8 |
| `color`, `background` | `#RRGGBB`; caption box `rgba(0,0,0,0.55)` by default, others none |
| `align`, `bold`, `fontFamily`, `maxWidthPct` | center; title bold; Inter; 86% of frame width |
| `safeArea` | Default true: inside the 90% title-safe area and, in 9:16, above the bottom 20% where the app UI sits |

Captions: one or two short lines, each on screen for its spoken words. Time them from word timing (`transcription_get`, `pr0ta-audio`), not by guess. A title clip with an image or video asset stays an overlay. `text` is always an object; a title clip with no asset and empty `text.content` renders nothing and is reported as `empty_text_clip`.

**Social deliverables.** A cut counts as social when its frame is portrait 4:5 or taller (width/height ≤ 0.8) or square, or when `provenance.deliverable` names a platform (Instagram, Reel(s), TikTok, YouTube Shorts, Shorts, Stories, Facebook, LinkedIn, Snapchat). A social cut with no text clip at all gets `no_on_screen_text`; one with audible speech (a dialogue or narration clip, or a video's own sound) and no caption clips gets `no_captions`. Both are warnings.

## Audio

**One rule decides what you hear, in preview and render.** A video clip's own sound plays unless (1) the clip has `audioEnabled: false` or `muted: true`; (2) a linked audio clip of the same media replaces it, or an audio clip extracted from this clip's own sound does (`metadataOverrides.origin.source` `embedded_video_audio` or `native_video_audio` with `origin.sourceClipId` = the video clip's id); or (3) its track is muted, or another track is soloed. Its level is clip `volume` × track `volume`, with `volumeKeyframes` and fades, like any audio clip.

**Same media** means one thing everywhere (replacement, doubled audio, caption sources): each clip's media key is `sourceMedia.sourceAssetId`, else `assetId`, else `assetUrl` (the URL only when neither clip has an asset id), and the keys match.

**Link picture to its sound** when you put a video's audio on an audio track (to mix it, J/L-cut it, or keep it when you change the picture): `post_clips_link` with the video clip and the audio clip(s). Same media: the audio clip replaces the embedded sound, and the two move and trim together. Other media (sound cut from another file): the link does not silence the video, both play, and analysis reports `linked_audio_not_replacing`; pass `mute_video_audio: true` (or set `audioEnabled: false` on the video). An unlinked copy of the same source under its video plays twice, phasey, and drifts when either moves; analysis reports it as `double_audio_risk`.

Generated video carries thin incidental sound; set `audioEnabled: false` unless the sound was designed for the shot.

**Mix** lives in `audioMix`:

```json
{ "audioMix": { "ducking": [ { "sourceTrack": "music", "keyTrack": "dialogue", "duckedGain": 0.35,
                               "attackMs": 300, "releaseMs": 500 } ], "narrationOffsetMs": 1500 } }
```

`ducking` is an array of rules; `duckedGain` is the fraction of nominal volume while the key track plays (`0.5` ≈ −6 dB). `volumeKeyframes` on a track use program time; on a clip, clip time. Each keyframe has `time`, `value` (linear) or `db`, and optional `interpolation`. `pr0ta-api` → `reference/timeline-api.md` has the full contract.

## Transitions

A transition is an object on the clip it belongs to: `{ "transition": { "type": "dissolve", "duration": 0.5 } }`. `dissolve`, `crossfade` and `wipe` go on the **incoming** clip and need adjacent clips on one track; `fade-up` opens from black; `fade-out` and `fade-to-black` close to black. `duration` is seconds (at most 10). A cut has no transition (`"transition": null` removes one). If the viewer notices the transition, it is in the way.

## Frame-Accurate Picture Cuts

PR0TA normalizes picture clips to `[startFrame, endFrame)` from the sequence frame rate. Use `startFrame`, `durationFrames`, `sourceInFrame` and `sourceOutFrame` for frame-critical edits. A 1–2 frame gap or overlap on a track is drift: keep the incoming cut frame and adjust the outgoing side. On beat-locked cuts, cover boundary artifacts with a 4–8 frame outgoing tail handle; never hold a last frame to the boundary. After a repair, read the clips back and confirm `startFrame`, `endFrame` and `durationFrames`.

## Editorial Primitives

`pr0ta-api` → `reference/editorial-primitives.md` has every shape. Asset marks (`POST /api/v2/projects/{project_id}/assets/{asset_id}/marks`) hold source in/out points; program marks (`POST /timeline/marks`) anchor story beats, absolutely or to a transcript word. 3-point edits (`POST /timeline/edits`, preview with `POST /timeline/edits/preview`) compute the fourth point. Trims (`POST /timeline/edits/{clip_id}/trim`) take `ripple`, `roll`, `slip` or `slide`; `linked: true` trims linked companions. Lock a link group (`PATCH /timeline/links/{link_group_id}` with `locked: true`) once sync is confirmed.

**Source shortfalls.** A source shorter than its program range leaves a real gap and a `source_shortfall` warning (`requestedDuration`, `shortfallDuration`, `gapStart`, `gapEnd`). Decide: a longer take, a companion shot, different media, or a deliberate `fitToFill: true` retime (slow motion on cinematic B-roll only).

**Slow motion must be interpolated.** Below 1× a clip repeats frames. `post_clip_slow_motion` attaches an interpolated rendition (`clip.slowMotion`): `engine: "draft"` (free) to judge, `"topaz"` (paid) to deliver, after `quote_only: true` and the user's OK, passed as `confirm_credits`. It counts only while the clip's speed and range are unchanged; analysis reports `slow_motion_not_interpolated` and `slow_motion_draft_only` (`pr0ta-api` → `reference/source-shortfalls-and-fit-to-fill.md`).

### Snapshots

`POST /timeline/snapshot` (`{"name": "pre-polish"}`) creates or replaces a named snapshot; `GET /timeline/snapshots` lists them; `POST /timeline/snapshot/{name}/restore` restores one; `GET /timeline/snapshot/{name}/diff` shows added, removed and modified clips; `GET /timeline/history` lists recent saves. If a pass makes things worse, restore instead of rebuilding.

A snapshot is not an edit: creating one keeps the sequence `version` and announces no save, so your `baseVersion`, an approval and a verification render stay valid. Restoring one is an edit (a new version; a changed cut returns to `in_review`). A rename (send `baseVersion`; a stale one is 409) returns the new version: use it as your next `baseVersion`.

## Provenance and Review

Every sequence carries `provenance`: `author`, `missionId`, `intent`, `deliverable`, `status` (`draft`, `in_review`, `approved`, `changes_requested`), `notes`, `flags`. Describe the cut when you save it: `post_sequence_save` with `provenance: {"intent": "...", "deliverable": "Instagram Reel 9:16, ≤30 s", "notes": [...]}`. Write the intent in one or two sentences: what the cut is for and its story spine. An Operator mission's save marks the cut `author: operator`, names the mission and puts it `in_review`; existing intent and notes are kept, and only the `provenance` argument changes intent or deliverable (a copy inside the timeline payload does not). Notes and flags are add-only for agents. Only the user, editing in the app, can remove a flag: a save through MCP, the Operator, REST or a personal access token keeps every stored flag (it can add one, never clear `do_not_publish`).

**Review is human-only.** `approved` and `changes_requested` are set only through `POST /timeline/review?sequence_id=` with `{"decision": "approve" | "request_changes" | "reopen", "note": "...", "baseVersion": <the version reviewed>}`, by a signed-in user in the app; agents, MCP clients and access tokens get `403 review_requires_user_session`. A review without `baseVersion` gets `428 base_version_required`, and one of an older version gets `409 stale_write`, so a decision never lands on a cut the reviewer has not seen. Approving records `approvedVersion`, `reviewedBy` and `reviewedAt`. No save can set or change those fields: the server keeps the stored values. When any writer saves a change to the cut's content (tracks, clips, framing, mix, links) and the stored status is `approved` or `changes_requested`, the server sets it back to `in_review` and clears `approvedVersion`. A rename or a save that leaves the content as it was keeps the approval current. So: never edit an approved cut you were not asked to change. Add `do_not_publish` to `flags` for a cut that must not leave the project.

## The Verification Loop

Run this on every pass, not only before delivery. `reference/verification-loop.md` has every finding code and its fix.

1. **Analyze.** `post_sequence_analyze`; fix every `deliveryChecks` entry of severity `warning` or `error`, and the gaps, overlaps and shortfalls it lists.
2. **Look at the framing.** `post_frames_get` with the `sequence_id` and `count` 8 (or `times` at the cuts that matter): letterboxing, crops, captions in the safe area.
3. **Render low.** `post_render_start` with `render_request: {"quality": "low"}`. Poll `tasks_get` until it succeeds; record its `asset_id`. Renders and exports are stamped at creation with the sequence id and the saved version they show; only a finished full-length render of exactly the current saved version verifies it (`GET /timeline/verification?sequence_id=` returns `latestRender` and `coversCurrentVersion`). A section render (`from`/`to`, stamped `render_range`) is for looking at a passage: it never verifies the cut and its loudness never stands for the cut's. A render of an inline timeline never verifies a sequence.
4. **Watch the render.** `post_frames_get` with that `asset_id`: the first frame, the last, and the frames at each beat, title and caption. These are the frames that will ship.
5. **Listen.** Read the finished task's `loudness` (integrated LUFS, true peak), or run `audio_meter` windows. Social and web: about −14 LUFS integrated, true peak at most −1 dBTP. `audio_analyze` shows ducking and the music under narration.
6. **Debug report.** `post_sequence_debug_report`; every warning is fixed or explained.
7. **Fix and repeat.** Targeted edits, then render again. A cut is ready for review when analysis shows no warnings you cannot explain and the frames and loudness check out.
8. **Hand off for review.** Save with `provenance` (intent, deliverable, what changed), tell the user which `sequence_id` to open, and wait for approval before the final export.

For a narration or dialogue fix, also transcribe the rendered audio. `video_quality_control_analyze` adds a paid timecoded audio-visual QC pass; run it only on the ship-quality render, and say it is paid.

## Final Export

`post_export_start` (`POST /export`) renders the locked master from exactly the saved sequence, loaded by its `sequence_id`. Save first, then export by `sequence_id`: an export request whose inline `timeline_data` differs from the saved content is refused with `400 export_requires_saved_sequence`. Use it only for a cut that passed `pr0ta-editorial`'s ship gate, the verification loop, and review. The export gate reads the saved sequence, never the request: when it has provenance and either its `author` is not `user` or its flags include `do_not_publish`, the export passes only if `status` is `approved`, `approvedVersion` equals the current `version`, and `do_not_publish` is absent. Otherwise it answers `400` with `detail: {code: "export_requires_confirmation", message, status, flags}`, and only the user's explicit confirmation (`confirm_unapproved: true`) exports it anyway. Export at the sequence's own size: a 9:16 cut exports 1080×1920, never through a 16:9 preset. Record the `sequence_id`, export task ID and export asset ID together; client review links get the full-quality export, never a low preview. `POST /export-fcpxml` exports the edit for another NLE.

## Standard Workflow

1. **Generate or gather** material: scripted shots in the Production Queue (`pr0ta-prep`), others with `pr0ta-image`, `pr0ta-video`, `pr0ta-audio`, `pr0ta-music`.
2. **Probe sources** (`assets_probe`) and **set the sequence** to the deliverable's shape; create tracks: `video`, `dialogue`, `music`, `sfx`, `titles` as needed.
3. **Build the edit**: narration-driven work through the narration timeline and `narration_materialize_to_post`; otherwise clips with placement, `fit`, and Ken Burns.
4. **Frame and caption**: reframe mismatched sources, add caption and title clips.
5. **Sound**: link picture to its sound, disable stray generated audio, set ducking and levels.
6. **Snapshot**, then run **the verification loop** until it is clean.
7. **Hand off** with provenance; read the user's changes back and address notes with targeted edits.
8. **Final export** after approval.
