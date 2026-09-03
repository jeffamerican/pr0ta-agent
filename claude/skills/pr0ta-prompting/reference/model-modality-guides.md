# Model and Modality Prompt Routing

Use this reference whenever the selected model belongs to one of the curated families below. Prompting advice is keyed by **exact model family plus active operation**. A family name alone is never enough.

## Required Routing Order

1. Resolve the exact current `model_id` from model discovery or the generation request.
2. Resolve the active operation: T2V, I2V, audio-to-video, first/last frame, Omni/reference, video edit/extend, T2I, image edit/reference, image-to-3D, TTS, audio reference, image-to-audio, text-to-music, or image-to-music.
3. Apply only the matching row below. Do not transfer tokens, section grammar, negative-prompt behavior, or reference semantics across models or routes.
4. Query `models_get_defaults` before building the payload. This reference controls prompt writing, not the live endpoint schema.
5. When a deep reference is named, read it before producing the final provider prompt.

## Video Models

### Seedance 2.0

Deep reference for Omni/reference work: `pr0ta-video/reference/seedance-omni.md`.

| Operation | Prompt order | Critical rule |
|---|---|---|
| T2V | genre/framing → subject and setting → chronological action → camera → light/sound → end state | Write concise audiovisual film direction. |
| I2V | `@image1` role → motion onset and development → camera → sound → end state | The image owns the opening look; do not reconstruct it. |
| First/last | first-frame state → chronological physical bridge → one camera path → exact last-frame landing | Treat the supplied frames as ordered endpoints; do not invent positional tokens for this dedicated route. |
| Omni/reference | reference-role ledger → chronological action → camera/style → audio intent → end state | Bind lowercase positional `@imageN`, `@videoN`, and `@audioN` tokens after finalizing list order. |
| Video edit | source clip role → requested transformation → optional `@imageN` bindings → preserved motion/composition/audio → result | The source clip is implicit; bind only optional image references and state what must remain unchanged. |
| Continuation by reference | `@video1` continuity role → next causal beat → new landing state | A clip reference is guidance, not a guaranteed frame-exact seam. |

Give each reference one primary job. State whether a video controls performance, camera, or edit rhythm and what visible event should synchronize to audio. Keep trained-character token families distinct. Seedance 2.0 is also a strong candidate for designed text: attach a typography authority when available, quote the copy, describe its motion/hold, and inspect every frame.

