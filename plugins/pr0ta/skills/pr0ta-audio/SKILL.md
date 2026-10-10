---
name: pr0ta-audio
description: "PR0TA speech and voice: narration, voiceover, dialogue and scene dialogue takes (text-to-speech), voice clone, voice design, voice changer (speech-to-speech), lip sync audio, transcription, word timing, subtitles, and the time-indexing rule every edit relies on. Read before generating, transcribing or cutting any speech."
---

# PR0TA Audio

This skill covers speech: text-to-speech, scene dialogue, voices, transcription
and time-indexing. Score and sound effects are in `pr0ta-music`. Timing
strategy (cue sheets, narration-first plans, the narration timeline) is in
`pr0ta-sync`. Whether a visible speaker should use native video audio or TTS is
decided in `pr0ta-video`.

Before generating for an existing project, call `memory_context_pack` with a
`task_intent` and the scene or character `scope`, and follow approved voice, accent,
language, pronunciation and performance notes. Record an accepted voice,
pronunciation rule or performance note with `memory_record_decision` or
`memory_record_note`. In a scripted project the cast and their voices come from
Casting (`pr0ta-prep` → "Casting and voices"); use those voices, do not invent
new ones.

Pass `project_id` on every call; parallel submission limits are in `pr0ta-api` → "Rate limits and concurrency".

## Choose the model

Every generation step resolves its model from the platform:

| Step | Modality key |
|---|---|
| Text-to-speech, dialogue | `dialogue_model` |
| Voice design | `voice_design_model` |
| Speech-to-speech (voice changer) | `voice_to_voice_model` |
| Transcription | `audio_to_text_model` |

1. Resolve the key with `models_preferred(modality: "<key>")` (`pr0ta-api` →
   "Choosing a model" owns the full rule), then `models_get_defaults(model_id)`
   for that model's fields and limits.
2. Read the reference for the resolved model before writing its text:

| Resolved model | Read |
|---|---|
| ElevenLabs v4 (`eleven_v4`, `eleven_v4_turbo`) or v3 (`eleven_v3`) | `reference/elevenlabs-v3-audio-tags.md` |
| Gemini TTS routes (`fal-ai/gemini-3.1-flash-tts`, `gemini-3.1-flash-tts-preview`, `gemini-2.5-flash-preview-tts`, `gemini-2.5-pro-preview-tts`) | `reference/gemini-tts.md` |
| Seed Audio 1.0 (`bytedance/seed-audio-1.0`) | `reference/seed-audio.md` |
| Any other route | its `models_get_defaults` fields |

Prompt grammar per model family (ElevenLabs V4/V3, Gemini TTS, Seed Audio) is in
`pr0ta-prompting` → `reference/model-modality-guides.md`.

Capabilities, for when the user asks for one:

- **Inline performance tags in the text:** ElevenLabs v4 and v3 read bracketed tags
  (`[whispers]`, `[sigh]`) as direction. Seed Audio reads bracketed cues as
  audio direction (sound effects, room tone, pauses) inside one continuous take.
- **Separate style direction and multi-speaker config:** Gemini TTS routes take
  `style_instructions` and `speakers`; the Fal Gemini 3.1 Flash TTS route also
  takes `language_code`, `temperature` and `output_format`.
- **Voice from a reference clip without cloning:** Seed Audio takes up to three
  reference audio clips, or one reference image, per request. The Operator
  uses a clip only as a named speaker's approved voice; a recurring speaker
  needs a fixed voice (see "One voice per speaker").
- **A cloned or designed voice:** `voices_clone` and `voices_design` create
  ElevenLabs voices; use them with an ElevenLabs TTS model.

## One voice per speaker

A narrator, host or character who speaks in more than one take must speak in
one fixed voice. A model copying a voice from a clip guesses again on every
request, so the voice drifts from shot to shot even when the words are right.

- **Establish the voice before any lines.** Clone it from at least 30 s of
  clean speech by that one person (`voices_clone`; one to three minutes clones
  best), or design it. Generate one short audition line, save the voice to the
  speaker's cast entry (`cast_list_save`, `pr0ta-prep`), and ask the user to
  listen and approve it (in Casting, or on a voice review card; see below).
  A real person's voice needs their approval of the audition.
