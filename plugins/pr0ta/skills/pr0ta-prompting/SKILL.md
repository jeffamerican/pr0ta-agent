---
name: pr0ta-prompting
description: "PR0TA prompting guide and router for image, video, speech, audio, music, and humanoid motion prompts; model-and-modality techniques; prompt bibles; controlled references; anti-patterns; and multi-shot consistency. Read before writing generation prompts."
---

# Prompting Guide for PR0TA Productions

This skill routes and explains effective generation prompts across PR0TA media models. The visual house principle is: **every prompt must be completely self-contained** -- no assumed context, no pronouns referencing other shots, no "same as before."

## Required Model and Modality Routing

Before writing a prompt for Seedance 2.0/2.5, Wan 3.0/Prime, Hailuo H3, FLUX 3, LTX 2.5, GPT-Image-02, Grok Imagine Image 2.0, Nano Banana Pro/2, Seedream 5, Midjourney, Kling O3/V3, Meshy v7, Gemini Omni, ElevenLabs V3, Gemini TTS, Seed Audio 1.0, or Lyria, read `reference/model-modality-guides.md`.

Resolve the exact `model_id` and active operation first. T2V, I2V, audio-to-video, first/last, Omni/reference, video Edit/Extend, image generation/editing, image-to-3D, TTS, audio-reference, and music routes have different prompt contracts even within one family. Never transfer tokens or grammar between sibling versions. Use current endpoint discovery for payload fields.

> **Humanoid motion is the exception to this visual house style.** A text-to-motion model emits one skeleton's joint motion, not a rendered world. Read "Motion Prompting Is an Exception" below before using `generator=motion`.

> **For TTS and dialogue prompting**, see `pr0ta-audio` → "Gemini Flash TTS Prompting" first. Use ElevenLabs v3 audio tags only for fallback or legacy ElevenLabs workflows.

> **For controlled designed-world reference-to-image prompts**, read `reference/designed-world-reference-image.md` before selecting references or constructing the prompt. It defines the preferred paired flat/depth guidance package, backward-compatible semantic/appearance path, department authority, five-section, QC, receipt, and approval contracts.

> **For net-new character, hero-prop, or wardrobe references**, read `reference/reference-design-bootstrap.md` and use the matching `character_reference_design`, `prop_reference_design`, or `wardrobe_reference_design` profile. These profiles accept zero existing references, enforce the department-correct chain, and return a candidate package for user approval before generation.

> **For World Labs Marble persistent 3D environments**, read `reference/marble-world-generation.md` before choosing text, single-image, multi-image, panorama, video, or depth-panorama input or writing a location prompt. Marble prompting is spatial-environment prompting, not shot prompting.

> **For compact Seedance 2.0 Omni storyboard sequences**, use `agent_chat_orchestrate_prompt` with `prompt_profile: "seedance_storyboard_sequence"` and read `pr0ta-video/reference/seedance-global-storyboard.md`. Every production-prompt orchestration consults Stylist and Propmaster from Settings → Agents before Storyboarder; selecting Director, Storyboarder, or Cinematographer as the generic entry role does not shorten the configured department chain. Each specialist returns typed department facts or `not_applicable`. Contributed specialist facts are mandatory Storyboarder and terminal prompt authority and must fit the selected endpoint's published budget. Storyboarder owns complete reference accounting and shot bindings, and Cinematographer alone renders the provider-ready prompt. Seedance 2.5 uses the generic model-aware video contract instead: omit the 2.0 profile, keep the default department chain, preserve Director structure through the Storyboarder's typed shot receipt, and use natural-language reference roles.

## Motion Prompting Is an Exception

Image and video prompting advice does **not** transfer to text-to-motion. Use one actor, present tense, **12–20 words**, and body geometry only. Omit props, environment, clothing, multiple actors, camera, face, and looping instructions. For Hunyuan, start at guidance 4–5, vary the seed, and measure joint behavior before visual approval.

Before writing or reviewing any motion prompt, read `reference/motion-prompting.md`. It owns the full reframing rule, unsupported-content list, bad/good examples, seed strategy, and numerical verification contract.

