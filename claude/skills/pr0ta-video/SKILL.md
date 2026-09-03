---
name: pr0ta-video
description: "PR0TA video generation guide for Seedance 2.0/2.5, Wan 3.0/Prime, Hailuo H3, FLUX 3, LTX 2.5, Kling, references, storyboard chunks, multi-shot continuity, extension, camera/audio control, duration limits, typography, and provider fallback. Read when generating, extending, or troubleshooting video."
---

# Video Generator Reference

For recurring characters, locations, or props, read `pr0ta-consistency` first. Before writing any generation prompt, read `pr0ta-prompting` and the selected model-family reference named below.

For an existing project, call `memory_context_pack` with `task_intent: "video_generation"` or `"storyboard_prompt"` and the relevant scope. Carry approved references, continuity decisions, and unresolved conflicts into the shot plan. Record a selected take or provider-strategy change with `memory_record_decision` or `memory_record_note`.

## Model Selection

**Seedance 2.5 Omni Reference (`muapi/seedance-2.5-omni-reference`) is the preferred production path.** Depart only for a specialist requirement or a documented recovery path.

- **Seedance 2.5:** preferred reference-led production family; 4–30 seconds; dedicated T2V, I2V, first/last, Omni, **Seedance 2.5 Video Edit**, and **Seedance 2.5 Video Extend** routes; model-ID resolution tiers through 4K. Read `reference/seedance-2.5.md`.
- **Seedance 2.0 Omni:** use for trained `character_id` identities, lowercase positional `@image1` / `@video1` / `@audio1` binding, or rhythm-led mixed references. Read `reference/seedance-omni.md`.
- **Wan 3.0 / Prime:** use exact T2V, I2V, or R2V routing for 2–30 second audiovisual work, optional terminal guidance on I2V, or ordered image/video/audio references on R2V. Read `reference/wan-3.0.md`.
- **Gemini Omni Flash 1.1:** use Fal T2V, I2V, or R2V for fast 3–10 second audiovisual generation, or the dedicated Edit route for a focused natural-language change to a source video. All four routes expose 360p through 4K. Read `reference/gemini-omni-flash-1.1.md`.
- **Hailuo H3 / H3 Max:** use H3 for fixed-2K work; use H3 Max T2V/I2V or its mixed image/video/audio R2V route for 480P/768P, configurable prompt expansion, and 5–15 second native-audio shots. Read `reference/hailuo-h3.md`.
- **FLUX 3:** use for 24 fps timed keyframes, Draft-to-Enhance promotion, extensions, or high-quality native motion typography and animated design. Read `reference/flux-3.md`.
- **LTX 2.5:** use for Pro/Fast T2V or I2V, duration/FPS-specific output, first/last frames, native multi-shot, source-audio-led video, or typography-capable audiovisual generation. Current LTX 2.5 does not support Retake, Extend, or Reframe. Read `reference/ltx-2.5.md`.
- **Kling V3 / O3:** use for Elements, structured `camera_control`, Motion Brush, deliberate multi-shot work, or native-4K source-video finishing. The O3 4K V2V routes are premium, approval-gated operations. Read `reference/kling-prompting.md`.

### Decision Rules

