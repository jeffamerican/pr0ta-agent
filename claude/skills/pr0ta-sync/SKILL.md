---
name: pr0ta-sync
description: "PR0TA timing and sync strategy: cue sheets and timing plans, picture-first, narration-first or music-first order, the narration timeline (transcript anchors, cut list, alignment check, materialize to post), voiceover and dialogue timing, beat sync and montage, SFX hit points, and re-timing after audio changes. Read before planning any piece where picture, voice, music and sound effects must line up."
---

# PR0TA Sync

This is the timing strategy layer: what to generate, in what order, against
what timing plan. Three skills share a production:

| Skill | Role | When |
|---|---|---|
| `pr0ta-sync` | Strategy: cue sheet, anchor order, narration timeline, montage rules. | Before generating. |
| `pr0ta-timeline` | Execution: clips, Ken Burns, audio mix, preview, render. | Every edit. |
| `pr0ta-editorial` | Judgment: what to cut, where, and when the cut ships. | Before and after every edit pass. |

Each generation is an isolated call with no time relationship to the others.
Six clips, six narration lines and six music cues are eighteen unrelated
assets: the audio seams at every cut and the voice drifts off the pictures it
describes. The fix is to plan the timing before generating, then build it on
the narration and post-production timelines.

Before planning for an existing project, call `memory_context_pack` with the
scene, department or task scope and carry approved decisions and open
questions into the plan. Record accepted timing, cue and sync decisions with
`memory_record_decision` or `memory_record_note`.

## Where timing starts

- **A production with a story** starts in the screenplay pipeline:
  Development (`pr0ta-development`), then breakdown, shot lists, storyboards and
  the Production Queue (`pr0ta-prep`). The screenplay fixes scene order; the
  shot lists fix what each shot shows. Use a cue sheet inside that pipeline for
  timing: target durations per scene and shot, sync points, narration windows,
  the music arc and SFX hit points. Build it from the shot lists
  (`get_scene_shotlist`) and the scenes' breakdown (`production_context_get`),
  keyed by scene and shot number; do not invent a parallel scene list.
- **A short piece with no script** (a promo, a montage, a title sequence, a
  music-driven reel) may start from a cue sheet directly, then generate
  (`pr0ta-image`, `pr0ta-video`, `pr0ta-audio`, `pr0ta-music`).

## The cue sheet

The cue sheet is the timing contract for the piece and its single source of
truth.

```json
{
  "title": "Product Launch Trailer",
  "total_target_duration": 30.0,
  "scenes": [
    {
      "id": "scene_01",
      "description": "Wide: dawn over the city skyline",
      "target_duration": 5.0,
      "actual_duration": null,
      "markers": [
        { "id": "M1", "time": 0.0, "label": "picture_start" },
        { "id": "M2", "time": 2.5, "label": "title_reveal", "sfx": "whoosh_rise" }
      ],
      "narration": { "text": "In a world moving faster than ever...", "target_start": 0.5, "target_end": 4.5 }
    }
  ],
  "music": {
    "style": "Cinematic orchestral, modern hybrid",
    "arc": "Quiet tension 0-10s, building 10-20s, peak at 20s, warm resolution 25-30s",
    "total_duration": 30.0
  },
  "sfx": [ { "marker": "M2", "description": "Rising whoosh transition", "duration": 2 } ]
}
```

In a scripted project, `id` is the scene number (and a shot entry per shot).

Rules:

- Every scene has a `target_duration`; `actual_duration` is filled in from the
  generated or placed media.
- Marker times are absolute from the start of the piece.
- Narration lines map to windows (`target_start`, `target_end`).
- The music arc names times or markers.
- Sound effects are point events tied to markers.

Building one: break the idea into scenes (three to ten for a 30 to 60 second
piece), give dense action short scenes and emotional beats long ones, mark the
moments that must sync (reveals, impacts, transitions, key words), write the
narration into windows, describe the music arc, list the effects at their
markers.