## Why Prompting Matters for Consistency

Each PR0TA generation (image or video) is an isolated API call. The model has zero knowledge of your other shots, your cue sheet, or your story. If Shot 3's prompt says "the same probe enters the cave," the model doesn't know what "the same probe" looks like or what "the cave" refers to. It will invent something new.

Self-contained prompts + stored reference images (Elements/Characters) are how you control consistency. The prompt handles description and direction; the references handle visual identity. Both are required. Neither alone is sufficient.

## Memory Before Prompting

Before writing prompts for a real project, call `memory_context_pack` with the active role, task intent, and scene/character/asset scope when available. Use approved facts, decisions, references, and continuity constraints as source material for the prompt. Candidate claims are usable, but keep them marked as candidate in your reasoning and do not present them as approved facts. If the pack includes conflicts or open questions, surface them before generating.

Use `memory_search` for targeted lookups such as a character's wardrobe rule, a location note, a director's camera preference, or an executive constraint. After the user accepts a prompt strategy, visual rule, selected reference, or continuity constraint, record it with `memory_record_decision` or `memory_record_note` so later agents inherit it.

## Reference Binding Is a Submission Contract

Never write an internal statement such as “preserve the approved portrait” or “match the character sheet” unless the exact project asset is attached to the generation request. Prompt prose does not attach an asset and the provider cannot resolve a project-internal name.

For every identity, style, location, prop, or composition reference:

1. Select the exact approved project asset ID; do not infer a file name or substitute a storage URL.
2. Put the edit base in `image_asset_id` when it is the image being transformed. Put additional ordered identity/style references in `reference_image_asset_ids`.
3. Bind every attached image in the provider prompt using that model's documented syntax and its final one-based order. For GPT Image 2 Edit, use natural role language such as `Image 1, the attached approved BUG portrait, is the identity reference; preserve its facial structure, freckles, hair, and pale hazel-green eyes.` For Seedance 2.0, use its literal positional `@image1` syntax. Do not transfer a token grammar to a model that does not support it.
4. Submit requested geometry as structured fields as well: for 9:16 GPT Image 2 Edit, set `aspect_ratio: "9:16"` and `image_size: "portrait_16_9"` (or explicit vertical dimensions). Never rely on prompt prose for dimensions.

If no exact approved asset is available, say so and generate without claiming reference preservation. A reference mention without its attached asset ID is a failed generation contract, not a harmless prompt omission.

## The Self-Contained Prompt Rule

Every prompt you write for a generation must pass this test: **Could someone with zero context about your project read this prompt and understand exactly what should appear on screen?**

**Bad (assumes context from other shots):**
> "The same probe enters the nebula. It glows like before."

**Good (fully self-contained):**
> "@Element1 -- a sleek silver cylindrical space probe with blue LED running lights along its fuselage and a rotating antenna array at its nose -- drifts into a dense violet-and-magenta nebula. The probe's LED lights cast faint blue reflections on nearby gas clouds. Camera tracks the probe from a 3/4 rear angle as it penetrates deeper into the swirling gas. Slow, deliberate motion. Deep space ambience, volumetric lighting through gas clouds, 4K cinematic."

The second prompt names everything, describes everything, and assumes nothing.

**Field-tested on loose-reference Kling and Seedance 2.0 workflows:** Restate the critical subject, environment, lighting, and camera anchors instead of saying *"the same person, now smiling."* H3 and Seedance 2.5 I2V are different: their first frame owns opening appearance and composition, so prompt the motion/evolution and repeat only traits that must remain locked. Wan 3.0 I2V follows the same first-frame-authority rule. Follow the exact model reference whenever this general self-containment rule and an endpoint-specific I2V rule differ.

## Named Techniques (Field-Tested)

Two specific phrases and one pattern have been repeatedly confirmed to shift model behavior on Kling and Seedance. Memorize them.

### Technique 1: Enumerate Every Frame Value

**For countdowns, timers, tickers, score displays, or any shot where exact on-screen values must change over time, name every state with an explicit timestamp.**

