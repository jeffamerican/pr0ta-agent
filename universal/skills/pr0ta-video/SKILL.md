---
name: pr0ta-video
description: "PR0TA video generation and repair: text-to-video, image-to-video, reference-to-video, first/last frame, keyframes, extend, video edit and video-to-video, lip-sync, motion control and motion transfer, camera moves and multi-angle trajectories, native audio and dialogue, multi-shot continuity, on-screen text, duration limits, upscale, and provider recovery. Read when generating, extending, editing, or troubleshooting video."
---

# Video Generation

For recurring characters, locations, or props, read `pr0ta-consistency` first. Before writing any generation prompt, read `pr0ta-prompting` and the model reference that the resolved model routes to below.

For an existing project, call `memory_context_pack` with `task_intent: "video_generation"` or `"storyboard_prompt"` and the relevant scope. Carry approved references, continuity decisions, and unresolved conflicts into the shot plan. Record a selected take or a change of approach with `memory_record_decision` or `memory_record_note`.

## Resolve the Model

The platform chooses models, not this skill. The admin pins models per modality and each user may override them in Settings → Tools.

1. Name the operation, then its modality key:

| Operation | Modality key |
|---|---|
| Prompt-only shot | `video_model` |
| Animate a still (opening frame, optional last frame) | `video_edit_model` |
| Mixed image, video, or audio references | `reference_to_video_model` |
| Continue an existing clip | `video_extend_model` |
| Transform or restyle a source clip | `video_to_video_model` |
| Make a still or clip speak a finished soundtrack | `lipsync_model` |
| Drive a character image with a performance video | `motion_transfer_model` |
| Talking-head dialogue from image plus audio | `dialogue_video_model` |
| Upscale, denoise, deblur, interpolate | `video_upscale_model` |
| Reframe to another aspect ratio | `video_reframe_model` |
| Remove a background | `video_bg_removal_model` |

2. If the user named a model, use it. Otherwise resolve the key with `models_preferred(modality=...)`; `pr0ta-api` → "Choosing a model" owns the full rule, including a null `model_id`.
3. Call `models_get_defaults(model_id)`. Send a `mode` from its `supported_modes` unless the model reference documents a route-specific mode, and treat its schema as the field, enum, duration, and resolution authority. Several image-to-video routes (Gemini Omni Flash 1.1, H3 Max, Wan 3.0 Prime, Grok Imagine Video 1.5, and others) accept only `ref_to_vid`.
4. If the `models_get_defaults` response has a `draft_mode` block, the model can draft: render a cheap low-resolution draft, review it, and finish only the approved draft at full resolution. Draft by default for new or changed shots and anything likely to need more than one attempt; generate directly only for an already-approved shot or an edit or extend. Read `reference/draft-to-final.md`.
5. Read the model reference for the resolved id (routing table below) before writing its prompt.
6. For cost-sensitive choices, query `GET /api/crew/model_pricing?model_id={model_id}` for each exact candidate and output configuration. Skills carry no prices.

REST equivalents: `GET /api/v2/models/preferred?modality=...`, `GET /api/v2/models`, and `GET /api/crew/model_defaults?model_id={model_id}`.

### Capability Facts

Use these only when the user asks for the capability; they are not a ranking.

- **Trained character identity tokens:** Seedance 2.0 Omni is the only route with `character_id` / `character_ids[]`; the Seedance 2.0 family is the one with positional `@image1`/`@video1`/`@audio1` binding.
- **Elements, `camera_control`, `voice_ids[]`, custom multi-shot arrays:** Kling routes only.
- **Scripted camera trajectory from one image:** `minimax/h3-max/multi-angle/image-to-video` follows 2–12 camera keyframes (normalized time, azimuth, elevation, distance) around a frozen or animated scene.
- **Images pinned to exact frame positions:** FLUX 3 keyframes (1–10 images on a 24 fps timeline); FLUX 3 also has a Draft→Enhance lifecycle.
- **Single takes up to 30 seconds:** Seedance 2.5 routes (4–30 s) and Wan 3.0 / Prime (2–30 s).
- **Audio owns the timing:** LTX 2.5 audio-to-video builds picture around a required source track; lip-sync routes animate a still or clip to finished dialogue.
- **Performance transfer from a driving video:** motion-control routes; read `reference/motion-transfer.md`.
- **Native 4K:** Seedance 2.5 `-4k` routes, Gemini Omni Flash 1.1 (`4k`), Kling V3/O3 4K routes.
- **Colour-critical 10-bit 1080p or MOV 4:4:4:** `byteplus/seedance-2.5` (ModelArk).
- **Many reference images with tagged roles:** Grok Imagine Video 1.5 reference-to-video (1–7 images tagged `<IMAGE_0>`…), Seedance 2.5 Omni (up to 30 images, 10 videos, 10 audios).

