# Post-Production Timeline API — Reference

The **post-production timeline** is the primary editing surface for both AI agents and human collaborators. It stores persistent clip state, Ken Burns presets, audio mix configuration, and supports incremental edits — no more full-rebuild build scripts.

**For workflow guidance** (when to add clips, how to set Ken Burns presets, preview/render loop, snapshot handoff patterns), see `pr0ta-timeline`. This file documents the API shapes the timeline skill relies on.

Paths below are relative to the project's post-production prefix (UUID or slug), for example `/timeline` is `GET /api/post-production/{project_id}/timeline`.

## Timeline State

```
GET /timeline                    — Returns the main sequence
POST /timeline                   — Save/merge timeline-level fields (merges submitted keys into existing state; does not replace omitted keys)
PATCH /timeline                  — Partial update of timeline-level fields (preferred for targeted changes)
POST /sequences                  — Create a named empty sequence with optional dimensions
POST /sequences/{sequence_id}/duplicate — Duplicate a sequence with clips intact
GET /timeline/state?sequence_id=timeline_v2   — Normalized state + _clip_index
GET /timeline/clips?sequence_id=timeline_v2   — Flattened clip list with track metadata
GET /timeline/debug-report?sequence_id=timeline_v2   — Render-risk diagnostics for agents
```

`PATCH /timeline` merges submitted keys into existing state — submitting `{ "audioMix": { ... } }` updates `audioMix` without touching clips or snapshots. `POST /timeline` replaces the sequence and requires a full `tracks` array. Both return `sequence_id`, updated `version` (integer), and `lastSaved` (ISO 8601 datetime with timezone offset, e.g. `2026-04-12T19:39:30.991013+00:00`). Prefer `PATCH` for single-field updates.

### Create Fresh Sequence

When a review cut has accumulated bad patch state, create a clean sequence instead of continuing to mutate the old one. Field-tested triggers: more than one structural review revision, one-frame diagnostics that move after each patch, audio patch artifacts twice, stale narration/patch tracks, orphan tracks, muted keyframe remnants, or duplicate semantic shot families.

```http
POST /api/post-production/{project_id}/sequences
Content-Type: application/json
```

```json
{
  "sequence_id": "review_v4_clean",
  "name": "Review v4 Clean",
  "sequence": { "width": 1080, "height": 1920, "frameRate": 30 }
}
```

`POST /sequences` does not accept custom tracks, audio mix, or metadata. Save those in a complete payload after the empty sequence exists:

```http
POST /api/post-production/{project_id}/timeline?sequence_id=review_v4_clean
Content-Type: application/json
```

```json
{
  "name": "Review v4 Clean",
  "sequence": { "width": 1080, "height": 1920, "frameRate": 30 },
  "tracks": [
    { "id": "video", "type": "video", "label": "Video", "clips": [] },
    { "id": "dialogue", "type": "audio", "label": "Narration", "clips": [] },
    { "id": "music", "type": "audio", "label": "Music", "clips": [] }
  ],
  "audioMix": {
    "ducking": [
      { "sourceTrack": "music", "keyTrack": "dialogue", "duckedGain": 0.35, "attackMs": 300, "releaseMs": 500 }
    ]
  },
  "metadata": {
    "reason": "review-rebuild",
    "sourceSequenceId": "timeline_v2"
  }
}
```

Then add clips to `review_v4_clean` using frame-native timing and render/export with `sequence_id=review_v4_clean`. Record `sequence_id`, render task ID, export asset ID, review round ID, and review URL in the production ledger.

To preserve settings, audio mix, metadata, or track definitions, read the source sequence first, copy only the intended fields into the complete new payload, and save it to the new `sequence_id`. Use `POST /sequences/{sequence_id}/duplicate` when you want a full copy with all clips intact.

### Map a Review Timestamp to Clips

Fetch the flattened clip list:

```http
GET /api/post-production/{project_id}/timeline/clips?sequence_id=review_v4_clean
```