**Bad (ambiguous — model will hallucinate intermediate frames):**
> "Digital timer counts down from 9 to 1 over 2.5 seconds."

**Good (one line per state — Seedance will honor this):**
> "A digital seven-segment timer on a black background. At 0.0s display `00:00:09`. At 0.3s display `00:00:08`. At 0.6s display `00:00:07`. At 0.9s display `00:00:06`. At 1.2s display `00:00:05`. At 1.5s display `00:00:04`. At 1.8s display `00:00:03`. At 2.1s display `00:00:02`. At 2.4s display `00:00:01`. Numerals are amber-gold, massive, centered, no other elements on screen."

Field case: Kling O3 Pro produced `08 → 00 → 09` on an identical-reference countdown because the prompt said "count down from 9". Seedance 2.0 Omni executed the enumerated version cleanly first try. **Always prefer Seedance for enumerated-state shots** (see `pr0ta-video` decision table).

Applies to: countdown timers, score tickers, stock tickers, UI state transitions, date changes, progress bars, dice rolls, any on-screen text/number that must move through specific values.

### Technique 2: Hold the Existing Composition

**For shots where you want minimal motion — a text pulse, slight push-in, eyes blinking, a flag rippling — explicitly instruct the model to lock the composition.**

The magic phrase, append verbatim near the end of the prompt:

> *"Hold the existing composition. Minimal camera movement. Only [specific element] animates."*

**Example:**

> "A man in his 40s in a charcoal suit sits at a cherry-wood desk, warm tungsten key light from camera-right, cool blue fill from the window. Shallow depth of field, 85mm. **Hold the existing composition. Minimal camera movement. Only his eyes blink once and his mouth slightly parts as if about to speak.**"

Dramatically reduces unwanted scene rewrites, camera drifts, and hallucinated motion on Kling reference-to-video. Particularly valuable for title cards, talking-head B-roll, and "breathing still" shots where the rest of the frame must remain stable.

### Technique 3: Line-Locked Poster Prompt (Text-Heavy Stills)

**Use this pattern any time a still needs exact on-screen words — title cards, flash cards, quote posters, lower-thirds baked into images.** It routes around the safety/softening pass that rewrites "provocative" phrases into blander substitutes and fixes the "almost right but one word wrong" failure mode.

**The pattern:** one `EXACTLY` instruction, one line per line of text, with `Line N (style): EXACT TEXT` formatting. No prose paraphrase of the copy anywhere else in the prompt.

**Template:**

```
The poster text must read EXACTLY the following, with no other words on the image:
Line 1 ([style]): [EXACT TEXT LINE 1]
Line 2 ([style]): [EXACT TEXT LINE 2]
Line 3 ([style]): [EXACT TEXT LINE 3]
...
[Environment / background / composition description here, with NO additional text on the image.]
```

**Worked example (field-tested, Nano Banana 2, 9:16 title card):**

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

**Why this works, and why prose fails.** Field-observed failure modes on the same copy in prose form:

- `"The government can't run out of money"` → rendered as `"CAN'T RUN OUT OF FUNDS"` (softening)
- `"Modern Monetary Theory"` → rendered as `"CONTEMPORARY ECONOMIC THEORY"` (euphemism)

Both look like model hallucination, but the root cause is an upstream softening pass that rewrites copy it considers provocative. The `EXACTLY` + line-numbered format bypasses that pass because the text is structured as a quoted specification rather than a prose paraphrase.

**Rules when using this pattern:**

1. **Never describe the copy in prose elsewhere in the prompt.** If you say "a poster about public finance that reads..." the model may re-paraphrase from the prose description instead of the quoted lines.
2. **Include `with no other words on the image`** — this suppresses hallucinated sub-headlines, URLs, and "lorem ipsum"-style filler text.
3. **Verify pixel-perfect before moving on.** If any character is wrong, regenerate or edit the still. Do not accept attractive typography with incorrect copy.
4. **Choose animation by required certainty.** A premium video model with verified typography capability may generate or animate the text natively; specify the literal copy, typography, placement, and motion, then inspect every frame. For legal, credit, or brand-critical copy—or after any temporal text drift—animate the verified still deterministically on the timeline with a hold or Ken Burns preset.

