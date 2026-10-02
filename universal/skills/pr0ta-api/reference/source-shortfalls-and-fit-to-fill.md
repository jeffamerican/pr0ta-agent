## Source Shortfalls and Fit To Fill

PR0TA treats too-short source media like a professional NLE: it cuts only the available source and leaves a real timeline gap for the unfilled tail. Retiming is never implicit — it must be requested explicitly via `fitToFill`.

For generated I2V card edits, compare the generated source duration to the intended beat duration before placement. If the source is shorter, either generate/extend a long enough animation or place it through `/timeline/edits` with `fitToFill: true`. Do not place a 3-5s animation into an 8-10s beat through raw clip creation and hope the renderer will pad it.

Renderer contract: a valid `fitToFill` clip must have enough source range, after applying `speed`, to cover the requested program duration. PR0TA computes fit-to-fill against rendered frame duration, not just raw decimal seconds, so sub-frame tails are treated as real render risks. If the renderer cannot cover the full requested range, render preparation should fail or surface a warning instead of silently producing a transparent/checkerboard tail.

Never solve short media by holding the last frame to the render end. Use a deliberate generated extension, a different source, a trim, or explicit retiming.

---

### Default Behavior: Source-Accurate Edits

When the requested program range is longer than the available source media, PR0TA inserts only the available source and leaves a gap.

**Example:** If `asset_short` is 3 seconds long and the edit requests 5 seconds:

```json
{
  "mode": "overwrite",
  "track": "V1",
  "source": {"assetId": "asset_short", "in": 0},
  "program": {"in": 52.0, "out": 57.0},
  "label": "Short source edit"
}
```

The inserted clip is 3 seconds. The interval from 55.0 to 57.0 remains a real timeline gap.

**Edit response includes a `source_shortfall` warning:**

```json
{
  "edit": {
    "computed": {
      "source": {"assetId": "asset_short", "in": 0.0, "out": 3.0},
      "program": {"in": 52.0, "out": 57.0},
      "clipDuration": 3.0,
      "editDuration": 5.0,
      "fitToFill": false
    },
    "warnings": [
      {
        "kind": "source_shortfall",
        "assetId": "asset_short",
        "requestedDuration": 5.0,
        "insertedDuration": 3.0,
        "availableSourceDuration": 3.0,
        "shortfallDuration": 2.0,
        "gapStart": 55.0,
        "gapEnd": 57.0
      }
    ]
  }
}
```

**Skill guidance:**

- Treat `source_shortfall` as user-visible editorial information — always surface it.
- Do not assume PR0TA filled the duration with a freeze frame. It did not.
- If the user did not ask for retiming, preserve the gap and report it.
- If the user wants the gap filled, offer retiming (`fitToFill`) or a different media choice.

---

### Timeline Analysis: Source Shortfalls

`GET /api/post-production/{project_name}/timeline/analysis?sequence_id=timeline_v2`

The analysis response includes source-shortfall diagnostics in `summary.sourceShortfallCount` and the `sourceShortfalls[]` array:

```json
{
  "summary": {
    "gapCount": 3,
    "reusedMediaCount": 2,
    "sourceShortfallCount": 1,
    "shortVisualClipCount": 0
  },
  "sourceShortfalls": [
    {
      "kind": "source_shortfall",
      "clipId": "clip_short",
      "label": "Short source edit",
      "trackId": "video",
      "trackLabel": "Primary Video",
      "trackType": "video",
      "assetId": "asset_short",
      "requestedDuration": 5.0,
      "availableSourceDuration": 3.0,
      "shortfallDuration": 2.0,
      "authoredDuration": 5.0,
      "requiredFrames": 150,
      "availableFrames": 90,
      "gapStart": 55.0,
      "gapEnd": 57.0,
      "speed": 1.0,
      "fitToFill": false,
      "renderRisk": "transparent_or_checkerboard_tail",
      "recommendation": "Use fitToFill=true on a three-point edit or set clip speed explicitly if retiming is desired."
    }
  ]
}
```

**Recommended skill behavior before render/export:**

1. Call `/timeline/analysis`.
2. If `summary.sourceShortfallCount > 0`, warn the user.
3. Present the affected clips, tracks, and gap intervals.
4. Treat `renderRisk: "transparent_or_checkerboard_tail"` as a visible failure risk, especially for image-labeled I2V videos.
5. Ask whether to leave the gap, choose another source, generate/extend a longer clip, or retime with fit-to-fill.

