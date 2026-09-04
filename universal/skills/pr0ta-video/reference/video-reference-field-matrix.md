## Video Reference Field Matrix (Unified API)

**This is the validator-derived reference-field contract enforced by the unified video request validator (`POST /api/v2/projects/{project_id}/generate`).** Source: current PR0TA validator and provider schemas, August 2026. Treat it as the copy-paste-safe surface; provider behavior downstream can still be stricter in specific cases, so always cross-check against the Provider-Certified matrix below for Kling variants.

### Field Families

**Image reference fields:**
- `start_image_asset_id`, `start_image_url`
- `image_asset_id`, `image_url`
- `end_image_asset_id`, `end_image_url`
- `reference_image_asset_ids[]`, `reference_image_urls[]`
- `references[]` with image-like entries
- `element_ids[]`, `elements[]`

**Multimodal reference fields (model-specific):**
- `reference_video_urls[]`
- `reference_audio_urls[]`
- `references[]` with video/audio entries

These generic multimodal arrays are limited to the exact reference-capable models listed below, including Wan 3.0 R2V, Seedance Omni/2.5 Omni or Edit, and Hailuo H3 R2V. FLUX 3 and LTX 2.5 do **not** consume these generic arrays; they use operation-specific `image_url`, `start_image_url`/`end_image_url`, `keyframes[]`, `video_url`, or `audio_url` fields as shown in the per-model rows.

**Seedance 2.0 Omni character controls:**
- `character_id`, `character_ids[]`

**Kling-only adjunct controls:**
- `camera_control`
- `voice_ids[]`

### Per-Model Matrix

