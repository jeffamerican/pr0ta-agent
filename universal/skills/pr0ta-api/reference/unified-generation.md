# Unified Generation API — Reference

The primary way to trigger all generation programmatically. A single submission route dispatches to the appropriate generation backend. This file documents the full request/response contract for every generator/mode combination.

## Retry safety

Every paid submission should carry a stable `idempotency_key` (maximum 200 characters). Reuse the same key when retrying after a timeout; PR0TA claims it before remote media validation and provider submission, preventing a second generation or charge. An in-progress retry returns a typed `409`; after acceptance, retrying returns the existing task. REST callers may alternatively send the standard `Idempotency-Key` header. When neither is supplied, `metadata.operation_instance_id` is promoted into a stable operation-scoped key.

For batch REST submissions, an `Idempotency-Key` header is the stable batch key. PR0TA derives one indexed key per item before replay validation. An item's explicit body `idempotency_key` takes precedence when supplied.

## Overview

### Submit Generation (Auth Required)

```
POST /api/v2/projects/{project_id}/generate
```

Behavior:
- Resolves `project_id` and verifies edit access
- Resolves input asset IDs to stable internal URLs
- Resolves stored project `element_ids` and `character_ids` into provider-ready references
- Dispatches to the image, video, 3D, Lipsync, audio, or music generation stack
- Returns a task ID for event/task polling

**Important:** `generator` is required on every request. Sending only `model` and `mode` will fail validation.

### Supported Generators and Modes

| Generator | Mode | Description |
|-----------|------|-------------|
| `image` | `txt_to_img` | Text-to-image (Nano Banana 2 default, GPT Image 2 for prompt adherence / character consistency) |
| `image` | `img_to_img` | Prompt-based image editing |
| `image` | `ref_to_img` | Reference-driven image generation |
| `image` | `edit_img` | Direct image editing |
| `video` | `ref_to_vid` | Reference-to-video (Kling, Runway, etc.) |
| `video` | `txt_to_vid` | Text-to-video (Seedance, LTX, etc.) |
| `video` | `extend_video` / `video_extend` | Extend a source video with a cataloged extension model |
| `video` | `video_to_video` | Transform a source video with an edit-capable model (Beeble SwitchX, Seedance 2.5 Edit, Gemini Omni Flash 1.1 edit), or derive a matte with `fal-ai/birefnet/v2/video` or `bria/video/background-removal` (no prompt; provider controls go in `parameters`); SwitchX also accepts `alpha_asset_id` mattes |
| `3d` | `image_to_3d` | Image-to-3D asset/body generation (SAM 3D, Meshy, Rodin, etc.) |
| `3d` | `animate_3d` | Rig a humanoid GLB and generate multiple Meshy animation clips |
| `lipsync` | `lipsync` / `video_audio_to_video` | Video/audio-driven Lipsync |
| `audio` | `txt_to_speech` | Text-to-speech (Gemini Flash TTS default, ElevenLabs v3 fallback) |
| `audio` | `text_to_sound` | Text-to-sound effects (ElevenLabs Sound Effects) |
| `music` | `txt_to_music` | Text-to-music (ElevenLabs Music) |

Unsupported combinations return `400`.

The public compatibility aliases `text_to_image` and `image_edit` normalize to `txt_to_img` and `img_to_img` respectively. Agents should still emit the canonical modes above. An edit must preserve its source authority through `image_asset_id`, `reference_image_asset_ids`, or the corresponding URL fields; do not recover from an edit validation error by changing the operation to text-to-image.

### Image-to-3D Request

```json
{
  "generator": "3d",
  "mode": "image_to_3d",
  "model": "fal-ai/sam-3/3d-body",
  "image_asset_id": "project-image-asset-id",
  "parameters": {"include_3d_keypoints": true, "export_meshes": true}
}
```

The model must be classified under `generator=3d` by `GET /api/v2/models`. The route resolves project image assets, submits asynchronously, registers the returned 3D asset, and returns a task ID for normal polling. Use `parameters` for fields from `models_get_defaults` that are not common unified request fields.

Meshy v6 and v7 image-to-3D also accept `enable_rigging`, `rigging_height_meters`, `enable_animation`, and one `animation_action_id` from 0-696. When rigging or animation is explicitly requested, the task fails if the provider returns only the unrigged base model. The Meshy v7 multi-image route accepts one to four views of the same object through `parameters.image_urls`; project assets in `reference_image_asset_ids` are resolved into that array automatically.

