# Native Audio & Sound Control — Reference

**Start here:** this file is the deep dive on native video audio. The decision rule ("native audio vs separate TTS") lives in `pr0ta-video/SKILL.md`. Read this file when you need to prompt for sync dialogue, enforce the post-generation transcription gate on any audio-bearing video, or extract an audio track from a generated clip.

---

## Native Audio & Sound Control

### When to Use Native Audio vs Separate TTS

This is a critical production decision. Simply overlaying separate TTS on silent visible-speaker video produces no lip sync. Use an endpoint with verified native dialogue, a dedicated lip-sync workflow, or deliberately stage the speaker off camera. Seedance 2.0 `@audio1` is a conditioning reference, not a guarantee of verbatim speech or phoneme-level sync.

| Clip Type | Preferred audio plan | Why |
|-----------|----------------------|-----|
| **Dialogue (speaker visible)** | Use an audio-bearing route | Native audio gives lip sync, ambient sound, and natural speech timing |
| **Narration over footage (speaker NOT visible)** | Use a silent-capable route, then layer TTS | Separate TTS gives stronger voice and wording control |
| **B-roll / montage** | Use a silent-capable route when precise post sound is required | Music and SFX remain independently editable |
| **Ambient / atmosphere** | Use an audio-bearing route | Native ambient sound adds realism (rain, crowd, traffic) |

### Sound Parameter Is Endpoint-Specific

Set `sound` only when the selected endpoint's live defaults expose it:

```json
{
  "sound": "on"
}
```

- `"on"` -- request native audio baked into the video on an endpoint that supports the field
- `"off"` -- silent video output for post-production audio layering

Do not generalize this control across model families. A missing audio field does not mean a silent result:

- **Seedance 2.5:** every route returns audio-bearing video. T2V, I2V, first/last, Omni, Spicy, and International expose no audio opt-out; Edit and Extend expose route-specific `generate_audio` behavior.
- **Hailuo H3:** every video route returns native stereo audio and exposes no sound toggle.
- **FLUX 3 video:** native audio is supported across the video family. Current Fal generation schemas expose `generate_audio`, defaulting to `true`, so silence must be requested explicitly where that field exists; Draft Enhance preserves the draft's audio state and accepts no replacement audio prompt. Read `flux-3.md` for dialogue structure and the Draft lifecycle.
- **LTX 2.5:** T2V and I2V return synchronized generated audio and expose `generate_audio`, defaulting to `true`. Audio-to-video carries the required source audio into the synchronized result and uses a narrower payload surface. Read `ltx-2.5.md` before sending A2V fields.
- **Wan 3.0 / Prime:** T2V, I2V, and R2V generate synchronized audio by default through `enable_audio: true`. Set `enable_audio: false` explicitly for silent output; standard and Prime share this contract.
- **Seedance 2.0:** audio controls remain route-dependent; current VIP schemas do not document one universal control.

Query `models_get_defaults`, read the model reference, and verify the returned media. If the production requires silence, select a model/route that explicitly supports disabling audio rather than assuming omission will do so.

### Mandatory Time-Indexing for Audio-Bearing Video

**Every generated video asset that actually contains speech-bearing audio must be transcribed before it enters the post-production timeline.** This includes explicit audio-on requests, always-audio families such as Seedance 2.5 and Hailuo H3, and default-audio families such as Wan 3.0, FLUX 3, and LTX 2.5. Video with dialogue, diegetic speech, or ambient speech falls on the speech side of the two-path gate — transcribe it with Scribe V2. This is the same hard rule that applies to pure audio assets — see `pr0ta-audio` → "Mandatory Time-Indexing Rule (Two Paths)" for the full policy.

Why this matters specifically for video-with-audio:

- **Dialogue cuts need word-level timing.** If you intend to cut a line in half, shorten a beat of dialogue, or match a cut to the word the character says, you need Scribe V2 word timing on the video asset itself.
- **Speaker IDs drive multi-character dialogue tracks.** Scribe V2's automatic diarization routes lines to the right speaker so the editor can cut a conversation reliably.
- **Audio events mark cuttable moments.** Breaths, silences, laughter, and emphasis are editorial hooks — without the transcription, they're invisible.

**Two ways to transcribe a video asset — pick the right one.**

**Option 1 — Direct video transcription (simple case).** `POST /api/v2/projects/{project_id}/transcribe` now accepts video asset IDs and video file uploads directly. PR0TA extracts a derived audio asset under the hood and queues transcription against it in a single call. Use this when you only need the transcript and don't need the audio track as a standalone reusable asset. The response surfaces the derivation so you can see what happened:

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

For direct audio inputs, `source_asset_id` equals `asset_id`, `source_kind` is `audio`, and `extracted_audio_asset_id` is `null`.

