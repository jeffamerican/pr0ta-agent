---
name: pr0ta-music
description: "PR0TA music and SFX generation for scores, ambient beds, point effects, foley, music prompts, composition workspace, and beat analysis. Read when scoring or generating non-speech audio."
---

# Music Generator Reference

> **See also:** For placing music in a production timeline with proper ducking, crossfades, and cue-sheet-driven timing, read `pr0ta-sync`. For editorial judgment on whether the score serves the story, read `pr0ta-editorial`. **After generating instrumental music or SFX, time-index it** with MCP `music_analyze` (REST fallback: `POST /api/v2/projects/{project_id}/music/analyze`) before adding it to the timeline — see `pr0ta-audio` → "Mandatory Time-Indexing Rule".

Before scoring or generating SFX for an existing project, call `memory_context_pack` with the scene, sequence, department, or edit-pass scope. Use approved tone, music, pacing, director, client, and editorial decisions as constraints. After accepting a score direction, cue, motif, SFX rule, or beat-analysis conclusion, record it with `memory_record_decision` or `memory_record_note`.

## Overview

PR0TA exposes separate **ElevenLabs Music** and **ElevenLabs Sound Effects** paths through the unified generator. They handle two distinct production needs:

- **Scores and beds** — continuous background music that runs under narration or video. Typically 30-120 seconds. Generated once, placed on a dedicated `music` track, ducked under dialogue.
- **Point SFX and foley** — short isolated sounds (whooshes, impacts, ambient textures, UI sounds) placed at specific cue-sheet timestamps. Typically 1-10 seconds.

The distinction matters because scores need emotional arc descriptions and duration planning, while SFX need precise sound-design language and short durations.

## MCP Quick Reference

Prefer the bundled PR0TA MCP connector for agent workflows. Submit with `generation_submit`, then poll with `tasks_get`.

```json
{
  "project_id": "project-uuid-or-slug",
  "request": {
    "generator": "music",
    "mode": "txt_to_music",
    "model": "music-v1",
    "prompt": "Tense orchestral underscore with low cello drones and sparse pizzicato strings, building slowly over 45 seconds to a crescendo with timpani rolls",
    "duration": 45,
    "output_format": "mp3_44100_192"
  }
}
```

For a sound effect, use the audio generator's dedicated SFX mode rather than the music mode:

```json
{
  "project_id": "project-uuid-or-slug",
  "request": {
    "generator": "audio",
    "mode": "text_to_sound",
    "model": "eleven_text_to_sound_v2",
    "prompt": "Short cinematic metal whoosh, one second, bright attack with a tight reverb tail",
    "duration": 1,
    "output_format": "mp3_44100_192"
  }
}
```

## REST Fallback

Use REST/curl only when MCP is unavailable or for high-volume scripts. Music and sound-effect generation use the same unified endpoint but different generator/mode pairs:

```bash
curl -X POST "https://app.pr0ta.com/api/v2/projects/{project_id}/generate" \
  -H "Authorization: Bearer $PR0TA_PAT" \
  -H "Content-Type: application/json" \
  -d '{
    "generator": "music",
    "mode": "txt_to_music",
    "model": "music-v1",
    "prompt": "Tense orchestral underscore with low cello drones and sparse pizzicato strings, building slowly over 45 seconds to a crescendo with timpani rolls",
    "duration": 45,
    "output_format": "mp3_44100_192"
  }'
```

For SFX, submit `generator: "audio"`, `mode: "text_to_sound"`, `model: "eleven_text_to_sound_v2"`, plus `prompt` and optional `duration`/`output_format`.

**Key parameters:**

| Parameter | Description | Default |
|-----------|-------------|---------|
| `prompt` | Text description of the music | Required |
| `duration` | Target length in seconds | 30 |
| `model` | `music-v1` for music; `eleven_text_to_sound_v2` for SFX | User default |
| `output_format` | `mp3_44100_192`, `pcm_44100`, or legacy `"mp3"` | `mp3_44100_192` |

See `pr0ta-api` for the full request/response schema, task polling, and error handling.

## Writing Effective Music Prompts

For Lyria, first select text-to-music or image-to-music in `pr0ta-prompting/reference/model-modality-guides.md`. Other music endpoints may remain text-only; query the current model schema before supplying references. A good text prompt specifies five things:

1. **Genre and style** — "cinematic orchestral", "lo-fi hip-hop", "ambient electronic", "jazz trio"
2. **Instruments** — name them: "cello, piano, brushed snare, synth pad" not "various instruments"
3. **Energy and mood** — "tense and building", "warm and reflective", "high-energy and driving"
4. **Progression** — describe the arc: "starts sparse with solo piano, strings enter at the midpoint, builds to a full orchestral crescendo in the final quarter"
5. **Production quality** — "warm analog tone", "clean digital production", "lo-fi with vinyl crackle"

**Prompt examples by use case:**

**Score — documentary underscore:**
> "Contemplative ambient score with warm analog synth pads, slow evolving textures, gentle piano arpeggios entering at the midpoint, and a gradual swell of low strings toward the end. Minimal percussion. Introspective and hopeful. 60 seconds."

**Score — trailer:**
> "Epic cinematic trailer music building from a single sustained cello note through layered strings, brass stabs, and taiko drum hits to a massive orchestral crescendo with choir. Dark to triumphant arc. 45 seconds."

**Point SFX — transition whoosh:**
> "Short cinematic whoosh transition sound, 1 second, metallic with reverb tail, left-to-right pan feeling"

**Point SFX — ambient texture:**
> "Gentle rain on a window with distant thunder rumbles, cozy indoor ambience, 10 seconds, loopable"

## Music Prompt Restrictions (TOS)

ElevenLabs Music rejects prompts containing artist or band name references — this is a TOS violation, not a soft preference. The rejection is immediate and non-negotiable.

```
❌ REJECTED: "Ólafur Arnalds meets Hans Zimmer — ambient piano with cinematic strings"
❌ REJECTED: "in the style of Radiohead — atmospheric electronic"
❌ REJECTED: "Billie Eilish-inspired dark pop with breathy vocals"

✅ WORKS: "Ambient electronic with ethereal piano, deep cinematic bass, orchestral strings building to a climax"
✅ WORKS: "Dark atmospheric pop with breathy female vocals, sparse reverb-heavy production"
✅ WORKS: "Minimalist neo-classical piano with granular synthesis textures and slow string swells"
```

The fix is always the same: describe the *sound* you want (instruments, production techniques, mood, energy) rather than the *artist* you want it to sound like. Genre descriptors, instrument names, and production vocabulary are all safe.

## Music Composition Workspace

For longer or structurally complex pieces, the composition workspace lets you plan before generating:

- **Section durations** — break a 90-second score into intro (8s), verse (24s), build (16s), chorus (24s), bridge (12s), outro (6s)
- **Beat markers** — set tempo and key signature per section
- **Lyrical cues** — anchor vocal melodies or rhythmic patterns to specific bars
- **Iteration** — adjust structure and re-generate without starting from scratch

This is particularly useful for scores that need to hit specific cue-sheet timestamps — plan the sections to align with your scene changes, then generate.

## Time-Indexing Generated Music and SFX

Every generated music or SFX asset with no speech must be time-indexed before it can enter the timeline. Call MCP `music_analyze` with the asset ID, poll with `tasks_get`, and use REST `POST /api/v2/projects/{project_id}/music/analyze` only as a fallback. This produces:

- `editorial_anchors` — key structural moments useful for cut points
- `downbeat_times` — beat-aligned timestamps for beat-keyed editing
- `beat_times`, `transients[]` — raw timing data
- `tempo_bpm`, `beat_confidence` — metadata

Scribe V2 transcription (Path A) is for speech — it does not produce beat or downbeat data and should not be used for instrumental music.

## Integration with the Production Pipeline

1. **Plan the music arc in your cue sheet** — decide duration, emotional progression, and where the score should peak relative to the video. See `pr0ta-sync`.
2. **Generate one continuous piece** covering the full production when possible. One 90-second generation with a described arc produces better results than three 30-second pieces stitched together.
3. **Time-index immediately** after generation via MCP `music_analyze`.
4. **Place on a dedicated `music` track** — never on the same track as narration or dialogue. Concurrent audio on the same track is invalid and the renderer rejects it. Create the track first with `POST /timeline/tracks`. See `pr0ta-timeline`.
5. **Configure ducking** — set the timeline's `duckedGain` property so the music dips under dialogue automatically. See `pr0ta-timeline` → "Audio Mix".
6. **Check balance** — use `GET /audio/analyze` to verify music-vs-narration levels before rendering a full preview.
7. **Point SFX** — after generation, call `music_analyze` and wait for `tasks_get` to report success; only then place each effect on a separate `sfx` track at its cue-sheet timestamp.
