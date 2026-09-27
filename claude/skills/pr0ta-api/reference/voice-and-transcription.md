## Voice Browser API

Resolve the TTS model with `models_preferred(modality="dialogue_model")`; `pr0ta-audio` → "Choose the model" covers choosing when nothing is set.

Discover available provider voices before making TTS calls where the user has not provided an exact voice.

### Browse Voices

```
MCP: voices_list
REST: GET /api/v2/projects/{project_id}/voices/browser
```

Parameters: `provider` (`all`, `elevenlabs`, `google`/`gemini`, `minimax`, `kling`, `xai`), `search`, `page_size`, `include_live`, and `include_custom`. Returns normalized voice profiles with `provider`, `voice_id`, `name`, `category`, `voice_type`, `supported_models`, optional `preview_url`, and `selection`.

**Usage:** Call this browser before TTS generation to let users browse/search/select voice IDs programmatically, rather than hardcoding voice IDs or requiring the browser Voice Design tab. Copy the selected voice's `selection` fields into `generation_submit` or REST `/generate`.

**ElevenLabs model compatibility.** Voice metadata such as `high_quality_base_model_ids` or `verified_languages[].model_id` is not a hard gate for a given ElevenLabs model; do not derive a `supports_v3` flag from it. If the resolved model rejects a voice, report it and choose again with `models_list(modality="dialogue_model")`. See `voice-v2.md` for the full response shape.

---

## Transcription API

PR0TA exposes editorial-grade transcription with word- or segment-level timestamps under the **audio-to-text modality**. Two providers are exposed:

Pass `model_id` from `models_preferred(modality="audio_to_text_model")` (Settings → Tools → Audio→Text, else the admin pin). When `model_id` is omitted, the transcription routes use ElevenLabs Scribe V2. Capabilities of the audio-to-text models:

- **ElevenLabs Scribe V2** (`fal-ai/elevenlabs/speech-to-text/scribe-v2`): speaker IDs, audio event detection (laughter, applause, breaths), and per-word `event_type` classification on top of word timing. The short aliases `scribe-v2` and `scribe_v2` normalize to this id server-side.
- **Whisper** (`fal-ai/whisper`): broad language coverage; word timing without speaker or event labels.

**This is the source of truth for any timing, sync, subtitle, or dialogue-matching work.** Always go through this endpoint; the post-production timeline and narration timeline both depend on the word-level output.

### Start Endpoint (Auto-Populates Narration Timeline)

```
MCP: transcription_start
Required: project_id, asset_id
Optional: model_id (omitted: Scribe V2), timestamp_granularity (default word)

REST fallback:
POST /api/audio/transcription/start
```

```json
{
  "asset_id": "<narration_audio_asset_id>",
  "project_id": "<project_id>",
  "model_id": "<model_id from models_preferred(modality=\"audio_to_text_model\")>"
}
```

Both camelCase (`assetId`, `projectId`) and snake_case (`asset_id`, `project_id`) field names are accepted.

**Side effect:** On completion, the project's narration timeline transcript layer is auto-populated with word-level timestamps, sentence boundaries, and paragraph boundaries. This is what enables the narration-timeline editing workflow.

### Standalone Transcription Route

For transcription work that does not need to auto-populate a narration timeline (e.g. subtitle generation, dialogue matching):

```
POST /api/v2/projects/{project_id}/transcribe
```

Provide exactly **one** input source:

```json
{ "asset_id": "existing-pr0ta-audio-asset-id" }
```
```json
{ "source_url": "https://example.com/audio.wav" }
```
Or multipart form-data: `file=@audio.wav`

Optional parameters:

```json
{
  "model_id": "<model_id from models_preferred(modality=\"audio_to_text_model\")>",
  "language": "en",
  "diarization": true,
  "timestamp_granularity": "word"
}
```

- `model_id`: the audio-to-text model. Pass it explicitly (from `models_preferred`) so the result does not depend on the route's fallback.
- `timestamp_granularity`: `"word"` or `"segment"` (one mode per call — `"both"` is not supported).
- `diarization`: speaker labels when `true`. With Scribe V2, diarization is automatic — speaker IDs appear in word-level results without requiring this flag.
- `language`: ISO code; omit for auto-detect.

### Response (Async Task)

```json
{
  "task_id": "uuid",
  "status": "queued",
  "asset_id": "target-audio-asset-id",
  "input_kind": "asset|source_url|upload",
  "created_asset": false,
  "download_url": "/api/v2/projects/{project_id}/assets/{asset_id}/download"
}
```

Poll `task_id` via the standard reliability contract.

