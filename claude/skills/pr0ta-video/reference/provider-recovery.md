# Video Provider Recovery

Use this reference only after reading a task's terminal error. Preserve the original error and classify it before changing prompts or models.

## Allowed-Content False Positives

This ladder is for content that complies with PR0TA policy, provider policy, law, and the user's brief but was incorrectly classified. It must never be used to evade a real safety restriction.

1. Confirm the error is a content classification, not an invalid field, missing reference, or quota failure.
2. If the exact endpoint exposes a tolerance/safety control, retry once at the highest policy-compliant setting.
3. If it still rejects, switch to a live suitable fallback: Grok Imagine, then LTX 2.3, then WAN 2.7/2.6/2.5 as available.
4. Rewrite or soften the creative shot only after suitable alternate providers also reject it, because rewriting changes the user's intent.

Positive prompt framing does not repair a true provider classifier rejection. Preserve the evidence and switch only when the content is allowed.

## Provider Stalls

Treat unchanged `running` progress for more than three minutes as a stall unless the endpoint documents a longer no-progress phase.

1. First stall: cancel and resubmit the identical request once to the same provider.
2. Second stall on the same shot: cancel and pivot to a compatible provider rather than making a third same-backend attempt.
3. If both providers stall: stop submitting and surface the state before using a third model class or replacing motion with a still.

Do not pivot silently when the shot has locked character, matched motion, camera, audio, or keyframe constraints. A different provider can produce a materially different take.

## Common Seedance 2.0 Omni to Kling V3 I2V Pivot

| Intent | Seedance 2.0 Omni | Kling V3 I2V |
|---|---|---|
| Project start image | `reference_image_asset_ids: ["..."]` or `image_asset_id` | `start_image_asset_id: "..."` |
| URL start image | `reference_image_urls: ["..."]` | `start_image_url: "..."` |
| Prompt token | lowercase positional `@image1` when role binding matters | `@Image1` for the start image |
| Duration | integer 4–15 | integer 3–15 |
| Character lock | Seedance character resource | Kling Element bundle instead |
| Camera control | prompt/video reference | structured `camera_control` where supported |

Translate creative intent, not just field names. Re-read `video-reference-field-matrix.md` and the target model's prompting reference before submitting the pivot.