Current premium image families can produce strong typography; use the exact PR0TA model catalog rather than assuming older models are incapable. For motion typography, FLUX 3, Wan 3.0, Seedance 2.0, Seedance 2.5, and MiniMax H3 are current candidates; select the exact route by the shot's reference, duration, edit, audio, and design needs, then apply frame-by-frame QC. If one model softens or mutates the copy, fan out and pick rather than falling back to a categorical ban on generative text.

### Technique 4: Frame Motion and State Positively, Never Negatively

**Video models silently drop negations embedded in prose prompts.** `"Don't destroy the carving"`, `"the gate does not close"`, `"no cutting motion"` — the model reads past the `don't` / `no` / `does not` and renders the thing you forbade. This is not a Kling quirk or a Seedance quirk; it is how current video models process prompts.

**The rule:** describe the desired *end state* and the *motion toward it* in positive terms only. If you catch yourself writing a negation, rewrite it as a positive assertion.

**Bad (negation — model renders the forbidden action):**
> "The craftsman polishes the carving. Don't destroy the carving. No cutting motions."

**Good (positive assertion of the preserved state):**
> "The craftsman runs a soft cloth in slow circular polishing motions over the already-completed carving. The carving's surface remains fully intact throughout; the finished form is preserved from start to end."

**Translation table for common cases:**

| Negation (avoid) | Positive rewrite (use) |
|---|---|
| "don't break the glass" | "the glass remains whole and upright throughout" |
| "the door does not close" | "the door stays open at the same angle throughout" |
| "no cutting / chipping / damaging" | "performs [finishing action] on the already-completed surface" |
| "not facing the camera" | "back of head toward camera; fronts facing the horizon line" |
| "doesn't change clothes" | "wearing the same [described garment] throughout the shot" |
| "no extra fingers" | "exactly one thumb and four fingers per hand, five digits total" (use alongside a negative prompt; positive framing is the stronger signal) |

**Field-tested** across Seedance 2.0 Omni and Kling V3/O3. The positive form works on the first try in cases where every negation variant failed repeatedly.

### Technique 5: Self-Contained Prompts on Every Reference Shot

Every reference shot must name its subjects, intended action, reference roles, and continuity constraints without relying on phrases such as "same as before." For loose-reference Kling and Seedance 2.0 workflows, restate the key visual anchors. For H3 and Seedance 2.5 I2V, preserve first-frame authority: describe motion, camera, atmosphere changes, and the end state without contradicting or needlessly reconstructing the supplied frame. Wan 3.0 I2V follows the same rule, with optional `last_image` guidance defining the terminal target.

### Technique 6: Prompt the BEFORE Moment for Image-to-Video

**When generating a key frame (still image) that will be animated via image-to-video, prompt the state BEFORE the action, not the action itself.**

The natural tendency is to prompt the storyboard moment — the peak of the action. This works for storyboards but fails for i2v. The reason: the video model will start from whatever the image shows and then animate forward. If the image already shows the peak action, the video either shows the action floating (already mid-event) or awkwardly continues past the interesting moment.

**Bad — prompts the action itself:**
> "A glass of milk falling to the ground, shattering, milk splashing everywhere"
→ Result: a glass frozen mid-air, then hitting the ground. Looks wrong.

**Good — prompts the BEFORE state:**
> "A full glass of milk sitting on the edge of a wooden kitchen table, morning light, slightly precarious position"
→ Then the video prompt says: "The glass gets bumped and falls off the table, shattering on the tile floor, milk splashing outward."

**Another example — a candle going out:**
- Bad key frame: "A candle sputtering, smoke wisps, dim light" → video starts with it already dying
- Good key frame: "A tall beeswax candle burning brightly, steady warm flame, wax dripping down the side" → video shows it flickering, sputtering, and going dark

