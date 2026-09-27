---
name: pr0ta-prompting
description: "PR0TA prompt writing for image, video, speech, music, 3D world, and humanoid motion generation: self-contained prompts, prompt bibles, reference binding and token syntax per model, camera and lighting language, on-screen text and title cards, key frames for image-to-video, video edit/extend prompts, storyboard prompts, negative-phrasing fixes, anti-patterns, and multi-shot consistency. Read before writing any generation prompt."
---

# Prompting for PR0TA Productions

The visual house principle: **every prompt is completely self-contained.** No assumed context, no pronouns that point at other shots, no "same as before."

## Route by Model and Operation

1. Resolve the model first. `pr0ta-image` and `pr0ta-video` own model resolution (`models_preferred(modality=...)`, then `models_list(modality=...)` when it returns null). Never pick a model from this skill.
2. Resolve the operation: T2I, image edit/reference, T2V, I2V, first/last frame, keyframes, Omni/reference, audio-to-video, video Edit/Extend, motion transfer, image-to-3D, TTS, music. Prompt contracts differ by operation even inside one family.
3. Read the resolved model's row in `reference/model-modality-guides.md`, then its deep reference below. Never transfer tokens or grammar between sibling versions or providers.
4. Take payload fields from `models_get_defaults`; prompt guides describe writing, not the live schema.

| Resolved model family | Deep reference |
|---|---|
| Seedance 2.5 (MuAPI or ModelArk), including Seedance 2.5 Omni Reference, Video Edit, and Video Extend | `pr0ta-video/reference/seedance-2.5.md`; sung performance: `pr0ta-video/reference/seedance-2.5-sync-sound.md` |
| Seedance 2.0 Omni and other 2.0 routes | `pr0ta-video/reference/seedance-omni.md`; storyboard chunks: `pr0ta-video/reference/seedance-global-storyboard.md` |
| Wan 3.0 and Wan 3.0 Prime | `pr0ta-video/reference/wan-3.0.md` |
| MiniMax Hailuo H3, H3 Max, H3 Max Multi-Angle | `pr0ta-video/reference/hailuo-h3.md` |
| FLUX 3 video | `pr0ta-video/reference/flux-3.md` |
| LTX 2.5 | `pr0ta-video/reference/ltx-2.5.md` |
| Kling V3 / O3 video | `pr0ta-video/reference/kling-prompting.md` |
| Gemini Omni Flash 1.1 | `pr0ta-video/reference/gemini-omni-flash-1.1.md` |
| Grok Imagine Video 1.5 | `pr0ta-video/reference/grok-imagine-video-1.5.md` |
| Motion-control / performance transfer | `pr0ta-video/reference/motion-transfer.md` |
| GPT Image 2.5 (Sunburst, Flare) | `reference/gpt-image-25.md` |
| Other image models (Nano Banana, Seedream, Midjourney, Kling Image, Grok Image, Reve), Meshy 3D, TTS, Seed Audio, Lyria | `reference/model-modality-guides.md` |
| Any on-screen text in image or video | `pr0ta-video/reference/generative-typography.md` |

### Reference Syntax Is Per Model

| Family | How references are named in the prompt |
|---|---|
| Seedance 2.0 | Lowercase positional `@image1..9`, `@video1..3`, `@audio1..3`; `@character:<request_id>` and `@omni-character:<char_id>` are different token families |
| Seedance 2.5, Wan 3.0 | Plain-language roles ("the first reference video controls camera pace"); no `@` tokens |
| Kling | `@Image1` is the start image; `@ElementN` for Element bundles; the end image is implicit and never `@Image2` |
| Hailuo H3 / H3 Max | Literal `Image 1`, `Video 1`, `Audio 1`; dialogue as `(S1)` speakers with `<d>[Language] exact text</d>` |
| Gemini Omni Flash 1.1 R2V | Zero-based `<IMAGE_REF_N>` and `<VIDEO_REF_N>` |
| Grok Imagine Video 1.5 R2V | Zero-based `<IMAGE_0>`, `<IMAGE_1>`, … |
| GPT Image 2.5, Nano Banana, Seedream edits | Natural numbered roles: "Image 1 is the identity reference; Image 2 supplies only the set" |
| Reve 2.1 Remix | `<frame>N</frame>` |
| FLUX 3 keyframes | Unique `frame_index` values on a 24 fps timeline, not seconds |

