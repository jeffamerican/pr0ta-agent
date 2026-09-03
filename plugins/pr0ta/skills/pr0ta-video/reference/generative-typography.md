# Generative Typography in Image and Video

Use this reference whenever a PR0TA asset must contain readable words: titles, kinetic type, signs, packaging, interfaces, charts, formulas, menus, lower thirds, credits, or environmental lettering.

## Core Policy

Do not reject generative text because older models often produced gibberish. Premium current image and video models can render useful, sometimes production-ready typography. Select by current capability, prompt the copy as a designed element, and verify the actual pixels or frames.

Capability does not remove the acceptance test. Exact copy may still mutate, flicker, or acquire extra glyphs. A verified generated result is valid; a deterministic overlay or still animation is the fallback when a take fails, not the mandatory starting point.

## Current Capability Routing

### Premium image candidates

- **GPT Image 2:** use for professional image generation/editing, instruction adherence, and text-bearing marketing or design assets.
- **Nano Banana 2 / current Gemini image family:** use for fast text-bearing stills and iterative edits; current Gemini image guidance explicitly supports advanced text rendering.
- **Seedream 5.0 Pro:** use for dense layouts, multilingual typography, posters, interfaces, and information visualization when exposed by the live catalog.
- **Current FLUX image routes:** use when the live model catalog exposes a typography-capable FLUX operation.

Query `models_list` and `models_get_defaults` before dispatch. Do not keep an old static allowlist when the catalog has newer premium choices.

### Premium video candidates

- **FLUX 3:** preferred when typography or animated design is central. BFL explicitly documents strong typography generation and animated designs. Read `flux-3.md`.
- **Wan 3.0 / Prime:** valid for native titles, signs, charts, formulas, infographics, and motion typography. Alibaba advertises advanced multilingual text rendering, while also noting that exact on-screen accuracy can still improve. Read `wan-3.0.md`.
- **Seedance 2.0:** a strong typography candidate for reference-led text animation and designed title shots. Attach the approved text design when available, name its role explicitly, and inspect the temporal result. Read `seedance-omni.md`.
- **Seedance 2.5:** a strong premium choice for longer typography-led sequences, multimodal reference, and targeted video editing. Use an approved design reference or source-video edit when exact visual direction matters. Read `seedance-2.5.md`.
- **MiniMax H3:** a strong commercial typography and brand-rendering choice. MiniMax explicitly highlights accurate text and brand rendering; use H3's structured audiovisual grammar and native 2K output. Read `hailuo-h3.md`.
- **LTX 2.5:** a valid T2V/I2V typography candidate with stronger text detail documented by Lightricks, plus native audiovisual and multi-shot generation. Quote the copy, keep motion readable, and apply frame-by-frame acceptance. Read `ltx-2.5.md`.
- **Other current video families:** try native typography when provider documentation, current model positioning, or a controlled PR0TA test verifies it. Do not infer incapability from model age alone, and do not infer exactness from general visual quality.

## Choose Native Video or Deterministic Animation

Prefer native video typography when:

- the letters themselves transform, assemble, dissolve, interact, or move through 3D space;
- typography must participate in generated lighting, materials, particles, or camera motion;
- the selected endpoint has verified text capability;
- the copy is short enough to inspect frame by frame; and
- several variants can be generated and compared.

Prefer a verified still plus a timeline hold/Ken Burns preset when:

- legal, financial, safety, credit, or brand copy must be exact;
- the text is long or dense;
- the same typography must remain pixel-identical across several shots;
- accessibility requires guaranteed readability; or
- native video attempts fail spelling, stability, or timing QC.

This is an acceptance-risk decision, not a belief that video models cannot render text.

## Prompt Contract

Put literal copy early and in quotation marks. Describe it once as exact copy rather than paraphrasing it elsewhere.

Specify:

1. exact text and language;
2. type category and character, such as condensed sans, Didone serif, or hand-painted script;
3. size hierarchy and line breaks;
4. placement, alignment, and safe margins;
5. color, material, outline, glow, or dimensional effect;
6. entrance, hold, transformation, and exit motion;
7. the interval during which the words must remain unchanged; and
8. `no additional words` when no other copy may appear.

### Animated-title template

```text
Animated title design. The exact text "[COPY]" appears [placement] in [type style],
with no additional words. [time range]: [entrance motion]. [time range]: the complete
text remains unchanged and fully legible while [camera/background motion]. [time range]:
[exit motion]. [palette, material, lighting, and sound].
```

### I2V typography template

```text
The supplied frame owns the exact wording, letterforms, layout, and colors. Animate only
[named letters/design elements] through [motion]. Keep "[COPY]" unchanged and fully
legible from [time] through [time]. Preserve all other typography and composition.
```

Use the I2V preservation wording only with a video endpoint that has passed a typography test. It is a prompt contract, not a guarantee.

## QC Gate

Inspect the result at delivery resolution and frame by frame. Reject the take for any of these:

- misspelling, paraphrase, translation, or substituted word;
- duplicated, missing, or invented character;
- extra headline, URL, label, or filler copy;
- changing glyph shape, line break, spacing, or alignment during a required hold;
- flicker, crawling edges, or partial disappearance;
- motion blur or timing that makes the copy unreadable;
- incorrect language/script direction or broken diacritics; or
- incorrect brand color, hierarchy, or safe-area placement.

Do not let a correct thumbnail, first frame, or last frame stand in for the temporal inspection.

## Repair Ladder

1. Shorten the copy and remove duplicate prose descriptions.
2. Move the quoted text earlier and specify `no additional words`.
3. Simplify the type treatment or motion while preserving the creative intent.
4. Generate several variants or try the premium tier.
5. Switch to a stronger documented typography model, especially FLUX 3 for native motion design.
6. Generate or edit a pixel-verified still with a premium image model.
7. Animate that still deterministically on the PR0TA timeline.

Repair the defective shot or title asset only; do not regenerate an otherwise approved sequence.

## Primary Sources

- [BFL FLUX 3 launch](https://bfl.ai/blog/flux-3)
- [BFL typography prompting rules](https://github.com/black-forest-labs/skills/blob/master/skills/flux-best-practices/rules/typography-text.md)
- [Wan 3.0 release](https://modelstudio.console.alibabacloud.com/model-releases/wan3.0-video)
- [Wan 3.0 API reference](https://help.aliyun.com/en/model-studio/wan3-video-generation-api-reference)
- [Gemini image-generation guidance](https://ai.google.dev/gemini-api/docs/image-generation)
- [OpenAI image generation](https://openai.com/index/image-generation-api/)
- [Seedream 5.0 Pro launch](https://seed.bytedance.com/en/blog/beyond-generation-it-understands-design-introducing-seedream-5-0-pro)
- [Seedance 2.0](https://seed.bytedance.com/seedance2_0)
- [Seedance 2.5 launch](https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5)
- [MiniMax H3 launch](https://www.minimax.io/blog/minimax-h3)
- [LTX 2.5 support matrix](https://docs.ltx.io/models/ltx-2-5)