Select every returned clip whose `start <= review_time < end`, then prefer a `video` or `title` entry with `trackMuted: false` for the primary visual. `end` is the exclusive rendered-program boundary. If no clip overlaps, compute the nearest boundary and label that result as nearest rather than active. Returned entries include clip/asset data, track ID/alias/type/label/mute state, and normalized timing metadata.

### Sequence Settings

Set sequence dimensions before clip assembly and always target the rendered sequence explicitly:

```http
PATCH /api/post-production/{project_id}/timeline?sequence_id=timeline_v2
Content-Type: application/json

{
  "sequence": { "width": 1080, "height": 1920, "frameRate": 30 }
}
```

Omitting `sequence_id` when changing `sequence` returns `400 sequence_id_required`. The canonical editable/rendered sequence is `timeline_v2`, and render status payloads should report the same `full_payload.sequence` used for the completed MP4.

**PATCH accepts two shapes:**

Flat patch (fields at top level):
```json
{ "audioMix": { "ducking": [...] } }
```

Wrapped patch (fields under `updates` key):
```json
{ "updates": { "audioMix": { "ducking": [...] } } }
```

Both are accepted. **Do not mix them** — sending both `"updates": {...}` and top-level fields in the same request returns `400 invalid_field`.

## Track Creation

```
POST /timeline/tracks?sequence_id=timeline_v2   — Create an empty track
```

**Request body:**
```json
{
  "id": "dialogue",
  "type": "audio",
  "label": "Dialogue",
  "position": 2
}
```

- `id` — stable, caller-controlled identifier (e.g. `dialogue`, `music`, `sfx`)
- `type` — `video`, `audio`, or `title`
- `label` — human-readable display name
- `position` — optional; if omitted, the track is appended after existing tracks

Creates an empty track only. Add clips separately via `POST /timeline/clips`.

**Use this instead of rewriting the full `tracks[]` array through `PATCH /timeline`.** The PATCH approach is error-prone because stale `tracks[]` payloads can restore deleted clips.

**Core rule: concurrent audio on separate tracks.** Overlapping audio clips on the same track are invalid. The renderer will fail with a clear error. Always create separate tracks for narration, music, and SFX.

## Track Targeting (NLE Aliases and Selectors)

```
GET /timeline/tracks?sequence_id=timeline_v2   — Read track metadata with aliases
PATCH /timeline/tracks/{track_id_or_alias}?sequence_id=timeline_v2  — Rename, lock, reposition
```

Track reads now return NLE-style aliases alongside raw IDs:

```json
{
  "id": "dialogue",
  "type": "audio",
  "label": "Dialogue",
  "alias": "A1",
  "aliases": ["A1"],
  "index": 2,
  "kindIndex": 0,
  "clipCount": 1,
  "locked": false,
  "muted": false,
  "solo": false,
  "enabled": true
}
```

**Track selectors** — anywhere a track is referenced, these three forms are accepted:

- **Raw ID:** `dialogue`, `music`, `video`, `overlay` — stable, use in persisted scripts
- **NLE alias:** `V1`, `V2`, `A1`, `A2` — familiar to editors, use for human-readable commands
- **Unique label:** `Dialogue`, `Music` — rejected with an ambiguity error if duplicated

**Selector-aware fields** across the API:

- `POST /timeline/clips` → `placement.track_id` / `placement.track`
- `PATCH /timeline/clips/{clip_id}` → `track_id`
- `POST /timeline/clips/reorder` → operation `track_id`
- `POST /timeline/edits` and `/preview` → `track`, `affectedTracks`
- `POST /timeline/edits/{clip_id}/trim` and `/preview` → `affectedTracks`
- Linked moves → `linkedTrackMap` / `trackMap` values
- Audio preview/meter/render → `tracks=` solo list

**Track PATCH** — rename, lock, or reposition a track:

```json
{
  "label": "Production Dialogue",
  "locked": true,
  "position": 2
}
```

