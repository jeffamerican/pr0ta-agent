# Seedance 2.0 Omni (ByteDance Lynx)

Seedance 2.0 Omni is a quad-modal audiovisual model. It accepts text plus optional image, video, audio, and character references. Its strength is explicit multimodal role assignment followed by chronological film direction.

**PR0TA model ID:** `muapi/seedance-2-vip-omni-reference`

## Contents

- Current contract and positional token families
- Shared and route-specific prompting grammar
- Timed beats, characters, audio, and storyboards
- Extension boundaries and 2.0-vs-2.5 selection
- Known limitations and repairs

## Current Provider Contract

- Prompt: required, up to 4,000 characters.
- Duration: any whole second from 4 through 15.
- Aspect ratio: `21:9`, `16:9`, `4:3`, `1:1`, `3:4`, or `9:16`.
- Images: JPEG/PNG/WebP, up to 9.
- Videos: MP4, up to 3, at most 15 seconds each.
- Audio: MP3 or WAV, up to 3 files and 15 seconds total.
- Reference capacity: up to 15 files total by the per-modality ceilings: 9 image + 3 video + 3 audio.

The provider's current Omni schema requires only the prompt; references are optional. PR0TA's generic `ref_to_vid` validation can still require a reference because that mode promises reference-conditioned work. For prompt-only generation, prefer the dedicated Seedance 2.0 T2V endpoint. For any production pass, query `models_get_defaults` because PR0TA's cached catalog can lag MuAPI's live schema.

Seedance 2.0 is natively audiovisual at the model-family level. Whether a specific MuAPI route exposes generated-audio controls is a separate payload question. The current VIP schemas do not document a universal `sound` or `generate_audio` field. Verify live defaults and inspect the actual result before relying on native audio.

## Reference Tokens

Tokens are positional and lowercase in MuAPI's current documentation:

| Prompt token | Provider input | Meaning |
|---|---|---|
| `@image1` … `@image9` | nth `images_list` entry | identity, set, prop, composition, lighting, style, storyboard |
| `@video1` … `@video3` | nth `video_files` entry | performance, physical motion, camera trajectory, cuts, rhythm |
| `@audio1` … `@audio3` | nth `audio_files` entry | rhythm, timing, sound character, or speech-content guidance |
| `@character:<request_id>` | completed Seedance 2 Character-sheet request | provider injects that request's character image |
| `@omni-character:<char_id>` | trained Omni/Kinovi identity | persistent trained character identity |

Do not collapse the two character token families into one. MuAPI supports multiple characters, but PR0TA's structured `character_ids` resolver may impose a narrower current limit. Treat that as a PR0TA integration limit, not a Seedance model limit.

Build the final token order only after references have been selected. Reordering arrays changes every positional token.

## Prompting Grammar

There is no documented optimal word count. Official ByteDance examples range from one sentence to long shot descriptions. Use the shortest self-contained prompt that removes ambiguity.

For Omni/reference work, order the prompt as:

`reference-role ledger → chronological performance/action → camera → lighting/style → audio intention → final state`

```text
Use @image1 for the character's identity and wardrobe, @image2 for the location and lighting, @video1 for camera trajectory and performance rhythm, and @audio1 for pacing. [Named character] [chronological action and physical reaction]. The camera [precise path]. [Light/style]. Synchronize [specific motion or cuts] to @audio1 [rhythm/content]. End with [observable final state].
```

Rules:

1. Assign every supplied reference one primary job.
2. Use names or tokens wherever multiple subjects make pronouns ambiguous. Pronouns are not categorically forbidden.
3. Describe actions and physical interaction in playback order.
4. State what a camera reference controls—trajectory, framing, cut rhythm, or all three.
5. State what should synchronize to audio—steps, cuts, body motion, or another visible event.
6. Phrase preservation and exclusions as positive visible states.
7. Keep maximum reference counts as ceilings, not targets. Remove redundant or conflicting assets.

Official ByteDance examples often lead with genre or shot intent for T2V, motion for I2V, and reference roles for R2V. The old blanket rules “subject always comes first” and “early tokens are always weighted most” are not supported.

## Route-Specific Prompting

### Prompt-Only T2V

Prefer `muapi/seedance-2-vip-text-to-video` when there are no references:

```text
[Genre, shot scale, and opening composition]. [Subjects and setting]. First, [action]. Then, [physical development and reaction]. The camera [path and target]. [Lighting and sound events]. The shot ends with [observable state].
```

### Image-Led Work

