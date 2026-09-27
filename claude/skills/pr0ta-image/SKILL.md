---
name: pr0ta-image
description: "PR0TA image generation and editing: key frames, reference stills, character sheets, posters, title cards and flash cards, storyboard frames, product and location stills, prompt edits, inpaint and outpaint, background removal, relighting, upscale and restoration, image uploads, and fan-out for hard text shots. Read when generating, editing, uploading, or choosing image models."
---

# Image Generation and Editing

For images that will become Element or Character source material, read `pr0ta-consistency`. Before writing a prompt, read `pr0ta-prompting` and, for the resolved model, its row in `pr0ta-prompting/reference/model-modality-guides.md` (GPT Image 2.5 also has `pr0ta-prompting/reference/gpt-image-25.md`).

For an existing project, call `memory_context_pack` with the scene, character, asset, or department scope. Use approved visual decisions, references, continuity constraints, and conflicts when writing the prompt. After selecting a hero still, rejecting a take, or establishing a visual rule, record it with `memory_record_decision` or `memory_record_note`.

## Resolve the Model

The platform chooses models, not this skill. The admin pins models per modality and each user may override them in Settings → Tools. Text-to-image requests must always name a model; the platform does not pick one for them.

1. Name the operation, then its modality key:

| Operation | Modality key |
|---|---|
| Text-to-image (key frames, posters, stills) | `image_model` |
| Prompt edit of one image | `image_edit_model` |
| Combine several input images | `image_multi_edit_model` |
| Generate from Element or character bundles | `elements_to_image_model` |
| Inpaint a region / extend beyond the border | `image_inpaint_model` / `image_outpaint_model` |
| Remove a background | `bg_removal_model` |
| Upscale, denoise, sharpen, restore | `image_upscale_model` |
| Image to 3D model / image or text to 3D world | `image_to_3d_model` / `image_to_world_model`, `text_to_world_model` |

2. If the user named a model, use it and keep their quality setting; never swap it silently after a failure. Otherwise resolve the key with `models_preferred(modality=...)`; `pr0ta-api` → "Choosing a model" owns the full rule, including a null `model_id`.
3. Call `models_get_defaults(model_id)` for `supported_modes`, fields, enums, and limits. Fields do not transfer between models.
4. For cost-sensitive choices, query `GET /api/crew/model_pricing?model_id={model_id}` for each exact candidate. Skills carry no prices.

REST equivalents: `GET /api/v2/models/preferred?modality=...`, `GET /api/v2/models`, and `GET /api/crew/model_defaults?model_id={model_id}`.

### Capability Facts

Use these when the user asks for a capability; they are not a ranking. Confirm each against `models_get_defaults`.

- **GPT Image 2.5 (Sunburst and Flare, text-to-image and edit):** `quality` accepts `auto`, `low`, `medium`, `high`, `xhigh`, `max`; the highest level requires the literal `max` (the Fal default is `high`). Edit routes take up to 16 reference images and an optional `mask_url`; Flare is the faster variant. GPT Image 2 is a separate route: do not send it `xhigh` or `max`. Read `pr0ta-prompting/reference/gpt-image-25.md`.
- **Nano Banana 2 and Nano Banana 2 Edit:** output size follows the `resolution` field (`0.5K`, `1K`, `2K`, `4K`; `1K` when omitted, which gives about 768 px on the short side, such as 768×1376 at 9:16). `aspect_ratio` accepts `auto` plus fourteen ratios including 21:9, 4:5, and the extreme 4:1, 1:4, 8:1, 1:8. Up to 4 images per call, optional web search, `safety_tolerance` 1–6.
- **Midjourney V7, V8, Niji 7:** one optional `image_url`; each run returns four registered variants in `result.urls` (`result.download_url` is the first). Controls: `stylize` (0–1000), `chaos` (0–100), `weird` (0–3000), `negative_prompt`, `seed`. Niji 7 targets anime and manga.
- **Reve 2.1:** 4096-pixel native detail and layout-aware text for posters, packaging, and infographics. Remix takes 1–8 references addressed as `<frame>N</frame>`.
- **Seedream 5.0 Pro:** dense layouts and multilingual typography; its edit route takes up to 10 input images.
- **Kling Image O3:** 1–9 images per call or a 2–9 image series, 1K/2K/4K, optional Element control.
- **GPT Image 1.5:** fixed sizes 1024×1024, 1536×1024, and 1024×1536.
- **LoRA styles:** Qwen Image 2512 (LoRA) and Z-Image Turbo (LoRA) take up to 3 LoRA weights; find others with `models_list(search="lora")`.
- **Relight or replace the world behind a subject while keeping its pixels:** Beeble SwitchX (Still). Read `pr0ta-hybrid`.

## Submission Contract

Submit with `generation_submit` (or `generation_batch_submit` for up to ten items), then poll with `tasks_get`; parallel submission limits are in `pr0ta-api` → "Rate limits and concurrency".

