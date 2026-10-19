# QR Codes That Scan

Read this before any still, take or cut that must show a working QR code: a product, a poster, a screen, an end card.

## The rule

Never ask an image or video model to draw a QR code from text or a description. The result looks like a QR code and encodes nothing: the finder squares are there, the data is noise, and no phone reads it. Even an edit that starts from a real code keeps it scannable only some of the time. So:

1. **Generate the real code** with `qr_code_generate` (free, no credits, no model).
2. **Place it**: stills by an image edit that uses the code as a reference, motion by compositing in post.
3. **Verify every result** with `qr_code_verify`, and retry or fall back when it fails.

## 1. Generate the code: `qr_code_generate`

Pass `data` (or `url`): the exact text or address the code must open. Short links scan best; long addresses make denser codes that survive edits less well.

| Argument | Meaning |
| --- | --- |
| `error_correction` | `L`, `M`, `Q` or `H`. The default `H` survives 30% damage: keep it for anything edited, lit, warped or compressed. |
| `dark`, `light` | Hex colours (`#000000` on `#ffffff` by default). `light: "transparent"` gives a code to lay over a design. Keep strong contrast, dark modules on a light ground. |
| `scale` or `size` | Pixels per module (default 10), or an exact width in pixels (the quiet zone takes the remainder so modules stay whole). Not both. |
| `border` | Quiet zone in modules. Keep the standard 4; less may not scan. |
| `version` | A fixed size class (1-40); omitted, the smallest that fits. |
| `svg` | Also file an SVG copy for print or post. |
| `subject`, `folder_path` | Name and folder, as for other assets. |

The PNG is read back before it is saved, so a returned `asset_id` always decodes to its data. The asset records `labels.qr_code`, `labels.qr_payload` and the settings. Micro QR codes are refused: phones rarely read them and the scan check cannot verify them.

## 2a. Stills: place by edit, verify, retry

1. Submit an image edit (`generation_submit`, image edit mode, model from `models_preferred`) with the product or scene as the source image and the QR asset as a reference image. Describe where the code goes ("printed flat on the lower right of the box front, square, fully visible, undistorted, high contrast"). Ask for the code to be reproduced exactly, not redrawn or restyled.
2. Set `metadata.expected_qr_payload` to the code's data. Any generation that expects a payload, or uses a generated QR asset as a reference, is scanned automatically when it finishes: the verdict lands on each take as `labels.qr_check` and a failure as a take flag (`qr_code_unreadable` or `qr_code_mismatch`).
3. Read the result (`tasks_get`, or the take's `labels.qr_check`), or run `qr_code_verify` with `expected_payload` yourself.
4. On a failure, retry the edit (fan out two to four edits and keep the ones that pass). Keep the code large in frame, flat and frontal; curved, angled, tiny or heavily stylised placements fail most.
5. Still failing after a few tries: composite the real code onto the generated still with `planar_composite` instead (2b), or ask the person.

A failed check is a flag for the person, never a reason to delete a take on your own: they may prefer a take whose code only needs a post fix.

## 2b. Motion: composite in post

Video models do not hold a code's modules steady across frames. Generate the take without the code (leave a clean, flat area where it belongs), then `planar_composite` it with `qr_data` and the surface's 4 corners: it tracks the surface, matches light, blur and grain, and reports how many frames decode (`pr0ta-hybrid` → "Real Inserts on Flat Surfaces"). A code on a static, front-on area can also be an overlay clip in the timeline (`transform` scale and position; `pr0ta-timeline` → framing and transforms). For an end card, a held still with the code composited is the reliable route.

## 3. Verify the final render: `qr_code_verify`

Run it on every still and on the rendered cut (the render's `asset_id`) wherever the code must scan. Pass `asset_id` and `expected_payload` (a generated QR asset defaults to its own payload). For video, pass `times` (seconds, up to 12) covering when the code is on screen, or `count` for evenly spaced frames.

It returns `status` (`passed` or `failed`), `reason` (`unreadable` or `mismatch`), `payload`, `matches_expected`, the code's `bbox` and per-frame results, and records `qr_check` on the asset (pass `record: false` to only look). Decoding tries two detectors at several scales with thresholds and blur, so a code that fails here is very unlikely to scan on a phone. A drawn, fake code is found but does not decode, so it fails as `unreadable` with a note saying it is drawn.

REST: `POST /api/v2/projects/{project_id}/qr-codes` (same arguments as `qr_code_generate`) and `POST /api/v2/projects/{project_id}/assets/{asset_id}/qr-check` (`expected_payload`, `times`, `count`, `record`).