**Present the cue sheet for approval before generating.** Timing changes are
cheap now and expensive later.

**The cut plan comes before the assets.** For narration-driven work, write the
plan first (anchor word, target start and duration, what the picture shows on
each beat), then generate to match it, then place. Generating first turns every
decision into "where can this clip fit?" instead of "what does the narration
call for here?" (`pr0ta-editorial`).

Keep the approved cue sheet as `cue_sheet.json` beside your working files and
update `actual_duration` as media lands.

## Pick the anchor

Decide which track sets the clock:

- **Picture-first** (action, VFX, dialogue scenes): generate the visuals, lay
  them on the timeline, then fit narration and score to the locked picture.
  Mirrors professional practice: lock picture, then score.
- **Narration-first** (documentaries, video essays, explainers, voice-driven
  pieces): generate the narration first; its real durations set the edit. Build
  the cut list on the narration timeline, then materialize to post.
- **Music-first** (music videos, beat-driven montages, trailers cut to a
  track): generate or choose the music, run beat analysis
  (`pr0ta-music` → "Beat analysis"), and cut picture to its downbeats and
  accents.

## Picture-first

1. Generate key frames and clips to the cue sheet's target durations
   (`pr0ta-image`, `pr0ta-video`; each resolves its model with
   `models_preferred`). Generated durations are approximate; a 10-second
   request can return slightly more or less.
2. Place the clips on the post-production timeline (`pr0ta-timeline`), which
   measures and normalizes them. Read the measured durations back
   (`post_sequence_get`).
3. Replace each scene's `target_duration` with its `actual_duration` and move
   the markers.
4. Generate narration and score against the locked picture (`pr0ta-audio`,
   `pr0ta-music`).

## Narration-first: the narration timeline

The narration timeline is a server-side plan for narration-driven cuts: the
narration's word timing, registered visuals with content tags, a cut list
anchored to transcript words with a rationale per cut, and an alignment check.
Once verified it materializes into the post-production timeline, where editing
continues.

1. **Generate the narration** in as few takes as possible, ideally one per
   voice (`pr0ta-audio` → "Text to speech").
2. **Get its word timing.** The narration is transcribed in the background and
   fills the narration timeline's transcript layer; check it before starting
   anything (`pr0ta-audio` → "Time-indexing").
3. **Review and tag the transcript:** content labels on transcript ranges
   (for example `market_size`) link narration to the visuals that illustrate it.
4. **Generate visuals** at least as long as the narration segments they cover,
   and register them with matching affinity tags.
5. **Build the cut list:** one cut per narration segment with its position,
   asset, transcript anchor (word indices), rationale, Ken Burns motion and
   transition. The timeline tracks asset use, so repeats show up.
6. **Verify alignment**, the quality gate: per-cut drift, gaps, overlaps and
   misalignment flags. Fix flagged cuts, reflow, verify again.
7. **Configure** `narration_offset`, `pre_roll_duration`, `frame_rate` and
   `resolution`.
8. **Snapshot** before big changes; diff and restore when needed.
9. **Materialize** to the post-production timeline (`narration_materialize_to_post`).
   Cuts become clips with stable ids and their transcript provenance, motion
   becomes Ken Burns, narration and music become audio clips, and the offset
   and ducking intent land in the timeline's audio mix. From here on, edit on the
   post-production timeline (`pr0ta-timeline`).

`narration_timeline_get` reads the whole narration timeline.

REST, under `/api/v2/projects/{project_id}/narration-timeline`: `GET
/transcript` and `GET /transcript/words?from=44.0&to=52.0` (review), `POST
/transcript/populate` (rebuild the transcript layer from the narration's
transcription, for example after the narration changed or auto-fill was
skipped), `PUT /transcript/tags`, `POST /assets` with `affinity_tags`, `GET
/assets?affinity=market_size&status=unused`, `GET
/assets/suggest?transcript_range=44.0-52.0`, `POST /cuts`, `PATCH
/cuts/{cut_id}`, `POST /cuts/reflow`, `GET /verify`, `PUT /config`, `POST
/snapshot`, `GET /snapshot/{name}/diff`, `POST /snapshot/{name}/restore`,
`POST /materialize-to-post-production`. Full contract: `pr0ta-api` →
`reference/narration-timeline-api.md`.


