# Mattes and Alpha for Hybrid Shots

A matte tells the compositor what to keep. For SwitchX it is a grayscale image or video: white keeps the source, black is regenerated, gray blends. This reference covers where mattes come from in PR0TA and how to keep them valid.

## Contents

- Matte sources
- Keyframe mattes for select mode
- Timing and geometry rules
- Edge hygiene
- Reusing Beeble alphas

## Matte Sources

| Source | Output | Use as | Notes |
|---|---|---|---|
| Previous SwitchX take | `result_refs.alpha_asset_id`, a grayscale matte video with the prepared source timing | `custom` with `alpha_media_kind: "video"` | Cheapest and already conformed; reuse it across takes of the same plate |
| `fal-ai/birefnet/v2/video` with `output_mask` enabled | Subject plate plus `mask_video`; PR0TA registers the mask as a second asset with `labels.role = "matte"` and returns `matte_asset_id` and `plate_asset_id` | `custom` | Submit with `generation_submit`: `mode: "video_to_video"`, no prompt, `video_asset_id`, and `parameters: {"model": "Matting", "output_mask": true}`; `refine_foreground` helps hair. The Video Editor's Background Removal panel reaches the same route |
| `fal-ai/sam-3/video` or SAM 3.1 | The source with the mask applied, or detection overlays, plus bounding boxes | Object finding and tracking review only | Not a grayscale matte; derive the matte from BiRefNet or a keyframe once the object is confirmed |
| `bria/video/background-removal` | One composited video; `Transparent` with `webm_vp9` or `mov_proresks` keeps an alpha channel | `custom` after alpha extraction | Submit with `generation_submit`, no prompt, and `parameters: {"background_color": "Transparent", "output_container_and_codec": "webm_vp9"}`. RGBA is not a luma matte; extract the alpha channel before submitting |
| ProRes 4444 plate | Embedded alpha | `custom` | The Resolve plugin extracts it automatically and attaches it as the SwitchX matte |
| Painted or segmented first frame | One grayscale PNG | `select` | Beeble propagates it across the clip; invert it to regenerate inside a region |

## Keyframe Mattes for Select Mode

1. Extract the first frame of the prepared source, not the original upload, so the frame size matches.
2. Produce a grayscale mask with the Image Editor's mask tools or SAM 3 on the image, white for keep and black for regenerate.
3. Save it as a PNG project asset and submit it with `alpha_mode: "select"`, `alpha_asset_id`, and `alpha_media_kind: "image"`.
4. For wardrobe and prop swaps, mask only the region to change and keep the face fully white.

## Timing and Geometry Rules

- A `custom` matte must match the prepared source's frame count exactly. When the frames match but the frame-rate or duration metadata differs (BiRefNet labels a 23.976 fps source's matte as 24 fps), PR0TA re-stamps the matte frame-for-frame; it never resamples, and it rejects a matte with a different frame count.
- Prefer `custom` over `auto` whenever the subject is not clearly visible in the first frames or the plate is longer than 240 frames: `auto` re-detects the subject at the start of every chunk and can regenerate the people instead of keeping them.
- PR0TA rescales a matte to the prepared source dimensions, so aspect ratio must already match.
- Generate mattes from the normalized source asset that PR0TA registers before submission, or from `result_refs.source_asset_id` after a first run, so timing agrees.
- PR0TA chunks a plate over 240 frames automatically and cuts a `custom` matte with the same plan, so submit one full-length matte that matches the prepared source. If you split a plate yourself at a cut, split the matte at the same frame.

## Edge Hygiene

- Hair, motion blur, and semi-transparent edges need soft mattes; BiRefNet's `Matting` model and `refine_foreground` help.
- Erode a matte slightly when halos appear, and dilate it when the kept subject loses its outline. PR0TA has no dedicated erode tool; adjust the mask in the Image Editor for keyframes or regenerate the matte with a different BiRefNet model for video.
- Keep tracking markers and set edges inside the kept region only when the shot needs them for camera inference; masked-out markers cannot help SwitchX track.
- Never let a matte carry appearance: it is data, not a look.

## Reusing Beeble Alphas

Every completed SwitchX video task registers Beeble's own alpha with `labels.role = "switchx_alpha"` and links it to the render through `source_render_asset_id`. Reuse it as the `custom` matte on the next take of the same plate to stabilize identity across iterations, and record the alpha asset ID with `memory_record_decision` once the shot is approved.
