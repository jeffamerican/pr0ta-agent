# GPT Image 2.5 production prompting

## Selection and request contract

PR0TA's production preference is **Sunburst with `quality: "max"`** for premium stills and edits. Flare is the faster-iteration alternative. Both supersede GPT Image 2 / GPT-02; select that legacy model only on explicit user request. Keep explicit model, quality, and budget constraints. This is PR0TA policy, not a claim that every max-quality take will outperform every alternative.

| Operation | Sunburst | Flare |
|---|---|---|
| `txt_to_img` | `openai/gpt-image-2.5/sunburst/text-to-image` | `openai/gpt-image-2.5/flare/text-to-image` |
| `img_to_img`, `ref_to_img`, `edit_img` | `openai/gpt-image-2.5/sunburst/edit` | `openai/gpt-image-2.5/flare/edit` |

These are Fal routes. Fetch `models_get_defaults` for the exact route. Fal exposes `quality` values `auto`, `low`, `medium`, `high`, `xhigh`, `max`, defaulting to `high`. Highest-quality requests must explicitly send `max`. Use `image_size` presets or `{width, height}`; direct OpenAI's `size` string is not the Fal field. Keep dimensions within the provider's documented limits, and treat 4K output as experimental.

Fal accepts 1–10 outputs, prompts up to 32,000 characters, and up to 16 reference images on edit routes. The optional `mask_url` controls the edit region. Use PNG or WebP with `background: "transparent"` for transparency; `output_compression` (0–100) applies only to JPEG/WebP. Quality, compression, and dimensions are different controls. Do not invent seed, guidance, reference-strength, negative-prompt, or input-fidelity fields absent from the route schema.

## Author the production brief

Lead with the deliverable and its use in this production. Make composition, materials, lighting, literal text, and reference roles unambiguous. For edits, separate the intended change from the details that must remain. Iterate one change at a time. These practices follow the [official OpenAI image prompting guide](https://developers.openai.com/api/docs/guides/image-prompting).

PR0TA still brief example:

> Deliverable: a cinematic 16:9 hero frame for the approved observatory set. Scene: the astronomer stands in the right third beside the brass telescope, leaving the left third open for the title. Materials: tarnished brass, chipped dark-green paint, dust along the window ledge. Lighting: a narrow morning beam catches the telescope; the room retains soft cool shadow detail. Copy: only “THE LAST OBSERVATION”, upper left, two lines, ivory condensed capitals. Preserve the approved wardrobe and set geometry; no additional signs or figures.

Submit through `generation_submit` with these settings inside `request`, alongside the authored `prompt` and `generator: "image"`:

```json
{
  "mode": "txt_to_img",
  "model": "openai/gpt-image-2.5/sunburst/text-to-image",
  "quality": "max",
  "image_size": {"width": 2048, "height": 1152},
  "output_format": "png",
  "num_images": 1
}
```

## Edit from approved references

Resolve actual project assets first. Use `image_asset_id` for the base and ordered `reference_image_asset_ids` for additional inputs. Number roles in the final provider attachment order, not the order in which assets were found. PR0TA resolves these IDs to Fal's `image_urls`; mentioning an image in prose does not attach it.

PR0TA edit brief example:

> Image 1 is the approved hero portrait and owns identity, expression, pose, lens perspective, and wardrobe. Image 2 supplies only the observatory's architecture and materials. Place the subject from Image 1 into that observatory. Preserve facial proportions, eye color, hairline, skin texture, and costume seams. Match the subject's contact shadows to the window light. Keep the camera height and framing from Image 1. Do not import people or written labels from Image 2.

Use the `/edit` endpoint and `quality: "max"`. For a localized repair, attach a mask and describe the repair plus protected surroundings. An edit may still drift; inspect the complete image before accepting it. Use compositing when untouched pixels must remain identical.

## Acceptance and iteration

Check the rendered artifact for cast identity, reference assignment, wardrobe/prop continuity, exact text, panel order, anatomy, output dimensions, and alpha edges where relevant. Judge it at intended delivery scale. Record accepted assets and decisions in project memory; do not mark candidates as approved automatically.

Query current pricing and submit one compact canary before an authorized paid fan-out. For a comparison, hold the prompt, attachments, dimensions, and output format constant and record quality setting, time, cost, and acceptance. If Sunburst fails, retain the receipt and diagnose or use an authorized 2.5 alternative; never silently fall back to GPT Image 2.

Fal contracts: [Sunburst generation](https://fal.ai/models/openai/gpt-image-2.5/sunburst/text-to-image/api), [Sunburst edit](https://fal.ai/models/openai/gpt-image-2.5/sunburst/edit/api), [Flare generation](https://fal.ai/models/openai/gpt-image-2.5/flare/text-to-image/api), [Flare edit](https://fal.ai/models/openai/gpt-image-2.5/flare/edit/api).