Canonical Meshy v7 IDs are `meshy/v7/image-to-3d` and `meshy/v7/multi-image-to-3d`; do not add a `fal-ai/` prefix.

### Rig and Multi-Animation Request

```json
{
  "generator": "3d",
  "mode": "animate_3d",
  "model": "fal-ai/meshy/rigging/multi-animation",
  "model_asset_id": "humanoid-glb-asset-id",
  "animation_action_ids": [0, 30],
  "height_meters": 1.82
}
```

The source must be a provider-accessible humanoid GLB. `animation_action_ids` must contain 1-10 unique integer IDs from 0-696. The task persists the base rig, walking/running outputs, and every requested animation clip; it fails if a requested clip is missing.

**Mode/model compatibility:** The API validates that the chosen mode is compatible with the resolved model. Kling models are reference-only -- use `mode=ref_to_vid`. Seedance and LTX models support `mode=txt_to_vid`. Sending `txt_to_vid` with a reference-only model (or vice versa) returns `400`. Seedance image-based modes strictly require at least one image reference.

### Image Generation Request

```json
{
  "generator": "image",
  "mode": "txt_to_img",
  "model": "nano_banana_2",
  "prompt": "Extreme close-up inside a swirling psychedelic vortex...",
  "width": 2048,
  "height": 2048,
  "format": "png",
  "negative_prompt": "blurry, distorted"
}
```

Required fields: `generator`, `mode`, `prompt`
Optional fields: `model`, `width`, `height`, `image_size`, `num_images`, `format`, `negative_prompt`, `seed`, `thinking_level`

**Full image parameter reference:**

| Parameter | Type | Notes |
|-----------|------|-------|
| `width` | int | Output width in pixels |
| `height` | int | Output height in pixels |
| `image_size` | string | Alternative to width/height (e.g., `landscape_4_3`). GPT Image 1.5 ignores this. |
| `num_images` | int | Number of images to generate (default: 1) |
| `format` | string | `png`, `jpeg`, `webp`. NB2 may return PNG regardless. |
| `seed` | int | For reproducibility (leave blank for random) |
| `thinking_level` | string | Reasoning level for complex prompts. **Nano Banana 2 only** — passed through to provider. |
| `negative_prompt` | string | What to exclude from generation |

**Image format:** Accepted values: `png`, `jpeg`, `jpg`, `webp`. The value `jpg` is normalized to `jpeg`. Unsupported formats return `400`. Note: Nano Banana 2 may output PNG regardless of the requested format -- accept whatever format the asset comes back as.

**Image resolution constraints by model:**
- **Nano Banana 2 Edit** -- Supports resolutions `0.5K`, `1K`, `2K`, and `4K`; aspect ratios `auto`, `21:9`, `16:9`, `3:2`, `4:3`, `5:4`, `1:1`, `4:5`, `3:4`, `2:3`, `9:16`, `4:1`, `1:4`, `8:1`, and `1:8`. Unsupported values such as `2:1` are rejected before submission.
- **GPT Image 1.5** -- Ignores `image_size` parameter via API. Always outputs 1024x1024 regardless of requested dimensions. Use Nano Banana 2 for controlled dimensions.
- Other models -- Check `GET /api/v2/models` for supported dimensions.

### Model Capabilities Quick Reference