## Model References

Route by the resolved `model_id`:

| Resolved model id | Read |
|---|---|
| `muapi/seedance-2.5-*`, `byteplus/seedance-2.5` | `reference/seedance-2.5.md`; for songs and sung performance also `reference/seedance-2.5-sync-sound.md` |
| `muapi/seedance-2-*`, `muapi/sd-2-vip-*` (Seedance 2.0) | `reference/seedance-omni.md`; for storyboard chunks with a global visual bible also `reference/seedance-global-storyboard.md` |
| `muapi/wan3.0-*`, `alibaba/wan-3.0-prime/*` | `reference/wan-3.0.md` |
| `google/gemini-omni-flash/v1.1/*` | `reference/gemini-omni-flash-1.1.md` |
| `fal-ai/minimax/hailuo-03/*`, `minimax/h3-max*` | `reference/hailuo-h3.md` |
| `blackforestlabs/flux-3/*` | `reference/flux-3.md` |
| `lightricks/ltx-2.5/*` | `reference/ltx-2.5.md` |
| `kling/*`, `fal-ai/kling-video/*` | `reference/kling-prompting.md` |
| `xai/grok-imagine-video/v1.5/*` | `reference/grok-imagine-video-1.5.md` |
| any `motion_transfer_model` result | `reference/motion-transfer.md` |
| anything else | `reference/video-reference-field-matrix.md`, then `models_get_defaults` |

Cross-model references: `reference/draft-to-final.md` (draft first, finish the approved draft), `reference/video-reference-field-matrix.md` (validator and provider reference fields, durations), `reference/native-audio.md` (audio fields, dialogue prompting, extraction), `reference/generative-typography.md` (on-screen text), `reference/provider-recovery.md` (rejections, stalls, pivots).

## Submission Contract

Submit with `generation_submit` (or `generation_batch_submit` for up to ten items), poll with `tasks_get` to a terminal state, and inspect the finished asset before editorial use; parallel submission limits are in `pr0ta-api` → "Rate limits and concurrency". Use `agent_chat_orchestrate_prompt` when a department-authored, model-specific prompt package is required.


```json
{
  "project_id": "project-uuid-or-slug",
  "request": {
    "generator": "video",
    "mode": "<a mode from models_get_defaults(model_id).supported_modes>",
    "model": "<model_id from models_preferred>",
    "prompt": "Use the supplied image as identity, wardrobe, and set authority. The camera slowly pulls back while those traits hold.",
    "reference_image_asset_ids": ["approved-image-asset-id"],
    "duration": 5,
    "aspect_ratio": "16:9"
  }
}
```

Use REST only when MCP is unavailable, for high-volume scripts, or for an unexposed route: `POST /api/v2/projects/{project_id}/generate` (batch: `/generate/batch`). Read `pr0ta-api` for the shared request envelope.

### Modes

- `txt_to_vid`: text only. Send no reference fields; any reference on a text request can route it to a reference-capable model.
- `ref_to_vid`: any image, video, or audio conditioning, including single-image I2V, first/last frame, and Omni/R2V routes. FLUX 3 keyframe routes document `transition`; see `reference/flux-3.md`.
- `video_to_video`: transform a source clip (edit, restyle, relight, motion transfer).
- `extend_video`: continue a source clip.
- `video_audio_to_video` / generator `lipsync`: audio-driven video and lip-sync routes.

Always confirm against `supported_modes`; a family can use different modes per route. No current catalog video route lists `img_to_vid`.

Generic reference validation and provider-native contracts are separate layers. Read `reference/video-reference-field-matrix.md` before any reference-heavy payload:

- `character_id` / `character_ids[]` are restricted to Seedance 2.0 Omni.
- `camera_control` and `voice_ids[]` are Kling-only.
- Generic `reference_video_urls[]` / `reference_audio_urls[]` arrays work only on the multimodal reference routes listed there; FLUX 3 and LTX 2.5 use operation-specific fields.
- H3 and H3 Max R2V reject audio-only reference sets.

## Duration and Shape

Duration, aspect ratio, and resolution are per route; take them from `models_get_defaults` and the model reference. Inspect the delivered duration and dimensions before timeline placement.