- **Then name the speaker** (`character_name`) on every `generation_submit`
  speech request and omit the voice. A speaker with an approved voice speaks
  in it there and in Production Queue dialogue: the platform applies it, and
  refuses a different `voice_id`, a different reference clip, or a model that
  cannot speak it. Seed Audio speaks an approved voice from its approved clip.
  Change an approved voice only in Casting.
- **Never copy a voice from a clip** (`voice_settings.audio_urls`) for a
  speaker without an approved voice; the Operator's request is refused.
- **Only the user approves a voice.** `cast_list_save` does not save
  `approved_voice` or a voice design's approval from an agent; the stored
  approval stays as it is. The user approves in Casting, or, in an Operator
  mission, on a review card: `operator_checkpoint` with a `requires_review`
  notes draft whose `approves_casting_voices` names each character, the voice
  saved on its Casting record now (`voice_config.voice_id` in
  `cast_list_get`) and the audition asset they hear
  (`[{character, voice_id, sample_asset_id}]`). Approving that card approves
  exactly those voices in Casting; asking for changes approves nothing. When
  the user approves voices in chat or on a plain card, send this card: nothing
  else changes Casting. Never report a voice approved until the card's
  `casting_voice_results` say `approved`; `cast_list_get` then shows its
  `approved_voice`.
- **What a voice clip must be:** never speech PR0TA generated (an earlier
  take, or a trim or cleaned copy of one); at least 10 s for a reference clip
  and 30 s in total for a clone; one person speaking. The platform refuses
  generated or short clips, and removes music and noise when it can (clones
  remove it unless `remove_background_noise: false`). An approved Casting
  voice is used exactly as approved.