| Model | Modes | Prompt | Required Refs | Accepted Reference Fields | Notes |
|---|---|---|---|---|---|
| `muapi/seedance-2-vip-text-to-video` | `txt_to_vid` only | Required | None | No structured refs | Pure T2V; prompt-level `@character:<request_id>` can select character mode |
| `muapi/seedance-2-vip-image-to-video` | Image-to-video | Required | 1–9 images | Image fields only | No structured video/audio/character fields; prompt-level `@character:<request_id>` and `@omni-character:<character_id>` are supported |
| `muapi/seedance-2-vip-omni-reference` | All video modes | Required | ≥1 omni ref in PR0TA `ref_to_vid`; provider accepts prompt-only | **All** image fields + `reference_video_urls[]`, `reference_audio_urls[]`, `references[]`, `element_ids[]`, `elements[]`, `character_id`, `character_ids[]` | Use dedicated T2V for prompt-only work |
| `muapi/seedance-2.5-text-to-video*` | `txt_to_vid` | Required | None | No refs | 480p/720p/1080p/4K selected by model ID; public pages conflict on 1080p lineage |
| `muapi/seedance-2.5-image-to-video*` | I2V | Required | Exactly 1 image | Start-image fields | Dedicated first/last route owns terminal keyframes |
| `muapi/seedance-2.5-first-last-frame*` | FFLF | Required | Exactly 2 ordered images | `images_list[]` after unified resolution | First then last |
| `muapi/seedance-2.5-omni-reference*` | Reference video | Required | ≥1 reference | Up to 30 image, 10 video, 10 audio refs (50 total) | Audio-only and video-only accepted; no character IDs |
| `muapi/seedance-2.5-video-edit*` | `video_to_video` | Required | Source video | `video_url`; optional `reference_image_urls[]`, `reference_audio_urls[]` | Edit references are model-specific; supports `generate_audio` |
| `muapi/seedance-2.5-video-extend*` | `extend_video` / `video_extend` | Required | Source video | `video_url`; optional `last_image_url` | Target image is the desired final frame; supports `generate_audio` |
| `muapi/wan3.0-text-to-video`, `muapi/wan3.0-prime-text-to-video` | `txt_to_vid` | Required | None | No refs | 2–30s, 480p/720p/1080p, `enable_audio` defaults on; use T2V for prompt-only work |
| `muapi/wan3.0-image-to-video`, `muapi/wan3.0-prime-image-to-video` | I2V / optional terminal frame | Required | Exactly 1 opening image | Start-image fields; optional end-image fields map to `last_image` | Same endpoint owns both ordinary I2V and optional terminal-frame guidance |
| `muapi/wan3.0-reference-to-video`, `muapi/wan3.0-prime-reference-to-video` | Reference video | Required | Provider permits prompt-only; references optional | Up to 10 `images_list`, 5 `videos_list`, and 5 `audios_list` entries | Native audio defaults on; reference video duration plus output must remain at or below 30s; reference audio may total up to 15s |
| `alibaba/wan-3.0-prime/text-to-video` | `txt_to_vid` | Required | None | No refs | Fal-native route; `audio`, `enable_thinking`, and `enable_prompt_expansion` controls |
| `alibaba/wan-3.0-prime/image-to-video` | I2V / optional terminal frame | Optional | Start image | `start_image_url`; optional `end_image_url` | Fal-native field names; audio defaults on |
| `alibaba/wan-3.0-prime/reference-to-video` | Reference video | Provider-optional | Prompt or a deliberate reference input in PR0TA | 10 `reference_image_urls`, 5 `reference_video_urls`, 5 `reference_audio_urls`; optional `file_url`/`web_url` | File/web context requires `enable_thinking=true` |
| `google/gemini-omni-flash/v1.1/text-to-video` | `txt_to_vid` | Required | None | No refs | 3–10s, 360p through 4K, native audio |
| `google/gemini-omni-flash/v1.1/image-to-video` | I2V / FFLF | Required | Start image; optional end | `image_url`, optional `end_image_url` | Output has native audio |
| `google/gemini-omni-flash/v1.1/reference-to-video` | Reference video | Required | Image or video | Up to 10 `image_urls` and 3 `reference_video_urls` | Zero-based `<IMAGE_REF_N>` / `<VIDEO_REF_N>` bindings; each reference video is at most 3 seconds |
| `google/gemini-omni-flash/v1.1/edit` | `video_to_video` | Required | Source video | `video_url`; optional `resolution` | No duration, aspect-ratio, reference-array, or audio controls in the current schema |
| `beeble/switchx` | `video_to_video` | Optional when a reference image is sent | Source video plate | `video_asset_id`/`video_url`; optional single `reference_image_asset_ids[0]`/`reference_image_url`, `alpha_mode`, `alpha_asset_id`/`alpha_uri`, `alpha_media_kind`, `max_resolution` | Plate pixels stay; the masked region is regenerated and the kept subject relit; PR0TA registers render, alpha, and source outputs and chunks plates over 240 frames. Read `pr0ta-hybrid` |
| `fal-ai/birefnet/v2/video` | `video_to_video` | None (omit) | Source video | `video_asset_id`/`video_url`; `parameters`: `model`, `output_mask`, `operating_resolution`, `refine_foreground`, `video_output_type`, `video_quality`, `video_write_mode` | Matte route; returns `matte_asset_id` and `plate_asset_id`. Read `pr0ta-hybrid` |
| `bria/video/background-removal` | `video_to_video` | None (omit) | Source video | `video_asset_id`/`video_url`; `parameters`: `background_color`, `output_container_and_codec` | RGBA cutout, not a luma matte; `Transparent` requires `webm_vp9` or a ProRes container |
| `minimax/h3-max/text-to-video` | `txt_to_vid` | Required | None | No refs | 5–15s, 480P/768P, prompt expansion required/defaulted |
| `minimax/h3-max/image-to-video` | I2V / FFLF | Required | Start image in PR0TA; optional end | `image_url`, optional `end_image_url` | Output aspect follows first image |
| `fal-ai/minimax/hailuo-03/text-to-video` | `txt_to_vid` | Required | None | No refs | Fixed 2K, 5–15s |
| `fal-ai/minimax/hailuo-03/image-to-video` | I2V / FFLF | Required | Start image; optional end | Start/end image fields | Output aspect follows first image |
| `fal-ai/minimax/hailuo-03/reference-to-video` | Reference video | Required | Image or video | Up to 9 image, 3 video, 3 audio refs | Audio-only rejected; literal `Image N` roles |
| `blackforestlabs/flux-3/image-to-video*` | I2V | Required | Exactly 1 image | Provider-native `image_url` | Standard and Draft routes; prompt motion after frame zero |
| `blackforestlabs/flux-3/first-last-frame-to-video*` | FFLF | Required | Exactly 2 ordered images | `start_image_url`, `end_image_url` | Explicit 5–20s duration required |
| `blackforestlabs/flux-3/keyframes-to-video*` | Timed keyframes | Required | 1–10 images | `keyframes[]` objects with `image_url` + unique `frame_index` | Positions use the 24 fps output timeline, not seconds |
| `blackforestlabs/flux-3/extend-video*` | Extension | Required | Source video | `video_url` | Continue source camera/motion/audio; standard and Draft routes |
| `lightricks/ltx-2.5/image-to-video/*` | I2V / optional end frame | Required | Opening image | `image_url`; optional `end_image_url` | Not a multi-reference orchestration target; do not combine auto duration with an end image |
| `lightricks/ltx-2.5/audio-to-video/*` | Audio-driven video | Conditional | Required source audio; optional image | `audio_url`; optional `image_url` | Prompt required without image; A2V does not inherit I2V resolution/FPS/camera/end-image fields |
| `muapi/seedance-2-character` | Character-construction path | Not enforced | ≥1 image ref (up to 3) | Image fields only | **Character-sheet training.** Requires `character_name` + `outfit_description`. Async; returns Omni token in `result_refs.character_id` for later omni-reference calls. |
| `muapi/seedance-2-omni-reference-train` | Omni-token training path | Not enforced | ≥1 image ref | Image fields only | **Single-portrait training.** Requires `character_name`. Async; returns Omni token in `result_refs.character_id` for later omni-reference calls. Fastest path into Omni when one clean portrait is enough. See `pr0ta-consistency` → `reference/provider-consistency-systems.md` → "Creating A Seedance Character Token". |
| Kling I2V / ref-to-vid (`kling/*`, `fal-ai/kling-video/*`) | `ref_to_vid` / txt/video | Usually | Generic video rules | Image fields, `element_ids[]`, `elements[]`, `references[]` image entries | **Plus** `camera_control` and `voice_ids[]` (Kling only) |