| Model | Generator | Duration | Aspect Ratios | Key Features | Quirks |
|-------|-----------|----------|---------------|-------------|--------|
| Nano Banana 2 | image | n/a | All ratios, up to 4K | Fast, precise, thinking level | `portrait_4_3` returns landscape |
| GPT Image 1.5 | image | n/a | 1024x1024 only | Cheap, useful false-positive fallback for allowed prompts | Ignores `image_size` parameter |
| Kling O3 Pro | video | 3–15s | `16:9`, `9:16`, `1:1` (ref-to-video variant) | Multi-prompt (6 cuts), elements, voice, sound | Often outputs 1440×1440 square |
| Kling O3 4K V2V | video | 3–15s | Edit follows source; Reference adds `auto`, `16:9`, `9:16`, `1:1` | Native 4K edit/reference, Elements, image refs, `keep_audio` | Premium approval-gated finishing route; MP4/MOV source <=200 MB |
| MiniMax H3 Max R2V | video | 5–15s | `adaptive` plus six fixed ratios | Up to 12 mixed image/video/audio refs, native audio | `balanced`/`quality` prompt expansion; token-sensitive estimate |
| Kling V3 Pro | video | 3–15s | `16:9`, `9:16`, `1:1` | Multi-shot (5 shots), camera control, sound | Camera control API parameter |
| Seedance 2.0 Omni | video | Integer 4–15 | `21:9`, `16:9`, `4:3`, `1:1`, `3:4`, `9:16` | Character resources, quad-modal (9img/3vid/3aud) | Lowercase `@image`/`@video`/`@audio`; verify route-specific audio controls |
| Seedance 2.0 T2V / I2V | video | Integer 4–15 | same six ratios | Text-only (T2V) or image-to-video (I2V) | PR0TA defaults synchronized to live MuAPI OpenAPI |
| Seedance 2.5 standard family | video | Integer 4–30 | six common ratios plus `9:21` | T2V, I2V, first-last, and Omni at 480p/720p/1080p/4K model-ID tiers | Always audio-bearing; no audio toggle, negative prompt, or character token; public pages conflict on 1080p lineage |
| Seedance 2.5 Edit / Extend | video | Integer 4–30 | six common ratios plus `9:21` | Source-video editing and continuation at 480p/720p/1080p/4K by model ID | Audio-bearing; `generate_audio`; Edit accepts optional image/audio refs; Extend accepts optional `last_image_url` |
| Beeble SwitchX | video | Follows source; plates over 240 frames are chunked automatically | Follows source | Plate-preserving background swap and relight; alpha modes `auto`/`fill`/`select`/`custom`; one look reference; chunked jobs chain each rendered tail into the next look reference by default; registers render, alpha, and source | 720/1080 cap, 2,770,000-pixel budget, polling only, one job billed per chunk, identity may vary across runs |
| Beeble SwitchX Still | image | n/a | Follows source frame | Same engine on one frame via `edit_img` with `image_asset_id` and an optional grayscale `alpha_asset_id` | Angle-matched reference plates; `select` is treated as `custom` |
| BiRefNet v2 Video | video | Follows source | Follows source | Source-video matte via `video_to_video` with no prompt; `parameters` carry `model` (`Matting` for hair), `output_mask` (default on), and `refine_foreground`; returns `matte_asset_id` and `plate_asset_id` | Two assets per task; `parameters.model` is BiRefNet's own enum, not an endpoint id |
| Bria Video Background Removal | video | Follows source | Follows source | Source-video cutout via `video_to_video` with no prompt; `parameters` carry `background_color` and `output_container_and_codec` | `Transparent` needs `webm_vp9` or a ProRes container; the output is RGBA, not a luma matte |
| Hailuo H3 | video | Integer 5–15 | common six; R2V adds `adaptive`; I2V follows first image | Fixed 2K/24 fps T2V, first/optional-last I2V, mixed R2V and focused source edits | Always native-stereo audio; no toggle; literal `Image N`/`Video N`/`Audio N` roles |
| FLUX 3 video | video | 5–20s | `auto`, `21:9`, `2:1`, `16:9`, `4:3`, `1:1`, `3:4`, `9:16` where exposed | Eleven T2V/I2V/first-last/24 fps keyframe/extension/Draft/Enhance routes | Generation defaults `generate_audio` on; Enhance requires only `draft_cache_url` as creative input |
| LTX 2.5 | video / lipsync | Pro 6/8/10; Fast even 6–20 by resolution/FPS; A2V source 2–20 | `16:9`, `9:16`, or route `auto` | Six canonical Pro/Fast T2V, I2V, and audio-to-video routes | T2V/I2V default `generate_audio` on; A2V carries source audio and has a narrower field surface |
| ElevenLabs v3 | audio | Auto (by text length) | n/a | Best TTS quality, voice discovery | Max 5000 chars per call |
| Music v1 | music | 1–300s | n/a | Duration param, emotional arc prompts | Prompt for temporal cues |

Always verify current capabilities against `GET /api/v2/models`. For the authoritative per-model duration / aspect matrix see `pr0ta-video` → "Per-Model Duration Constraints" (synced with the PR0TA API team response).

### Image Edit Request

For `img_to_img`, `ref_to_img`, and `edit_img` modes. Requires at least one input image or element reference.

```json
{
  "generator": "image",
  "mode": "img_to_img",
  "model": "fal-ai/nano-banana-2/edit",
  "prompt": "Keep the subject identity and pose, but relight as a moody neon noir portrait with blue rim light and light rain.",
  "image_asset_id": "c4f3bdf3-472a-4d6a-ad08-ea3872b8ed0c",
  "reference_image_asset_ids": ["729f2c9e-94f6-4d16-a4d6-469d4c5457ac"],
  "format": "png"
}
```