Protected fields that cannot be patched: `id`, `type`, `clips`, `alias`, `aliases`, `index`, `kindIndex`.

**Skill guidance:** Before any multi-track edit, call `GET /timeline/tracks`, build a local `{alias → id, label → id}` mapping, and use raw IDs in persisted scripts. Use aliases for human-readable commands and labels only when unique.

## Clip CRUD

```
POST /timeline/clips?sequence_id=timeline_v2   — Create a clip (asset ID, track, position, in/out, kenBurns)
PATCH /timeline/clips/{clip_id}?sequence_id=timeline_v2  — Update properties, move between tracks
DELETE /timeline/clips/{clip_id}?sequence_id=timeline_v2&ripple=true|false  — Delete with optional ripple
POST /timeline/clips/reorder?sequence_id=timeline_v2  — Batch reorder/placement
```

**Canonical `POST /timeline/clips` payload:**

```json
{
  "clip": {
    "assetId": "asset_123",
    "start": 0,
    "duration": 2.5,
    "kenBurns": { "preset": "push_in" }
  },
  "placement": {
    "track_id": "video",
    "position": 0
  }
}
```

Clip data is nested under a `clip` key; placement under a `placement` key. Use `track_id` (not `track`) in placement. Legacy flat payloads (clip and placement fields mixed at the top level) may still be accepted for compatibility but are not the documented contract.

**`POST /timeline/clips` always creates a new clip — it does not upsert.** If you append clips iteratively via POST and don't track the returned `clip_id`, you will duplicate clips. Use `PATCH /timeline/clips/{clip_id}` for updates. Field-observed failure mode: ~30 intended clips ballooned to 72 after iterative append-only POSTs.

**Retiming rule:** Prefer `POST /timeline/edits` with `fitToFill: true` for editorial retiming. Raw `POST /timeline/clips` can create a retimed clip only when you provide a clear source range (`outPoint` or `sourceMedia.duration`) or an explicit non-zero `speed`; otherwise it returns a 4xx validation error. Do not rely on implicit retiming. Before render, `fitToFill` clips must have `(sourceOutPoint - sourceInPoint) / speed` covering `programDuration` within frame tolerance; otherwise the render path should fail or warn instead of producing a transparent/checkerboard tail.

**Clip-level timing fields:**
- `start` — clip start position on the timeline in seconds (authoritative).
- `duration` — clip playback duration in seconds (authoritative).
- `startFrame` / `durationFrames` — frame-native inputs accepted by clip create/update and resolved against the sequence frame rate into canonical seconds.
- `start_ms` / `duration_ms` — millisecond-precision equivalents (`start_ms = start × 1000`). These are compatibility/precision helpers, not a separate model. Do not assume `start` is always `0.0` or `duration` is always `1.0`.
- `in_point` / `out_point` — trim points within the source asset.
- `sourceInFrame` / `sourceOutFrame` — frame-native source trim inputs accepted by clip create/update and resolved into `inPoint` / `outPoint`.
- `fitToFill` / `speed` — explicit retime state when a source range is stretched/compressed to a program duration. A negative `speed` plays the clip reversed at `|speed|` (head = out point, tail = in point; `0` is refused). Changing `speed` through the clip PATCH keeps the frames that play (unless the update also sets the source points), measured on the clip as the PATCH leaves it: `{"speed": -1, "duration": 8}` reverses the 8 s the clip will play, not the 4 s it played before. It applies to the clip's same-media linked partners (link group or legacy `linkedClipId`); a partner whose duration equalled the clip's takes the new duration too, and partners on locked tracks are left alone. A reversed clip slips by `−delta·|speed|`; see `reference/source-shortfalls-and-fit-to-fill.md` → "Reversed Clips".
- `kenBurns` — Ken Burns motion (see below).
- `transition` — an object, never a bare name: `{"type": "dissolve", "duration": 0.5}` with `duration` in seconds (0 < duration ≤ 10). `null` removes it. Types, which clip carries each, defaults, and adjacency rules: `pr0ta-timeline` → "Transitions".
- `sourceGroup` / `source_group` / `usageFamily` / `usage_family` — optional semantic reuse family. Timeline analysis reports `semanticReuse[]` when a source family appears in multiple clips even if asset IDs differ.