For complete agent preflight, call:

```
GET /api/post-production/{project_name}/timeline/debug-report?sequence_id=timeline_v2
```

The debug report bundles track coverage, primary visual gaps, source-duration-vs-program-duration, retime state, audio asset presence, keyframe counts, and render-risk warnings in one response.

Render and export results always include explicit diagnostic arrays, even when empty. Classify each warning before repair:

- `timelineMediaGaps[]` plus `renderWarnings[]` entries with `code: "timeline_media_gap"` — deterministic timeline/media-coverage failures: rendered frames where no visual media source covers the program interval. The detector works in rendered frames and ignores a one-frame sub-frame rounding tail, so normal editorial math does not become a false short trim.
- `renderedPixelGaps[]` plus `renderWarnings[]` entries with `code: "rendered_pixel_gap"` — post-render exact-frame probes around clip boundaries found suspicious pixels. These entries include `start_frame`, `end_frame`, `start_timecode`, `end_timecode`, `duration_frames`, `clip_id`, `track_id`, confidence, and usually a thumbnail.
- `transparentOutputFrames[]` — one item per bad rendered frame with `frame` / `frame_index`, `time_seconds`, `timecode`, `expectedClipId`, `expectedClipLabel`, `assetId`, `trackId`, confidence, and thumbnail when available. Use this for frame-by-frame repairs and review annotation matching.

Classify rendered-pixel findings as one of: actual transparent/checkerboard frame, expected matte/pillarbox/letterbox around intentionally contained artwork, source-tail media gap, or uncertain. Actual transparent/checkerboard and source-tail gaps are hard failures. Expected matte is a warning/adjudication item, not automatically a missing-frame failure. Do not clear uncertain warnings without thumbnail/frame evidence.

---

### Frame-Native NLE Timing

PR0TA stores picture edits as standard NLE-style half-open frame intervals:

- program range: `[startFrame, endFrame)`
- `endFrameInclusive = endFrame - 1`
- seconds fields are derived from the sequence frame rate
- source trims use `sourceInFrame` / `sourceOutFrame` when frame-native fields are supplied

On save and render, video/title tracks are normalized onto integer frames. Adjacent same-track picture cuts with a 1-2 frame authored gap are snapped closed by extending the outgoing side to the incoming cut frame; adjacent 1-2 frame overlaps are snapped by trimming the outgoing side. This preserves the incoming cut point because narration and beat-aligned incoming frames own the next beat. It is an editorial drift correction, not a creative hold or freeze. Do not create or request "hold last frame to render end" behavior.

For repairs from review notes, prefer frame-native inputs (`startFrame`, `durationFrames`, `sourceInFrame`, `sourceOutFrame`) and verify clip reads expose matching `startFrame`, `endFrame`, and `durationFrames`.

### Beat-Locked Overlap Repair

For beat-accurate social-video cuts, do not pull the incoming shot earlier to hide a boundary artifact unless the user explicitly asks for a timing change. The canonical repair is:

```text
incoming.startFrame = exact beat/cut frame
outgoing.endFrame = incoming.startFrame + tailHandleFrames
```

Use a 4-8 frame tail handle as the default repair window. The incoming/top/latest visual owns the beat frame; the outgoing tail exists only as an underlap/handle to cover transparent source-tail behavior near the boundary. If the current timeline representation cannot express the overlap cleanly on the same track, reconform from the authoritative beat/cut list or place the handle on an appropriate lower visual layer rather than moving the incoming edit.

After reconform, treat render-level arrays as authoritative: `timelineMediaGaps`, `renderedPixelGaps`, `transparentOutputFrames`, and `renderWarnings` must all be clean. If render fails with `fitToFill clip ... cannot cover requested duration`, repair the source range/speed or regenerate/extend media; do not hide it by shifting beat-locked timeline cuts.

---

### Per-Clip Shortfall Metadata

`GET /api/post-production/{project_name}/timeline/clips?sequence_id=timeline_v2`

When a clip exceeds available source media, the clip entry includes `sourceShortfall`:

