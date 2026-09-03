# Google Gemini Omni Flash 1.1 on Fal

Use the exact Fal IDs:

- `google/gemini-omni-flash/v1.1/text-to-video`
- `google/gemini-omni-flash/v1.1/image-to-video`
- `google/gemini-omni-flash/v1.1/reference-to-video`
- `google/gemini-omni-flash/v1.1/edit`

The three generation routes produce native audiovisual video. They accept 3–10 whole seconds, default to 8 seconds, and expose `360p`, `720p`, `1080p`, and `4k` resolution with `16:9` or `9:16` aspect ratio. The Edit route instead accepts a source video plus a natural-language instruction; it exposes only `resolution`, defaulting to `720p`, and does not document duration, aspect-ratio, or audio controls.

## Route Contracts

| Route | Required | Optional references |
|---|---|---|
| T2V | `prompt` | None |
| I2V | `prompt`, `image_url` | `end_image_url` |
| R2V | `prompt` plus a deliberate reference package in PR0TA | `image_urls` (10), `reference_video_urls` (3) |
| Edit | `prompt`, `video_url` | `resolution`: `360p`, `720p`, `1080p`, or `4k` |

Each R2V reference video must be no longer than 3 seconds. The current Fal schema exposes no reference-audio field. Do not substitute Wan, Seedance, or H3 array names.

The table above names Fal's provider fields, not the preferred unified PR0TA input. When the image already belongs to the project, submit its canonical asset ID:

- I2V: `image_asset_id` or `start_image_asset_id`
- R2V: ordered `reference_image_asset_ids[]`

PR0TA resolves those assets to verified provider-facing signed URLs and maps them to Google `image_url` or `image_urls` during submission. Use direct URL fields only for media that is already externally hosted and provider-accessible. Do not download a project asset or invoke the asset-downloading workflow merely to construct a Google generation request; downloading is for retrieving completed outputs.

## Prompting

Use direct natural-language audiovisual direction for the shot body:

`framing and setting -> subject action in playback order -> camera -> dialogue and physical sound -> end state`

For I2V, let the supplied image own appearance and composition; describe motion after frame zero and the progression to `end_image_url` when present. Do not run the multi-reference orchestration compiler for I2V.

For R2V, finalize each array before writing the prompt. Bind images with zero-based `<IMAGE_REF_N>` tags and videos with zero-based `<VIDEO_REF_N>` tags; for example, `<IMAGE_REF_0> controls identity` and `<VIDEO_REF_0> controls camera motion`. PR0TA compiles these tags from the structured reference plan. Do not invent `@imageN`, one-based `Image N`, or reference-audio bindings.

For Edit, make the source clip authoritative. Request one focused transformation, locate it in space and time when needed, and state the identity, motion, timing, framing, and scene elements that must remain unchanged. Do not send generation-only fields that the Edit schema does not expose.

Every speech-bearing result must pass the Scribe V2 transcription gate before editorial use. Inspect actual duration, resolution, reference adherence, dialogue, and sync.

Official Fal API pages: [T2V](https://fal.ai/models/google/gemini-omni-flash/v1.1/text-to-video/api), [I2V](https://fal.ai/models/google/gemini-omni-flash/v1.1/image-to-video/api), [R2V](https://fal.ai/models/google/gemini-omni-flash/v1.1/reference-to-video/api), [Edit](https://fal.ai/models/google/gemini-omni-flash/v1.1/edit/api).