Reference-driven Kling image edit:
```json
{
  "generator": "image",
  "mode": "ref_to_img",
  "model": "kling/o1/image-to-image",
  "prompt": "Match the wardrobe and facial structure from the references, convert into polished sci-fi key art.",
  "reference_image_urls": ["https://example.com/hero-base.png", "https://example.com/style-ref.png"],
  "element_ids": ["project-element-uuid-1"]
}
```

GPT Image edit:
```json
{
  "generator": "image",
  "mode": "edit_img",
  "model": "fal-ai/gpt-image-1/edit-image",
  "prompt": "Replace the plain background with a softly lit editorial studio set.",
  "image_asset_id": "482ee64f-f2e2-4f7f-b5f5-2be9822f7758"
}
```

Valid image-edit inputs: `image_asset_id`, `image_url`, `start_image_asset_id`, `start_image_url`, `reference_image_asset_ids[]`, `reference_image_urls[]`, `element_ids[]`, `elements[]`.

### Video Generation Request (Basic Ref-to-Vid)

```json
{
  "generator": "video",
  "mode": "ref_to_vid",
  "model": "kling_o3_pro",
  "prompt": "@Image1 -- camera pulls back from psychedelic vortex to reveal logo...",
  "duration": 10,
  "aspect_ratio": "1:1",
  "refs_strength": 140,
  "start_image_asset_id": "abc-123",
  "end_image_asset_id": "def-456",
  "elements": [
    {
      "frontal_asset_id": "ghi-789",
      "additional_asset_ids": ["jkl-012"]
    }
  ],
  "negative_prompt": "blurry, distorted, low quality",
  "cfg": 0.5,
  "sound": "off"
}
```

Required fields: `generator`, `mode`, `prompt` (or `multi_prompt`), and one of `start_image_asset_id`, `start_image_url`, or `image_asset_id` for Kling-style workflows.
Optional fields: `model`, `duration`, `aspect_ratio`, `refs_strength`, `end_image_asset_id`, `end_image_url`, `elements[]`, `element_ids[]`, `character_ids[]`, `negative_prompt`, `cfg`, `sound`, `seed`

**Sound control:** Pass `sound: "on"` or `sound: "off"` only when the selected model's live defaults expose it. Do not send it to current Seedance 2.0 VIP T2V/I2V/Omni, Seedance 2.5 standard, or Hailuo H3 routes. Seedance 2.5 and H3 still return audio-bearing video. FLUX 3 and LTX 2.5 generation routes use their schema-level `generate_audio` field instead.

**CRITICAL Kling prompt rules** (same as browser UI):
- Use `@Image1` to reference the Start Image in the prompt.
- Do not use `@Image2`; the End Image is an implicit structural target, not a promptable token.
- Use `@Element1`, `@Element2`, and so on for added Elements.
- MuAPI Seedance 2.0 is different: use lowercase `@image1`, `@video1`, and `@audio1` tokens matching the submitted reference arrays.
- If `end_image_asset_id` is provided, `start_image_asset_id` is also required

### Video Extension Request

Use video extension when the user wants a generated continuation of an existing clip, not a still-frame hold. The unified route accepts `mode: "extend_video"` or `mode: "video_extend"` and routes to the video-extension manager.

```json
{
  "generator": "video",
  "mode": "extend_video",
  "model": "fal-ai/veo3.1/extend-video",
  "prompt": "Continue the slow dolly into a wider view of the neon market, preserving camera direction and lighting.",
  "video_asset_id": "source-video-asset-id",
  "duration": 7,
  "aspect_ratio": "9:16",
  "sound": "off"
}
```

Required fields: `generator`, `mode`, `prompt`, and one of `video_asset_id`, `video_url`, or `source_url`.

Supported extension-capable models include `muapi/seedance-2.5-video-extend`, `blackforestlabs/flux-3/extend-video`, `fal-ai/pixverse/extend`, `fal-ai/pixverse/v6/extend`, `fal-ai/magi/extend-video`, `fal-ai/veo3.1/extend-video`, `fal-ai/vidu/q2/video-extension/pro`, and `kling/v3/video-extend`. Check `/api/v2/models?category=video` for the current catalog and schema. Seedance 2.5 also has `-480p`, `-1080p`, and `-4k` variants selected directly by model ID; FLUX 3 also exposes a `/draft` extension route.

