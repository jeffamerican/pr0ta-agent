# The Verification Loop: Findings and Fixes

> **See also:** `pr0ta-timeline` SKILL.md → "The Verification Loop" for the order of the steps; `pr0ta-editorial` → `reference/verification-protocol.md` for what a ship-quality render must pass.

`post_sequence_analyze` returns `deliveryChecks`; `post_sequence_debug_report` folds the same findings into `warnings[]`; every `post_sequence_save` returns the save-time subset in `validationWarnings.deliveryWarnings`. Each finding has `code`, `severity` (`error`, `warning`, `info`), `message`, the clip, track or asset ids it concerns, and sometimes a `suggestion`.

## Findings

| Code | What it means | Fix |
|---|---|---|
| `letterboxed_source` | A source whose shape is more than 1% off the frame's sits inside it with bars (`barsPercent`): `fit` is `contain` and `transform.scale` is below 0.98 × the cover scale. Overlays (scale below 1, or moved off centre) are never flagged. | `"fit": "cover"`, then `transform.positionX`/`positionY` to keep the subject in frame; or a source shot for this shape. |
| `cover_crops_source` (info) | `cover` crops `croppedPercent` of the source. | Look at the frame (`post_frames_get`); reframe with `positionX`. |
| `stretched_source` | `fit: stretch` distorts people and objects. | `cover` or `contain`. |
| `unknown_source_dimensions` (info) | The source's size was never measured. | `assets_probe` on its asset, then analyze again. |
| `double_audio_risk` | A video's own sound is audible and overlaps an unlinked, audible audio clip of the same media (media key: `sourceMedia.sourceAssetId`, else `assetId`, else `assetUrl` when neither clip has an asset id). One rule, shared by saves, analysis and render. | `post_clips_link` (same media: the audio clip replaces the embedded sound), or `audioEnabled: false` on the video clip. |
| `linked_audio_not_replacing` | An audio clip is linked to a video but is other media (its media key differs, and it was not extracted from that clip), so the link does not silence the video's own sound: both play. | `audioEnabled: false` on the video clip (the finding's `suggestion`), or link the matching audio. |
| `linked_av_out_of_sync` | Linked picture and sound are offset (`start − inPoint` differs). | Align the audio clip's `start` and `inPoint` with the video clip. |
| `adjacent_same_source_slices`, `kind: continuous` | Two back-to-back clips are one continuous take split in two; the "cut" is invisible. | Merge them into one clip, or put a different shot between. |
| `adjacent_same_source_slices`, `kind: jump` (info) | Back-to-back clips jump forward or back inside one take. | Keep only as a deliberate jump cut; otherwise cut away between them. |
| `no_captions` | A social deliverable has audible speech (a dialogue or narration clip, or a video's own sound) and no caption clips. | Caption what is said (`text.role: caption`). |
| `empty_text_clip` | A title-track clip has no `assetUrl`, no `assetId` and empty `text.content`; it renders nothing. | Give it `text.content` or delete it. |
| `slow_motion_not_interpolated` (info while editing, warning on a final export) | A picture clip slowed below 1× repeats frames: no interpolated rendition covers what it plays at its current speed and the sequence frame rate (none made, or the clip changed since). Not reported for stills, text, `fitToFill` clips, or a high-frame-rate source that already has a frame for every slowed frame. | `post_clip_slow_motion` with `engine: "draft"` to judge it; `"topaz"` for delivery (`quote_only` first, then `confirm_credits`). |
| `slow_motion_draft_only` (info while editing, warning on a final export) | The clip's slow motion is a free draft interpolation (ffmpeg), fine to judge, not to ship. | `post_clip_slow_motion` with `engine: "topaz"`. |
| `proxy_missing` (info) | No browser preview proxy for a video source. | Nothing for renders; playback in the Timeline may stall until the proxy is built. |
| `no_verification_render` | No finished full-length render or export stamped with exactly the current saved version (an inline-timeline render or a `from`/`to` section render never counts). | `post_render_start` with `quality: low`, then look and listen. |
| `loudness_unknown` (info) | The latest render carries no loudness measurement. | `audio_meter` over the program. |
| `render_silent` | The latest render has no sound (measured silent, or no audio stream), but the cut definitely has audio: an audible, non-zero-gain audio-track clip, or a video whose `sourceMedia.hasAudio` is true. A video whose audio was never probed does not count. | Check those clips' media, mute and volume; render again and `audio_meter` it. |
| `loudness_out_of_range` | Integrated loudness is off the deliverable's target (`targetLufs`). | Adjust track and clip volumes; render again. |
| `true_peak_over_ceiling` | True peak above −1 dBTP; it will clip after platform encoding. | Lower the loudest track or its peaks. |

The structural lists sit beside them: `gaps` (holes on each track; caption and title holes are fine) and `primaryVisualGaps` (program time no visible video track covers: black in the render), `overlaps`, `sourceShortfalls`, `timelineMediaGaps`, `shortVisualClips`, `reusedMedia` (a source whose same frames appear twice; slices of one take that never overlap are not reuse), and `summary` counts including `letterboxedClipCount`, `adjacentSourceSliceCount` and `deliveryWarningCount`. Render and export results add `renderDiagnostics`, `timelineMediaGaps[]` and `renderedPixelGaps[]`; repair those by frame range (`reference/repairs-and-diagnostics.md`).

## Loudness Targets

| Deliverable | Integrated | True peak |
|---|---|---|
| Social and vertical (Reels, Stories, TikTok, Shorts), web | −14 LUFS (±2) | ≤ −1 dBTP |
| Broadcast | −23 LUFS (±1) (EBU R128; −24 for ATSC A/85) | ≤ −1 dBTP |
| Anything else (festival, presentation) | about −16 LUFS | ≤ −1 dBTP |

The target comes from the sequence's `provenance.deliverable`; a portrait 4:5-or-taller or square frame counts as social. Name the deliverable when you save, so the check measures against the right target.

## Looking at Frames

`post_frames_get` returns one contact sheet of up to 12 frames, filed as an image asset in "/Post/Frame checks" and shown to you with the result. Each tile is labelled with its index, time and clip.

- **With `asset_id`** (a finished render, or any video or image): exact decoded frames. This is what ships.
- **With `sequence_id`**: for each time, the top picture clip's source frame placed by its `fit` and `transform`, with text clips drawn in a stand-in font. Fast, and enough for framing and caption placement; it does not apply Ken Burns, keyframes, effects or transitions.
- `times` (seconds) picks the frames; without it you get the first frame, the last and `count − 2` between. Choose times at cuts, beats, titles, captions, and the hook in the first two seconds.

What to look for: bars or awkward crops, a subject cut off by a cover crop, captions over faces or below the 9:16 safe line, text you cannot read at phone size, black or frozen frames, the first frame (it is the thumbnail) and the last (it is what the viewer takes away).

An MCP client receives the sheet as image content beside the JSON result; REST clients can download the sheet asset (`pr0ta-downloading`).

## Rendering for Checks

`post_render_start` renders the saved sequence. `render_request` takes `from` and `to` (seconds) for a section (a `from` without `to` runs to the last clip's end; a `from` at or past the last clip's end is refused with 400) and `quality: "low"` for a half-size preview; omit them for a full-length, full-size render. Renders and exports are free. Poll `tasks_get` until `succeeded`; the result carries `asset_id`, `renderDiagnostics` and, when measured, `loudness` (`integratedLufs`, `truePeakDbtp`). Every render and export is stamped at creation with `sequence_id` and the saved `sequence_version` it shows; a finished full-length one of the current version clears `no_verification_render`. A section render (`from`/`to`) is stamped `render_range` instead: use it to look at a passage, but it never verifies the cut and its loudness is never read as the cut's. `GET /api/post-production/{project_id}/timeline/verification?sequence_id=` returns the same summary: `latestRender` (the newest full render: `taskId`, `kind`, `version`, `quality`, `finishedAt`, `loudness`, `captions`, `renderWarnings`) and `coversCurrentVersion`. Any save after the render (a new version) needs a new render; creating a snapshot is not a save and does not.