- Use the agentic multi-reference prompt composer only for an exact Omni, reference-to-video, or Elements endpoint. T2V and I2V routes keep their own prompt ownership; an opening image alone does not make an I2V route a multi-reference target.
- Hailuo H3 qualifies only on `fal-ai/minimax/hailuo-03/reference-to-video`. LTX 2.5 currently has no reference-to-video route and is outside this orchestration path.
- If approved visual authority exists, default to Seedance 2.5 Omni Reference and bind it.
- If no reference exists, create or approve a keyframe or consistency reference first unless exploration is intentionally text-only.
- For prompt-only work, use Seedance 2.5 T2V; choose FLUX 3, LTX 2.5, Wan, H3, Kling, or Seedance 2.0 only for a specific endpoint capability.
- For a reference-heavy storyboard chunk, use Seedance 2.5 Omni by default. Use the Seedance 2.0 global-bible workflow only when its positional tokens are required; read `reference/seedance-global-storyboard.md`.
- For exact opening-frame authority, use an I2V route. For exact opening and terminal authority, use a first/last route or an I2V endpoint that explicitly owns terminal guidance.
- To continue an existing Seedance 2.0 clip in PR0TA, use Omni Reference with the previous clip as `@video1` for **reference-guided continuation**. MuAPI's provider-native Seedance 2.0 extension routes require the original provider `request_id` and are not in the unified extension catalog; see `reference/seedance-omni.md`.
- For source-preserving transformation or continuation, use the exact Edit or Extend route. Do not substitute a generic reference call.
- For price-sensitive choices, query `models_list`, then `GET /api/crew/model_pricing?model_id={model_id}` for each exact candidate and requested output configuration. Do not infer live cost from this document.
- If a provider rejects allowed content, preserve the terminal error and use `reference/provider-recovery.md`. Never switch providers to bypass policy.

## Required Generation Contract

Prefer MCP. Submit with `generation_submit`, poll with `tasks_get`, and inspect the finished asset before editorial use. Use `agent_chat_orchestrate_prompt` when a department-authored, model-specific prompt package is required.

```json
{
  "project_id": "project-uuid-or-slug",
  "request": {
    "generator": "video",
    "mode": "ref_to_vid",
    "model": "muapi/seedance-2.5-omni-reference",
    "prompt": "Use the supplied image as identity, wardrobe, and set authority. The camera slowly pulls back while preserving those traits.",
    "reference_image_asset_ids": ["approved-image-asset-id"],
    "duration": 5,
    "aspect_ratio": "16:9"
  }
}
```

Use REST only when MCP is unavailable, for high-volume scripts, or for an unexposed route: `POST /api/v2/projects/{project_id}/generate`. Read `pr0ta-api/reference/unified-generation.md` for the shared request envelope. Query `models_get_defaults` or `GET /api/crew/model_defaults?model_id={model_id}` before production calls; model-specific fields are not portable.

### Modes

- `txt_to_vid`: text-only generation.
- `img_to_vid`: an image owns the opening visual state.
- `ref_to_vid`: model-specific identity, environment, motion, video, or audio conditioning.
- first/last frame: explicit opening and terminal frames on a supporting endpoint.
- `video_to_video`: transform a source clip with an explicit edit-capable model while preserving its relevant structure.
- `extend_video`: generate new continuation beyond a source clip.

Generic `ref_to_vid` validation and provider-native contracts are two different layers. Read `reference/video-reference-field-matrix.md` before any reference-heavy payload. In particular:

- `character_id` / `character_ids[]` are restricted to Seedance 2.0 Omni.
- `camera_control` and `voice_ids[]` are Kling-only.
- Wan, Seedance, and H3 generic reference arrays do not imply FLUX 3 or LTX 2.5 field compatibility.
- Seedance 2.5 Omni accepts image-, video-, and audio-led bundles; H3 R2V rejects audio-only input.
- A T2V request with reference fields may route differently from pure T2V. Send only `prompt` when the request must remain text-only.

## Duration and Aspect Contracts

Duration is endpoint-specific. Use whole seconds where the endpoint exposes an integer and inspect the delivered media duration before timeline placement.