- Correct words and clean levels are not a voice match. Automatic review
  compares each speech take with the speaker's approved voice and reports a
  different-sounding voice as a `voice` issue. When the take has one speaker
  and their voice is an ElevenLabs voice the remedy is `repair`: once the
  user keeps the take,
  change its voice with `voices_speech_to_speech` (`target_voice_id` = the
  speaker's `approved_voice.voice_id` from `cast_list_get`), which keeps the
  performance and timing; for a video take, ask the user to run Voice Change
  on it. A voice change turns the whole track into one voice, so a take with
  several speakers, or an approved voice that is only a clip, needs a new
  take (or clone the voice in Casting first).

## Voices

Browse before choosing a voice unless the user named an exact one or the cast
already has one.

`voices_list(provider?, search?, page_size?, include_live?, include_custom?)`
searches ElevenLabs, Google/Gemini, MiniMax, Kling and xAI voices, including
the user's cloned and designed voices. `provider` is one of `all`,
`elevenlabs`, `google` (or `gemini`), `minimax`, `kling`, `xai`; `page_size`
is at most 200. Each voice has `provider`, `voice_id`, `name`, `category`,
`supported_models`, an optional `preview_url`, and a `selection` object: copy
`selection` into the TTS request instead of mapping fields by hand (for Google
voices it carries `voice_settings.voice`).

Pick a voice from the resolved model's provider (`supported_models` lists
that provider's TTS models). Present names and previews to the user. After a voice-not-found or model-compatibility
error, browse again and retry with a fresh selection.

## Text to speech

Narration, voiceover and single-voice lines:

```json
{
  "project_id": "<project>",
  "request": {
    "generator": "audio",
    "mode": "txt_to_speech",
    "model": "<model_id from models_preferred>",
    "text": "<the words, plus direction in the resolved model's syntax>",
    "voice_id": "<from the voice's selection>"
  }
}
```

Submit with `generation_submit`, poll with `tasks_get`; the finished task
carries `result.asset_id`. Add the resolved model's own fields
(`models_get_defaults`) as its reference describes.

- Text beyond the model's limit is cut off: 10,000 characters on ElevenLabs
  v4, 5,000 on v3 and most other routes, less on some (the model's reference
  and `models_get_defaults` give its limit). Split long
  narration at paragraph or scene boundaries and use the same voice and
  direction for every part.
- Generate narration in as few takes as possible, ideally one per voice: one
  read keeps pace, tone and breath consistent (`pr0ta-sync` plans the timing).
- Check the take: listen, and read its transcript (`transcription_get`, see
  Time-indexing) for names, numbers, acronyms and dates. For a take generated
  from script lines, `text` follows the script spelling: read `script_check`
  (each misread or missing line, expected against heard) and `heard_text` for
  what was actually said. Regenerate a take that misreads them.
- `audio_meter` with the take's `asset_id` checks it before it is placed:
  loudness, true peak, clipping and silent dropouts inside the take. Every
  generated take is also reviewed automatically (`shot_quality_review`),
  including whether it sounds like the speaker's approved voice.
- Non-English speech: write the text in the target language and set the
  language field the model exposes.

REST: `POST /api/v2/projects/{project_id}/generate` with the same `request`
body. See `pr0ta-api` for auth and task polling.

## Scene dialogue takes

For scripted scenes, the Performances page renders a scene's dialogue as whole
takes: every line in order, each speaker in their cast voice, assembled into
one audio file per variant (two variants unless asked). The platform splits a
long scene into provider-sized requests and joins them, so pass the whole scene.
Each line may carry `cues` (performance or sound directions); they become the
model's inline direction (ElevenLabs v3 tags, Seed Audio bracketed cues).

Whole-scene takes have no MCP tool. With MCP tools (and in-app):

- ask the user to render the scene on the Performances page; or
- generate line by line: for each line, `generation_submit` a
  `txt_to_speech` request (above) naming the speaker (`character_name`, no
  voice: their approved voice is applied; without one, the cast voice from
  `cast_list_get`) and the line's cues written in the resolved model's syntax,
  then place the takes in order on the timeline (`pr0ta-timeline`); or
- for Production Queue audio items whose modality is text-to-speech,
  `production_queue_regenerate` renders the item's line in the speaker's cast
  voice (`pr0ta-prep` → "Production Queue").

REST: `POST /api/audio/dialogue/v3` with `projectId`, `sceneNumber`,
`lines` (`[{speaker, text, cues?}]`), `voices` (speaker name → voice config:
`voice_id` for ElevenLabs; `voice_settings` with `audio_urls`, `image_url` or
`voice` for Seed Audio), `model` (always pass the `dialogue_model` from
`models_preferred`; this route does not look it up), and optional `variants`
and `attachToAssetUid`. It returns a `task_id`; poll it with `tasks_get`.

## Voice clone, design and speech-to-speech

- **Clone from recordings:** `voices_clone(request: {name, sample_asset_ids |
  sample_urls, description?, remove_background_noise?})` returns a reusable
  ElevenLabs `voice_id` right away (no task). Use clean, single-speaker samples
  of at least 30 s in total; generated speech is refused as a sample.
- **Design from a description (two steps):** `voices_design(request:
  {voice_description, model_id, text? | auto_generate_text?})` with `model_id`
  from `models_preferred(modality: "voice_design_model")` returns `previews[]`,
  each with a `generated_voice_id` and audio. Let the user audition them, then
  `voices_design_commit(request: {generated_voice_id, voice_name,
  voice_description?})` creates the permanent voice. `voices_design` runs
  ElevenLabs voice-design models; if the resolved model is another provider's,
  design cast voices with `casting_voice_design`, which designs and saves a
  MiniMax voice on a cast member (`pr0ta-prep`).
- **Change the voice of a recording:** `voices_speech_to_speech(request:
  {target_voice_id, source_audio_asset_id | source_audio_url, model_id})` with
  `model_id` from `models_preferred(modality: "voice_to_voice_model")`. It keeps
  the source's timing, breath and emotion and changes only who speaks. Use it
  when the performance is right and the voice is wrong; regenerate TTS when the
  words, pace or delivery must change.

To pull a voice out of a mixed recording (a sung line over music, dialogue
under a bed), use `audio_stem_separate(asset_id)` on the audio or video asset:
its `vocals` stem is a new audio asset to re-time, trim, transcribe or feed to
speech-to-speech. `model_id: "fal-ai/elevenlabs/audio-isolation"` keeps only
the voice. Stems and results: `pr0ta-music` → "Stem separation".

New voices are not attached to cast members by themselves; save the choice to
the cast (`pr0ta-prep`) and record it in memory. Field-level contracts:
`pr0ta-api` → `reference/voice-v2.md`.

## Lip sync audio

A lip-sync route drives picture from finished audio, so the dialogue must be
final first: generate it here, approve it with the user, trim it to the line
(`assets_trim`), then hand the audio asset to the route resolved with
`models_preferred(modality: "lipsync_model")` (`pr0ta-video`). Whether a shot
uses native video dialogue or TTS plus lip sync is decided in `pr0ta-video`.

## Time-indexing

Word-keyed and beat-keyed editing needs an index: word timing for speech, beat
and transient anchors for music. PR0TA builds most of it for you.

**What PR0TA does in the background**

- Every generated or uploaded audio asset is transcribed with the project's
  Audio→Text setting (`audio_to_text_model` in Settings → Tools) at word
  granularity.
- A transcribed speech asset (dialogue, narration, voiceover, TTS) also fills
  the narration timeline's transcript layer; music and SFX do not.
- Some music generations are beat-analyzed as well.
- Video assets, and copies cut with `assets_trim`, are not indexed
  automatically. For a trimmed copy, shift the source's timing by the in point
  or index the copy.

**Before you cut on an asset's timing, check its index**

- Speech: `transcription_get(asset_id)`. A "Transcription not found" error
  means no index yet; for an asset created in the last minute or two,
  background indexing may still be running, so wait and read again before
  starting one. A result has `words[]`,
  `segments[]`, `timestamp_granularity`, and `transcription_summary.model_id`
  (the model that produced it).
- Music and SFX: `music_analyze(asset_id)` with default options returns the
  stored analysis when one exists and starts analysis only when none does.

**Start indexing only when needed**

Call `transcription_start(asset_id, model_id?, language?, diarization?,
timestamp_granularity?)` only when:

- the asset has no transcript, or it is a video asset (its audio is extracted;
  the task's `metadata.extracted_audio_asset_id` names the new audio asset);
- the stored transcript is segment-level and you need words; or
- you need a specific model's timing. ElevenLabs Scribe V2 returns a speaker
  id per word (diarization on unless disabled) and marks non-speech audio
  events such as laughter as timed entries with a `type`; use it for
  multi-speaker matching or cutting on breaths and laughs. Otherwise pass the
  `model_id` from `models_preferred(modality: "audio_to_text_model")`.
  (`transcription_start` uses Scribe V2 when `model_id` is omitted.)

Poll with `tasks_get`, then read with `transcription_get`.

Call `music_analyze` for instrumental music or SFX whose beats, downbeats or
transients will place cuts or hits (`pr0ta-music` → "Beat analysis").

**Rules**

- Transcription does not find beats and music analysis does not find words.
  Ignore transcripts of instrumental assets.
- A regenerated or edited take is a new asset with its own index. Never reuse
  timestamps from an earlier take; read the new asset's index.
- If indexing fails, fix the cause and index again; do not cut by ear on
  guessed times.

## Transcription

Uses: subtitles (segment granularity), word-accurate cuts and trims (word
granularity), dialogue matching (speaker ids), drift checks after an audio
change.

- `transcription_start` accepts audio or video assets; `language` is an ISO
  code (omit to detect); `timestamp_granularity` is `word` or `segment`, one
  per call.
- `transcription_get` returns `text`, `segments`, flat `words` with start and
  end times, counts, the options used, and `transcription_summary` (model id,
  detected language). While a transcription is still running it returns
  `{status, task_id, in_flight: true}` (REST answers `202`): poll the task. A
  clip with no speech has a finished transcript: `status: completed`,
  `words: []`, `text: ""`. Do not transcribe it again.
- Transcription is billed once per asset: `transcription_start` returns the
  existing transcript, or joins the running task, with `deduplicated: true`
  when it is compatible with the request (word timing when you ask for words,
  the language you name, speaker ids when you ask for diarization). An
  incompatible one starts a new transcription; `force: true` always does.
- If the narration timeline's transcript layer did not fill (for example the
  asset is not labeled as speech), `pr0ta-sync` covers repopulating it.

REST equivalents: `POST /api/audio/transcription/start` (`asset_id`,
`project_id`, `model_id`; snake_case or camelCase), `POST
/api/v2/projects/{project_id}/transcribe` with exactly one of `asset_id`,
`source_url` or an uploaded `file` (URLs and uploads become project audio
assets first), `POST /api/v2/projects/{project_id}/transcribe/batch` with
`asset_ids`, and `GET /api/v2/projects/{project_id}/assets/{asset_id}/transcription`
to read (404 when none exists). The asset's metadata
(`GET /api/v2/projects/{project_id}/assets/{asset_id}/metadata`) shows both
indexes as `whisper_index` and `music_analysis`. Contracts: `pr0ta-api` →
`reference/voice-and-transcription.md`.