If the narration timeline misaligns cuts you know are right, fails to
materialize, or flags cuts that make no sense, report it as a platform bug
rather than working around it.

## Continuous audio

**Generate fewer, longer audio pieces.** One score for the whole sequence and
one narration take per voice keep the arc, tone and breath continuous; per-scene
pieces seam at every cut. How to write and split them: `pr0ta-music` → "Score a
whole piece in one generation", `pr0ta-audio` → "Text to speech".

**Sound effects are the exception:** short, one per hit point, placed at their
markers (`pr0ta-music` → "Writing sound-effect prompts").

## Re-time after any audio change

When narration or dialogue is regenerated, re-recorded, revoiced or its script
is edited, the new take is a new asset with its own timing. Read its word
timing (`pr0ta-audio` → "Time-indexing"), rebuild every timing value and marker
from it, and on the narration timeline repopulate the transcript layer, reflow
and verify again. Even 200 to 400 ms of drift between takes of the same script
reads as random cut placement. Never carry old timestamps onto new audio.

## Narration offset and ducking

- **Offset:** narration-driven pieces usually need a few seconds of picture
  before the voice starts (title, establishing shot, mood). It is one audio mix
  setting on the timeline; materializing from the narration timeline carries
  its `narration_offset` across (`pr0ta-timeline` → "Audio Mix").
- **Ducking levels by content type** (the `duckedGain` fraction of music
  level while speech plays):
  - Voice-driven (documentary, essay, explainer): 0.08 to 0.10. Even 0.20 is too hot.
  - Cinematic and action: 0.25 to 0.40; the score carries more of the emotion.
  - Music-only passages: full level.

## Montage

For pieces that intercut stills and clips:

- Hold a still no longer than 3 to 4 seconds; cut between many.
- Intercut video into still montages; even one 5 to 10 second clip lifts
  attention.
- Alternate Ken Burns directions between neighbors (`push_in` → `pull_back`,
  `drift_left` → `drift_right`); repeating one direction reads as monotonous
  (`pr0ta-timeline` → "Ken Burns as a Clip Property").
- Flash cards use `hold` or `zoom_in_extreme`, never a slow preset.
- Never extend a clip by playing it forward then backward. Gentle slow motion
  (down to about 70%) is acceptable.
- Prefer fewer, longer video generations; multi-shot generations keep
  characters and scenes consistent across cuts (`pr0ta-video`).
- For narration-driven montage, cut on transcript anchors (names, years,
  emotional turns) in the narration timeline, then tune pacing in post.
- For music-driven montage, cut phrase starts on downbeats and accents on
  transients (`pr0ta-music` → "Beat analysis").

Title cards and flash cards are generated as images, not text overlays
(`pr0ta-image` → "Title Card").

## Sync checks before delivery

Alongside the editorial verification gates (`pr0ta-editorial`):

- Preview every frame-critical cut (name drop, year, emotional turn) and
  confirm the right picture is on screen during the right word.
- Preview two seconds either side of each cut for audio pops and jarring motion
  changes.
- Check the first and last ten seconds: narration lead-in, music fade-in, the
  ending beat, and no silent black tail after the narration.
- In the full render, listen for narration drifting from the picture in the
  second half of long pieces.

## Sung performance with generated video

When continuous music conditions a generated sung performance, follow the
[Seedance 2.5 sync-sound recipe](../pr0ta-video/reference/seedance-2.5-sync-sound.md):
choose one audible authority, keep exact source ranges and lyric timing, keep
accepted native sound paired with its picture, and review worst-case phrase
drift and actual mouth sync before expanding.