```json
{
  "id": "clip_short",
  "label": "Short source edit",
  "trackId": "video",
  "trackAlias": "V1",
  "trackType": "video",
  "trackLabel": "Primary Video",
  "duration": 5.0,
  "sourceShortfall": {
    "kind": "source_shortfall",
    "requestedDuration": 5.0,
    "availableSourceDuration": 3.0,
    "shortfallDuration": 2.0,
    "gapStart": 55.0,
    "gapEnd": 57.0
  }
}
```

Use `/timeline/clips` when working clip-by-clip. Use `/timeline/analysis` for full preflight diagnostics.

Clip reads/lists also expose retime and frame state when known: `fitToFill`, `frameSafeFitToFill`, `speed`, `sourceDuration`, `programDuration`, `renderedProgramFrames`, `renderedProgramDuration`, `startFrame`, `endFrame`, `endFrameInclusive`, `sourceInFrame`, `sourceOutFrame`, `sourceInPoint`, `sourceOutPoint`, `sourceSpan`, `effectivePlaybackDuration`, and `retimeReason`.

---

### Explicit Retiming: `fitToFill`

When the user explicitly wants the source fit to the requested program range, send `fitToFill: true` on 3-point or 4-point edits.

**Endpoints:**

```
POST /api/post-production/{project_name}/timeline/edits
POST /api/post-production/{project_name}/timeline/edits/preview
```

Raw `POST /timeline/clips` is not the canonical retiming path. It can accept `fitToFill` only when the payload also provides `outPoint`, `sourceMedia.duration`/`sourceDuration`, or an explicit non-zero `speed` (negative plays reversed); otherwise it returns a validation error so agents know to use `/timeline/edits`.

`PATCH /timeline/clips/{clip_id}` and raw clip creation accept frame-native timing fields for repairs: `startFrame`, `durationFrames`, `sourceInFrame`, and `sourceOutFrame` (snake_case aliases also work). PR0TA resolves them against the sequence frame rate and stores canonical seconds fields. Prefer these fields when repairing review annotations that already include `frame_index` and timecode.

Before render, verify the relationship:

```
effectivePlaybackDuration = (sourceOutPoint - sourceInPoint) / speed
```

For `fitToFill` clips, `effectivePlaybackDuration` must match `programDuration` within a small frame-rounding tolerance. If it does not, treat the clip as render-risk: regenerate/extend the source, adjust the source range, or redo the edit through `/timeline/edits`.

For frame-exact work, prefer `renderedProgramDuration` and `renderedProgramFrames` over hand-rounded decimals. A clip authored as `2.999s` at 30 fps still occupies 90 rendered frames (`3.0s`), and source coverage must satisfy that frame-snapped duration.

#### Three-Point Fit To Fill (Slow Motion)

Source is shorter than the program range → PR0TA slows the clip to fill:

```json
{
  "mode": "overwrite",
  "track": "V1",
  "source": {"assetId": "asset_short", "in": 0},
  "program": {"in": 52.0, "out": 57.0},
  "label": "Retimed short source",
  "fitToFill": true
}
```

If the available source is 3 seconds and the program range is 5 seconds:

```json
{
  "duration": 5.0,
  "inPoint": 0.0,
  "outPoint": 3.0,
  "fitToFill": true,
  "speed": 0.6
}
```

#### Four-Point Fit To Fill (Speed Up)

`fitToFill` also supports true four-point edits: source in/out plus program in/out.

```json
{
  "mode": "overwrite",
  "track": "V1",
  "source": {"assetId": "asset_long", "in": 0, "out": 8},
  "program": {"in": 10, "out": 14},
  "label": "Four-point fit",
  "fitToFill": true
}
```

This maps 8 seconds of source into 4 seconds of timeline:

```json
{
  "duration": 4.0,
  "inPoint": 0.0,
  "outPoint": 8.0,
  "fitToFill": true,
  "speed": 2.0
}
```

#### Speed Semantics

- `speed = 1.0` — normal speed (no retiming).
- `speed < 1.0` — slow motion. Source plays slower to fill a longer program range.
- `speed > 1.0` — speed-up. Source plays faster to fit a shorter program range.
- `speed < 0` — reversed. The clip plays its own `[inPoint, outPoint]` backwards at `|speed|`, sound included; every rule above uses `|speed|`. `speed = 0` is refused.

#### Reversed Clips