When an approved image establishes the frame, avoid contradictory scene reconstruction. Lead with motion:

```text
Using @image1 as the opening composition and identity source, [subject] begins [action onset], then [continuous motion and physical result]. The camera [path]. Preserve [critical visible traits and spatial relationships]. End with [state].
```

### Multimodal R2V

```text
Use @image1 as the shooting script/storyboard, @image2 for the character, @image3 for the set, and @image4 for the hero prop. Use @video1 for camera movement and action rhythm. [Chronological 15-second film direction]. [Sound and final state].
```

This follows ByteDance's official reference-role examples. Keep the ledger literal; do not expect the model to infer which reference supplies identity versus camera or style.

## Timed Beats and Multi-Shot Work

For ordered action, a compact timeline can reduce ambiguity:

```text
[00:00-00:04] [one action beat, shot scale, and camera behavior].
[00:04-00:09] [causally connected beat and result].
[00:09-00:15] [final beat and explicit landing state].
```

ByteDance confirms that Seedance 2.0 can reference shooting scripts/text storyboards and generate multi-shot audiovisual clips. PR0TA's one-approved-sheet workflow, strict panel-order wording, timed SHOT blocks, and HARD CUT separators are house techniques for reproducibility, not provider-required syntax. Read `seedance-global-storyboard.md` for that workflow.

## Character Workflow

For recurring characters, read `pr0ta-consistency` and create or reuse a provider resource before generation.

PR0TA exposes two training paths:

- A clean portrait through `muapi/seedance-2-omni-reference-train` produces an Omni identity token.
- A character sheet or 1–3 approved stills through `muapi/seedance-2-character` produces a character-sheet resource.

Persist the returned provider resource to the project's character store. In the final provider prompt, preserve the correct token type:

- `@omni-character:<char_id>` for a trained Omni identity.
- `@character:<request_id>` for a completed character-sheet request.

Even with a trained identity, repeat the critical wardrobe, age, hair, and distinguishing traits relevant to the shot. Use clear, compatible image references rather than many weak ones.

## Audio References

Audio references are conditioning inputs. MuAPI documents MP3/WAV, up to three files and 15 seconds total, addressed by `@audioN`.

```text
Use @audio1 for pacing. Synchronize the dancer's footfalls and the two camera cuts to @audio1's beat pattern.
```

Do not promise that Seedance preserves the uploaded waveform, reproduces verbatim speech, or guarantees lip sync. ByteDance confirms audiovisual generation and aligned generated dialogue/SFX at the model-family level, but the uploaded-audio reference contract does not guarantee phoneme-level synchronization. Inspect each take. Use a dedicated, tested dialogue/lip-sync route when deterministic speech sync is required.

For any audio-bearing result:

1. Verify whether the returned file actually contains audio.
2. Transcribe speech-bearing video before editorial use.
3. Analyze instrumental music separately when beat timing matters.
4. Replace or repair generated audio in post when exact dialogue or mix is required.

## Storyboard and Global Visual Bible

For recurring cast, sets, props, or style across several chunks:

1. Approve one global visual bible.
2. Generate one chronological storyboard sheet for the current 4–15 second chunk.
3. Select the final reference order.
4. Assign every `@imageN` token explicitly.
5. Describe panel order and action progression in chronological prose.
6. Verify the output against the approved sheet; never assume perfect text rendering or multi-subject consistency.

Read `seedance-global-storyboard.md` before using this workflow. Seedance 2.0 is a valid typography and animated-title candidate: attach the approved design as an image reference, name it as typography authority, quote the exact copy, describe the intended motion, and inspect every frame. Use a deterministic still/timeline treatment only when the selected native result fails exact-copy or temporal-stability QC.

## Typography and Designed Text

Use T2V for invented title designs and I2V/R2V when an approved card, sign, interface, or brand treatment should control the result. With R2V, give the text-bearing image one explicit role and refer to it with the correct lowercase positional token. Keep literal copy in quotation marks, request no additional words when appropriate, and state the interval during which the complete typography must remain unchanged.

Typography quality is take-dependent even on strong models. Review spelling, line breaks, glyph stability, flicker, placement, and readability throughout the clip; a correct first frame alone does not pass.

## Extension

Seedance 2.0 has two valid continuation paths with different contracts.

### Omni Reference continuation (available in PR0TA)

Submit the previous clip as the first video reference so it becomes `@video1`. This is useful for continuing action, environment, camera direction, performance, and audiovisual texture from the preceding clip. It is reference-guided continuation, not a guarantee of a frame-exact seam.