Build the final reference order before writing any positional or ordinal name. Reordering the arrays changes every token.

### Specialized Prompt Workflows

- **Controlled designed-world reference images:** read `reference/designed-world-reference-image.md` (paired flat/depth guidance, department authority, QC, receipts, approval).
- **Net-new character, hero prop, or wardrobe references with no approved image yet:** read `reference/reference-design-bootstrap.md` and use `prompt_profile: "character_reference_design"`, `"prop_reference_design"`, or `"wardrobe_reference_design"`. These return a candidate package for user approval before any generation.
- **World Labs Marble 3D environments:** read `reference/marble-world-generation.md`. Marble is spatial-environment prompting, not shot prompting.
- **Compact Seedance 2.0 Omni storyboard sequences:** call `agent_chat_orchestrate_prompt` with `prompt_profile: "seedance_storyboard_sequence"` and read `pr0ta-video/reference/seedance-global-storyboard.md`. Every production-prompt orchestration consults Stylist and Propmaster from Settings → Agents before Storyboarder; selecting Director, Storyboarder, or Cinematographer as the entry role does not shorten the configured department chain. Contributed department facts are binding prompt authority within the endpoint's prompt budget; Storyboarder owns reference accounting and shot bindings, and Cinematographer renders the provider-ready prompt. Seedance 2.5 omits this profile and uses the generic model-aware path with natural-language reference roles.
- **Speech and dialogue:** `reference/model-modality-guides.md` has each TTS model's prompt order; `pr0ta-audio` owns voices, request fields, and indexing (Gemini TTS: `pr0ta-audio/reference/gemini-tts.md`; ElevenLabs V3 tags: `pr0ta-audio/reference/elevenlabs-v3-audio-tags.md`; Seed Audio: `pr0ta-audio/reference/seed-audio.md`).


## Motion Prompting Is an Exception

Image and video advice does **not** transfer to text-to-motion (`generator=motion`). A motion model emits one skeleton's joint motion, not a rendered world. Use one actor, present tense, **12–20 words**, body geometry only. Omit props, environment, clothing, multiple actors, camera, face, and looping instructions. Start Hunyuan motion at guidance 4–5, vary the seed, and measure joint behavior before visual approval. Read `reference/motion-prompting.md` before writing or reviewing a motion prompt.

## Why Prompting Controls Consistency

Each generation is an isolated call. The model knows nothing about your other shots, your cue sheet, or your story; "the same probe enters the cave" invents a new probe. Self-contained prompts carry description and direction; stored references (Elements, Characters, approved stills) carry visual identity. Both are required.

## Memory Before Prompting

For a real project, call `memory_context_pack` with the `task_intent` and the scene, character, or asset `scope`. Use approved facts, decisions, references, and continuity constraints as source material. Candidate claims are usable but stay marked as candidate in your reasoning. Surface conflicts and open questions before generating. Use `memory_search` for targeted lookups (a wardrobe rule, a location note, a camera preference). After the user accepts a prompt strategy, visual rule, reference, or continuity constraint, record it with `memory_record_decision` or `memory_record_note`.

## Reference Binding Is a Submission Contract

Never write "preserve the approved portrait" or "match the character sheet" unless that exact project asset is attached to the request. Prose does not attach an asset, and the provider cannot resolve a project-internal name.