A reversed clip is anchored at its head, `top = min(outPoint, media end)` (without an `outPoint`, the implicit `inPoint + duration·|speed|`): it plays `[max(inPoint, top − duration·|speed|), top]` backwards, so its first frame is `top` and its last is the in point. When `top − duration·|speed|` is below the in point, the clip plays down to the in-point frame and is then blank (or holds that frame with `holdLastFrame`). At slow reversed speeds a head on the media's very last frame shows that frame for its first positions (as a forward clip at the same speed repeats it), so the clip never reads past the media; nothing is dropped and the clip's length is unchanged.

Edits mirror, measured from the played range `[bottom, top]` (`bottom = max(inPoint, top − duration·|speed|)`), never from a stored point outside it:
- A head trim moves `outPoint`; lengthening the head past the media end leaves `outPoint` at the media end (the extra length becomes blank or held tail). A tail trim moves `inPoint`.
- A slip by `delta` program seconds moves the played range by `−delta·|speed|` (a forward clip's points move `+delta·|speed|`), so the picture slides the same way on screen: a positive delta moves a reversed clip earlier in the source. It writes `[bottom', bottom' + (top − bottom)]`, stopping at source 0 and at the media end (a stored `outPoint` past the media end is replaced by the played top). A hold clip slips its in point the same way and keeps `top − inPoint` above it.
- Splitting at program time `t` gives `[top − (t − start)·|speed|, top]` and `[bottom, top − (t − start)·|speed|]`, both still reversed. A piece is never written below the clip's in point: a piece lying wholly in the blank tail is written `[in, in]` (no media, blank), or `[in, in + 0.001]` for a hold clip (it holds the in-point frame). A piece starting within 1 ms of the in point starts exactly on it.
- No edit writes a negative source point.
- Changing a clip's `speed` or direction (`PATCH /timeline/clips/{clip_id}` with `updates.speed`) applies to its same-media linked partners too (the picture and its own sound stay together; a linked clip of other media keeps its speed). Reversing keeps the frames that play: forward → reversed writes the forward played end as `outPoint`; reversed → forward writes `[bottom, top]` as `inPoint`/`outPoint`. If the update also sets `inPoint`/`outPoint`, the clip itself takes them as sent.

With `holdLastFrame`/`freezeFrame` the clip holds the in-point frame; trims never move that hold point, and a hold clip too short to reach it plays its range and holds nothing (no shortfall either way). Turning the hold on or off never changes the frames before the hold. Dissolve and wipe tails continue backwards into the source before the in point, or hold the in-point frame for the whole window when there isn't a full window of it; a tail never shows a frame past the media, and a clip with no media in its range has no tail. A reversed `fitToFill` clip plays, picture and its own sound, exactly the source range the same clip plays forward, backwards. A linked picture and sound playing in opposite directions are reported as `linked_av_out_of_sync`: reverse both, or neither.

#### Real Slow Motion (`clip.slowMotion`)

A clip at `|speed| < 1` shows each source frame several times (step printing): it stutters. Real slow motion uses an interpolated rendition of the source the clip plays, made on request and never automatically:

- **Make it:** `post_clip_slow_motion` (REST `POST /timeline/slow-motion?sequence_id=` with `{"engine", "clip_id", "confirm_credits"?, "idempotency_key"?}`). `engine: "draft"` (ffmpeg motion interpolation) is free and fast: judge the shot with it. `engine: "topaz"` (Topaz Apollo on Fal) is paid and for delivery: get the price first (`quote_only: true`, or `GET /timeline/slow-motion/quote?sequence_id=&clip_id=`), tell the user, then send `confirm_credits` of at least the quoted credits (without it: `428 price_confirmation_required`; a higher price since: `409 price_changed`). The charge never exceeds the quote or the credits you confirmed. A clip already covered answers `already_covered` and nothing runs; asking again while the same rendition is being made joins that task (`deduplicated: true`), whatever the key. Cancelling the task (`tasks_cancel`) stops it: nothing is attached or charged.
- **Limits (quoted as `available: false` with a `reason`):** at most 6000 rendition frames (`too_long`); Topaz takes at most 5 minutes of source (`too_long_for_topaz`), sources up to 4K, and at most about 4 minutes of 1080p24 or 1 minute of 4K24 output per run (`too_large_for_topaz`); beyond 8× at 120 fps only the draft engine applies (`too_slow_for_topaz`). Slow a shorter range, or use the draft.
- **What is made:** the played source range plus up to 0.5 s each side (within the media), retimed by `1/|speed|` to the sequence frame rate, picture only, saved as a new asset (labels `slowMotionOf`, `sourceIn`, `sourceOut`, `factor`, `engine`, `fps`). The task (`tasks_get`) then writes `clip.slowMotion = {assetId, engine, sourceIn, sourceOut, factor, fps, sourceAssetId, assetUrl, duration}` onto the clip; `result_refs.attached` and `attach_status` (`attached`, `clip_changed`, `clip_missing`, `track_locked`, `timeline_locked`, `topaz_kept` when a draft finishes after a Topaz rendition of the same clip, `no_asset_url`) say whether it did. The clip keeps its own `assetId`, points and `speed`. A long Topaz run keeps reporting progress; just keep polling.
- **When it is used:** preview and render play the rendition only while it covers what the clip plays at its current `|speed|` (factor within 1e-6) and the sequence frame rate. Change the speed, range or frame rate and the clip repeats frames again until you make a new one; a rendition whose asset was deleted counts as gone too (the render plays the original, never black). Reversed clips play it backwards; holds and dissolve or wipe tails work as before (a tail longer than the 0.5 s handle holds the rendition's last frame). Sound always comes from the original at `speed`.
- **Not eligible:** stills, text clips, compound clips and `fitToFill` clips (they retime their range to the slot; set an explicit `speed` to slow one down for real). A high-frame-rate source already at `fps / |speed|` or faster has a real frame for every slowed frame and needs none.
- **Checks:** `slow_motion_not_interpolated` (no covering rendition) and `slow_motion_draft_only`: info while editing, warnings on a final export.

#### Without `fitToFill`

Edit requests remain strict 3-point edits: exactly three of `source.in`, `source.out`, `program.in`, and `program.out` must be supplied. For frame-exact edits, use `source.inFrame`, `source.outFrame`, `program.inFrame`, and `program.outFrame` instead of floating-point seconds; they are resolved against the sequence frame rate.

Safe render option: send `avoidTransparentFrames: true` (or `diagnostics.avoidTransparentFrames: true`) to fail the render/export if `renderedPixelGaps[]` are detected. This does not hold the last frame; it fails with precise frame diagnostics so the edit can be repaired.

---

### Skill Guidance

- **Default (no `fitToFill`):** Use when the user wants source-accurate cutting and a visible/diagnosable gap. The gap appears in `/timeline/analysis` and can be addressed later.
- **`fitToFill: true`:** Use only when the user explicitly wants automatic retiming. The written `speed` value is part of the clip state and affects the renderer.
- **Manual `speed`:** Use when the user wants a specific slow-motion or speed-up value rather than automatic calculation.
- **Do not rely on freeze frames as padding.** PR0TA does not freeze-pad. If a clip is too short and `fitToFill` is not set, the tail is a real gap.
- **Do not hold the last frame to render end.** That is not an acceptable repair path. Trim, replace, retime, or generate/extend new media.
- **Do not treat accepted `fitToFill` as final proof.** Check `/timeline/clips` or `/timeline/debug-report` for `fitToFill`, `speed`, `sourceSpan`, `programDuration`, and `effectivePlaybackDuration`, then render a preview.
- **Verify frame ranges, not loose timestamps.** At 30fps, one frame is 0.033333s. Use `transparentOutputFrames[]`, `start_frame` / `end_frame`, and timecode from `renderedPixelGaps[]` or `renderFrameCoverage`, not hand-rounded seconds.
- **Adjudicate render warnings.** For every `timeline_media_gap` or `rendered_pixel_gap`, fetch or use the attached frame thumbnail, classify it as actual no-media/checkerboard, covered by another intended visual layer, or false alarm, then list the clip/timestamp repair action.

### User-Facing Copy Recommendations

When source is too short:

> The selected source only has 3.0s available, but the edit requested 5.0s. PR0TA inserted the available media and left a 2.0s gap from 55.0s to 57.0s. I can leave the gap, choose a different source, or fit the shot to the duration with a speed change.

When using `fitToFill`:

> I retimed the source to fit the requested timeline range. The clip now plays at 0.6x speed to fill 5.0s without freeze-padding.