**Option 2 — Extract audio first, then act on the audio asset.** When you want the audio track as a reusable asset (for music analysis, separate dialogue editing, waveform generation, future stem work) call `POST /api/v2/projects/{project_id}/assets/{asset_id}/extract-audio` first, then pass the extracted audio asset to the transcription endpoint (or to `POST /api/audio/transcription/start` for narration-timeline auto-population, or to the music analysis endpoint if it's an instrumental track). See "Audio Extraction From Video" below for the extract-audio endpoint details.

**Enforcement:**

1. After any video generation expected to contain speech reaches `succeeded`, verify that the file has an audio stream and route it to the correct path:
   - **Narration-timeline productions:** extract audio first (or use direct transcription), then call `POST /api/audio/transcription/start` with the audio asset so the narration timeline's transcript layer auto-populates.
   - **Standalone transcription (no narration timeline):** call `POST /api/v2/projects/{project_id}/transcribe` with the video asset directly.
   - Always pin Scribe V2: `model_id: "fal-ai/elevenlabs/speech-to-text/scribe-v2"`.
2. Poll the transcription task. Do not mark the video asset "ready for editing" until its transcription task has reached `succeeded`.
3. Verify via `GET /api/v2/projects/{project_id}/assets/{asset_id}/transcription` that `status: "ready"` with populated `words[]`. Use whichever asset ID was actually transcribed — that will be the extracted audio asset, not the source video.
4. Only then add the video to the post-production timeline.

**If the video has no audio stream, extraction and transcription will fail with a validation error.** Silent B-roll should be generated with the exact route control from the start, such as `sound: "off"`, `enable_audio: false`, or `generate_audio: false`.

**For a video verified to have no audio stream, transcription is not required.** On endpoints that support `sound: "off"`, silent B-roll can go straight to the timeline after that result is confirmed.

### Audio Extraction From Video

Sometimes you want the audio track of a video as a reusable, standalone asset — for music analysis on a scored clip, for separate dialogue editing, for waveform generation, or for future stem and cleanup workflows. PR0TA exposes a dedicated extraction endpoint for this.

```
POST /api/v2/projects/{project_id}/assets/{asset_id}/extract-audio
Authorization: Bearer $PAT
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

**Provenance fields on the derived audio asset.** Extracted assets carry provenance metadata so downstream skills can reason about origin:

- `derived_from_asset_id`
- `source_video_asset_id`
- `derivation_type: "extracted_audio"`
- `source_kind: "video"`
- `extracted_audio_codec`

These fields live in asset metadata and labels.

**When to use extract-audio vs direct video transcription:**

- **Use `extract-audio`** when you want an audio-only editing surface from a video, when you want to run music analysis on the audio track of a scored video clip, or when you want a reusable dialogue/music asset separate from picture.
- **Use `transcribe` directly on video** when you only need timing/transcript output and don't want to manually call extraction first.

**Important:** Video transcription is not "direct video transcription" in the implementation. It is "video → derived audio asset → transcription." PR0TA handles this under the hood, but the extracted audio asset is the thing that is actually transcribed and indexed. This is intentional: the derived audio asset is reusable by other workflows and preserves editorial clarity.

### Prompting for Native Sync Audio (Dialogue)

When a route has verified native dialogue, embed the speech directly in the prompt and inspect the take for wording, sync, and mix.

**Seedance 2.0 — generated-dialogue intent on an audio-capable route:**
```
@image1 — A woman in a red coat stands in a rainy alley. She turns to the camera
and says "We don't have much time. Follow me." Camera holds on her face as she
speaks, then she turns and walks into the rain. Ambient city sounds, rain on
pavement, distant traffic.
```

**Kling O3/V3 — dialogue in quotes within the scene description:**
```
@Element1 sits across the table in a dimly lit café. He leans forward and says
"I've been waiting for you." Camera slowly pushes in. Ambient café sounds,
soft jazz, clinking glasses.
```

**Tips for sync audio prompts:**
- Put dialogue in quotation marks within the natural scene description
- Describe ambient sound alongside the dialogue ("rain on pavement", "crowd noise", "wind")
- Keep dialogue short per clip — one or two lines. Long speeches drift.
- Include emotional/tonal cues: "whispers urgently", "shouts angrily", "says softly"

For Hailuo H3, do not use ordinary quoted dialogue as the primary contract. Read `hailuo-h3.md` and use stable `(S1)` speaker IDs plus `<d>[Language] exact text</d>` blocks.
- For multi-character dialogue, use multi-prompt mode with separate dialogue per segment

### Native Audio Language Limitations

**Native video audio works best for English.** For non-English dialogue:

- **Write dialogue in the actual target language**, not phonetic transliterations. For Hebrew, write actual Hebrew text (`"אומר בקול: 'סבא שלי אמר שיש הבטחה'"`), not English transliterations ("speaking aloud: 'Saba sheli omer...'"). Transliterations are almost always ignored — the model generates English speech or ambient sound instead.
- **Non-English results are still inconsistent.** Even with actual language text, some models may default to English or produce garbled speech. Test with a short clip first.
- **For reliable non-English dialogue:** Select a silent-capable endpoint, explicitly disable its audio, and use Gemini Flash TTS separately (see `pr0ta-audio` skill). Seedance 2.5 and Hailuo H3 cannot be made silent by omitting `sound`; choose another model when an isolated post-production voice track is required. Use ElevenLabs v3 only when the user needs a specific ElevenLabs voice.
- **For non-English narration over footage:** Always use separate PR0TA TTS — native audio language control is too unreliable for narration.

### Parameter Mapping Is Endpoint-Specific

On endpoints whose live PR0TA defaults expose `sound`, use `sound: "on"` / `sound: "off"`; PR0TA maps that control to the provider-native audio field. Never assume the mapping exists for another route. Current Seedance 2.0 VIP T2V/I2V/Omni, Seedance 2.5 standard, and Hailuo H3 routes do not accept this unified toggle. Seedance 2.5 and H3 remain audio-bearing despite that absence. Wan 3.0 exposes `enable_audio`, while FLUX 3 and LTX 2.5 expose `generate_audio`; follow the exact schema rather than substituting `sound`.

Wan 3.0-specific example:

```json
{
  "enable_audio": false
}
```

Use this explicit value when dialogue, narration, music, or SFX will be authored separately in post. When `enable_audio` is true or omitted, inspect the returned file for an audio stream and route speech-bearing content through transcription before editing.

| PR0TA API | Provider-level equivalent |
|-----------|--------------------------|
| `"sound": "on"` | `with_audio: true` / `generate_audio: true` |
| `"sound": "off"` | `with_audio: false` / `generate_audio: false` |