Prefer one longer clip only when the action genuinely belongs in one generation. Split at a motivated cut when a beat exceeds the route maximum. If motion must stay continuous, extend the source. Otherwise generate companion coverage or use a deliberate still with a Ken Burns move. Never leave an empty timeline tail or stretch a short source invisibly.

Input orientation does not guarantee output orientation. Always set `aspect_ratio` where the route exposes it (several I2V routes follow the input image instead; prepare it at the delivery ratio), and keep critical content away from crop-sensitive edges. Set the sequence resolution before placement; `POST /timeline/clips` normalizes scale, pad, format, and FPS to the sequence. Read `pr0ta-timeline` for source-shortfall and fit-to-fill rules.

## Continuity Workflows

- **Seedance 2.0 storyboard chunks:** one approved global visual bible plus one chronological sheet per chunk. Use `storyboard_chunks_list`, `storyboard_reference_sheet_generate`, `tasks_get`, and `storyboard_reference_sheets_list`, and select an approved sheet before dispatch. Read `reference/seedance-global-storyboard.md`.
- **Kling multi-shot:** up to 5 (V3) or 6 (O3) cuts in one generation with shared Elements. Its shot labels and `@Image1` / `@ElementN` tokens are not interchangeable with Seedance. Read `reference/kling-prompting.md`.
- **Continuing a Seedance 2.0 clip:** Omni Reference with the previous clip as `@video1` is reference-guided continuation. MuAPI's provider-native 2.0 extension routes need the original provider `request_id` and are not in the unified catalog; see `reference/seedance-omni.md`.
- **Source-preserving change or continuation:** use the family's exact Edit or Extend route (for example Seedance 2.5 Video Edit and Seedance 2.5 Video Extend, FLUX 3 Extend, Kling V3 Video Extend, Gemini Omni Flash 1.1 Edit). Do not substitute a generic reference call.

## Repairs and Enhancement

Choose the narrowest operation that fixes the defect:

- Continue motion: an extend route (`video_extend_model`).
- Change one region, object, or style while keeping the clip: an edit route (`video_to_video_model`); request one focused change and name what must stay.
- Correct framing: `video_reframe_model`.
- Remove or replace a background: `video_bg_removal_model`.
- Replace or relight the world behind a live-action subject while keeping the plate: Beeble SwitchX (`video_to_video`). Read `pr0ta-hybrid`.
- Resolution, noise, blur, or cadence without creative change: `video_upscale_model`. Topaz Precision, Denoise, Deblur, and Interpolate are fidelity utilities; Generative and Creative reconstruct detail and need the user's approval of that tradeoff. Query live defaults per route; controls do not transfer between Topaz families.

When a narration beat exceeds generation limits: split at a natural clause, extend a successful source, cut to companion coverage, then use a still or Ken Burns treatment. Regenerate the whole piece only when the defect is a global creative decision, not a local shot failure.

## Native Audio and Dialogue

Audio controls are endpoint-specific. Send an audio field (`sound`, `audio`, `generate_audio`, or Wan's `enable_audio: bool`) only where the selected schema exposes it. A missing toggle does not mean silence: Seedance 2.5, H3, H3 Max, and Gemini Omni Flash 1.1 generation routes return audio-bearing video; MuAPI Wan uses `enable_audio: bool` while Fal Wan Prime uses `audio`; FLUX 3 and LTX 2.5 expose `generate_audio`. Read `reference/native-audio.md` and the model reference.

Speech-bearing results need a transcript before timeline use. PR0TA indexes generated audio in the background with the project's Audio→Text setting; check the asset's index first and start `transcription_start` only when none exists or word-level timing from a specific model is required. `pr0ta-audio` owns this rule. Verify exact wording, speaker identity, sync, and unwanted speech.

## On-Screen Text

Current premium video models can generate and animate legible text; a verified generated result is valid production media. Read `reference/generative-typography.md` before producing on-screen copy. It owns exact-string prompting, frame-by-frame QC, repair, and the deterministic still-plus-timeline fallback.

## Reliability

Follow the `pr0ta-api` reliability contract.

- Provider errors arrive asynchronously. Preserve `error`, `error_detail`, and `error_reason`, and distinguish credits, validation, policy rejection, and stalls before retrying. Read `reference/provider-recovery.md`.
- An initial `credits_cost: null` is neither success nor failure; poll the task.
- Actual dimensions or duration may differ from the request; inspect the asset and normalize on the timeline.
- Premium operations (for example Kling O3 4K video-to-video) need the user's approval of the shown estimate before submission.