Official sources: [ByteDance launch and prompt examples](https://seed.bytedance.com/en/blog/seedance-2-0-official-launch), [model page](https://seed.bytedance.com/en/seedance2_0).

### Seedance 2.5

Deep reference: `pr0ta-video/reference/seedance-2.5.md`.

| Operation | Prompt order | Critical rule |
|---|---|---|
| T2V | shot intent → subject/setting → chronological performance → camera → atmosphere → end state | For longer clips, use a few compact causal beats. |
| I2V | action onset → continuous motion → camera → atmosphere change → preserved traits → end state | Spend the prompt on motion, not a description of the still. |
| First/last | first frame → observable intermediate bridge → one camera path → exact last-frame landing | The two images are ordered structural targets. |
| Omni/reference | image roles + video roles + audio roles → action → camera → preserved traits → end state | Assign roles in plain language on MuAPI routes. |
| Video Edit | source authority → one requested transformation → optional image/audio roles → preserved motion/composition/audio → end state | Keep the source clip's identity, timing, and motion authoritative unless explicitly changing them. |
| Video Extend | source continuity → next causal action → camera/sound evolution → optional target-image landing → new end state | Continue from the last frame; do not restart or summarize the source clip. |

Seedance 2.5 does **not** use Seedance 2.0's lowercase compact positional-token contract. Upstream ByteDance 2.5 examples show UI labels such as `@Image 1`, `@Video 1`, and `@Clay Render 1`, but MuAPI does not currently guarantee those labels for PR0TA routes. Use plain-language roles unless the exact live route documents token binding, and never invent a clay-render field. Seedance 2.5 is a strong premium typography candidate, particularly through Omni references and focused Edit passes; quote exact copy, define design/motion/hold, and inspect every frame. Every 2.5 route returns audio-bearing video; standard routes have no audio opt-out, so prompt the intended sound and time-index speech-bearing results.

Official source: [ByteDance Seedance 2.5](https://seed.bytedance.com/en/seedance2_5).

### MiniMax Hailuo H3

Deep reference: `pr0ta-video/reference/hailuo-h3.md`.

| Operation | Prompt grammar | Critical rule |
|---|---|---|
| T2V | `integrated_multimodal_description` → `overall_soundscape` → `non_diegetic_music` | Begin with `[Shot 1]`; later cuts get increasing timestamps. |
| I2V | H3 first-frame alignment → action evolution → camera → soundscape/music | The supplied image owns frame zero. |
| First/last | H3 picture-alignment statement → observable bridge → exact final landing | Use the documented Picture 1/Picture 2 alignment grammar. |
| Reference/edit | `subject_definitions` → `summary` → `retention_analysis` → `detailed_description` → soundscape/music | Bind literal `Image 1`, `Video 1`, and `Audio 1`; for a source-video edit, make `Video 1` authoritative and request one focused change. |

For dialogue, define stable speaker IDs and use `<d>[Language] exact words</d>`. Write camera direction in natural English. Do not transfer older Hailuo bracketed Director commands. H3 returns native stereo audio on every video route and exposes no sound toggle. MiniMax explicitly positions H3 as strong at accurate text and brand rendering; quote visible copy inside `integrated_multimodal_description`, define its design and hold interval, and inspect every frame.

Official sources: [H3 base prompt guide](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md), [H3 reference guide](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md).

H3 Max has separate Fal T2V, I2V, and R2V IDs. Its R2V route binds literal `Image 1`, `Video 1`, and `Audio 1` roles, accepts 12 files, and requires `balanced` or `quality` prompt expansion. Do not copy fixed-2K H3 fields into it.

### FLUX 3

Deep reference: `pr0ta-video/reference/flux-3.md`.

| Operation | Prompt order | Critical rule |
|---|---|---|
| T2V | core summary → scene → stable subject → dynamic narrative → audio → style/color | Use one paragraph for a simple shot or timecoded beats for dense action. |
| I2V | frame-zero authority → motion onset/development → camera → audio → landing | Spend the prompt on what changes after the image. |
| First/last or keyframes | ordered anchors → causal bridge → camera/audio continuity → landing | PR0TA keyframes use unique `frame_index` values on a 24 fps timeline. |
| Extend | source continuity → next causal beat → camera/audio evolution → new end state | Continue from the last frame; do not recap the source. |
| Draft/Enhance | write/approve the Draft → enhance its durable cache | Enhance accepts `draft_cache_url`, not a replacement creative prompt. |

FLUX 3's current BFL guides explicitly document core summary, scene, subject, dynamic narrative, audio, style/color, timestep prompting, strong typography, and animated design. Current Fal generation routes expose `generate_audio` and default it to `true`. Select one of the eleven exact standard, Draft, or Enhance model IDs from the deep reference; fields differ by operation.

Official sources: [FLUX 3 overview](https://docs.bfl.ai/flux_3/flux3_overview), [video prompting overview](https://docs.bfl.ai/guides/prompting_video_overview), [audio and speech](https://docs.bfl.ai/guides/prompting_video_audio).

### LTX 2.5

Deep reference: `pr0ta-video/reference/ltx-2.5.md`.

| Operation | Prompt order | Critical rule |
|---|---|---|
| T2V | shot scale → scene/light → character and physical action → camera movement → sound/dialogue | Write one flowing present-tense sequence, normally 4–8 concrete sentences for a simple shot. |
| I2V | opening-frame authority → chronological action → camera relative to subject → environmental motion → light/audio continuity | Spend words on what moves after frame zero; if `end_image_url` is supplied, describe a plausible progression that lands there. |
| Audio-to-video | shot/scene → visible performer or subject → motion responding to audio → camera response → light/atmosphere | Source audio owns rhythm, energy, timing, and the output soundtrack. Without `image_url`, fully establish the subject and scene. |
| Native multi-shot | opening shot → named transition → re-established framing/identity → audio continuity/change → next beat | Keep 2–4 shots in chronological prose. Name every cut and repeat stable subject identifiers after it. |

Use only canonical IDs under `lightricks/ltx-2.5/`; do not prepend `fal-ai/`. Pro accepts 6/8/10 seconds. Fast reaches 20 seconds only for eligible resolution/FPS combinations. T2V/I2V default `generate_audio` on. A2V has a narrower Fal field surface and must not inherit T2V/I2V resolution, FPS, camera, or end-image controls. Use physical emotion cues, quote dialogue with language/accent, and prefer plausible motion over chaotic physics. LTX 2.5 supports native multi-shot and improved typography, but not Retake, Extend, or Reframe; those operations remain LTX 2.3 Pro-only in the current Lightricks matrix.

Official sources: [LTX prompting guide](https://docs.ltx.io/api-documentation/implementation-guides/prompting-guide), [LTX 2.5 support matrix](https://docs.ltx.io/models/ltx-2-5).

### Wan 3.0 and Wan 3.0 Prime

Deep reference: `pr0ta-video/reference/wan-3.0.md`.

| Operation | Prompt order | Critical rule |
|---|---|---|
| T2V | framing/setting → subject and chronological action → camera path → dialogue/sound → final visible state | Keep beats proportional to the 2–30 second duration and use `thinking_mode` only for real complexity. |
| I2V | motion onset from frame zero → causal action → camera evolution → sound → end state | The source image owns subject, scene, composition, and style; optional `last_image` is terminal guidance on the same route. |
| R2V | plain-language ordinal reference ledger → chronological action → camera/reference relationship → sound → landing | Finalize each media array first and give every reference one primary job; numbering is separate within image, video, and audio arrays. |

Wan generates audio by default. MuAPI routes use `enable_audio` and `thinking_mode`; Fal-native `alibaba/wan-3.0-prime/*` routes use `audio`, `enable_thinking`, and `enable_prompt_expansion`. Their reference array names also differ. Standard and Prime share the same natural-language prompting approach, but payload fields must come from the selected provider schema. Wan 3.0 is a native typography candidate: quote exact copy, describe its design/motion/hold, and inspect every frame. Never use `@imageN`, `@videoN`, `@audioN`, `@ElementN`, character-token syntax, or an invented negative-prompt field. Treat exact dialogue and lip sync as take-level QC, not a guarantee.

Official sources: [MuAPI Wan 3.0](https://muapi.ai/wan-3), [Wan 3.0 T2V](https://muapi.ai/playground/wan3.0-text-to-video), [Wan 3.0 I2V](https://muapi.ai/playground/wan3.0-image-to-video), [Wan 3.0 R2V](https://muapi.ai/playground/wan3.0-reference-to-video). Alibaba's [Wan prompt guide](https://www.alibabacloud.com/help/en/model-studio/text-to-video-prompt) supports the family-level entity/scene/motion, I2V motion/camera, and sound-direction techniques, but its multi-shot and reference syntax currently name Wan 2.6/2.7 rather than Wan 3.0.

### Kling O3 and Kling V3 Video

Deep reference: `pr0ta-video/reference/kling-prompting.md`.

| Operation | Prompt order | Critical rule |
|---|---|---|
| T2V | scene → subject → chronological action → camera → atmosphere/audio → end state | Write directions to a cinematographer, not keyword inventory. |
| I2V | start-frame/reference role → action timeline → camera → atmosphere/audio → end state | The frame owns appearance. |
| Start/end | `@Image1` start role → physical journey → camera → final landing | In PR0TA's current tested O3 contract, the end frame is implicit; do not invent `@Image2`. |
| Elements/reference | bound tokens → scene/subjects → action → camera → atmosphere/audio → end state | Repeat stable `@ElementN` labels whenever ambiguity is possible. |
| Video reference | source/reference roles → bound subjects → action → camera → preserved style/motion/audio → end state | Name what the reference video contributes and use only tokens exposed by the route. |
| Video edit | source clip role → requested edit → bound replacement/reference → preserved motion/composition/audio → result | Request one focused change and state what must remain unchanged. |
| Custom multi-shot | per-shot framing → bound subject → one action → camera/audio → continuity handoff | Keep sequence narrative in the shot array and repeat Element labels per shot. |

Use only tokens exposed by the active route. One Element bundle represents one subject. Do not assume every Kling O3/V3 provider wrapper uses identical token casing or fields.

O3's native-4K V2V Edit and Reference routes bind `@Video1`, `@ImageN`, and `@ElementN`; preserve audio with `keep_audio` and approve the premium estimate.

Official sources: [Kling VIDEO 3.0 guide](https://home.kling.ai/quickstart/klingai-video-3-model-user-guide), [Kling VIDEO 3.0 Omni guide](https://home.kling.ai/quickstart/klingai-video-3-omni-model-user-guide).

### Gemini Omni

Fal's Gemini 1.1 generation routes produce 3–10 second audiovisual clips from 360p through 4K. R2V accepts `image_urls` and up to three `reference_video_urls`, each at most 3 seconds. The `/edit` route takes `prompt`, `video_url`, and optional `resolution`; it exposes no duration, aspect-ratio, reference-array, or audio controls.

| Operation | Prompt order | Critical rule |
|---|---|---|
| T2V | framing/camera → style/light/location → subject action → dialogue/sound → end state | Natural language works; control only the choices that matter. |
| I2V | image role → subject/environment motion → camera → audio/dialogue → end state | Name every image's distinct role. |
| R2V | zero-based reference tags → source roles → chronological action → camera → dialogue/sound → end state | Use `<IMAGE_REF_N>` and `<VIDEO_REF_N>` exactly; PR0TA compiles them from array order. |
| Video edit | source role → requested change → preserved motion/identity/timing/composition → result | Make one specific update and preserve explicit invariants. |

Use precise camera vocabulary when framing matters. Attribute dialogue to named speakers. Gemini R2V accepts no reference-audio array, and every reference video must be at most three seconds. For iterative edits, request one focused change rather than rewriting the whole scene.

Official sources: [Gemini Omni prompt guide](https://deepmind.google/models/gemini-omni/prompt-guide/), [Gemini Omni API](https://ai.google.dev/gemini-api/docs/omni).

## Image Models

### GPT-Image-02

| Operation | Prompt order | Critical rule |
|---|---|---|
| T2I | background/scene → subject → details → composition → style/light → constraints and intended use | Use short labeled sections for complex layouts. |
| Edit/reference | exact change → target → preserved identity/composition/style/text → intended result | Say “change only…” and “keep everything else the same.” |

Name multiple inputs by index and role. Quote literal text and specify placement and typography. Iterate with small changes.

Official source: [OpenAI GPT Image prompting guide](https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide).

### Nano Banana Pro and Nano Banana 2

| Operation | Prompt order | Critical rule |
|---|---|---|
| T2I | style → subject → setting → action → composition → light/color → output details | State spatial relationships explicitly. |
| Edit/reference | base-image role → requested change → other reference roles → preserved details → output format | Name Image 1, Image 2, and their distinct jobs. |

Use Nano Banana Pro's fuller structured brief for complex professional layouts or multi-subject work; Nano Banana 2 responds well to direct natural language and focused iteration. Specify exact text, aspect, and format when they matter.

Official sources: [Gemini image generation](https://ai.google.dev/gemini-api/docs/image-generation), [Gemini image prompt guide](https://deepmind.google/models/gemini-image/prompt-guide/).

### Seedream 5

| Operation | Prompt order | Critical rule |
|---|---|---|
| T2I | style positioning → subject details → environment/action → composition → color/light → exact text | List dense panels and subjects in spatial order. |
| Edit/reference | base/reference role → change action → changed object → new feature → preserved elements | Use explicit verbs such as remove, add, replace, relight, translate, or reference. |

Seedream 5 can follow dense layout, multilingual text, annotations, and spatial requirements. For local edits, protect untouched regions rather than asking for a broad redesign.

Official sources: [ByteDance Seedream 5.0 Pro](https://seed.bytedance.com/en/seedream5_0_pro), [BytePlus image API](https://docs.byteplus.com/en/docs/ModelArk/1824121).

### Midjourney

| Operation | Prompt order | Critical rule |
|---|---|---|
| T2I | subject → medium → environment → lighting/color → mood/composition → parameters | Keep prompts short and put parameters last. |
| Image/Omni/style reference | reference + concise final-image description + essential composition/style + parameters | Describe the result, not instructions for changing the reference. |

Use precise counts and positive desired content. Keep text simple when a style reference is strong and avoid conflicting style words.

Official sources: [prompt basics](https://docs.midjourney.com/docs/prompts), [image prompts](https://docs.midjourney.com/hc/en-us/articles/32040250122381-Image-Prompts), [Omni Reference](https://docs.midjourney.com/hc/en-us/articles/36285124473997-Omni-Reference).

### Kling O3 and Kling V3 Image

| Operation | Prompt order | Critical rule |
|---|---|---|
| T2I | subject/action → environment → composition/angle → lens/depth → light/tone → style | Use concrete cinematography rather than the word “cinematic” alone. |
| Edit/reference | base image → reference roles → edit → composition/lens/light → preserved traits | Name each image's role and keep recurring subject labels stable. |

For storyboards or series, label ordered beats and preserve eyelines, screen direction, and subject placement. One Element contains one subject.

Official source: [Kling IMAGE 3.0 Omni guide](https://home.kling.ai/quickstart/klingai-image-3-omni-user-guide).

### Grok Imagine Image 2.0

Use the Fal routes `xai/grok-imagine-image/v2.0/text-to-image` and `xai/grok-imagine-image/v2.0/edit`; do not route these through PR0TA's direct xAI image endpoint.

| Operation | Prompt order | Critical rule |
|---|---|---|
| T2I | subject/action → environment → composition/viewpoint → style/material → lighting/palette → mood and exact text | Be specific about spatial relationships, visual hierarchy, and the intended image rather than stacking generic adjectives. |
| Edit | input-image roles → exact target/change → preserved identity/layout → style/light → output placement/size | Use plain-language spatial targets and state what must remain untouched. With multiple inputs, name the distinct contribution of each image. |

Grok responds well to detailed natural-language briefs covering subject, style, lighting, composition, and mood. For photorealism, specify natural materials and textures, light quality, and lens or editorial treatment. Quote literal copy and describe its placement and typography.

Official sources: [xAI image generation](https://x.ai/grok/use-cases/image-generation), [xAI image editing](https://x.ai/grok/use-cases/image-editing).

## 3D Models

### Meshy v7

Meshy image-to-3D is input-authority work more than prose prompting. The optional `texture_prompt` describes materials and surface appearance; it does not repair weak geometry references.

| Operation | Input/prompt order | Critical rule |
|---|---|---|
| Single image | whole unobstructed object → front or three-quarter view → plain background → neutral light → optional texture/material description | The silhouette must be legible. Use pose controls only for clearly humanoid subjects. |
| Multi-image | same subject → 2–4 distinct 45–90° views → consistent scale/style/detail → neutral light/background → optional texture/material description | Keep the object centered and identical across views; prefer front, side, three-quarter, and rear coverage. |

Use sharp references around 1040×1040 or larger when available. Avoid cropping, occlusion, duplicate angles, cluttered backgrounds, specular glare, inconsistent scale, or views of different objects. Use `texture_prompt` only when `should_texture` is enabled; describe the desired material directly and do not invent a negative-prompt field.

Official sources: [Meshy Image to 3D](https://help.meshy.ai/en/articles/9996860-how-to-use-meshy-image-to-3d), [Meshy Multi-View](https://help.meshy.ai/en/articles/12634481-how-to-use-multi-view), [Meshy texture prompting](https://help.meshy.ai/en/articles/12127474-revamping-model-texture-with-text-prompt-or-image-upload).

## Speech and Audio Models

### ElevenLabs V3

Write natural performance-ready text. Insert a few compatible audio tags where delivery changes, use punctuation for rhythm, ellipses for weighted pauses, and capitals sparingly for emphasis. Choose a voice whose training character already fits the target emotion. In multi-speaker dialogue, prefix every line with its assigned speaker.

Do not use SSML break tags with V3. Do not stack many experimental tags or expect a calm source voice to shout convincingly.

Official source: [ElevenLabs V3 prompting guide](https://elevenlabs.io/docs/best-practices/prompting).

### Gemini TTS Models

Applies to current Gemini 3.1 Flash TTS and Gemini 2.5 Flash/Pro TTS routes.

Prompt order: `AUDIO PROFILE → SCENE → DIRECTOR'S NOTES → SAMPLE CONTEXT when useful → exact TRANSCRIPT`.

- Put tone, pace, accent, emotional arc, audience, and mic feel in style instructions.
- Keep the transcript exact and separate from direction.
- For multi-speaker dialogue, speaker labels must exactly match configured speaker names.
- Select a prebuilt voice whose inherent character supports the performance.

Official source: [Google Gemini speech generation](https://ai.google.dev/gemini-api/docs/speech-generation).

### Seed Audio 1.0

| Operation | Prompt order | Critical rule |
|---|---|---|
| Text-to-audio | format/duration/language → scene → speakers and exact lines → ambience → music → SFX → ending | Write a complete sound-production brief in playback order. |
| Audio-reference | `@AudioN` role ledger → scene → dialogue → ambience/music/SFX → ending | Bind references by final list order; give each one job. |
| Image-to-audio | image role → location/time → speakers/events → ambience/music/SFX → ending | Describe sounds causally connected to the image. |

PR0TA's current Fal route accepts up to three audio references or one image; the two reference types are mutually exclusive. Query the live schema for current limits.

Official source: [ByteDance Seed Audio 1.0](https://seed.bytedance.com/en/seedaudio1_0).

## Music

### Lyria

| Operation | Prompt order | Critical rule |
|---|---|---|
| Text-to-music | genre → tempo → instrumentation → mood → structure/dynamics → vocal profile → lyrics | Describe the musical arc, not only the mood. |
| Image-to-music | image people/place/action/mood → genre → tempo → instruments → dynamics → vocals/lyrics | Translate visible meaning into concrete musical decisions. |

Name instruments and their roles. Prefix supplied words with `Lyrics:` or describe a lyrical theme when lyrics should be generated.

Official source: [Google Lyria prompt guide](https://deepmind.google/models/lyria/prompt-guide/).

## Final Prompt Check

Before sending any curated-family prompt, verify:

- Exact family and operation were resolved.
- No syntax was copied from a sibling version or another provider.
- Every reference has one explicit role and uses only route-supported names/tokens.
- Actions and audible events are written in playback order.
- Preservation requirements are positive and observable.
- Payload fields still come from the current endpoint schema, not this prose guide.
