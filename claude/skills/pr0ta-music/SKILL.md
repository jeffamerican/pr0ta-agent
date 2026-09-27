---
name: pr0ta-music
description: "PR0TA music and sound design: score, soundtrack, underscore, ambient beds, stingers and songs with lyrics; sound effects (SFX), foley and ambience; music prompts, composition plans and section editing; beat analysis for beat sync and hit points. Read before generating, analyzing or placing any non-speech audio."
---

# PR0TA Music and Sound Effects

This skill covers non-speech audio: music and sound effects. Speech is in
`pr0ta-audio`. Where the score peaks and where each effect lands is planned in
the cue sheet (`pr0ta-sync`); placing, ducking and mixing happen on the
timeline (`pr0ta-timeline`); whether the score serves the story is judged in
`pr0ta-editorial`.

Before scoring or designing sound for an existing project, call
`memory_context_pack` with the scene, sequence or edit-pass scope and follow
approved tone, music, pacing and director decisions. Record an accepted score
direction, motif, cue or sound rule with `memory_record_decision` or
`memory_record_note`.

Pass `project_id` on every call; parallel submission limits are in `pr0ta-api` → "Rate limits and concurrency".

## Two jobs

- **Score and beds:** continuous music under picture, narration or dialogue,
  usually 30 seconds or longer. Needs an emotional arc and a planned duration.
  Goes on a `music` track and ducks under speech.
- **Point effects and foley:** short isolated sounds (whooshes, impacts, doors,
  footsteps, UI sounds, ambience loops) placed at cue-sheet hit points. Needs
  precise sound-design language and short durations. Goes on an `sfx` track.

## Choose the model

1. Music: `models_preferred(modality: "music_model")`. Sound effects:
   `models_preferred(modality: "sfx_model")`. Pass the returned `model_id`.
2. If `model_id` is null, choose with `models_list(modality: ...)` (pinned
   models first) and tell the user which you chose and why.
3. Call `models_get_defaults(model_id)` for the model's fields (duration range,
   lyrics, instrumental, output formats) before building the payload.
4. Read the guide for the resolved model before writing its prompt:

| Resolved model | Read |
|---|---|
| ElevenLabs Music routes | `reference/eleven-music.md` |
| Lyria routes | `pr0ta-prompting` → `reference/model-modality-guides.md` → "Lyria" |
| Any other route | its `models_get_defaults` fields |

Capabilities, for when the user asks for one:

- **Composition plans** (fixed sections with their own durations, styles and
  lyrics) and **section editing of stored songs** exist only on ElevenLabs
  Music routes; other music routes ignore or reject a plan.
- **Reference inputs** (an image or audio to score from) vary by route: supply
  one only when `models_get_defaults` lists the field.

## Generate

Music:

```json
{
  "project_id": "<project>",
  "request": {
    "generator": "music",
    "mode": "txt_to_music",
    "model": "<model_id from models_preferred>",
    "prompt": "Tense orchestral underscore: low cello drones and sparse pizzicato, building over 45 seconds to a crescendo with timpani rolls",
    "duration": 45
  }
}
```

Sound effect (the audio generator's `text_to_sound` mode, not the music
generator):

```json
{
  "project_id": "<project>",
  "request": {
    "generator": "audio",
    "mode": "text_to_sound",
    "model": "<model_id from models_preferred>",
    "prompt": "Short cinematic metal whoosh, bright attack, tight reverb tail",
    "duration": 2
  }
}
```

Submit with `generation_submit`, poll with `tasks_get`.

- Music `duration` is 3 to 600 seconds; the route may allow less.
- Force an instrumental or a vocal track with `parameters.instrumental` or
  `parameters.vocals` (if you send both, they must be opposites).
- Sound-effect `duration` is a whole number of seconds. Generate slightly long
  and trim to the hit with `assets_trim`.

REST: `POST /api/v2/projects/{project_id}/generate` with the same `request`
body. See `pr0ta-api` for auth and task polling.

## Writing music prompts

Specify five things:

1. **Genre and style:** "cinematic orchestral", "lo-fi hip-hop", "ambient
   electronic", "jazz trio".