### Validator Rules That Matter In Practice

**1. Generic `ref_to_vid` requires ≥1 image-bearing reference.** Accepted fields: `start_image_asset_id`, `start_image_url`, `image_asset_id`, `image_url`, `reference_image_asset_ids[]`, `reference_image_urls[]`, `element_ids[]`, `elements[]`.

**2. `txt_to_vid` with refs is NOT equivalent to pure text-to-video.** If you include any reference field (image, video, audio, character, element, references[]) on a `txt_to_vid` request, the unified resolver may prefer a reference-capable default model instead of the pure t2v path. If you truly want pure text-to-video, send only `prompt` — no reference fields of any kind.

**3. `character_id` / `character_ids[]` are restricted to `muapi/seedance-2-vip-omni-reference`.** The validator rejects stored character refs on every other video model. If you need character continuity, route through Seedance Omni.

**4. `camera_control` and `voice_ids[]` are Kling-only.** The validator rejects them on any non-Kling model.

### Copy-Paste-Safe Payloads

**Pure text-to-video — `muapi/seedance-2-vip-text-to-video`:**

```json
{
  "generator": "video",
  "mode": "txt_to_vid",
  "model": "muapi/seedance-2-vip-text-to-video",
  "prompt": "...self-contained scene description...",
  "duration": 5,
  "aspect_ratio": "9:16"
}
```
Do not include image/video/audio/character refs. Any ref present will likely route you to a different model.

**Image-to-video from a single still — `muapi/seedance-2-vip-image-to-video`:**

```json
{
  "generator": "video",
  "mode": "ref_to_vid",
  "model": "muapi/seedance-2-vip-image-to-video",
  "prompt": "...self-contained scene description enumerating every state change...",
  "start_image_asset_id": "a73b9aad-...",
  "duration": 5,
  "aspect_ratio": "9:16"
}
```
Do **not** include `reference_video_urls[]`, `reference_audio_urls[]`, or `character_id`.

**Wan 3.0 text-to-video — standard or Prime:**

```json
{
  "generator": "video",
  "mode": "txt_to_vid",
  "model": "muapi/wan3.0-text-to-video",
  "prompt": "...chronological audiovisual shot direction...",
  "resolution": "720p",
  "aspect_ratio": "16:9",
  "duration": 5,
  "thinking_mode": false,
  "enable_audio": true
}
```