| Model | Accepted `duration` | Source |
|---|---:|---|
| `muapi/seedance-2-vip-text-to-video` | `4`..`15` | Current MuAPI OpenAPI |
| `muapi/seedance-2-vip-image-to-video` | `4`..`15` | Current MuAPI OpenAPI |
| `muapi/seedance-2-vip-omni-reference` | `4`..`15` | Current MuAPI OpenAPI |
| `muapi/seedance-2.5-*` standard routes | `4`..`30` | Current MuAPI route schemas |
| `muapi/wan3.0-*` | `2`..`30` | Current MuAPI Wan 3.0 OpenAPI |
| `alibaba/wan-3.0-prime/*` | `smart` or `2`..`30`; omitted defaults to `5` | Checked-in Fal OpenAPI |
| `google/gemini-omni-flash/v1.1/{text,image,reference}-to-video` | `3`..`10` | Checked-in Fal OpenAPI |
| `google/gemini-omni-flash/v1.1/edit` | Not exposed; output follows the source edit | Checked-in Fal OpenAPI |
| `minimax/h3-max/*` | `5`..`15` | Checked-in Fal OpenAPI |
| `fal-ai/minimax/hailuo-03/*` | `5`..`15` | Checked-in Fal OpenAPI |
| `blackforestlabs/flux-3/*` generation routes | `5`..`20`; first/last and keyframes require an explicit integer | Checked-in Fal OpenAPI |
| `lightricks/ltx-2.5/*/pro` | `auto` or `6`, `8`, `10` where exposed | Checked-in Fal OpenAPI |
| `lightricks/ltx-2.5/*/fast` | even `6`..`20`, constrained by resolution/FPS | Checked-in Fal OpenAPI |
| Kling V3/O3 Fal generation routes | `3`..`15` | Checked-in Fal OpenAPI |

H3 Max R2V accepts at most 12 total image/video/audio files. Each reference video or audio clip is 2–15 seconds and all timed references together are capped at 15 seconds. Kling O3 4K V2V accepts a 3–15 second MP4/MOV source from 720–3840 pixels and at most 200 MB; Elements plus reference images total at most four.

Current Seedance 2.0 T2V, I2V, and Omni routes accept `21:9`, `16:9`, `4:3`, `1:1`, `3:4`, `9:16`. Other families differ; use the selected reference and live defaults.

Prefer fewer, longer clips only when the action genuinely belongs in one generation. Split at a motivated cut when a beat exceeds the endpoint maximum. If motion must remain continuous, extend the source. Otherwise generate companion coverage or use a deliberate still/Ken Burns clip. Never leave an empty timeline tail or stretch a short source invisibly.

## Reference and Continuity Workflows

### Seedance 2.0 Omni

Seedance 2.0 Omni is the trained-character and positional-token exception. It supports prompt-led calls plus image, video, audio, and character references. For tokens, character training, limits, continuation, and payloads, read `reference/seedance-omni.md`.

For advanced storyboard work with a global visual bible and chronological chunk sheets, read `reference/seedance-global-storyboard.md`. Use `storyboard_chunks_list`, `storyboard_reference_sheet_generate`, `tasks_get`, and `storyboard_reference_sheets_list`; select an approved sheet before dispatch.

### Kling V3 / O3

Kling uses `@Image1` for the start image and `@Element1..N` for attached Element bundles. Its shot-labeling, token, end-frame, action-timeline, and per-shot rules are not interchangeable with Seedance. Read `reference/kling-prompting.md` before writing any Kling multi-shot payload.

## Source Editing, Enhancement, and Repairs

Choose the narrowest operation that fixes the defect:

- Continue motion: an Extend route.
- Change only a region or object: Inpaint or a model's focused edit route.
- Preserve the source but alter style/action: Edit or video-to-video.
- Correct framing: Reframe.
- Remove/replace a background: Roto Bg.
- Repair resolution, noise, cadence, or compression without creative reconstruction: a matching Topaz utility route.

For Topaz video enhancement, query live defaults for the exact endpoint. Use `topaz/upscale/video/precision` for faithful general enhancement, `topaz/denoise/video` for noise reduction, and other cataloged variants only when their declared tradeoff is intentional. Do not treat a generative reconstruction route as a lossless utility.

When a long narration beat exceeds generation limits, prefer: split at a natural clause; extend a successful source; cut to companion coverage; then use a still/Ken Burns treatment if needed. Regenerate the whole show only when the defect reflects a global creative decision, not a local shot failure.

## Output Dimensions and Timeline Placement

Input orientation does not guarantee output orientation. Always set `aspect_ratio`, inspect actual width/height/duration, and keep critical content away from crop-sensitive edges. Provider output may not match delivery pixels exactly.