```json
{
  "project_id": "project-uuid-or-slug",
  "request": {
    "generator": "image",
    "mode": "txt_to_img",
    "model": "<model_id from models_preferred(modality=\"image_model\")>",
    "prompt": "Dark navy infographic showing global market growth, gold accent text, clean vector style.",
    "aspect_ratio": "16:9",
    "format": "png"
  }
}
```

Add size, resolution, and quality fields exactly as the model's schema names them (`resolution`, `image_size`, `quality`, `num_images`, `output_format`). Never ask for a higher resolution in prompt prose.

### Modes and Inputs

| Mode | Use |
|---|---|
| `txt_to_img` | Text-to-image |
| `img_to_img` | Prompt edit of a base image |
| `ref_to_img` | Generate from reference images or Elements |
| `edit_img` | Direct edit (inpaint-style, mask) |

Take the mode from `supported_modes`; some families list only edit modes even when the image input is optional. Edit modes need at least one input: `image_asset_id`, `image_url`, `start_image_asset_id`, `reference_image_asset_ids[]`, `element_ids[]`, or `elements[]`. Put the image being transformed in `image_asset_id` and ordered identity or style references in `reference_image_asset_ids`, then bind each attachment in the prompt with the model's own syntax (see `pr0ta-prompting` → "Reference Binding Is a Submission Contract").

```json
{
  "generator": "image",
  "mode": "img_to_img",
  "model": "<model_id from models_preferred(modality=\"image_edit_model\")>",
  "prompt": "Image 1 is the subject; keep identity and pose. Relight as a moody neon-noir portrait with blue rim light, matching the palette of Image 2.",
  "image_asset_id": "uuid-source-image",
  "reference_image_asset_ids": ["uuid-style-ref"],
  "format": "png"
}
```

Edit modes are the tool for consistency correction: fixing character drift in a key frame before it goes to video. See `pr0ta-consistency`.

`format` accepts `png`, `jpeg`, `jpg` (normalized to `jpeg`), and `webp`; other values return `400`. Some models return PNG regardless of the requested format, so check the delivered file's type.

REST (only when MCP is unavailable, for high-volume scripts, or for an unexposed route):

```bash
curl -X POST "https://app.pr0ta.com/api/v2/projects/$PROJECT_ID/generate" \
  -H "Authorization: Bearer $PR0TA_PAT" \
  -H "Content-Type: application/json" \
  -d '{"generator": "image", "mode": "txt_to_img", "model": "'"$MODEL_ID"'",
       "prompt": "...", "aspect_ratio": "16:9", "format": "png"}'
# Returns {"task_id": "...", "status": "queued"}; poll the task, then download result.asset_id (see pr0ta-api).
```

Batch: `POST /api/v2/projects/{project_id}/generate/batch` takes up to 10 items.

## Enhancement and Restoration

Upscaling, denoising, sharpening and restoration resolve through `image_upscale_model`: call `models_preferred(modality: "image_upscale_model")`, and when the user asks for a specific repair, pick from `models_list(modality: "image_upscale_model")`. These routes are image-to-image processors: they accept no text-generation inputs unless the schema exposes a prompt, and controls do not transfer between families (`models_get_defaults`).

Capabilities, for when the user asks for one: the Topaz image families cover faithful enhancement with optional face or subject recovery (Precision), noise removal (Denoise; start with the least aggressive setting), blur and focus recovery (Sharpen), white balance and colorizing monochrome (Adjust), damaged-photo and scan repair (Restore), alpha-preserving PNG upscales (Transparent), and detail reconstruction (Generative, Creative). All but Generative and Creative are fidelity-oriented; those two invent detail rather than restore it, so use them only when the user approves that tradeoff.


## Uploading Existing Images

The best reference is sometimes a real photograph, a sketch, a location scout, a product shot, or a frame from footage. Upload it and use the returned asset `id` anywhere an asset id is accepted: `image_asset_id`, `start_image_asset_id`, `reference_image_asset_ids[]`, or Element and Character sources.

Use `assets_upload_start` (or `assets_upload_batch_start` for several files) to get a signed upload handoff, PUT the bytes, and let the storage event finalize the asset; call `assets_upload_finalize` only if it did not. Optional metadata on finalize: `category`, `subject`, and `labels`.

REST multipart alternative: `POST /api/v2/projects/{project_id}/assets/upload` with one or more `files` fields (images only); it returns `AssetRead` objects and stamps `labels.source = "upload_api"`. With the Python client:

```python
from pr0ta_client import upload_images

assets = upload_images(project_id, ["/path/to/actor-headshot.jpg", "/path/to/location-photo.png"])
headshot_id = assets[0]["id"]
```

See `pr0ta-api` → `reference/image-upload.md` for error cases.

Upload real material that should anchor the production (actor likenesses, brand assets, location scouts, product photos, storyboard scans); generate new synthetic imagery. Most productions use both.

## Image Genre Recipes

Different shot types have opposite requirements.

### Scene Image

The general guidance in `pr0ta-prompting` applies: self-contained, specific subject, lighting, and camera, grounded environment.

### Key Frame for Video