Use `muapi/wan3.0-prime-text-to-video` for the same payload at the Prime tier. Do not attach references or send a negative-prompt field.

**Wan 3.0 image-to-video with optional terminal-frame guidance:**

```json
{
  "generator": "video",
  "mode": "ref_to_vid",
  "model": "muapi/wan3.0-image-to-video",
  "prompt": "The approved frame begins moving... End by landing on the supplied terminal frame.",
  "start_image_asset_id": "a73b9aad-...",
  "end_image_asset_id": "b84c0bee-...",
  "resolution": "720p",
  "duration": 8,
  "enable_audio": false
}
```

The unified mapper resolves the opening image to provider-native `image_url` and the optional end image to `last_image`. Omit `end_image_asset_id` for ordinary I2V. Prime uses `muapi/wan3.0-prime-image-to-video` with the same contract.

**Wan 3.0 multimodal reference-to-video:**

```json
{
  "generator": "video",
  "mode": "ref_to_vid",
  "model": "muapi/wan3.0-reference-to-video",
  "prompt": "The first reference image controls identity. The first reference video controls camera pace. The first reference audio controls ambience. ...chronological action and landing...",
  "images_list": ["https://.../identity.png"],
  "videos_list": ["https://.../camera.mp4"],
  "audios_list": ["https://.../ambience.wav"],
  "resolution": "720p",
  "duration": 8,
  "enable_audio": true
}
```

Prime uses `muapi/wan3.0-prime-reference-to-video` with the same contract. Arrays are provider-optional, but use dedicated T2V for prompt-only work. Preserve final list order before writing ordinal reference roles. Reference-video duration plus output must not exceed 30 seconds; reference audio may total at most 15 seconds.

**Preferred general video path — `muapi/seedance-2.5-omni-reference`:**

```json
{
  "generator": "video",
  "mode": "ref_to_vid",
  "model": "muapi/seedance-2.5-omni-reference",
  "prompt": "Use the supplied images as identity, wardrobe, set, and style authority. Use the supplied video for camera rhythm. Preserve those traits through the chronological action and explicit end state.",
  "reference_image_asset_ids": ["a73b9aad-..."],
  "reference_video_urls": ["https://.../camera-reference.mp4"],
  "duration": 8,
  "aspect_ratio": "16:9"
}
```
Use this route first whenever at least one approved image, video, or audio authority exists. It accepts up to 30 images, 10 videos, and 10 audio references, with 50 inputs total. It does not accept Seedance 2.0 character IDs or positional `@` tokens.

**Trained character-token exception — `muapi/seedance-2-vip-omni-reference`:**

```json
{
  "generator": "video",
  "mode": "ref_to_vid",
  "model": "muapi/seedance-2-vip-omni-reference",
  "prompt": "...self-contained scene description...",
  "reference_image_asset_ids": ["a73b9aad-..."],
  "character_ids": ["char_dario_v1"],
  "reference_audio_urls": ["https://.../beat.wav"],
  "duration": 5,
  "aspect_ratio": "9:16"
}
```
Use this older route when a trained `character_id` or Seedance 2.0 positional-token contract is required. It is not the general default.

**Character-sheet training — `muapi/seedance-2-character`** (use when you have 1-3 approved stills or a real character sheet):

```json
{
  "generator": "video",
  "mode": "ref_to_vid",
  "model": "muapi/seedance-2-character",
  "images_list": [
    "https://example.com/maya-sheet-front.jpg",
    "https://example.com/maya-sheet-profile.jpg"
  ],
  "character_name": "Maya",
  "outfit_description": "charcoal three-piece suit, cream dress shirt, burgundy tie, oxford lace-ups"
}
```
Async. Returns an Omni token in `result_refs.character_id` on completion. `outfit_description` is **required**. Accepts up to 3 stills.

**Single-portrait training — `muapi/seedance-2-omni-reference-train`** (use when you have one clean hero portrait):

