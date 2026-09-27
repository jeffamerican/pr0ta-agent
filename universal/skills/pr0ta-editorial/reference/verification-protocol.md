# Render Verification Protocol

> **See also:** the parent `pr0ta-editorial` SKILL.md for the ship gate and the five-pass loop; `pr0ta-timeline` for preview, render diagnostics, and export.

## Why This Exists

The agent checks its own work. If the user is the one who notices that the end is blank, that a shot does not match the narration, or that the audio drops out, verification failed. This protocol is the gate between "I rendered something" and "I can show this to the user."

## When to Run

Run it on **every render before handoff**: previews between passes and final exports before delivery. Previews get the lighter pass at the end of this file; final exports get the full protocol.

## Start With the Platform's Diagnostics

Before looking at frames, read what PR0TA already measured:

- **Timeline analysis before the render**: gaps, overlaps, reused media, source shortfalls, and frame coverage (`pr0ta-timeline` → Analyze Before Render). Unintended gaps on primary tracks, repeated `asset_id`s, and `sourceShortfallCount > 0` are failures.
- **Render diagnostics on the finished task**: `timelineMediaGaps[]` (program frames with no media), `renderedPixelGaps[]` (transparent or checkerboard frames after render), and `transparentOutputFrames`. Every entry is a hard review item; repair by its frame range, not by loose timestamp.
- **Audio**: `audio_analyze` predicts levels, ducking, and the render gain envelope without rendering; `audio_meter` measures LUFS and true peak on short windows. Check at least one narration-quiet window for music audibility.

## The Full Protocol

### Step 1: First and End Frames

The first frame is the thumbnail and decides whether a viewer clicks. The last frames are what the viewer takes away. Confirm that the first frame is the intended opening composition and that the frames at `duration − 1.0s` and `duration − 0.1s` show the intended final composition (credits, final beat, deliberate fade), not an unintended black frame, transparency, or a frozen mid-transition. A clip slot longer than its media can drop frames at the end, so do not trust the timeline's reported duration alone.

### Step 2: Audio Integrity

Look for unintended silent windows of a second or more. Do not trust integrated loudness or a whole-file mean; they average away local dropouts. If a silence is not a deliberate pause, trace it to the timeline (a gap between clips, a missing track, a clip with no audio) and fix it before anyone hears it.

Music must be measurable, not buried: peaks around −15 to −6 dBFS while ducked under narration, up to −3 dBFS in narration-quiet sections. With music automation, test at least one narration gap after render.

### Step 3: Concept-Word Frame Audit

For narration-driven work, check the frame at each concept word (`word.end + narration_offset + 0.4s`): the visual matches what the narration says, the shot has arrived (not the previous cut), and it is not a black frame or a transition artifact.

### Step 4: Visual Integrity

Scan for unintended black stretches, transparency artifacts, and frozen frames outside the editorial design. Unintended black usually means a clip slot extends past its media, or a gap in the track.

### Step 5: Random Spot Checks

Check three to five frames at random points for generator artifacts (warped faces, melted text, impossible geometry), style breaks, aspect-ratio or letterbox errors, and quality drops.


### Doing the Steps Locally

Download the render (`pr0ta-downloading`) and check it with ffmpeg. Save frames to a `qc_frames/` folder named `cut_<idx>_<anchor>_<time>s.jpg` so the user can spot-check them.

```bash
# Duration
DURATION=$(ffprobe -v error -show_entries format=duration -of csv=p=0 output.mp4)

# Step 1: first and end frames
ffmpeg -ss 0 -i output.mp4 -frames:v 1 qc_frames/first_frame.jpg
ffmpeg -ss $(echo "$DURATION - 1.0" | bc) -i output.mp4 -frames:v 1 qc_frames/end_minus_1s.jpg
ffmpeg -ss $(echo "$DURATION - 0.1" | bc) -i output.mp4 -frames:v 1 qc_frames/end_minus_0.1s.jpg

# Step 2: silent windows of 1s or more below -50 dB
ffmpeg -i output.mp4 -af silencedetect=noise=-50dB:d=1.0 -f null - 2>&1 | grep silence_

# Step 3: one frame per concept word (AUDIT_TIME = word.end + narration_offset + 0.4)
ffmpeg -ss $AUDIT_TIME -i output.mp4 -frames:v 1 "qc_frames/cut_${IDX}_${ANCHOR}_${AUDIT_TIME}s.jpg"

# Step 4: near-black stretches
ffmpeg -i output.mp4 -vf "blackdetect=d=0.5:pix_th=0.10" -f null - 2>&1 | grep black_

# Step 5: random spot checks
for t in $(python3 -c "import random; d=$DURATION; print(' '.join(f'{random.uniform(0.5,d-0.5):.1f}' for _ in range(5)))"); do
  ffmpeg -ss $t -i output.mp4 -frames:v 1 "qc_frames/spot_${t}s.jpg"
done
```

For a narration fix, also transcribe the exported file's audio, not only the source narration asset.

## The Gate

This is a gate, not a checklist to wave through. If any step fails: identify the issue in the timeline, fix it (swap, retime, regenerate, remix), re-render, and rerun the full protocol on the new render. Do not surface a failed render with caveats ("a small issue at 2:15 but otherwise fine"). The user never sees a render that has not passed QC.

## Lighter Pass for Preview Renders

Between passes, run a reduced protocol:

1. **End frames**: the preview does not trail into black.
2. **Concept words**: three to five critical words, frame-checked.
3. **Audio**: the first 5 seconds, the last 5 seconds, and one middle section for obvious problems.

Save the full protocol for the ship-quality render, but never skip QC entirely.