1. Select the exact approved project asset id; do not infer a file name or substitute a storage URL.
2. Put the image being transformed in `image_asset_id`; put ordered identity or style references in `reference_image_asset_ids`.
3. Bind every attachment in the prompt with that model's syntax (table above) and its final order, for example `Image 1, the attached approved BUG portrait, is the identity reference; preserve its facial structure, freckles, hair, and pale hazel-green eyes.`
4. Put requested geometry in the route's structured fields (`aspect_ratio`, `image_size`, `resolution`) as well as the prose. Never rely on the prompt for dimensions.

If no approved asset is available, say so and generate without claiming reference preservation. A reference mention without its attached asset id is a failed generation contract.

## The Self-Contained Prompt Rule

Test every prompt: **could someone with zero context read it and know exactly what should appear on screen?**

**Bad:** "The same probe enters the nebula. It glows like before."

**Good:** "@Element1 -- a sleek silver cylindrical space probe with blue LED running lights along its fuselage and a rotating antenna array at its nose -- drifts into a dense violet-and-magenta nebula. The probe's LED lights cast faint blue reflections on nearby gas clouds. Camera tracks the probe from a 3/4 rear angle as it penetrates deeper into the swirling gas. Slow, deliberate motion. Volumetric light through gas clouds."

For loose-reference Kling and Seedance 2.0 workflows, restate the critical subject, environment, lighting, and camera anchors instead of "the same person, now smiling." For H3 and Seedance 2.5 I2V, preserve first-frame authority: the frame owns opening appearance and composition, so prompt the motion, camera, atmosphere change, and end state, and repeat only traits that must stay locked. Wan 3.0 I2V follows the same rule, with optional `last_image` guidance defining the landing. Where this rule and an endpoint's I2V rule differ, follow the model reference.

## Named Techniques

### 1. Enumerate Every Frame Value

For countdowns, timers, tickers, scores, progress bars, dates, or any on-screen value that changes, name every state with a timestamp.

**Bad:** "Digital timer counts down from 9 to 1 over 2.5 seconds."

**Good:** "A digital seven-segment timer on a black background. At 0.0s display `00:00:09`. At 0.3s display `00:00:08`. … At 2.4s display `00:00:01`. Numerals are amber-gold, massive, centered, no other elements on screen."

Field case: on an identical-reference countdown, Kling O3 Pro produced `08 → 00 → 09` from "count down from 9", while Seedance 2.0 Omni executed the enumerated version cleanly on the first try.

### 2. Hold the Existing Composition

For minimal-motion shots (a text pulse, a slight push-in, a blink, a flag rippling), append near the end:

> *"Hold the existing composition. Minimal camera movement. Only [specific element] animates."*

> "A man in his 40s in a charcoal suit sits at a cherry-wood desk, warm tungsten key light from camera-right, cool blue fill from the window. Shallow depth of field, 85mm. **Hold the existing composition. Minimal camera movement. Only his eyes blink once and his mouth slightly parts as if about to speak.**"

This sharply reduces scene rewrites, camera drift, and invented motion on reference-to-video, title cards, talking-head B-roll, and "breathing still" shots.

### 3. Line-Locked Poster Prompt (Text-Heavy Stills)

Use this whenever a still needs exact words: title cards, flash cards, quote posters, baked-in lower thirds. It routes around the softening pass that rewrites "provocative" copy and fixes the one-word-wrong failure.

One `EXACTLY` instruction, one line per line of text in `Line N (style): EXACT TEXT` form, and no prose paraphrase of the copy anywhere else:

```
The poster text must read EXACTLY the following, with no other words on the image:
Line 1 (small white caps): MODERN MONETARY THEORY
Line 2 (HUGE bold amber-gold): THE GOVERNMENT
Line 3 (HUGE bold amber-gold): CAN'T RUN OUT
Line 4 (HUGE bold amber-gold): OF MONEY.

Flat vector poster on a deep navy background. Extreme saturation.
Massive sans-serif display type occupying 60-70% of the frame,
centered, tight letter-spacing. No other elements, no icons, no
decorative marks. 9:16 vertical composition.
```

In prose form the same copy came back as "CAN'T RUN OUT OF FUNDS" and "CONTEMPORARY ECONOMIC THEORY": an upstream pass rewrote it. The quoted, line-numbered specification survives that pass.

