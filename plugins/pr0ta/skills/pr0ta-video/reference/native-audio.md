# Native Audio and Sound Control

Read this file when a video route's audio behavior matters: deciding between native sound and post-production audio, silencing a route, prompting dialogue, or pulling the audio track out of a generated clip. Transcript and indexing policy belongs to `pr0ta-audio`.

## Native Audio or Separate Audio

Overlaying separate TTS on a silent clip with a visible speaker produces no lip sync. Use a route with native dialogue, a dedicated lip-sync route (`lipsync_model`), or stage the speaker off camera. Seedance 2.0 `@audio1` is a conditioning reference, not a guarantee of verbatim speech or phoneme-level sync.

| Clip type | Audio plan | Why |
|---|---|---|
| Dialogue with a visible speaker | Audio-bearing route, or lip-sync after the take | Native audio gives lip sync, ambience, and natural timing |
| Narration over footage (speaker not visible) | Silent-capable route, then TTS | Separate TTS gives stronger voice and wording control |
| B-roll or montage needing precise post sound | Silent-capable route | Music and effects stay independently editable |
| Ambient or atmosphere | Audio-bearing route | Native ambience (rain, crowd, traffic) adds realism |

## Audio Fields Are Route-Specific

Send an audio field only when the selected route's `models_get_defaults` schema exposes it. A missing field does not mean silent output.

- **Seedance 2.5 (MuAPI):** every route returns audio-bearing video. T2V, I2V, first/last, Omni, Spicy, and International expose no audio opt-out; Edit and Extend expose route-specific `generate_audio`.
- **Seedance 2.5 on ModelArk (`byteplus/seedance-2.5`):** exposes `generate_audio`; `mov` output carries PCM audio. The catalog does not certify its audio, so inspect the file.
- **Hailuo H3 and H3 Max (including Multi-Angle):** every video route returns native audio and exposes no sound toggle.
- **FLUX 3 video:** native audio across the family. Generation schemas expose `generate_audio`, defaulting to `true`, so request silence explicitly; Draft Enhance preserves the draft's audio state and accepts no replacement audio prompt. Read `flux-3.md` for dialogue structure and the Draft lifecycle.
- **LTX 2.5:** T2V and I2V return synchronized generated audio and expose `generate_audio`, defaulting to `true`. Audio-to-video carries the required source audio into the synchronized result and uses a narrower payload surface. Read `ltx-2.5.md` before sending A2V fields.
- **Wan 3.0 / Prime:** T2V, I2V, and R2V generate synchronized audio by default through `enable_audio: true` on MuAPI routes (Fal-native Prime uses `audio`). Set `enable_audio: false` explicitly for silent output; standard and Prime share this contract.
- **Gemini Omni Flash 1.1:** generation routes return native audio with no toggle. The Edit route documents no audio control and has returned audio-bearing output; inspect it.
- **Grok Imagine Video 1.5:** the provider advertises native synchronized audio with no toggle; PR0TA verifies audio on the delivered file.
- **Kling:** on routes whose live defaults expose `sound`, PR0TA maps `sound: "on"` / `"off"` to the provider's audio field; some Kling routes also expose `voice_ids` (check the schema). Kling O3 4K video-to-video preserves source audio with `keep_audio`.
- **Seedance 2.0:** audio controls are route-dependent; the VIP schemas document no universal control.

Never substitute `sound` for `enable_audio: bool` or `generate_audio`, or the reverse. If the production requires silence, choose a route that explicitly supports disabling audio; Seedance 2.5 (MuAPI), H3, Gemini generation, and Grok routes cannot be silenced by omission.

## Transcripts Before Editing

Speech-bearing video needs a transcript before timeline editing: word timing drives dialogue cuts, speaker labels route lines, and breaths and pauses mark cut points. PR0TA indexes generated audio in the background; check the asset's index first and start `transcription_start` only when none exists or a specific model's word timing is required. Read `pr0ta-audio` → "Time-indexing" for the rule.

A clip verified to have no audio stream needs no transcript. Extraction and transcription of a silent file fail with a validation error, so generate silent B-roll with the route's explicit control from the start (`sound: "off"`, `enable_audio: false`, or `generate_audio: false`).

## Audio Extraction From Video

Extract the audio track when you need it as a standalone asset: music analysis on a scored clip, separate dialogue editing, or waveform work.

```
POST /api/v2/projects/{project_id}/assets/{asset_id}/extract-audio
{"codec": "wav", "category": "extracted_audio", "subject": "Optional label"}
```

The response returns `source_asset_id`, `extracted_asset_id`, `download_url`, and the new asset. `POST /api/v2/projects/{project_id}/transcribe` also accepts a video asset directly: PR0TA extracts a derived audio asset and transcribes that, returning `source_asset_id`, `source_kind: "video"`, and `extracted_audio_asset_id`. Read the transcript from the extracted asset's id via `GET /api/v2/projects/{project_id}/assets/{asset_id}/transcription`.

Derived audio assets carry provenance: `derived_from_asset_id`, `source_video_asset_id`, `derivation_type: "extracted_audio"`, `source_kind: "video"`, and `extracted_audio_codec`. The extracted audio asset, not the source video, is what gets indexed.

## Prompting Native Dialogue

Embed speech in the prompt only on a route with native dialogue, then inspect wording, sync, and mix.

**Seedance 2.0 (audio-capable route):**
```
@image1 — A woman in a red coat stands in a rainy alley. She turns to the camera
and says "We don't have much time. Follow me." Camera holds on her face as she
speaks, then she turns and walks into the rain. Ambient city sounds, rain on
pavement, distant traffic.
```

**Kling O3/V3 (dialogue in quotes within the scene):**
```
@Element1 sits across the table in a dimly lit café. He leans forward and says
"I've been waiting for you." Camera slowly pushes in. Ambient café sounds,
soft jazz, clinking glasses.
```

- Put dialogue in quotation marks inside the scene description and attribute it to a named speaker.
- Describe ambience alongside the dialogue.
- Keep dialogue to one or two lines per clip; long speeches drift.
- Add delivery cues: "whispers urgently", "says softly".
- For multi-character dialogue on Kling, use multi-prompt mode with one exchange per segment.
- Hailuo H3 uses stable `(S1)` speaker IDs plus `<d>[Language] exact text</d>` blocks; read `hailuo-h3.md`.

## Non-English Dialogue

- Write dialogue in the target language and script, not a transliteration. Transliterations are usually ignored and the model produces English speech or ambience instead.
- Non-English native results remain inconsistent. Test a short clip first.
- For reliable non-English dialogue, choose a silent-capable route, disable its audio explicitly, and generate the voice with a TTS model from `models_preferred(modality="dialogue_model")` (see `pr0ta-audio`), then lip-sync if the speaker is visible.
- For non-English narration over footage, use separate TTS.