### Retrieval — Dedicated Endpoint (Only Supported Path)

After the transcription task reaches `succeeded`, retrieve word-level timing data from the dedicated transcription endpoint:

```
MCP: transcription_get
REST fallback:
GET /api/v2/projects/{project_id}/assets/{asset_id}/transcription
```

Response shape:

```json
{
  "status": "ready",
  "asset_id": "asset-uuid",
  "text": "Hello world",
  "words": [
    { "text": "Hello", "start": 0.0, "end": 0.35, "speaker": "S1", "event_type": "speech" },
    { "text": "world", "start": 0.40, "end": 0.82, "speaker": "S1", "event_type": "speech" }
  ],
  "segments": [
    {
      "text": "Hello world",
      "start": 0.0,
      "end": 1.2,
      "words": [ /* same word entries */ ]
    }
  ]
}
```

Use `words[]` for flat word-level timing, or `segments[].words[]` for segment-grouped timing. Scribe V2 additionally populates `speaker` and `event_type` on every word entry.

### Batch Mode

```
POST /api/v2/projects/{project_id}/transcribe/batch
```
```json
{
  "asset_ids": ["asset-1", "asset-2"],
  "model_id": "<model_id from models_preferred(modality=\"audio_to_text_model\")>",
  "language": "en",
  "timestamp_granularity": "segment"
}
```

### Behavior Notes

- `asset_id` inputs are validated against the current project.
- `source_url` and uploads are first materialized as PR0TA audio assets, then transcribed through the same pipeline.
- For remote `source_url` assets, transcription uses the original external URL, not a placeholder storage path.

See the `pr0ta-audio` and `pr0ta-sync` skills for workflow integration.

## Audio Extraction From Video Asset

PR0TA supports extracting a standalone audio asset from a project video asset, and transcribing video inputs by first deriving a real audio asset and then transcribing it. This feeds audio-only editorial work, dialogue timing, music analysis on scored video clips, waveform generation, and future stem/cleanup workflows.

### Extract Audio

```
POST /api/v2/projects/{project_id}/assets/{asset_id}/extract-audio
```

Request body:

```json
{
  "codec": "wav",
  "category": "extracted_audio",
  "subject": "Optional label",
  "folder_path": "/optional/folder"
}
```

Response:

```json
{
  "success": true,
  "source_asset_id": "video-asset-id",
  "extracted_asset_id": "audio-asset-id",
  "download_url": "/api/v2/projects/{project_id}/assets/{audio-asset-id}/download",
  "asset": {
    "...": "standard AssetRead payload"
  }
}
```

**Provenance fields** on the derived audio asset:

- `derived_from_asset_id`
- `source_video_asset_id`
- `derivation_type: "extracted_audio"`
- `source_kind: "video"`
- `extracted_audio_codec`

These fields are stored in asset metadata and labels so downstream skills can reason about origin.

### Transcription Inputs

`POST /api/v2/projects/{project_id}/transcribe` accepts:

- audio assets
- video assets with audio
- uploaded audio files
- uploaded video files with audio
- source URLs to audio files
- source URLs to video files

For video inputs, PR0TA:

1. creates or resolves the source video asset,
2. extracts a standalone derived audio asset,
3. queues transcription against that derived audio asset.

The response includes derivation metadata:

```json
{
  "task_id": "task-id",
  "status": "queued",
  "asset_id": "transcription-audio-asset-id",
  "input_kind": "asset",
  "created_asset": false,
  "download_url": "/api/v2/projects/{project_id}/assets/{transcription-audio-asset-id}/download",
  "source_asset_id": "original-video-asset-id",
  "source_kind": "video",
  "extracted_audio_asset_id": "transcription-audio-asset-id"
}
```

For direct audio inputs:

- `asset_id` is the audio asset being transcribed.
- `source_asset_id` equals `asset_id`.
- `source_kind` is `"audio"`.
- `extracted_audio_asset_id` is `null`.

### When to Use Each Path

- **Use `extract-audio`** when you want an audio-only editing surface from a video, a reusable asset for music analysis on a scored clip, or a dialogue asset separate from picture.
- **Use `transcribe` directly on video** when you only need timing/transcript output and don't want to manually call extraction first.

**Implementation note.** Video transcription is implemented as "video → derived audio asset → transcription," not "direct video transcription." This is intentional — the derived audio asset is reusable by other workflows and preserves editorial clarity.

**Failure mode.** If a video has no audio stream, extraction and transcription both fail with a validation error. Silent B-roll should be generated with `sound: "off"` from the start and routed directly to the timeline.
