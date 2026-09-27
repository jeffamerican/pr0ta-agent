# Provider Consistency Systems

Read this when creating, registering, using, or troubleshooting provider consistency resources. `SKILL.md` holds the rules and the order of work; this file holds the lifecycle details and payload shapes. Every example resolves its generation model with `models_preferred` (or `models_list` when it returns null); none of them chooses a model.

## Contents

- Kling Elements
- Seedance 2.0 Characters
- Seedance Omni multi-modal references
- Multi-prompt and multi-shot generation
- Camera control
- Reference pipeline
- Image edit for consistency correction

## Kling Elements

### What an Element Is

An Element is a reference bundle for one subject: a character, prop, location, or object.

- **One frontal (hero) image**: the clearest, front-facing view. It tells the model "this is the subject."
- **One to three more images**: other angles, poses, or views of the same subject, which improve consistency when the subject turns or moves.

Good bundles: a character's front, profile, three-quarter, and back views; a prop's hero, side, and detail views; a location's establishing wide plus key detail angles. Every image in an Element shows the **same** subject; make a separate Element for each distinct subject, era, or wardrobe. Build the bundle from the approved Prep references (casting portraits and sheets, looks, props, set plates) and generate only the missing angles.

### Creating an Element

An Element is created on Kling, then registered in the project.

1. **Create it on Kling** from the approved images.
   `POST /api/kling/elements` with the project and the images. PR0TA resolves project asset URLs to provider-readable ones:

   ```json
   {
     "project_id": "project-uuid",
     "reference_type": "image_refer",
     "element_name": "Sarah",
     "element_image_list": {
       "frontal_image": "<approved front asset URL>",
       "refer_images": [{ "image_url": "<approved profile asset URL>" }]
     }
   }
   ```

   The response carries a task ID; poll `GET /api/kling/elements/tasks/{task_id}` until it returns the `element_id`. `GET /api/kling/elements?project_id=` lists the project's Elements. A video Element uses `reference_type: "video_refer"` with `element_video_list.refer_videos[]`.
2. **Register it in the project**:

   ```json
   consistency_resources_create({
     "resource_type": "element",
     "resource": {
       "name": "Sarah",
       "provider": "kling",
       "provider_resource_id": "<element_id from Kling>",
       "reference_asset_ids": ["uuid-frontal", "uuid-profile", "uuid-three-quarter"],
       "labels": { "character_name": "Sarah" }
     }
   })
   ```

   REST: `POST /api/v2/projects/{project_id}/elements` with the same body. The character bundle finds an Element by its labels or name matching the character, or by shared reference assets.

### Using Elements in Generation

Pass stored Elements by project ID or provider ID in `element_ids[]` on a Kling route that accepts Elements:

```json
{
  "generator": "video",
  "mode": "ref_to_vid",
  "model": "<model_id from models_preferred(modality: \"reference_to_video_model\")>",
  "prompt": "@Element1 walks into the room and looks around nervously...",
  "start_image_asset_id": "uuid-scene-frame",
  "element_ids": ["element-uuid-sarah", "element-uuid-desk-prop"],
  "duration": 10
}
```

Check the resolved model's `models_get_defaults` `supported_modes` and fields first; not every route accepts Elements. For a one-off bundle without a stored Element, pass inline Elements:

```json
"elements": [
  { "frontal_asset_id": "uuid-frontal", "additional_asset_ids": ["uuid-profile", "uuid-three-quarter"] }
]
```

**Prompt tokens:** `@Element1` is the first Element, `@Element2` the second; `@Image1` is the start image. Never refer to subjects by pronoun; use the token or a fixed label.

### Element Practice

1. Build the recurring character, prop, and location Elements before video generation.
2. Reuse the same Elements for every shot of that subject.
3. Four references per character (front, profile, three-quarter, back) is the strong case.
4. Upload real references (actor headshots, product photos, scouts) when they exist.
5. Generate four to six takes of any missing reference and keep the strongest; the references set the ceiling for the production.

## Seedance 2.0 Characters

### What a Seedance Character Is

Seedance 2.0 Omni holds a character's identity through a trained Omni token. Train it from:

- **one clean frontal portrait**, the identity anchor; or
- **a character sheet or up to three approved stills**: front, back, profile, an action pose, and expressions, with an outfit description.

A character sheet gives the model the full appearance in one image: several angles and expressions laid out as a professional reference sheet. Strong sheets render every panel clearly, keep the appearance identical across angles, show distinctive features, use a neutral background, and cover front, back, profile, and at least one expressive pose. Start from the approved Prep sheet (`cast_list_get`); if none exists, build the brief with `casting_character_sheet_prompt_resolve`, generate with `models_preferred(modality: "image_model")`, fan out four to six takes, and have the user approve one.

Never mix hairstyles, outfits, makeup, or ages in one training set. Providers average ambiguous references and every downstream shot drifts. One identity, one era or look, one wardrobe concept per Character.

### Training the Token

Training runs through unified generation (`generation_submit`, REST `POST /api/v2/projects/{project_id}/generate`) on one of two Seedance character training routes:

| You have | Route | Required inputs |
|---|---|---|
| One clean frontal portrait | `muapi/seedance-2-omni-reference-train` | `image_url` or `image_asset_id`, `character_name`; optional `description` |
| A character sheet or 1–3 approved stills | `muapi/seedance-2-character` | `images_list[]` (up to three), `character_name`, `outfit_description` |

Single portrait:

```json
{
  "generator": "video",
  "mode": "ref_to_vid",
  "model": "muapi/seedance-2-omni-reference-train",
  "image_asset_id": "uuid-approved-portrait",
  "character_name": "Maya",
  "description": "Female lead, black leather jacket, studio portrait, neutral expression"
}
```

Character sheet or stills:

```json
{
  "generator": "video",
  "mode": "ref_to_vid",
  "model": "muapi/seedance-2-character",
  "prompt": "Create a reusable character profile for later Seedance Omni Reference shots.",
  "images_list": ["<approved sheet URL>", "<approved profile URL>", "<approved close-up URL>"],
  "character_name": "Maya",
  "outfit_description": "Black leather jacket, white tee, dark jeans"
}
```

Poll with `tasks_get` until `succeeded`. The task's `result_refs` carry the Omni token as `character_id` (the `result` media envelope does not), the character name, any sheet assets, and `project_character_id`: PR0TA has already stored the Character for the project. Add the approved Prep reference asset IDs to it with `consistency_resources_update(resource_type: "character", resource_id, updates: {reference_asset_ids})` and tag the source portrait or sheet as a `character_reference` so the bundle finds it.

A token trained outside PR0TA is registered with `consistency_resources_create(resource_type: "character", resource: {name, provider: "muapi", provider_resource_id: "<token>", reference_asset_ids})` (REST `POST /api/v2/projects/{project_id}/characters`). Characters support only `provider: "muapi"`, and one token registers once per project.

### Using Characters in Generation

```json
{
  "generator": "video",
  "mode": "ref_to_vid",
  "model": "<model_id of a Seedance 2.0 Omni route>",
  "prompt": "@omni-character:<token> walks through a bustling Tokyo market at golden hour. Camera tracks from behind.",
  "character_ids": ["project-character-uuid-maya"],
  "reference_image_urls": ["https://example.com/scene-ref.png"],
  "duration": 10
}
```

`character_ids[]` accepts the project Character ID or its token. A request carries at most three, and each must appear in the prompt as `@omni-character:<token>`; the bundle's `provider_payloads.seedance.prompt_tokens` gives the exact tokens. Test a take before relying on more than one lock in a shot. Seedance 2.0 Omni is the only route with trained character tokens (`pr0ta-video`); on other routes, pass the approved references as images.

## Seedance Omni Multi-Modal References

Seedance 2.0 Omni is quad-modal: text plus up to 9 images, 3 videos, and 3 audio files.

| Reference | Max | What the model takes from it | Use for |
|---|---|---|---|
| Images (`@image1`–`@image9`) | 9 | Features, composition, lighting, palette, pose, environment | Identity, composition, style, location |
| Videos (`@video1`–`@video3`) | 3 | Camera path, movement speed, pacing, choreography | Camera trajectory, motion style, pacing |
| Audio (`@audio1`–`@audio3`) | 3 | Rhythm, content, mood, timing cues | Music-synced motion and speech guidance; verify sync per take |

