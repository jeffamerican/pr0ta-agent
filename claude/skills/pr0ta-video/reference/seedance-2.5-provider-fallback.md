# Seedance 2.5 provider fallback

## Real-person fallback

ModelArk refuses input images or a driving video that may show a real person (`InputImageSensitiveContentDetected.PrivacyInformation`, "may contain real person"), which includes realistic character references from Prep and live-action plates. PR0TA resubmits such a refusal as the same task on MuAPI on every path (generation, Production Queue, Hybrid Studio):

| Refused route | MuAPI route |
|---|---|
| `byteplus/seedance-2.5` | `muapi/seedance-2.5-omni-reference` |
| `byteplus/seedance-2.5-image-to-video` | `muapi/seedance-2.5-image-to-video` |
| `byteplus/seedance-2.5-first-last-frame` | `muapi/seedance-2.5-first-last-frame` |
| `byteplus/seedance-2.5-video-edit` | `muapi/seedance-2.5-video-edit` |
| `byteplus/seedance-2.5-video-extend` | `muapi/seedance-2.5-video-extend` |

The fallback keeps the requested resolution: a `1080p` request renders on the route's `-1080p` variant, `480p` on `-480p`, and 720p (or no resolution) on the unsuffixed route. A draft keeps the unsuffixed route, the one that drafts at 480p and finishes at 1080p. The refused attempt is hidden, the submission result carries `model_fallback`, and the Queue notes it on the take. Do not resubmit it yourself; mention the switch in one line.

"Output audio ... copyright" under that code refuses the soundtrack, not a person (`seedance-2.5-prompt-craft.md`).