A still that will be animated should show the state before the action, not its peak (`pr0ta-prompting` → Technique 6). Generate it at the delivery aspect ratio: several image-to-video routes follow the input image's shape.

### Flash Card (Sub-One-Second Shots)

Flash cards are felt more than read: year drops, name drops, impact beats.

- **Extreme saturation.** One dominant hue per card; vary hue between adjacent cards so the viewer registers color before content.
- **Massive type.** The text fills 50–80% of the frame; if it reads at thumbnail size, it is big enough.
- **Zero background detail.** A solid field or one subtle gradient.
- **One typographic element.** One word, number, or short phrase.
- **Flat, hard lighting.** Flat vector rendering reads faster than realism.

```
A full-frame flash card design. Solid [SINGLE DOMINANT COLOR] background, no other scene elements. Massive centered [TEXT] in a [BOLD SANS-SERIF / CONDENSED DISPLAY] typeface, occupying approximately 60-70% of the frame height, rendered in [CONTRASTING COLOR]. Flat vector style, hard edges, no shadows, no gradient on the type. The single typographic element is the entire image. Poster graphic, not a photograph.
```

Example: a "2027" card in amber-gold (#F5A623) with deep navy numerals, followed by a "2029" card in electric blue (#1E90FF) with cream numerals. The saturation jump does the editorial work at speed. Avoid scene-photography language ("a photograph of the number 2027 on a textured wall"), which produces a scene, not a card.

### Title Card

A title held 1.5–3 seconds is a hybrid: the type dominates, with room for one subtle background element (soft gradient, faint glyph, vignette). A generated still animated with a timeline Ken Burns preset usually beats an overlay text filter for polish.

### Any Still With On-Screen Text

This is a reliability rule. If the still has any rendered text (title, brand, tagline, credit, sign in the scene):

1. **Use the Line-Locked Poster pattern** (`pr0ta-prompting` → Technique 3): `Line N (style): EXACT TEXT` with an `EXACTLY` directive. Prose copy fails often enough to treat as unreliable: duplicated lines, garbled glyphs, softened or paraphrased copy ("CAN'T RUN OUT OF MONEY" became "CAN'T RUN OUT OF FUNDS"), dropped characters.
2. **Check every glyph after generation.** Read the image letter by letter against the intended copy and regenerate on any mismatch.

Brand names, exact-copy titles, and anything a stakeholder will read at full size are worth fanning out.

## Fan-Out and Pick for Hard Shots

For a hard shot (exact text, complex composition, specific mood), submit the same prompt to 3–5 models in parallel and pick the winner. Concurrent image jobs finish in about the time of one, and image calls are inexpensive; one model almost always lands the shot, while sequential retries on one model are slower and less reliable.

Choose the candidates from `models_list(modality="image_model")`: pinned models first, then models whose catalog notes document typography or layout when the copy is critical. Tell the user which models you fanned out to.

```python
candidates = [m["provider_model_id"] for m in models_list(modality="image_model")["models"][:5]]
tasks = {}
for model_id in candidates:
    request = {"generator": "image", "mode": "txt_to_img", "model": model_id,
               "prompt": PROMPT, "aspect_ratio": "9:16"}
    request.update(schema_specific_fields(model_id))  # e.g. quality "max" where the schema offers it
    task = generation_submit(project_id=project_id, request=request)
    if task.get("task_id"):
        tasks[model_id] = task["task_id"]
# Poll all tasks with tasks_get, review each result, and pick by eye.
```

Or send the same list as one `generation_batch_submit` call (up to ten items).

Selection criteria, in order:

1. **Exact text match.** Softened or mutated copy is disqualified regardless of beauty.
2. **Composition and hierarchy.** Hero line dominant, secondary lines clearly subordinate.
3. **Color integrity.** The requested palette is actually present.
4. **Polish.** Clean glyph edges, clean background, correct aspect ratio.

Log every attempt (prompt, model, seed, task id, winner) in `assets.json` (see the `pr0ta` hub → "Local ledger") so a winning combination can be re-rendered consistently.

Video fan-out is not cheap. For video, prefer one well-prompted call (or a verified still animated on the timeline) and fan out only where the creative risk justifies the spend. Skip image fan-out for routine B-roll and background plates.

## Output Resolution and the Timeline

Image models return the size their resolution field selects, not the pixel size an aspect ratio implies. The post-production timeline normalizes every clip to the sequence's delivery resolution when you add it with `POST /timeline/clips`, so stills need no pre-upscaling. Set the sequence once (for example 1080×1920 vertical or 1920×1080 horizontal).

When a still must be delivered at a specific size outside the timeline (a thumbnail export), raise the model's own resolution or size field where it offers one, or run an `image_upscale_model` utility.

## Reliability

Use the `pr0ta-api` reliability contract: poll every task to a terminal state, treat task events as acceleration rather than the only completion signal, and fall back to asset discovery when a task read lags. If an allowed prompt is falsely rejected, preserve the provider error, retry once at the highest policy-compliant `safety_tolerance` where the schema offers it, then choose another model for the same mode from `models_list(modality=...)` and say so. Never switch models to evade a real policy restriction.