Provider-specific options can be passed when supported by the model schema, including `resolution`, `style`, `fps`, `num_frames`, `generate_audio_switch`, and `extension_mode`/`extend_direction` (`start` or `end` for models that expose start/end extension).

### Video Generation with Stored Consistency Resources

Use `element_ids` to reference project-scoped Kling elements and `character_ids` for Seedance characters instead of passing inline references every time.

Advanced Kling request with stored elements + multi-prompt + camera control:
```json
{
  "generator": "video",
  "mode": "ref_to_vid",
  "model": "kling/o3/image-to-video",
  "prompt": "Hero exits frame into fog",
  "element_ids": ["project-element-uuid-1", "project-element-uuid-2"],
  "multi_prompt": [
    { "prompt": "Hero steps into frame" },
    { "prompt": "Hero turns and exits into fog" }
  ],
  "prompt_mode": "multi_prompt",
  "camera_control": {
    "type": "simple",
    "config": { "horizontal": 5 }
  },
  "voice_ids": ["1234567890"]
}
```

Preferred Seedance 2.5 Omni Reference request:
```json
{
  "generator": "video",
  "mode": "ref_to_vid",
  "model": "muapi/seedance-2.5-omni-reference",
  "prompt": "Use the supplied images as identity, wardrobe, set, and style authority. Preserve those traits through the chronological action and explicit end state.",
  "reference_image_asset_ids": ["a73b9aad-..."],
  "duration": 8,
  "aspect_ratio": "16:9"
}
```

Seedance 2.0 trained-character exception—use only when trained character IDs or its positional `@` reference-token contract are required:
```json
{
  "generator": "video",
  "mode": "ref_to_vid",
  "model": "muapi/seedance-2-vip-omni-reference",
  "prompt": "Use @image1 for character identity, @video1 for motion style, and @audio1 for rhythm.",
  "character_ids": ["project-character-uuid-1"],
  "reference_image_urls": ["https://example.com/hero.png"],
  "reference_video_urls": ["https://example.com/motion.mov"],
  "reference_audio_urls": ["https://example.com/music.wav"],
  "references": [
    { "type": "image", "image_url": "https://example.com/hero.png" },
    { "type": "video", "video_url": "https://example.com/motion.mov" },
    { "type": "audio", "audio_url": "https://example.com/music.wav" }
  ]
}
```

**Notes on consistency fields:**
- `element_ids[]` -- references stored project Elements (resolved server-side to Kling provider format)
- `character_ids[]` -- references stored project Characters (currently resolves one character per request)
- `character_id` -- direct MuAPI Seedance character reference (alternative to stored resolution). To **create** a new Omni character token, use `muapi/seedance-2-omni-reference-train` (single portrait) or `muapi/seedance-2-character` (character sheet / 1-3 stills); both return the token in `result_refs.character_id`. See `pr0ta-consistency` → `reference/provider-consistency-systems.md` → "Creating A Seedance Character Token".
- **Consistency bundle** -- before multi-shot character generation, read `GET /characters/{id}/consistency` or `GET /characters/consistency?name=...` to get all approved references, Elements, tokens, and `provider_payloads` in one call. See `reference/projects-models-resources.md` → "Character Consistency Bundles".
- `multi_prompt[]` -- array of prompt segments for multi-shot generation; set `prompt_mode: "multi_prompt"` to activate
- `camera_control` -- structured camera control for Kling V3/O3
- `references[]` -- typed multi-modal references for Seedance Omni (`image`, `video`, `audio`)
- `reference_video_urls[]` -- video reference URLs for Seedance Omni
- `reference_audio_urls[]` -- audio reference URLs for Seedance Omni; Seedance 2.5 Omni allows up to 10 files but enforces a 15-second combined duration
- `keep_audio` -- preserve source audio on Kling O3 4K V2V routes; defaults to `true`
- `shot_type` -- `customize` on Kling O3 4K V2V routes
- `voice_ids[]` -- voice control for Kling O3
- `sound` -- `"on"` or `"off"` only when the selected endpoint's live schema exposes audio control; omit it for H3 and Seedance 2.5 standard routes, which remain audio-bearing without the field.
- `seed` -- reproducibility seed

### Audio Generation Request (Text-to-Speech)