2. **Instruments, named:** "cello, piano, brushed snare, synth pad", not
   "various instruments".
3. **Energy and mood:** "tense and building", "warm and reflective".
4. **Arc over time:** "sparse solo piano, strings enter at the midpoint, full
   orchestra in the last quarter". Tie the arc to cue-sheet times when the
   score must hit them: "gentle piano 0-10s, percussion enters at 10s, brass
   peak at 22s, warm resolution 26-32s".
5. **Production quality:** "warm analog tone", "clean modern mix", "lo-fi with
   vinyl crackle".

Describe the sound, never an artist or band. ElevenLabs Music rejects artist
names outright; "in the style of" prompts are also weaker on every model than
concrete instruments, techniques and moods.

Examples:

- Documentary underscore: "Contemplative ambient score with warm analog synth
  pads, slow evolving textures, gentle piano arpeggios entering at the
  midpoint, a gradual swell of low strings toward the end. Minimal percussion.
  Introspective and hopeful. 60 seconds."
- Trailer: "Epic cinematic trailer music building from a single sustained cello
  note through layered strings, brass stabs and taiko hits to a full orchestral
  crescendo with choir. Dark to triumphant. 45 seconds."

## Writing sound-effect prompts

Name the source, the action, the material and the space: "heavy wooden door
closing in a stone hallway, short echo", "gentle rain on a window with distant
thunder, cozy interior, loopable". Give one sound per request; layer several
effects on the timeline rather than asking for a mix in one prompt.

## Score a whole piece in one generation

One continuous score for the full sequence beats several short pieces: the arc
flows, moods change musically instead of at hard cuts, and nothing needs
stitching.

1. Take the total length and the arc from the cue sheet (`pr0ta-sync`); in
   picture-first work, take the length from the locked timeline.
2. Generate one piece covering it. When it is longer than the route allows,
   generate two or three sections that overlap by 3 to 5 seconds and crossfade
   them on the timeline (`pr0ta-timeline` → "Transitions").
3. For structure that must land on exact times, use a composition plan where
   the resolved route supports one.

## Beat analysis

Beat-keyed cuts and hit points need the music's anchors. Check before
starting: `music_analyze(asset_id)` with default options returns the stored
analysis when one exists and starts a task only when none does
(`pr0ta-audio` → "Time-indexing" owns the indexing rule). Poll a started task
with `tasks_get`. Optional hints: `min_bpm`, `max_bpm`, `beats_per_bar`, and
`include_beats`, `include_downbeats`, `include_transients` (all on unless
turned off).

The analysis returns `tempo_bpm`, `beat_confidence`, `beat_times`,
`downbeat_times`, `transients` (time and strength) and `editorial_anchors`, a
single stream of downbeat, beat and transient anchors to snap cuts to.

Pick the stream for the cut:

1. **Downbeats:** structural cuts, section changes, montage phrase starts,
   scene transitions.
2. **Beats:** rhythmic cutting within a phrase.
3. **Transients:** accents and impacts, and the peak of a sound effect.
4. **`editorial_anchors`:** the combined stream, when any anchor will do.

The detector works best on instrumental music with a steady pulse. Downbeats
are inferred, so in rubato, ambient, orchestral or meter-changing music rely on
transients and your own listening. Analyze an effect only when its transient
must land on a frame; most effects are placed by their marker time.

REST: `POST /api/v2/projects/{project_id}/music/analyze` starts or returns
analysis; `GET /api/v2/projects/{project_id}/music/analyze/{asset_id}` reads it
(404 when none exists). Contract: `pr0ta-api` → `reference/music-analysis.md`.

## Put it in the cut

1. Plan the arc, peak and hit points in the cue sheet (`pr0ta-sync`).
2. Generate, then check the beat analysis if cuts will follow the music.
3. Place music on its own `music` track and effects on an `sfx` track, never
   on the dialogue track: overlapping audio on one track is rejected at render.
4. Duck music under speech with the timeline's audio mix (`pr0ta-timeline` →
   "Audio Mix"; `pr0ta-sync` gives levels by content type).
5. Check the balance with `audio_analyze` before rendering a preview, and with
   `audio_meter` when a loudness spec matters.