Set the sequence resolution before placement. Adding clips through `POST /timeline/clips` lets the timeline normalize scale, pad, format, and FPS to the sequence. Use `result_refs.output_diagnostics` when available. Read `pr0ta-timeline` for source-shortfall and fit-to-fill rules.

## Native Audio and Voice

Audio controls are endpoint-specific. Send `sound`, `audio`, `enable_audio`, or `generate_audio` only where the selected endpoint exposes that field. A missing toggle does not imply silence: H3, H3 Max, Gemini Omni Flash 1.1 generation routes, and Seedance 2.5 return audio-bearing video; MuAPI Wan uses `enable_audio`, while Fal Wan Prime uses `audio`; FLUX 3 and LTX 2.5 expose their own contracts. The Gemini 1.1 Edit page does not document an audio guarantee or control, so inspect its result before treating it as audio-bearing. Read `reference/native-audio.md` and the selected model reference.

Every speech-bearing generated video must be transcribed with Scribe V2 before timeline use. Verify exact wording, speaker identity, sync, and unwanted speech. For the mandatory indexing gate and audio extraction decision, read `pr0ta-audio`.

Kling O3 supports endpoint-specific `voice_ids`; do not generalize that field to other families.

## Known Limitations and Workarounds

Use the `pr0ta-api` reliability contract and poll every task to a terminal state.

- **Audio controls are endpoint-specific.** Query live defaults; inspect and transcribe every speech-bearing result.
- **Provider errors are asynchronous.** Preserve `error`, `error_detail`, and `error_reason`; distinguish credits, payload validation, policy rejection, and stalls before retrying.
- **Initial `credits_cost: null` is not success or failure.** Poll the task for the authoritative result.
- **Actual dimensions or duration may differ.** Inspect the asset and normalize intentionally on the timeline.
- **Kling start-image translation and asset-download zero-byte defects are documented as fixed.** Project asset downloads still require bearer authorization or a scoped delivery token; keep reliability fallbacks as defense in depth, not as the normal path.

## On-Screen Text — Use Text-Capable Video Models Deliberately

Do not claim that image or video models are categorically incapable of generated typography. Premium current models can generate and animate legible text. Seedance 2.0, Seedance 2.5, MiniMax H3, FLUX 3, Wan 3.0, and LTX 2.5 are valid candidates when their rendered results meet the brief. A verified premium video result is valid production media.

Read `reference/generative-typography.md` before producing on-screen copy. It owns model selection, exact-string prompting, frame-by-frame QC, repair tactics, and the deterministic still/timeline fallback for outputs that fail exact-copy acceptance.

## Deep References

- `reference/seedance-2.5.md` — all Seedance 2.5 routes and prompts.
- `reference/seedance-omni.md` — Seedance 2.0 Omni tokens, references, and continuation.
- `reference/seedance-global-storyboard.md` — positional storyboard-chunk workflow.
- `reference/wan-3.0.md` — Wan 3.0 / Prime T2V, I2V, R2V, audio, and typography.
- `reference/gemini-omni-flash-1.1.md` — Gemini Omni Flash 1.1 Fal routes, fields, reference limits, and prompting.
- `reference/hailuo-h3.md` — H3 multimodal prompting, editing, audio, and text.
- `reference/flux-3.md` — FLUX 3 generation, keyframes, Draft/Enhance, extension, and typography.
- `reference/ltx-2.5.md` — LTX 2.5 Pro/Fast T2V, I2V, audio-to-video, multi-shot, typography, and version boundaries.
- `reference/kling-prompting.md` — Kling Elements, multi-shot, camera, and prompt grammar.
- `reference/video-reference-field-matrix.md` — validator and provider reference-field contracts.
- `reference/native-audio.md` — endpoint audio fields, transcription, and verification.
- `reference/generative-typography.md` — native video typography decisions and QC.
- `reference/provider-recovery.md` — allowed-content rejection, retry, stall, and fallback policy.