```json
{
  "generator": "audio",
  "mode": "txt_to_speech",
  "model": "fal-ai/gemini-3.1-flash-tts",
  "text": "AUDIO PROFILE\nWarm documentary narrator, close-mic studio recording, natural conversational delivery.\n\nSCENE\nA short voiceover for a family-friendly animated story.\n\nDIRECTOR NOTES\nPace around 145 words per minute. Keep it playful but not exaggerated.\n\nTRANSCRIPT\nOnce upon a time, a little turtle found a very large cake.",
  "voice": "Kore",
  "style_instructions": "Warm, playful, clear.",
  "language_code": "en-US"
}
```

Required fields: `generator`, `mode`, `text`
Optional fields: `model`, `voice`, `language_code`, `style_instructions`, `temperature`, `speakers`, `voice_id`, `voice_settings`

Notes:
- Gemini Flash TTS is the default model for new TTS requests.
- `voice_id` is for the ElevenLabs v3 fallback and references a voice profile created in the Audio Generator's Voice Design tab or available as a platform default.
- `text` max length: 5000 characters. For longer narrations, split into multiple requests.
- Output is an audio asset (typically MP3).

### Music Generation Request (Text-to-Music)

```json
{
  "generator": "music",
  "mode": "txt_to_music",
  "model": "music-v1",
  "prompt": "Playful Mozart-style piano piece, major key, light and cheerful",
  "duration": 30,
  "output_format": "mp3_44100_192"
}
```

Required fields: `generator`, `mode`, `prompt`
Optional fields: `model`, `duration`, `output_format`

**`output_format` is the canonical field** for specifying audio output format. Accepted values: `mp3_22050_32`, `mp3_44100_64`, `mp3_44100_96`, `mp3_44100_128`, `mp3_44100_192`, `pcm_16000`, `pcm_22050`, `pcm_44100`, `pcm_48000`, `opus_48000_32`, `opus_48000_64`, `opus_48000_96`, `opus_48000_128`, `opus_48000_192`, `ulaw_8000`, `alaw_8000`. The legacy `format` shorthand (e.g. `"mp3"`, `"wav"`, `"opus"`) is still accepted and normalized (e.g. `"mp3"` → `"mp3_44100_192"`, `"wav"` → `"pcm_44100"`). Unsupported values return `400`.

Notes:
- `duration` is in seconds (default: 30).
- Output is an audio asset.

### Sound-Effect Generation Request (Text-to-Sound)

```json
{
  "generator": "audio",
  "mode": "text_to_sound",
  "model": "eleven_text_to_sound_v2",
  "prompt": "Heavy steel door slam in a concrete corridor, sharp impact and short decay",
  "duration": 3,
  "output_format": "mp3_44100_192"
}
```

Required fields: `generator`, `mode`, `prompt`. Optional fields: `model`, `duration`, `output_format`, `folder_path`. The compatibility aliases `txt_to_sfx` and `text_to_sfx` normalize to `text_to_sound`; agents should emit the canonical mode. The legacy model ID `sound-effects-v1` is accepted and resolves to `eleven_text_to_sound_v2`.

### Asset ID Resolution

The route resolves asset IDs to verified provider-facing signed URLs before dispatching. All referenced assets must belong to the same project and remain accessible in storage or the request returns `400` before provider task creation.

Built-in resolutions:
- `image_asset_id` -> `image_url`
- `start_image_asset_id` -> `start_image_url`
- `end_image_asset_id` -> `end_image_url`
- `reference_image_asset_ids[]` -> `reference_image_urls[]`
- `reference_video_asset_ids[]` -> `reference_video_urls[]`
- `reference_audio_asset_ids[]` -> `reference_audio_urls[]`
- `elements[].frontal_asset_id` -> `frontal_image_url`
- `elements[].additional_asset_ids[]` -> `reference_image_urls[]`

Stored resource resolution:
- `element_ids[]` -> provider-ready Kling element references
- `character_ids[]` -> provider-ready Seedance/MuAPI character references

You can also pass URLs directly (`start_image_url`, `end_image_url`, `reference_image_urls[]`, `reference_video_urls[]`, `reference_audio_urls[]`) instead of asset IDs.

### Submission Response

```json
{
  "task_id": "task_xyz123",
  "status": "queued",
  "estimated_seconds": 120,
  "credits_cost": 147.0
}
```

- `task_id` -- use for polling
- `status` -- usually `queued` or `started`
- `estimated_seconds` -- optional estimate
- `credits_cost` -- optional and nullable; do not assume it is always populated

**Note on task status:** The `provider` and `model_id` fields on initial task objects may be `null` -- this does not indicate a dispatch failure. The task transitions through `queued` -> `started`/`running` -> `succeeded`/`failed` as normal.

---