1. Never describe the copy in prose elsewhere in the prompt.
2. Include `with no other words on the image` to suppress invented sub-headlines, URLs, and filler.
3. Verify every character before moving on; regenerate or edit on any mismatch.
4. Choose animation by required certainty. A video model with documented typography can animate the text natively (quote the copy, describe type, placement, and motion, then inspect every frame). For legal, credit, or brand-critical copy, or after any temporal drift, animate the verified still on the timeline with a hold or Ken Burns preset.

Current image and video models can render strong typography; do not assume older incapability. If one model softens or mutates the copy, fan out and pick (`pr0ta-image`). `pr0ta-video/reference/generative-typography.md` owns the typography QC gate and repair ladder.

### 4. State Motion Positively, Never Negatively

Video models drop negations in prose: "don't destroy the carving" renders the destruction. Describe the desired end state and the motion toward it in positive terms.

**Bad:** "The craftsman polishes the carving. Don't destroy the carving. No cutting motions."

**Good:** "The craftsman runs a soft cloth in slow circular polishing motions over the already-completed carving. The carving's surface remains fully intact throughout; the finished form is preserved from start to end."

| Negation (avoid) | Positive rewrite |
|---|---|
| "don't break the glass" | "the glass remains whole and upright throughout" |
| "the door does not close" | "the door stays open at the same angle throughout" |
| "no cutting / chipping" | "performs [finishing action] on the already-completed surface" |
| "not facing the camera" | "back of head toward camera, facing the horizon line" |
| "doesn't change clothes" | "wearing the same [described garment] throughout the shot" |
| "no extra fingers" | "exactly one thumb and four fingers per hand" (plus a negative prompt where the route has one) |

Keep genuine negatives in a route's `negative_prompt` field, never in the prompt body.

### 5. Self-Contained Reference Shots

Every reference shot names its subjects, action, reference roles, and continuity constraints without "same as before." Restate anchors on loose-reference workflows; on first-frame-authority I2V routes, describe motion, camera, atmosphere, and end state without contradicting the frame.

### 6. Prompt the BEFORE Moment for Image-to-Video Key Frames

A key frame that will be animated should show the state before the action, not its peak. The video model animates forward from whatever the image shows.

- Bad key frame: "A glass of milk falling to the ground, shattering." (The glass hangs frozen mid-air.)
- Good key frame: "A full glass of milk on the edge of a wooden kitchen table, morning light, slightly precarious." Then the video prompt: "The glass gets bumped and falls off the table, shattering on the tile floor, milk splashing outward."
- Bad: "A candle sputtering, smoke wisps." Good: "A tall beeswax candle burning brightly, steady warm flame," and let the video take it to dark.

Shots that express an arc A→B→C need the key frame at A.

### 7. Custom I2V Prompt Per Card

Animated cards, diagrams, posters, quote panels, and transcript-timed social edits each need their own image-to-video prompt:

- Preserve the still's exact typography, layout, colors, and composition.
- Animate only elements relevant to that card's concept.
- State the delivery frame ("vertical 9:16, no crop, no added border").
- Keep text stable unless the card calls for text animation.
- If one card fails, change the prompt or model for that card only.

## Prompt Structure

Write like scene directions to a cinematographer:

**`[Scene/Environment] + [Subject & Appearance] + [Action/Motion] + [Camera Movement] + [Lighting & Atmosphere] + [Technical Style]`**

Model references can reorder this (reference-role ledgers first, audiovisual sections, core summary first); follow the reference when it differs.

