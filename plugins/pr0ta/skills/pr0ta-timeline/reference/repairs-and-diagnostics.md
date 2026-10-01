# Timeline Repairs and Diagnostics

> **See also:** the parent `pr0ta-timeline` SKILL.md for the workflow, `pr0ta-editorial` for when a cut is done, and `pr0ta-api` → `reference/timeline-api.md`, `reference/asset-tags-and-analysis.md`, and `reference/source-shortfalls-and-fit-to-fill.md` for response shapes.

## Contents

- Reading the diagnostics
- Adjudicating render warnings
- Frame repairs
- Source shortfalls
- Mix failures
- Rebuilding a contaminated sequence
- Handing a render to review

## Reading the Diagnostics

Three layers report problems, each at a different moment:

| Layer | When | What it reports |
|---|---|---|
| Edit responses | On each 3-point edit or trim | `source_shortfall` warnings with the gap range |
| `GET /timeline/analysis` | Before render | Gaps, overlaps, reused media, source shortfalls, frame coverage, `trackCoverage`, counts in `summary` |
| Render and export results | After render | `timelineMediaGaps[]`, `renderedPixelGaps[]`, `transparentOutputFrames` |

`GET /timeline/debug-report` adds render-risk detail for a sequence. Clip reads and lists carry retime diagnostics when known (`fitToFill`, `speed`, `sourceDuration`, `programDuration`, `effectivePlaybackDuration`, frame fields).

## Adjudicating Render Warnings

Every `timelineMediaGaps[]` and `renderedPixelGaps[]` entry is a review item, not noise.

1. Record its `startFrame`, `endFrame`, and timecode.
2. Look at the frames (a range preview around it) and keep the frame or thumbnail with your notes.
3. Classify it: a source tail shorter than its slot, a gap between clips, a transparent or checkerboard source region, or a deliberate black or silence.
4. Choose the repair (next section) and apply it by frame range.
5. Re-render and confirm the entry is gone. Do not clear a warning because a black-frame check passed; transparency and checkerboards are not black.

## Frame Repairs

Work in frames (`startFrame`, `durationFrames`, `sourceInFrame`, `sourceOutFrame`). Seconds are derived from the sequence frame rate.

- **Source tail shorter than its slot.** Trim the outgoing clip to the frames its media covers, then close the gap by extending coverage from the outgoing side, never by pulling the incoming cut early.
- **Checkerboard or transparent frames at a beat-locked cut.** Keep `incoming.startFrame` on the beat. Extend the outgoing clip 4–8 frames past the cut as a tail handle underneath; the incoming clip sits on top at the cut and the handle covers boundary sampling.
- **A one- or two-frame gap or overlap on one track.** Treat it as drift: keep the incoming cut frame and adjust the outgoing side.
- **A window longer than any take.** Generate a longer or extended take, or add a companion shot. A visible retime (`fitToFill`) is acceptable only as a deliberate choice.
- **Never** hold the last frame to fill a gap, and never let the timeline hide missing media.

After each repair, read the clips back and confirm `startFrame`, `endFrame`, `endFrameInclusive`, and `durationFrames` match the intended cut. If repairs start moving the warning from one boundary to the next, stop nudging and rebuild.

## Source Shortfalls

A shortfall is a real gap PR0TA left because the source ran out. For each one, present the clip and decide with the user when it matters to the story:

- **Leave the gap** only when it becomes a deliberate beat (a held black or silence) that the editor can name.
- **Choose another source**: overwrite the gap region with different media.
- **Generate** a longer take or a companion shot (reaction, cutaway, alternate angle).
- **Retime** with `fitToFill: true`, only for deliberate slow motion. Confirm `effectivePlaybackDuration >= programDuration` within a frame; if it does not cover the range, fix the edit instead of shipping it.

`summary.sourceShortfallCount` must be zero before a ship render (`pr0ta-editorial`, ship criterion 4).

**Reversed clips** (negative `speed`) play `[inPoint, outPoint]` backwards, sound included: the head shows the out point (or the media end, whichever comes first) and the tail ends on the in point. Repair them mirrored: a head trim moves `outPoint`, a tail trim moves `inPoint`, and a slip by `delta` moves the played range by `−delta·|speed|` (the opposite of a forward clip, so the picture slides the same way on screen). Trims and splits are measured from the range the clip actually plays and never write a negative point; a split piece lying wholly past the in point is written `[in, in]` (blank) or `[in, in + 0.001]` for a hold clip. A reversed `holdLastFrame` clip holds its in-point frame; trims keep that hold point. Changing a clip's speed or direction changes its same-media linked sound too; `linked_av_out_of_sync` saying the two "play in opposite directions" means reverse both, or neither. `pr0ta-api` → `reference/source-shortfalls-and-fit-to-fill.md` → "Reversed Clips" has the full rules.

## Mix Failures

- **Music inaudible in narration gaps.** Run `audio_analyze` over the gap and read the music segment's `render_gain_envelope`. A ducking rule with a long release or a very low `duckedGain`, or a stray manual keyframe, is the usual cause. Fix it, then meter the window with `audio_meter` or listen to an audio preview. If the rendered mix is still silent where the envelope says music should play, report it (`bug_report_create`) with the render task ID and the envelope.
- **Clipping or harsh peaks.** Meter the loudest windows; keep true peak at or below −1 dBTP. Lower the offending clip or track with `volumeKeyframes` rather than the whole mix.
- **A competing third source.** Generated video often carries a thin ambient track. Mute it unless the sound was designed at generation time.
- **Pops at edits.** Add a short crossfade between adjacent audio clips, or trim to a zero-crossing-friendly boundary.

## Rebuilding a Contaminated Sequence

Rebuild when any of these appear: more than one structural review revision; a one-frame or media-gap warning that moves after repair; audio patches that produce artifacts twice; orphan patch tracks, stale narration, muted keyframe remnants, or duplicate shot families.

1. Snapshot the old sequence so nothing is lost.
2. `POST /sequences` with a new `sequence_id` (for example `review_v3_clean`), a name, and the dimensions.
3. Save the complete payload to the new sequence: tracks (`video`, `dialogue`, `music`, and only the extra tracks you need, each with empty `clips`), `audioMix` (ducking rules, narration offset), and `metadata` (`reason`, `sourceSequenceId`). To keep settings, read the source first and copy only the fields you intend; `POST /sequences/{sequence_id}/duplicate` copies everything, including the contamination.
4. Place clips frame-native from the authoritative beat or cut list and known-good media.
5. For narration fixes, add one regenerated narration asset, confirm it is time-indexed, and reflow the cuts to its word timing.
6. Analyze, render, and verify with the new `sequence_id`, and point review and export at it.

## Handing a Render to Review

- Internal checks may use `quality=low`. Client review links get a full-quality export.
- Keep internal words such as "review cut" off client-facing titles and credits.
- Record together: `sequence_id`, render or export task ID, export asset ID, review round ID, and review URL.
- After submitting, confirm the review asset ID matches the export you intended to show and that the review URL resolves.
- When a replacement round supersedes an old one, mark the old annotations addressed where possible and link the new round.