**The principle:** shots that express a transformation or arc (A→B→C) require the key frame to show state A. Prompt the beginning, then let the video prompt describe the journey to B and C. This is counterintuitive — your instinct is to visualize the dramatic moment, but for i2v you need the setup, not the payoff.

### Technique 7: Custom I2V Prompt Per Card

For animated cards, diagrams, posters, quote panels, and transcript-timed social edits, every card needs its own image-to-video prompt. Do not reuse one generic "animate this card" prompt across the batch.

Required ingredients:
- Preserve exact typography, layout, colors, and composition from the still frame.
- Describe the specific concept depicted on that card and animate only relevant elements.
- Keep the delivery frame explicit, such as "vertical 9:16, no crop, no added border."
- Keep text stable unless the card intentionally calls for text animation.
- If one card fails, change model or prompt for that card only; do not globally pivot the batch.

## Prompt Structure Formula

Write prompts like scene directions to a cinematographer. Follow this master structure:

**`[Scene/Environment] + [Subject & Appearance] + [Action/Motion] + [Camera Movement] + [Lighting & Atmosphere] + [Technical Style]`**

### 1. Scene/Environment (Ground the Space)

Always start with the environment. This gives the model spatial and lighting context before introducing motion. Without spatial anchoring, subjects float in ambiguous space -- a telltale AI artifact.

- Name the location specifically: "a glass-walled corner office on the 40th floor" not "an office"
- Include ground plane references: floors, surfaces, terrain
- Specify time of day and weather if relevant
- Use architectural terms: "Art Deco lobby," "Brutalist concrete corridor," "Victorian conservatory"

### 2. Subject & Appearance (Anchor Identity)

Every time a character, prop, or object appears, describe it fully. Use proper nouns as stability anchors.

**Characters:**
- Name them: "Sarah" not "the woman" or "she"
- List defining features: "Sarah, a tall woman with olive skin, shoulder-length black hair with a natural wave, wearing a fitted navy blazer over a cream linen shirt"
- Include distinctive marks: "slight scar above left eyebrow," "gold wedding ring on left hand"
- Never use pronouns when referring to characters -- always use their name or label (`@Element1`)

**Props:**
- Be specific about materials and colors: "a matte black leather briefcase with brass latches" not "a briefcase"
- Name recurring props consistently -- use the exact same words every time

**Locations:**
- Name them: "The Garden Study" not just "the room"
- Lock architectural elements: "mahogany bookshelves, Persian rug with geometric pattern, tall east-facing windows"

### 3. Action/Motion (Choreograph Clearly)

Describe what happens in sequential, unambiguous terms.

- Use timeline language: "First [A], then [B], finally [C]"
- One clear action per 5-second segment
- Describe physics when relevant: "the tires smoke as the car drifts 90 degrees" not "car turns"
- For character motion, specify body mechanics: "Sarah pivots on her heel and strides toward the door" not "she turns and walks away"

### 4. Camera Movement (Direct the Lens)

Specify camera behavior precisely. Both Kling and Seedance respond well to professional cinematography terms.

**Reliable camera terms:**
- **Dolly in/out** -- smooth forward/backward on rails
- **Truck left/right** -- lateral camera movement
- **Tracking shot** -- camera follows the subject
- **Orbit** -- camera circles subject
- **Pan** / **Whip pan** -- horizontal rotation
- **Tilt up/down** -- vertical rotation
- **Rack focus** -- shift focus between foreground/background
- **Low-angle / high-angle** -- perspective
- **POV / FPV** -- point-of-view
- **Static wide shot** -- camera doesn't move
- **Slow push-in** -- subtle forward creep

**Match camera to shot type:**
- Establishing shot: static wide or slow pan to reveal
- Dialogue: medium shot, minimal movement
- Action: tracking or handheld
- Emotional beat: slow push-in to close-up
- Transition: dolly or crane

**Avoid:** Vague camera language like "move camera around" or "cinematic camera." Say exactly how the camera behaves over time.

### 5. Lighting & Atmosphere (Paint with Light)

Use specific light source descriptions, not abstract mood words.

**Instead of abstract mood words, describe the actual light:**