Clip reads/lists expose retime diagnostics when known: `fitToFill`, `frameSafeFitToFill`, `speed`, `sourceDuration`, `programDuration`, `renderedProgramFrames`, `renderedProgramDuration`, `startFrame`, `endFrame`, `endFrameInclusive`, `sourceInFrame`, `sourceOutFrame`, `sourceInPoint`, `sourceOutPoint`, `sourceSpan`, `effectivePlaybackDuration`, and `retimeReason`.

**Clip metadata (read-only, present on `GET /timeline`):**
- `sourceMedia.width` / `height` — original media dimensions (when known from asset metadata).
- `sourceMedia.aspectRatio` — human-readable reduced aspect ratio string (e.g. `1:1`, `4:3`, `16:9`, `9:16`).
- `sourceMedia.duration` — source asset duration in seconds (when known).
- `sourceMedia.fitsSequence` — `true` if source aspect ratio matches sequence aspect ratio within tolerance; `false` if mismatch (pillarbox/letterbox likely); `null`/omitted if dimensions unavailable.
- `generation_context.prompt` — best-effort originating prompt (truncated for timeline use).
- `generation_context.model` — best-effort originating model ID/name.

These fields allow skills to audit a cut for aspect-fit issues and explain clip provenance without calling `GET /assets/{id}` per clip.

## Ken Burns as a Clip Property

**The agent never writes zoompan expressions.** Ken Burns is a clip property — the platform renders it with super-resolution, FPS consistency, and duration-aware motion internally.

```json
{ "kenBurns": { "preset": "push_in" } }
```

Presets the renderer knows: `push_in`, `pull_back`, `drift_left`, `drift_right`, `hold`. Any other preset name renders as `hold`.