1. **Environment first.** Name the location specifically ("a glass-walled corner office on the 40th floor"), include a ground plane, time of day, weather, and architectural terms. Unanchored subjects float.
2. **Subject and appearance.** Name characters ("Sarah", or `@Element1`), list defining features and distinctive marks, and describe props by material and color. Use the exact same words every time.
3. **Action.** Sequential and unambiguous: "First [A], then [B], finally [C]." One clear action per five seconds. Describe physics and body mechanics ("Sarah pivots on her heel and strides toward the door").
4. **Camera.** Precise terms: dolly in/out, truck left/right, tracking, orbit, pan, whip pan, tilt, rack focus, low/high angle, POV/FPV, static wide, slow push-in. Match to the shot: establishing (static wide or slow reveal), dialogue (medium, minimal movement), action (tracking or handheld), emotional beat (slow push-in). Avoid "cinematic camera."
5. **Lighting.** Describe sources, not moods: "single overhead fluorescent tube casting hard shadows," not "dramatic lighting"; "golden hour sunlight through office windows, long warm shadows," not "warm feeling." Backlight, low-key, and hazy light often look most convincing.
6. **Technical style.** End with one project style sentence copied verbatim across prompts: lens ("85mm portrait lens"), stock ("Kodak Portra 400 aesthetic"), grade ("teal and orange"), texture ("subtle film grain").

## The Prompt Bible

Before any multi-shot production, write a prompt bible: the single source of truth for every description.

```
SARAH (Protagonist):
  Physical: tall, athletic build, olive skin, dark brown eyes, shoulder-length black hair with natural wave
  Wardrobe: fitted navy blazer, cream linen shirt, tailored grey trousers
  Distinctive: slight scar above left eyebrow, gold wedding ring
  Element ID: element-uuid-sarah
  Style anchor: "Sarah, a tall athletic woman with olive skin and shoulder-length black hair, wearing a navy blazer over cream linen, gold wedding ring visible"

THE GARDEN STUDY:
  Architecture: Victorian study, 12-foot ceilings, crown molding, east-facing bay windows
  Lighting default: morning light through east windows, warm dappled shadows
  Style anchor: "a Victorian study with crown molding and east-facing bay windows, morning light casting dappled shadows across a mahogany desk and Persian rug"

THE ARTIFACT:
  Style anchor: "an ancient palm-sized bronze compass with jade-green patina and inscribed symbols"

VISUAL STYLE:
  "Cinematic, 35mm Kodak Portra film aesthetic, shallow depth of field, slightly warm grade with cool blue shadows."
```

Copy anchors verbatim into each shot. Do not paraphrase or abbreviate.

For Seedance 2.0 productions the bible can become a visible reference: one approved global visual bible as `@image1` across the production, plus one chronological storyboard sheet per 4–15 second chunk. Name the sheet's real token after the order is final ("@image3 is the chronological storyboard reference sheet for this chunk. It controls panel order, action progression, staging, composition, and final state."). `pr0ta-video/reference/seedance-global-storyboard.md` owns that workflow.

## Anti-Patterns

The three that break consistency most: **(1) assumed context or ambiguous pronouns**; **(2) negations in prose** (Technique 4); **(3) shifting descriptors** instead of bible anchors. Read `reference/anti-patterns.md` for the full list with examples.

## Shot Templates

- **Establishing:** `[Wide/Aerial] of [LOCATION + architecture]. [Time of day] light. [Atmosphere]. [Camera: static wide / slow pan / drone descent]. No characters visible.`
- **Dialogue:** `[Medium shot] of [CHARACTER, full appearance] in [LOCATION]. [Action with body mechanics]. [Lighting matching location]. Camera: [subtle movement or static].`
- **Close-up:** `[Close-up] of [detail]. [CHARACTER/OBJECT, key features]. [Minimal background]. [Light on subject]. Shallow depth of field.`
- **Action:** `[Shot type] of [CHARACTER, appearance] in [LOCATION]. First A, then B, finally C. [Physics]. Camera: [tracking / handheld].`

## Workflow

1. Write the prompt bible; copy its anchors into each shot.
2. Resolve the model and operation, read its reference, and write in its structure and syntax.
3. Check self-containment, chronology, reference roles and bindings, consistent descriptors, and positive end states.
4. Remove ambiguity, redundant references, unsupported fields, conflicting camera or action instructions, and filler.
