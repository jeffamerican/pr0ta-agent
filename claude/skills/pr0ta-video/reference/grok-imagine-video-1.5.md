# Grok Imagine Video 1.5 on Fal

Use this reference when the resolved model is one of:

| Model id | Mode | Image inputs |
|---|---|---|
| `xai/grok-imagine-video/v1.5/text-to-video` | `txt_to_vid` | none; any image input is rejected |
| `xai/grok-imagine-video/v1.5/image-to-video` | `ref_to_vid` | exactly one opening image |
| `xai/grok-imagine-video/v1.5/reference-to-video` | `ref_to_vid` | 1–7 reference images |

The image-to-video route does not accept `img_to_vid`; send `ref_to_vid`. Older `xai/grok-imagine-video/*` routes without `v1.5` are separate contracts; do not copy these limits to them.

## Contract

- `prompt` is required, at most 4,096 characters.
- `duration`: whole seconds from 1 through 15.
- `resolution`: `480p`, `720p`, or `1080p` on text-to-video and image-to-video; `480p` or `720p` on reference-to-video.
- `aspect_ratio`: `16:9`, `4:3`, `3:2`, `1:1`, `2:3`, `3:4`, or `9:16` on text-to-video and reference-to-video. Image-to-video rejects `aspect_ratio`; its output follows the input image, so prepare the image at the delivery ratio.
- Project images go in the usual unified fields (`image_asset_id`, `start_image_asset_id`, or ordered `reference_image_asset_ids[]`); PR0TA resolves them to Fal's `image_url` or `reference_image_urls`.
- The provider advertises native synchronized audio (speech, ambience, music, effects). There is no audio toggle in the schema, and PR0TA verifies audio on the delivered file; inspect it before assuming sound or silence.

Query `models_get_defaults` before submission for the current defaults.

## Prompting

Write natural-language audiovisual direction in playback order:

`framing and setting → subject and action → camera path → dialogue and sound → end state`

- **Text-to-video:** establish the subject and location fully, then one causal action arc and one camera path.
- **Image-to-video:** the image owns frame zero. Spend the prompt on motion, camera, and sound, and repeat only the traits that must stay locked.
- **Reference-to-video:** tag references with zero-based `<IMAGE_0>`, `<IMAGE_1>`, … in the final array order and give each one role, for example `The courier from <IMAGE_0> rides past the storefront from <IMAGE_1>.` Do not use `@image1`, `Image 1`, or `<IMAGE_REF_N>`; those belong to other families.
- Put spoken lines in quotation marks, attributed to a named on-screen speaker, and keep them short.

## Review

Check identity against each tagged reference, the delivered duration and resolution, and any speech. Speech-bearing results follow the `pr0ta-audio` indexing rule before timeline use.