```json
{
  "generator": "video",
  "mode": "ref_to_vid",
  "model": "muapi/seedance-2-omni-reference-train",
  "image_url": "https://example.com/hero-portrait.jpg",
  "character_name": "Maya",
  "description": "Female lead, black leather jacket, studio portrait, neutral expression"
}
```
Async. Returns an Omni token in `result_refs.character_id` on completion. Fastest path into Omni Reference when a single clear face-forward image is enough. Persist the returned token via `POST /characters` (provider: `muapi`) for later reuse via `character_ids[]` on `muapi/seedance-2-vip-omni-reference`. See `pr0ta-consistency` → `reference/provider-consistency-systems.md` → "Creating A Seedance Character Token" for the full lifecycle.

**Kling image-to-video (cinematic continuation):**

```json
{
  "generator": "video",
  "mode": "ref_to_vid",
  "model": "kling_o3_pro",
  "start_image_asset_id": "a73b9aad-...",
  "prompt": "...self-contained scene description...",
  "camera_control": { "type": "push_in", "strength": 0.4 },
  "duration": 5,
  "aspect_ratio": "9:16"
}
```
`camera_control` and `voice_ids[]` are allowed on Kling only.

### Provider-Certified Reference Fields (Source: Provider OpenAPI Specs)

**The unified validator accepts a broad reference-field surface, but provider endpoints downstream have stricter, per-variant contracts.** The following matrix comes from provider-native OpenAPI specs (fal.ai for Kling, MuAPI for Seedance) and is the authoritative source for "what the provider actually wants."

Read this as a two-layer contract:

1. **What the provider endpoint requires** (provider-native field names)
2. **What PR0TA must translate into that shape** (unified field → provider field)

PR0TA's unified fields are convenience fields, not provider-native fields. A unified request like `start_image_asset_id: "abc"` is only valid downstream **if PR0TA resolves the asset and translates it to the specific provider-native field name that endpoint expects**.

| Provider Model | Provider Endpoint | Required | Provider Reference Fields |
|---|---|---|---|
| **Kling V3 Pro (I2V)** | `POST /fal-ai/kling-video/v3/pro/image-to-video` | `start_image_url` | `start_image_url`, `end_image_url`, `elements[]`, `voice_ids[]`, `multi_prompt` |
| **Kling O3 Pro (I2V)** | `POST /fal-ai/kling-video/o3/pro/image-to-video` | `image_url` | `image_url`, `end_image_url`, `multi_prompt` |
| **Kling O3 Pro (Ref-to-Video)** | `POST /fal-ai/kling-video/o3/pro/reference-to-video` | prompt + refs | `start_image_url`, `image_urls[]`, `elements[]`, `end_image_url`, `multi_prompt` |
| **Seedance 2.0 T2V** | `POST /api/v1/seedance-2-vip-text-to-video` | `prompt` | (none) |
| **Seedance 2.0 I2V** | `POST /api/v1/seedance-2-vip-image-to-video` | `prompt`, `images_list` | `images_list[]` |
| **Seedance 2.0 Omni Reference** | `POST /api/v1/seedance-2-vip-omni-reference` | `prompt` | `images_list[]`, `video_files[]`, `audio_files[]` |
| **Seedance 2.0 Video Edit** | `POST /api/v1/seedance-2-video-edit` | `prompt`, `video_urls` | `video_urls[]`, optional `images_list[]` |
| **Seedance 2.5 I2V** | MuAPI route selected by model ID | `prompt`, `image_url` | one `image_url` |
| **Seedance 2.5 First/Last** | MuAPI route selected by model ID | `prompt`, exactly two `images_list` entries | ordered `images_list[]` |
| **Seedance 2.5 Omni** | MuAPI route selected by model ID | `prompt`, at least one ref in PR0TA | `images_list[]`, `videos_list[]`, `audios_list[]` (10 files; 15 seconds combined) |
| **Seedance 2.5 Video Edit** | MuAPI route selected by model ID | `prompt`, `video_url` | source `video_url`; optional `reference_image_urls[]`, `reference_audio_urls[]` |
| **Seedance 2.5 Video Extend** | MuAPI route selected by model ID | `prompt`, `video_url` | source `video_url`; optional `last_image_url` target |
| **Wan 3.0 / Prime T2V** | `POST /api/v1/wan3.0-text-to-video` or `POST /api/v1/wan3.0-prime-text-to-video` | `prompt` | None |
| **Wan 3.0 / Prime I2V** | `POST /api/v1/wan3.0-image-to-video` or `POST /api/v1/wan3.0-prime-image-to-video` | `prompt`, `image_url` | optional `last_image` terminal frame |
| **Wan 3.0 / Prime R2V** | `POST /api/v1/wan3.0-reference-to-video` or `POST /api/v1/wan3.0-prime-reference-to-video` | `prompt` | `images_list[]` (10), `videos_list[]` (5), `audios_list[]` (5) |
| **Wan 3.0 Prime on Fal R2V** | `POST /alibaba/wan-3.0-prime/reference-to-video` | prompt or reference input in PR0TA | `reference_image_urls[]` (10), `reference_video_urls[]` (5), `reference_audio_urls[]` (5), optional `file_url`/`web_url` |
| **Gemini Omni Flash 1.1 I2V** | `POST /google/gemini-omni-flash/v1.1/image-to-video` | `prompt`, `image_url` | optional `end_image_url` |
| **Gemini Omni Flash 1.1 R2V** | `POST /google/gemini-omni-flash/v1.1/reference-to-video` | `prompt` plus references in PR0TA | `image_urls[]` (10), `reference_video_urls[]` (3) |
| **Gemini Omni Flash 1.1 Edit** | `POST /google/gemini-omni-flash/v1.1/edit` | `prompt`, `video_url` | optional `resolution` |
| **MiniMax H3 Max I2V** | `POST /minimax/h3-max/image-to-video` | `prompt`, image in PR0TA, `prompt_expansion_mode` | `image_url`, optional `end_image_url` |
| **Hailuo H3 I2V** | `POST /fal-ai/minimax/hailuo-03/image-to-video` | `prompt`, `image_url` | `image_url`, optional `end_image_url` |
| **Hailuo H3 R2V** | `POST /fal-ai/minimax/hailuo-03/reference-to-video` | `prompt`, image or video | `reference_image_urls[]`, `reference_video_urls[]`, optional `reference_audio_urls[]` |