Typed references:

```json
{
  "references": [
    { "type": "image", "image_url": "https://example.com/hero.png" },
    { "type": "image", "image_url": "https://example.com/style-ref.png" },
    { "type": "video", "video_url": "https://example.com/camera-motion.mov" },
    { "type": "audio", "audio_url": "https://example.com/rhythm-track.wav" }
  ],
  "reference_image_urls": ["https://example.com/hero.png", "https://example.com/style-ref.png"],
  "reference_video_urls": ["https://example.com/camera-motion.mov"],
  "reference_audio_urls": ["https://example.com/rhythm-track.wav"]
}
```

Give every reference one job and name it in the prompt: "Match @image1 as the character, shoot in the style of @image2, use the @video1 camera movement, sync to the @audio1 beat." `pr0ta-video` → `reference/seedance-omni.md` owns the full Omni contract.

## Multi-Prompt and Multi-Shot Generation

Kling and Seedance routes with multi-prompt generate several timed shots in one video, which holds consistency across all of them.

```json
{
  "generator": "video",
  "mode": "ref_to_vid",
  "model": "<model_id from models_preferred>",
  "prompt": "Hero navigates the warehouse",
  "prompt_mode": "multi_prompt",
  "multi_prompt": [
    { "prompt": "Hero steps cautiously into a dark warehouse. Camera follows from behind." },
    { "prompt": "Hero spots something across the room. Camera pushes in on their face." },
    { "prompt": "Hero turns and exits into fog. Camera holds as they disappear." }
  ],
  "element_ids": ["element-uuid-hero"],
  "duration": 15
}
```

`prompt_mode: "multi_prompt"` activates it; `multi_prompt` is an array of segments; Elements apply to every segment. The segment limit is per route; read it from `models_get_defaults` or the model's reference in `pr0ta-video`.

Use multi-prompt when the shots share a scene, consistency inside the sequence matters, the camera flows between them, and the total fits one generation. Use separate generations for different locations, different characters per shot, sequences longer than the route's maximum, or shots that need independent control.

## Camera Control

Kling routes that accept it take structured camera movement instead of prompt text alone:

```json
{ "camera_control": { "type": "simple", "config": { "horizontal": 5 } } }
```

Combine it with multi-prompt for choreographed shots.

## Reference Pipeline

For productions that need high consistency, before any shot generation:

1. **Characters**: approved Prep portraits and sheets; generate only missing angles (`image_model` or `image_edit_model`), four to six takes each.
2. **Locations and sets**: approved Prep set plates; generate missing establishing and detail views.
3. **Props**: approved Prep prop references; generate clean multi-angle views where missing.
4. **Label and build**: tag approved references (`character_reference` and so on), then create every Element and Character before video.
5. **Key frames**: compose scene key frames from the Element or reference bundles (`elements_to_image_model`) so the right characters and props appear in the right places.
6. **Video**: pass the bundle's `element_ids[]` or `character_ids[]` on every generation of that subject.

Final shot with a key frame and Elements:

```json
{
  "generator": "video",
  "mode": "ref_to_vid",
  "model": "<model_id from models_preferred(modality: \"reference_to_video_model\")>",
  "prompt": "@Image1 -- @Element1 enters frame from the left...",
  "start_image_asset_id": "uuid-keyframe-scene-1",
  "element_ids": ["element-uuid-sarah", "element-uuid-briefcase"],
  "duration": 10
}
```

## Image Edit for Consistency Correction

When a key frame almost matches but drifts (hair, jacket, prop), correct it with an image edit before generating video:

```json
{
  "generator": "image",
  "mode": "img_to_img",
  "model": "<model_id from models_preferred(modality: \"image_edit_model\")>",
  "prompt": "Keep the composition and pose; match the character's appearance to the reference exactly: same hair color, same jacket.",
  "image_asset_id": "uuid-generated-frame-with-issues",
  "reference_image_asset_ids": ["uuid-character-reference"],
  "element_ids": ["element-uuid-character"]
}
```

Include `element_ids` only when the resolved edit model accepts Elements. Use corrections for appearance drift in key frames, matching lighting or style to the production look, and fixing props or wardrobe.