Custom parameters (when presets don't fit):
```json
{ "kenBurns": { "start_zoom": 1.0, "end_zoom": 1.15, "pan": [0, 0] } }
```

`start_zoom` and `end_zoom` are clamped to 0.1–10 and `pan` values to −1..1. Motion is linear; there is no easing field. At render time, still-image clips with `kenBurns` metadata emit MLT `affine` filters, and the platform handles FPS and dimension normalization. When to use which: `pr0ta-timeline` → "Ken Burns as a Clip Property".

## Audio Mix Properties

Audio mixing is a timeline-level property stored in `timeline.audioMix`. Set it via `POST /timeline` or `PATCH /timeline`:

```json
{
  "audioMix": {
    "ducking": [
      {
        "sourceTrack": "music",
        "keyTrack": "dialogue",
        "duckedGain": 0.35,
        "attackMs": 300,
        "releaseMs": 500
      }
    ],
    "narrationOffsetMs": 1500
  }
}
```

**`ducking` is an array of rules.** Each rule defines one ducking relationship. Multiple rules can coexist (e.g. music ducks under dialogue, SFX ducks under narration).

**`duckedGain` is the canonical ducking field.** It is the fraction of nominal source-track volume while the key track is active: `1.0` = no ducking, `0.5` ≈ −6 dB, `0.0` = full mute. The old `threshold` field is a deprecated alias — the backend normalizes it to `duckedGain`.

**camelCase is the documented standard** for all audioMix fields (`sourceTrack`, `keyTrack`, `duckedGain`, `attackMs`, `releaseMs`, `narrationOffsetMs`). Legacy snake_case forms may still be accepted for compatibility.

**Render behavior:** Ducking renders as generated gain automation on affected clips (animated MLT gain envelopes). Clip and track volume automation render through the same envelope system. Adjacent crossfades and dissolves are synthesized at render time via overlay playlists. This is gain-envelope-based ducking, not a true sidechain compressor graph — but it produces clean ducking in rendered output.

## Audio Level Keyframes (`volumeKeyframes`)

Skills can read and write audio level automation at two levels:

- **Track-level automation** — keyframe times are absolute program/timeline time. Use for broad mix moves on a lane (lower the music bed during narration, ramp SFX under a title).
- **Clip-level automation** — keyframe times are relative to clip start. Use for source-specific moves that travel with the clip (fade in a music clip, boost dialogue at the end).

The renderer multiplies both: `final gain = track gain at program time × clip gain at clip-relative time`.

### Writing Track-Level Keyframes

```
PATCH /api/post-production/{project_name}/timeline/tracks/{track_id_or_alias}?sequence_id=timeline_v2
```

```json
{
  "volumeKeyframes": [
    {"time": 0.0, "value": 1.0},
    {"time": 20.0, "value": 1.0},
    {"time": 21.0, "value": 0.45},
    {"time": 35.0, "value": 0.45},
    {"time": 36.0, "value": 1.0}
  ]
}
```

### Writing Clip-Level Keyframes

```
PATCH /api/post-production/{project_name}/timeline/clips/{clip_id}?sequence_id=timeline_v2
```

```json
{
  "volumeKeyframes": [
    {"time": 0.0, "value": 0.0},
    {"time": 2.0, "value": 1.0},
    {"time": 18.0, "value": 1.0},
    {"time": 20.0, "value": 0.25}
  ]
}
```

### Keyframe Fields

- `time` — seconds (program-time for tracks, clip-relative for clips).
- `value` — linear gain multiplier: `1.0` = unchanged, `0.5` ≈ −6 dB, `0.0` = silence, `2.0` ≈ +6 dB. Clamped to `0.0–4.0`. Negative numeric `value`/`volume`/`gain`/`level` values are interpreted as dB attenuation, so `{"value": -12}` becomes approximately `0.251` linear gain instead of silence.
- `interpolation` — `linear` (default) or `hold`.

### Value Aliases

The backend also accepts `volume`, `gain`, `level` as synonyms for `value`, and `db`/`decibels` for dB input (converted to linear gain). Time can be passed as `timeSeconds` or `time_seconds`.

### Compatibility Aliases

The backend normalizes these field names to `volumeKeyframes`: `audioLevelKeyframes`, `levelKeyframes`, `gainKeyframes`, `audio.volumeKeyframes`, `audio.audioLevelKeyframes`, `audio.levelKeyframes`, `audio.gainKeyframes`, `audio.keyframes`. Always send `volumeKeyframes` in new code.

### Interaction With Ducking

Ducking (`audioMix.ducking`) generates additional clip-level `volumeKeyframes` on the ducked source clips. If both manual keyframes and ducking are present, PR0TA merges/normalizes keyframes and the rendered gain envelope reflects the combined automation. Use `audioMix.ducking` for automatic dialogue-aware ducking. Use `volumeKeyframes` for intentional manual mix moves. For precise manual control, prefer explicit `volumeKeyframes` over ducking.

After applying music automation, inspect `/audio/analyze` `render_gain_envelope`, then verify with `/preview/audio`, `/audio/meter`, or a short render around at least one narration gap. Inspect the waveform or run a silence check; the music bed should remain audible where narration is absent.

### When to Use Track vs Clip

| Instruction pattern | Level | Example |
|---|---|---|
| "lower the music during the narration" | Track | `PATCH /tracks/music` |
| "bring all production audio down after the cut" | Track | `PATCH /tracks/production` |
| "fade this music clip in over 2 seconds" | Clip | `PATCH /clips/{clip_id}` |
| "make this dialogue clip louder at the end" | Clip | `PATCH /clips/{clip_id}` |
| "dip this specific production-audio segment" | Clip | `PATCH /clips/{clip_id}` |

## Preview, Audio Preview, and Render

```
GET /preview?from={seconds}&to={seconds}&sequence_id=timeline_v2
    — Video+audio preview render (defaults to full sequence resolution)
GET /preview/audio?from={seconds}&to={seconds}&sequence_id=timeline_v2
    — Audio-only preview render (.wav), no picture cost
GET /audio/analyze?from={seconds}&to={seconds}&sequence_id=timeline_v2
    — Render-envelope audio prediction (levels, ducking, mix balance), no media render
GET /audio/meter?from={seconds}&to={seconds}&sequence_id=timeline_v2
    — Actual LUFS/LRA/true-peak metering (renders audio via MLT + ffmpeg ebur128)
POST /render
    — Preview render (loads saved timeline automatically; control-only body is valid)
POST /export
    — Final export (master delivery render)
GET /render/{task_id}/status
    — Poll preview/export render progress
```

### Preview Quality

If `quality` is omitted, preview renders at the **saved sequence resolution** (e.g. 1080×1920 for a vertical project). Supported values:

- `quality=full` — sequence resolution (same as omitting)
- `quality=low` or `quality=preview` — half-res lightweight preview

For fast iteration, send `quality=low`. For pixel-accurate checks, omit it or send `quality=full`.

### Render Preview

`POST /render` is the **preview-task route** used by the toolbar workflow. It is not the final-export endpoint.

If the request body contains only render-control fields, the backend loads the saved post-production sequence automatically:

```json
{}
{"from": 0, "to": 212}
{"resolution": "full"}
{"quality": "full", "width": 1080, "height": 1920, "format": "mp4"}
```

You do not need to send full timeline JSON. The route queues a `timeline_render` task.

**Error behavior:**
- `400` if the resolved timeline has zero clips (instead of queueing a stub render)
- `503` if required render tooling (MLT) is unavailable

### Final Export

`POST /export` is the **final-export route** for master delivery renders. It renders exactly the saved sequence named by `sequence_id`; a request whose inline `timeline_data` differs from the saved content is refused with `400 export_requires_saved_sequence` (save first). A render with `from`/`to` is stamped `render_range` and never counts as verification.

Use `POST /render` for preview-task rendering during editorial iteration. Use `POST /export` when the cut is locked and ready for final delivery.

### Audio-Only Preview

Returns a background task payload (like existing preview/export endpoints) that renders a `.wav` preview instead of an `.mp4`. Use when you need to hear the mix without paying for video rendering.

**Optional `tracks` parameter:** `?tracks=dialogue,music` — solo only the specified audio track IDs in the preview mix.

### Audio Analysis (No Render)

Returns an approximate analysis of audio levels, ducking impact, and mix balance without rendering any media. Best used to answer: is narration louder than music? Did ducking attenuate a track? Is a segment effectively silent?

**Optional `tracks` parameter:** `?tracks=dialogue,music` — analyze only the specified tracks.

**Response shape:**
```json
{
  "analysis_type": "approximate",
  "duration": 30.0,
  "window": { "from": 0.0, "to": 30.0, "sequence_id": "timeline_v2", "solo_track_ids": ["dialogue", "music"] },
  "tracks": [
    {
      "id": "dialogue",
      "label": "Dialogue",
      "muted": false,
      "solo": false,
      "volume": 1.0,
      "segments": [
        {
          "clip_id": "clip_123",
          "label": "Narration",
          "from": 0.0,
          "to": 12.0,
          "asset_url": "/api/assets/...",
          "muted": false,
          "source_mean_db": -20.1,
          "source_peak_db": -3.2,
          "clip_volume": 1.0,
          "track_volume": 1.0,
          "envelope_average_gain": 1.0,
          "ducking_applied": false,
          "predicted_mean_db": -20.1,
          "predicted_peak_db": -3.2
        }
      ]
    }
  ],
  "mix": { "predicted_mean_db": -19.7, "predicted_peak_db": -2.4 }
}
```

This analysis is a render-envelope prediction — it uses source-asset loudness plus the same frame/gain envelope path used by MLT render, and each segment includes `render_gain_envelope`. It is useful for mix iteration and debugging, not mastering-grade measurement.

### Audio Metering (Actual Loudness)

`GET /audio/meter` renders audio-only through MLT and measures with `ffmpeg ebur128`. This is **actual** loudness metering, not the predictive source-loudness estimate from `/audio/analyze`.

**Query params:** `sequence_id`, `from`, `to`, `tracks` (comma-separated IDs to solo), `format` (default: `lufs`).

**Response shape:**
```json
{
  "analysis_type": "actual",
  "format": "lufs",
  "duration": 212.0,
  "window": { "from": 0.0, "to": 212.0, "sequence_id": "timeline_v2", "solo_track_ids": ["dialogue", "music"] },
  "integrated_lufs": -16.2,
  "range_lu": 4.8,
  "true_peak_dbfs": -1.1,
  "short_term_lufs_timeline": [
    {"time": 0.4, "lufs": -19.8},
    {"time": 0.8, "lufs": -18.4}
  ]
}
```

Use `/audio/meter` when you need to verify the mix meets loudness spec (e.g. −14 LUFS for streaming, −24 LUFS for broadcast). Use `/audio/analyze` for quick render-envelope checks during iteration.

**Error behavior:** `503` if MLT/render tooling is unavailable, `400` for invalid request windows or parameters, `404` if the referenced sequence does not exist.

### Escalation pattern

1. `/audio/analyze` — instant render-envelope diagnostic (no media render)
2. `/audio/meter` — actual LUFS/LRA/true-peak metering (audio render required)
3. `/preview/audio` — ear-based review (audio render, listenable `.wav`)
4. `/preview` — full picture+sound verification (video render)

Only escalate to full video preview once the mix is plausibly correct.

**Known issue: nested-asyncio server-render bug.** If a full render returns `"Cannot run the event loop while another loop is running"`, retry the render or fall back to exporting the preview at the full range. Platform fix tracking separately.

## Timeline History and Snapshots

```
GET /timeline/history?sequence_id=timeline_v2   — Recent mutation history (reverse chronological)
POST /timeline/snapshot?sequence_id=timeline_v2  — Create/replace a named snapshot
GET /timeline/snapshots?sequence_id=timeline_v2  — List saved snapshots
POST /timeline/snapshot/{name}/restore?sequence_id=timeline_v2  — Restore a snapshot
GET /timeline/snapshot/{name}/diff?sequence_id=timeline_v2  — Diff vs snapshot (added/removed/modified clips)
```

Creating a snapshot does not change the sequence `version` and broadcasts no `timeline_sequence_saved` event (it returns `{name, created_at, state, version}`, `version` being the version captured); restoring one saves a new version and broadcasts it. A snapshot that keeps losing a race with concurrent writes answers `409 stale_write`; retry it. Snapshots and history are held by the server: any `snapshots` or `history` sent with a save (`POST` or `PATCH /timeline`, `post_sequence_save`) is ignored and the stored ones are kept.

A rename (`PATCH /sequences/{sequence_id}` with `{"name": "...", "baseVersion": <the version you hold>}`) saves a new version and returns `{success, sequence_id, version, name}`; adopt that version only from a successful answer. With `baseVersion`, a sequence that has moved on answers `409 stale_write` with `current_version` (reload, then rename again). Without `baseVersion` the rename is unconditional.

**Collaboration pattern:** The agent creates a snapshot before handing off to the user. The user makes changes in the browser. The agent diffs against the snapshot to see exactly what changed, then addresses remaining notes without re-reading the entire timeline.

## Timing and Duration Semantics

**Sequence-level duration** is the total length of the edited sequence, derived from the last clip's end time. It is not a field you set; it is computed from the clip arrangement.

**Clip-level timing** is authoritative and expressed in seconds (`start`, `duration`). The ms-precision fields (`start_ms`, `duration_ms`) are `start × 1000` and `duration × 1000` respectively — compatibility/precision helpers, not a separate conflicting model. When both are present, treat seconds fields as canonical.

**Timestamp fields** across the timeline API (including `lastSaved`, `history[].timestamp`, `snapshots[].created_at`) are ISO 8601 datetimes with timezone offsets, e.g. `2026-04-12T19:39:30.991013+00:00`.

## Data Model

The timeline schema includes:
- `clip.kenBurns` — per-clip Ken Burns motion metadata
- `clip.start` / `clip.duration` — clip timing in seconds (authoritative); `clip.start_ms` / `clip.duration_ms` as ms-precision equivalents
- `clip.sourceMedia` — source-media metadata, recomputed on every save from the asset's measurements (`assets_probe`): `width`, `height`, `aspectRatio`, `duration`, `fitsSequence` (false when the source's shape differs from the sequence frame), `fps`, `hasAudio`, and for a trimmed asset `sourceAssetId`, `sourceInPoint`, `sourceOutPoint` (the original file and the slice's place in it)
- `clip.fit` — `contain` (absent; whole source, bars where shapes differ), `cover` (fill, crop overflow) or `stretch`, applied to video and image clips before `clip.transform`
- `clip.transform` — `scale` (1.0 = fitted size), `positionX`/`positionY` (fractions of frame width/height), `rotation`, `opacity`, plus keyframes; applied on top of the fitted frame
- `clip.text` — on title-track clips with no asset: `content`, `role` (`title`, `caption`, `lower_third`), `position`, `fontFamily`, `fontSizePct` (of frame height), `color`, `background`, `align`, `bold`, `maxWidthPct`, `safeArea`. Burned in at render; captions also export as SRT. `pr0ta-timeline` → "Text and Captions"
- `clip.audioEnabled`, `clip.muted`, `clip.linkedClipId` — a video clip's own sound plays unless `audioEnabled` is false, `muted` is true, or a linked audio clip of the same asset replaces it (`linkedClipId` either way, or a shared `linkGroupId`); never both
- `clip.generation_context` — generation provenance: `prompt` (truncated), `model`
- `clip.linkGroupId` — optional; present when the clip belongs to a link group (see `reference/editorial-primitives.md`)
- `clip.volumeKeyframes` — clip-level audio automation (clip-relative time, linear gain). See "Audio Level Keyframes".
- `track.volumeKeyframes` — track-level audio automation (absolute program time, linear gain). See "Audio Level Keyframes".
- `timeline.audioMix` — ducking rules (array), narration offset, volume automation
- `timeline.audioMix.ducking[]` — array of `{sourceTrack, keyTrack, duckedGain, attackMs, releaseMs}` rules
- `timeline.origin` — provenance metadata (e.g., materialized from narration timeline)
- `timeline.provenance` — who made the cut and its review state: `author` (`user`, `operator`, `agent`), `authorName`, `missionId`, `intent`, `deliverable`, `status` (`draft`, `in_review`, `approved`, `changes_requested`), `notes[]`, `flags[]` (e.g. `do_not_publish`), `approvedVersion`, `reviewedBy`, `reviewedAt`, `updatedAt`. Kept across saves that omit it; agents set it through `post_sequence_save`'s `provenance` argument and never approve. `status`, `approvedVersion`, `reviewedBy` and `reviewedAt` are server-held: only `POST /timeline/review?sequence_id=` (`{decision: approve|request_changes|reopen, note?, baseVersion}`, signed-in user in the app; agents, MCP OAuth tokens and personal access tokens get 403; no `baseVersion` → 428 `base_version_required`, an older one → 409 `stale_write`) sets them, and a save that changes the cut's content returns an approved or changes-requested cut to `in_review`. `flags` are add-only for every writer except the user's own session in the app: a REST, PAT, MCP or Operator save cannot remove `do_not_publish`
- `timeline._clip_index` — indexed clip lookup map
- `timeline.history` — mutation log; each entry has `timestamp` (ISO 8601)
- `timeline.snapshots` — named checkpoint states; each has `created_at` (ISO 8601)

For **asset marks**, **program marks**, **3-point edits**, **trim operations**, and **clip link groups**, see `reference/editorial-primitives.md`.