### Critical Findings From Provider Specs

**1. Kling variants do NOT share a universal reference contract.** This is the most important takeaway. They expose materially different reference fields at the provider level:

| Kling variant | Primary image field |
|---|---|
| Kling V3 Pro I2V | `start_image_url` (required) |
| Kling O3 Pro I2V | `image_url` (required — **not** `start_image_url`) |
| Kling O3 Pro Reference-to-Video | `start_image_url` + `image_urls[]` + `elements[]` |

Do not assume a reference field that works on one Kling endpoint works on another. They are separate provider endpoints with separate schemas.

**2. Kling O3 Pro has two distinct endpoints: Image-to-Video and Reference-to-Video.** These are not interchangeable:
- I2V takes a single `image_url` for a basic start frame
- Reference-to-Video takes `start_image_url` + `image_urls[]` + `elements[]` for rich multi-reference composition

When you need richer reference composition on Kling, the Reference-to-Video endpoint is the correct target — not assumptions layered onto the I2V endpoint.

**3. Seedance I2V uses `images_list`**, not `image_url` or `images_urls`. PR0TA's unified `start_image_asset_id` / `reference_image_asset_ids[]` must resolve and map into `images_list` for the MuAPI Seedance I2V call.

**4. Seedance Omni Reference provider-native fields are `images_list[]`, `video_files[]`, `audio_files[]`.** These map to PR0TA's unified `reference_image_*`, `reference_video_urls[]`, and `reference_audio_urls[]` respectively.

### The Kling V3 Pro Caveat — RESOLVED (April 2026)

The previously field-tested failure (`kling_v3_pro` silently accepting `start_image_asset_id` and then failing downstream with `"Invalid reference index 1 for image. Only 0 images provided."`) is **now fixed end-to-end**.

**What changed:**
- Kling V3 Pro's provider endpoint **requires** `start_image_url`.
- PR0TA's unified layer now resolves `start_image_asset_id` → provider-native `start_image_url` via `input_asset_resolver.py` → `request_mapper.py` → `fal_request_builder.py`, which preserves the provider-native field name on the outbound Fal submission instead of rewriting it to a `first/last` alias.
- Targeted regression test coverage (`test_fal_request_builder.py`) now protects this outbound payload shape.

