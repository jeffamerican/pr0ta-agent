# Frame Paint

Use `post_frames_get` with `detail: "native"` and exact source frame indices to locate the defect and inspect the donor. A donor can be the same frame, a neighboring frame, or an aligned clean plate of the same pixel dimensions. For a same-frame clone, pick an offset that samples clean texture.

Call `frame_paint` once per specified frame. Give the target video `asset_id`, a zero-based decoded `frame`, and `regions`. Each region has a target polygon in native `[x, y]` pixels from the top left. The optional `offset_x` and `offset_y` point from each target pixel to its donor. A small `feather` softens the edge inside the polygon.

```json
{
  "asset_id": "<target video ID>",
  "frame": 168,
  "donor_frame": 167,
  "regions": [{
    "points": [[80, 110], [120, 111], [118, 140], [78, 135]],
    "offset_x": 0,
    "offset_y": 0,
    "feather": 2
  }]
}
```

For a separate same-project donor, supply `donor_asset_id` and, for video, `donor_frame`. Supported video is constant frame rate with square pixels and starts with picture at zero. The tool copies existing pixels, uses no generation credits, and saves a transparent PNG patch of the original dimensions. Its `asset_id` identifies the patch. Attach `preview_asset_id` to the review card and name the shot and exact frame. The preview shows the clone composited over the original. If preview storage failed, the result identifies the saved patch and reports that failure.

## Place the patch

For a requested placement, read the current sequence with `post_sequence_get`. Use the `post_frame_paint` title track above the video tracks. Put the patch in a one-frame title clip with `type: "title"`, `mediaKind: "image"`, `audioEnabled: false`, and the patch's `assetId`. Set `framePaint` to `{sourceClipId, sourceAssetId, sourceFrame, fps}` using the exact target clip and the tool's source fields.

The target must be the visible, untransformed picture at that frame and match the sequence's resolution and frame rate. Place the clip at the sequence time of the source frame, allowing for the target clip's in-point. Set its duration to `1/fps`. Replace an earlier patch for that frame on the same track. Keep the target and audio clips intact and save using `post_sequence_save` with the current `baseVersion`. Render a short span around the patch and inspect the repaired frame and its neighbors. The overlay stays tied to its source frame through normal trims and moves.