| Abstract (avoid) | Specific (use) |
|-------------------|----------------|
| "dramatic lighting" | "single overhead fluorescent tube casting hard shadows" |
| "moody atmosphere" | "fog at ground level, harsh overhead light cutting through" |
| "warm feeling" | "golden hour sunlight through office windows, long warm shadows" |
| "dark and mysterious" | "single blue LED panel from below, deep shadows on upper face" |

**Time-of-day lighting:**
- Golden hour: warm directional light, long shadows, orange tones
- Blue hour: cool twilight, soft and diffuse
- Harsh midday: contrasty, bright, short shadows
- Overcast: soft and even, no harsh shadows

**Pro tip:** AI excels at backlighting, low-key scenes, and hazy atmospheric light. These often look more convincing than perfectly lit scenes.

### 6. Technical Style (Lock the Look)

End every prompt with consistent style anchors. Use the same style sentence across all prompts in a project:

> "Cinematic lighting, 35mm film grain, shallow depth of field, slightly desaturated with cool blue shadows, high production value."

This creates visual continuity even when scenes change. Pin these details in your prompt bible and copy them verbatim.

**Effective style anchors include:**
- Lens reference: "85mm portrait lens," "wide-angle 24mm"
- Film stock: "Kodak Portra 400 aesthetic," "Fuji Velvia saturation"
- Color grade: "teal and orange color grade," "desaturated noir palette"
- Texture: "subtle film grain," "clean digital," "anamorphic lens flares"

## The Prompt Bible

For any multi-shot production, create a **prompt bible** before writing any prompts. This is your single source of truth for all visual descriptions.

### What Goes in the Prompt Bible

**Characters:**
```
SARAH (Protagonist):
  Physical: tall, athletic build, olive skin, dark brown eyes, shoulder-length black
  hair with natural wave
  Wardrobe: fitted navy blazer, cream linen shirt, tailored grey trousers, brown
  leather belt
  Distinctive: slight scar above left eyebrow, gold wedding ring, minimal jewelry
  Element ID: element-uuid-sarah
  Style anchor: "Sarah, a tall athletic woman with olive skin and shoulder-length
  black hair, wearing a navy blazer over cream linen, gold wedding ring visible"
```

**Locations:**
```
THE GARDEN STUDY:
  Architecture: Victorian study with 12-foot ceilings, crown molding, east-facing
  bay windows
  Furnishings: mahogany desk, leather wingback chair, Persian rug (geometric
  pattern, deep red and navy), floor-to-ceiling bookshelves
  Lighting default: morning light through east windows, warm dappled shadows through
  glass panes
  Palette: warm earth tones (ochre, taupe, deep green, leather brown)
  Style anchor: "a Victorian study with crown molding and east-facing bay windows,
  morning light casting dappled shadows across a mahogany desk and Persian rug"
```

**Props:**
```
THE ARTIFACT:
  Description: ancient bronze compass, palm-sized, with jade-green patina and
  inscribed symbols on the outer ring
  Style anchor: "an ancient palm-sized bronze compass with jade-green patina and
  inscribed symbols"
```

**Global style:**
```
VISUAL STYLE:
  "Cinematic, 35mm Kodak Portra film aesthetic, shallow depth of field, slightly
  warm color grade with cool blue shadows, professional broadcast quality."
```

### Using the Prompt Bible

When writing each shot's prompt, copy the relevant anchors verbatim from the bible. Don't paraphrase. Don't abbreviate. The exact same words every time create the strongest consistency signal.

### Global Visual Bible + Storyboard Chunks

For advanced Seedance productions, the prompt bible can become a visible global reference: one dense approved visual bible used as `@image1` across the production, plus chunk-specific storyboard frames and references for each 10-15 second story unit. Use this when the story has recurring cast, locations, props, or a strong look that must survive many generations.

For complex action, process, or story continuity, do not rely on prose alone. Generate a **chronological storyboard reference sheet** first, then prompt Seedance to animate that sheet in strict panel order. The prompt should name the sheet's actual token explicitly after the reference order is final, for example: `@image3 is the chronological storyboard reference sheet for this chunk. It controls panel order, action progression, staging, composition, and final state.`