**Operational rule:** Agents may use `start_image_asset_id` (or `start_image_url`) directly on `fal-ai/kling-video/v3/pro/image-to-video`. If asset-backed project media is involved, `start_image_asset_id` is the cleanest unified field. The same fix applies to `end_image_asset_id` → `end_image_url`.

**If a future V3 Pro failure appears, do not assume the asset-id translation is the root cause.** Check `task.error_reason` and the actual provider response — the translation gap is closed.

Seedance 2.5 Omni Reference is the preferred default for reference-heavy work. Use Seedance 2.0 Omni when trained character IDs or its positional-token contract are required, and Kling V3 Pro when the shot specifically needs Kling's Elements, structured controls, or atmospheric continuation.

### Failure-Mode Guidance

When a reference payload fails, **trust the error message.**

- **Validator rejection** surfaces as an explicit server-side error at submission time. Read the error text — it usually names the specific field that's wrong.
- **Downstream provider rejection** surfaces as a task failure after submission. Check `task.error_reason` for the provider's actual complaint — don't assume it's a known translation gap (the historical Kling V3 Pro case is now fixed).
- Neither failure mode is silent hallucination — if a shot silently produced the wrong content, the issue is prompting (see `pr0ta-prompting`), not a reference-field validation bug.

If in doubt, test the payload against a short 2-second generation before committing a full production to it.

### Skills-Facing Compatibility Quick Reference

This table is the copy-paste-safe surface for agents — what provider-native field each model requires, and which unified PR0TA field to send.

| Model | Provider-Native Required | Preferred PR0TA Unified Field | Alternates | Translation Implemented | Tested |
|---|---|---|---|---|---|
| `fal-ai/kling-video/v3/pro/image-to-video` | `start_image_url` | `start_image_asset_id` | `start_image_url`, `end_image_asset_id`, `end_image_url`, `elements[]` | Yes | Yes |
| `fal-ai/kling-video/o3/pro/image-to-video` | `image_url` | `image_asset_id` | `image_url`, `start_image_asset_id`, `start_image_url`, `end_image_asset_id`, `end_image_url` | Yes | Partial |
| `fal-ai/kling-video/o3/pro/reference-to-video` | practical: prompt + refs | `start_image_asset_id` + `reference_image_asset_ids[]` | `start_image_url`, `reference_image_urls[]`, `elements[]`, `end_image_*` | Yes | Partial |
| `muapi/seedance-2-vip-image-to-video` | `images_list[]` | `reference_image_asset_ids[]` | `reference_image_urls[]`, `start_image_asset_id`, `start_image_url` | Yes | Yes |
| `muapi/seedance-2-vip-omni-reference` | `prompt` + multimodal refs | `reference_image_asset_ids[]`, `reference_video_urls[]`, `reference_audio_urls[]` | `reference_image_urls[]`, `elements[]`, `character_id`, `character_ids[]` | Yes | Yes |
| `muapi/wan3.0-text-to-video`, `muapi/wan3.0-prime-text-to-video` | `prompt` | no references | `resolution`, `aspect_ratio`, `duration`, `thinking_mode`, `enable_audio`, `seed` | Yes | Yes |
| `muapi/wan3.0-image-to-video`, `muapi/wan3.0-prime-image-to-video` | `prompt`, `image_url` | `start_image_asset_id` | `start_image_url`; optional `end_image_asset_id` / `end_image_url` maps to `last_image` | Yes | Yes |
| `muapi/wan3.0-reference-to-video`, `muapi/wan3.0-prime-reference-to-video` | `prompt`; optional provider arrays | `images_list[]`, `videos_list[]`, `audios_list[]` | unified reference image/video/audio URL fields | Yes | Yes |

**Legend:** *Implemented* = unified→provider translation is wired. *Tested* = targeted provider-specific outbound assertion exists. *Partial* = path looks wired but full provider-specific outbound assertion is not at the same confidence level as Fal Kling V3 Pro.

**Matrix status:** The validator-derived matrix is authoritative for submission-time validation. The provider-certified rows above are authoritative for what actually reaches the provider. Both are now in sync for the common paths.