```json
{
  "generator": "video",
  "mode": "ref_to_vid",
  "model": "muapi/seedance-2-vip-omni-reference",
  "prompt": "@video1 establishes the preceding action and camera direction. Continue with the next causal beat: the runner clears the doorway, slows, and ends facing the elevator as the camera settles behind her.",
  "reference_video_urls": ["https://example.com/previous-clip.mp4"],
  "duration": 7,
  "aspect_ratio": "16:9"
}
```

Rules:

- Clarify whether the target means additional continuation time or total sequence time, then split the remaining duration into 4–15 second segments.
- State that `@video1` supplies preceding action, environment, camera direction, and continuity.
- Describe only the next causal beat and desired end state.
- Reinforce identity with approved stills if drift appears.
- Verify the join frame, visual continuity, audio continuity, and true duration before assembly.
- Trim duplicate join frames on the PR0TA timeline when necessary.

Do not claim automatic last-frame locking or soundtrack carry-over. Validate the actual result.

### Provider-native Seedance extension (MuAPI capability; not currently unified in PR0TA)

MuAPI publishes `seedance-2-vip-extend` and `seedance-v2.0-extend`. These routes require the original MuAPI provider `request_id`; the source video's last frame becomes implicit `@image1`. Their current shared schema accepts an optional continuation prompt, up to eight additional images (`@image2`–`@image9`), three video references, three audio references, the six Seedance 2.0 aspect ratios, integer 4–15 second duration, and `basic`/`high` quality.

This is the stronger provider-native route for continuing a MuAPI-generated Seedance shot because it identifies the original generation rather than merely conditioning on a downloaded clip. It is not a Seedance 2.5 route.

PR0TA preserves provider request IDs in task metadata, but the unified `extend_video` path currently expects a source video URL/asset and does not catalog these MuAPI request-ID routes. Do not submit a MuAPI Seedance extend model through unified generation until live discovery and routing expose its `request_id` contract. For now, use Omni `@video1` continuation inside PR0TA or a currently returned unified extension model.

## Choosing Seedance 2.0 vs 2.5

Prefer Seedance 2.0 Omni when the shot needs:

- Positional `@image`, `@video`, or `@audio` role binding.
- A trained Omni or character-sheet resource.
- Model-family audiovisual generation, with result-level verification.
- The established PR0TA global-bible/storyboard-token workflow.

Prefer Seedance 2.5 when the shot needs:

- A 16–30 second single generation.
- The larger Omni capacity of 30 images, 10 videos, and 10 audios (50 total inputs).
- Dedicated first/last-frame routing.
- A 480p draft route followed by a 720p final candidate.

Seedance 2.5's current MuAPI routes do not expose 2.0's character tokens or documented positional reference tokens. Do not transfer those features by name.

## Known Limitations and Repairs

| Failure | Repair |
|---|---|
| Wrong reference role | Lead with an explicit reference-role ledger |
| Multi-subject identity drift | Use trained characters and fewer, clearer references; repeat distinguishing traits |
| Critical text mutates | Keep text as an approved still or timeline overlay |
| Uploaded speech does not sync | Treat audio as conditioning; use a dedicated lip-sync workflow for deterministic dialogue |
| Audio distortion | Inspect and replace/repair audio in post |
| Action order changes | Use chronological beats with visible intermediate states |
| Camera conflicts with reference | Choose either the video reference or prose as camera authority, or explicitly reconcile them |
| Prompt becomes diffuse | Remove redundant references and prose; one job per input |
| PR0TA rejects prompt-only Omni | Use the dedicated T2V route or the mode-specific payload contract |
| Omni continuation seam breaks | Regenerate with the previous clip as `@video1` and a narrower next beat, or use a currently returned unified extension model; inspect/trim the join on the timeline |

## Sources

- [Official Seedance 2.0 launch and prompt examples](https://seed.bytedance.com/en/blog/seedance-2-0-official-launch)
- [Official Seedance 2.0 model page](https://seed.bytedance.com/en/seedance2_0)
- [Seedance 2.0 technical report](https://arxiv.org/abs/2604.14148)
- [MuAPI OpenAPI](https://api.muapi.ai/openapi.json)
- [MuAPI Omni task metadata](https://muapi.ai/api/app/get-task-data?name=seedance-2-vip-omni-reference)
- [MuAPI Seedance 2 VIP Extend](https://muapi.ai/playground/seedance-2-vip-extend)

PR0TA defaults are synchronized to the live provider schemas. Re-check `models_get_defaults` before production because provider contracts can change.