Before writing those prompts, read `pr0ta-video` -> `reference/seedance-global-storyboard.md`. Keep this skill focused on prose anchors; the reference file owns MCP tool names, Seedance token roles, payload shape, and storyboard sheet workflow.

## Model-Specific Prompting

### Kling O3 Pro / V3

Kling uses `@Image1` for the start image and `@ElementN` for reusable subjects; its end image is implicit and never `@Image2`. Write film direction with chronological action and precise camera language, and repeat every Element token inside every multi-shot segment. Kling V3 supports up to five shots plus structured camera control; O3 supports up to six cuts. **Read `pr0ta-video/reference/kling-prompting.md` for the complete token, multi-shot, negative-prompt, and failure-repair contract.**

### Hailuo H3

H3 uses a structured audiovisual timeline, not Kling/Seedance tokens or older Hailuo bracket commands. Use `integrated_multimodal_description`, `overall_soundscape`, and `non_diegetic_music`; use stable `(S1)` speaker IDs plus `<d>[Language] exact text</d>` for dialogue. Reference-to-video binds literal `Image 1`, `Video 1`, and `Audio 1` roles. For a focused source-video edit, make `Video 1` authoritative, request one change, and state the identity, performance, camera, timing, composition, and audio that remain preserved. H3 outputs fixed 2K at 24 fps on the current Fal routes. **Read `pr0ta-video/reference/hailuo-h3.md` before writing any H3 prompt.**

### FLUX 3 Video

FLUX 3 supports T2V, I2V, first/last, timed keyframes, extension, and a Draft/Enhance lifecycle across eleven separate Fal routes. Use BFL's current prompt order: core summary, scene, stable subject description, chronological dynamic narrative, audio, then style/color. Use timecoded beats only when the duration needs them. Keyframes use unique `frame_index` values on a 24 fps timeline. Generation defaults `generate_audio` on; Enhance accepts only the approved `draft_cache_url` as creative input, so fix creative problems in Draft rather than trying to reprompt Enhance. **Read `pr0ta-video/reference/flux-3.md` before writing any FLUX 3 video prompt or payload.**

### LTX 2.5

LTX 2.5 uses six canonical `lightricks/ltx-2.5/` Pro/Fast T2V, I2V, and audio-to-video routes. Write four to eight concrete sentences for a simple shot: framing, scene/light, stable subject, chronological physical action, camera relative to subject, sound/dialogue, and landing. For native multi-shot, name each cut and re-establish stable identity, light, framing, and audio after it. Pro is the 6/8/10-second fidelity route; Fast reaches 20 seconds only for supported resolution/FPS combinations. Audio-to-video makes the source audio authoritative and exposes a narrower field surface than T2V/I2V. Lightricks documents stronger typography, so quote designed copy and inspect it frame by frame. Retake, Extend, and Reframe remain LTX 2.3 Pro operations, not LTX 2.5. **Read `pr0ta-video/reference/ltx-2.5.md` before writing any LTX 2.5 prompt or payload.**

### Wan 3.0 and Wan 3.0 Prime

Wan uses natural-language audiovisual direction across exact T2V, I2V, and R2V routes. T2V should move from framing and setting through chronological action, one camera path, sound, and a visible end state. In I2V, the source image owns frame zero; prompt motion and camera evolution, and describe the physical landing when optional `last_image` guidance is present. In R2V, finalize array order first, then assign every image, video, and audio reference one plain-language ordinal role such as "the first reference video controls camera pace." Audio defaults on through `enable_audio`; set it to `false` for a silent post workflow. Standard and Prime share prompt grammar, so settle direction with standard and use Prime only as a deliberate higher-fidelity pass. Never invent Seedance/Kling `@` tokens, character IDs, or a negative-prompt field. **Read `pr0ta-video/reference/wan-3.0.md` before writing any Wan 3.0 prompt.**

### Seedance 2.5

