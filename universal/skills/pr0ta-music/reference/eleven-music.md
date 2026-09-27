# ElevenLabs Music on PR0TA

Read this when the resolved `music_model` is an ElevenLabs Music route:
the native routes (`music-v1`, `music-v2`) or the Fal routes
(`elevenlabs/music/v2`, `elevenlabs/music/v2.5`). Only the native routes take
composition plans and edit sections of stored songs. Confirm fields with
`models_get_defaults(model_id)`.

## Fal routes (Music v2 and v2.5)

- Length comes from `duration` (sent as `music_length_ms`, 3 to 600 seconds);
  leave it out and the model chooses.
- `parameters.instrumental` guarantees no vocals.
- Billed per output minute, rounded up to the next whole minute: a 61-second
  cue costs two minutes. Size cues to just under a minute boundary when the
  edit allows it.
- No composition plans and no section editing. When a score must hit cue-sheet
  times, use a native route below.

## Prompt-only requests

- `prompt`: 1 to 4,100 characters. Describe the sound, never an artist:
  ElevenLabs rejects prompts that name artists or bands. Write "breathy
  close-mic female vocal over sparse reverb-heavy piano", not "in the style of"
  anyone.
- `duration`: 3 to 600 seconds.
- `parameters.instrumental` or `parameters.vocals`: force an instrumental or
  a vocal track. If you send both, they must be opposites.

## Composition plans

A plan fixes the structure before rendering: sections (or chunks) with their
own durations, styles and lyrics. Use it when a score must hit cue-sheet times
(`pr0ta-sync`): make section boundaries land on scene changes and sync points.

The two routes use different plan shapes; a plan in the wrong shape is
rejected.

| Route | Plan shape |
|---|---|
| Music v1 | `sections`, each with its `duration_ms`. |
| Music v2 | `chunks` (1 to 30). A generated chunk has `duration_ms` (3,000 to 120,000), `text` with lyrics or a section direction (at most 6,000 characters), optional `positive_styles` and `negative_styles` (at most 50 each), `context_adherence` (`low`, `medium`, `high`) and `condition_strength` (`low` to `xhigh`). |

Submit a plan through `generation_submit` as `parameters.composition_plan`.
`prompt` is still required by the request, but the plan drives the render and
its total length sets the duration. `parameters.seed` (an integer) applies only
with a plan and makes renders repeatable.

To draft a plan from a prompt first, `POST /api/audio/music/plan` with
`prompt`, `model`, optional `music_length_ms` and optional
`source_composition_plan` (to revise an existing plan). It returns
`composition_plan`; edit it with the user, then generate with it.

## Section editing from stored songs (Music v2)

Music v2 can rebuild part of an existing song while keeping the rest:

1. Store the song in the project: an audio asset becomes a stored song with a
   `song_id`. Music v2 generations are stored for this by default
   (`parameters.store_for_inpainting`); other audio can be stored explicitly.
2. In a v2 plan, a chunk with `song_id` and `range` (`start_ms`, `end_ms`,
   at least 50 ms) reuses that part of the stored song as is. A generated chunk
   may add `conditioning_ref` (`song_id` and a `range` of at most 30 seconds)
   to continue from that material.
3. Keep the chunks that work, regenerate only the chunks that do not.

Only songs stored in the same project can be referenced.

Stored songs: `GET /api/audio/music/references?project_id=...` lists them;
`POST /api/audio/music/references` with `project_id` and `asset_id` stores an
audio asset and returns its `song_id`.
