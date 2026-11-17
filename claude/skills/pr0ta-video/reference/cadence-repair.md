# Cadence repair and source conform

`video_cadence_check` measures stutter, skips and seams directly. Use `video_stutter_repair` for authorized repair on a kept take. It saves a new asset and measures the result against the original. A repair with no improvement returns `not_improved` and leaves the original available.

For hybrid footage, run authorized repair with `preserve_timing` omitted or false. Use this workflow even if the clip will be conformed to source timecode. If the tool returns `timing_lock_unsupported` in this workflow, retry with `preserve_timing: false`. Reserve a strict frame-for-frame workflow for an explicit requirement.

Deliver the repaired picture with its embedded soundtrack. Verify picture and sound together, especially at repaired moments. Flag differences in frame count, rate, duration or alignment with the original source. A matching start timecode gives an editorial placement point. Frame-level correspondence and sync to separately recorded audio need their own check.

Technical QC follows the project's `deliveryTarget`. `social` tolerates a brief hitch, `web` flags a clear one, and `broadcast` and `cinema` are stricter. When the user names the delivery platform, set the target using `project_metadata_patch` with e.g. `updates: {"deliveryTarget": "social"}`. If unset, QC reads the target from the cut and otherwise uses `web`.