**Seedance 2.5 Omni Reference is the preferred video-generation path.** Attach at least one approved image, video, or audio reference and assign every reference one clear role in natural language. Seedance 2.5 runs 4–30 seconds. Its T2V, I2V, first/last, Omni, source-video Edit, and Extend modalities have dedicated 480p/720p/1080p/4K routes selected by model ID; MuAPI's public pages currently conflict about 1080p render lineage, so do not promise native or upscaled internals. Every route returns audio-bearing video; standard routes expose no audio toggle, while Edit and Extend expose `generate_audio`. Use chronological action, one clear camera path per beat, and an explicit end state. For 15–30 seconds, use compact setup/development/turn/resolution beats. Upstream ByteDance examples show spaced labels such as `@Image 1`, `@Video 1`, and `@Clay Render 1`, but MuAPI does not guarantee that UI syntax: use natural-language roles and ordinary image references unless the exact live route documents token binding. Never invent Seedance 2.0 lowercase compact tokens, character IDs, clay-render fields, or negative prompts. **Read `pr0ta-video/reference/seedance-2.5.md` before writing a 2.5 prompt.**

### Seedance 2.0 Omni

Seedance 2.0's positional tokens are real and lowercase: `@image1..9`, `@video1..3`, and `@audio1..3`. Lead a reference-driven prompt with an explicit role ledger, then chronological action, camera, style/light, audio intention, and final state. Distinguish `@character:<request_id>` from trained `@omni-character:<char_id>`. MP3 and WAV audio references condition rhythm/content but do not guarantee verbatim speech or lip sync. There is no official optimal word count or subject-first weighting rule. **Read `pr0ta-video/reference/seedance-omni.md` before writing a 2.0 prompt.**

### Nano Banana 2

Use a clear subject, environment, photographic lighting/lens description, style, and positive constraints. Raise thinking level for complex layouts, precise text, or character sheets; keep exact recurring descriptions unchanged. Use the Line-Locked Poster technique above for critical copy and read `pr0ta-image` for current controls, fan-out, reference-sheet, and safety guidance.

### OpenAI GPT Image 2 (Escalation Model)

GPT Image 2 is the escalation model for difficult prompt adherence and identity-preserving edits. Write natural detailed prose, keep the Line-Locked Poster and glyph-QC rules for critical copy, and query live defaults rather than assuming width/height fields. Read `pr0ta-image` for current endpoint controls and fan-out strategy.

## Prompt Anti-Patterns (What Breaks Consistency)

The three most critical anti-patterns: **(1) Assumed context or ambiguous pronouns** -- name subjects/tokens whenever identity could be unclear; never use "the same as before." **(2) Negations in prose** -- video models often drop `don't`/`no`/`does not`; rewrite as positive assertions (see Technique 4). **(3) Shifting descriptors** -- use the exact same words from the prompt bible every time.

For the full list of 11 anti-patterns with bad/good examples, see `reference/anti-patterns.md`.

## Shot-Type Prompt Templates

- **Establishing:** `[Wide/Aerial] of [LOCATION + architecture]. [Time of day] light. [Atmosphere]. [Camera: static wide / slow pan / drone descent]. No characters visible.`
- **Medium (Dialogue):** `[Medium shot] of [CHARACTER NAME, full appearance] in [LOCATION]. [Action with body mechanics]. [Lighting matching location]. Camera: [subtle movement or static].`
- **Close-Up:** `[Close-up] of [specific detail]. [CHARACTER/OBJECT, key features]. [Minimal background]. [Lighting on subject]. Shallow depth of field.`
- **Action:** `[Shot type] of [CHARACTER, appearance] in [LOCATION]. [Sequential action: "First A, then B, finally C"]. [Physics details]. Camera: [tracking / handheld / dynamic].`
## The Complete Prompt Writing Workflow

1. Create the prompt bible and copy its relevant anchors verbatim into each shot.
2. Load the exact model reference, then write the route-specific prompt structure.
3. Verify self-containment, chronology, reference roles, identity/style consistency, and positive end states.
4. Remove ambiguity, redundant references, unsupported fields, conflicting camera/action instructions, and unnecessary prose.
