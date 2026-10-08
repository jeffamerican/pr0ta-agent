# PR0TA MCP tool catalog, part 2

Generated from the live MCP server; do not edit. The index is `mcp-tools.md`.

## shotlist

- `shotlist_generate`(**scene**, **producer_analysis**, **director_analysis**): Generate and durably save a Director shot list for one scene; returns a task for polling.
- `shotlist_generate_batch`(**scenes**, **producer_analysis**, **director_analysis**): Generate and save Director shot lists for multiple scenes in one background task.
- `shotlist_scene_chat`(**scene**, **messages**, producer_analysis, director_analysis): Ask the Director agent to revise or discuss one scene.
- `shotlist_scene_descriptions_generate`(**script_supervisor_data**, producer_analysis, director_analysis): Generate concise Director scene descriptions for Shotlisting; returns a task for polling.

## storyboard

- `storyboard_chunks_list`(scene_number, scene_range_end, max_duration_seconds): List Seedance-ready storyboard beat chunks assembled from screenplay, shotlist, storyboard prompts, and approved references.
- `storyboard_first_frame_propose`(**scene_number**, **shot_number**, **asset_id**): Put a ready storyboard image on a shot as its first-frame candidate (the take Storyboarding shows selected).
- `storyboard_generate`(**scene**, **director_shotlist**, **producer_analysis**, **director_analysis**): Generate and durably save storyboard prompts for one scene; returns a task for polling.
- `storyboard_generate_batch`(**scenes**, **director_shotlists**, **producer_analysis**, **director_analysis**): Generate and save storyboard prompts for multiple scenes in one background task.
- `storyboard_reference_sheet_generate`(**chunk_id**, variation_count, quality, model, reference_asset_ids, reference_image_urls, include_chunk_reference_urls, storyboard_sheet_prompt): Generate a GPT Image 2.5 Sunburst optimized Seedance storyboard reference sheet for one beat chunk.
- `storyboard_reference_sheets_list`(chunk_id, limit, offset, include_download): List generated Seedance storyboard reference sheet assets.
- `storyboard_sequences_get`(): List the manual and generated Storyboarding sequence records used by the Storyboarding and Queue pages.
- `storyboard_sequences_save`(**sequences**, replace_scene_numbers): Update Storyboarding sequence records (selected sheets, prompts, references).

## style

- `style_package_get`(include_assets): Load the Style-page package from project metadata and optionally include persisted style-reference assets.
- `style_package_save`(**styles**, asset_annotations): Persist a complete Style-page package and annotate its PR0TA assets.
- `style_world_assign_scenes`(**style_id**, **scene_numbers**): Replace one alternate Style world's screenplay-scene assignments.
- `style_world_create`(**name**, style_id, scope, style_prompt, typography_prompt, usage_notes, scene_numbers, is_default): Create and persist one new Style-page world without replacing existing worlds.
- `style_world_delete`(**style_id**): Delete one Style world while preserving at least one world and a valid default.
- `style_world_update`(**style_id**, name, scope, style_prompt, typography_prompt, usage_notes, generation_overrides, make_default): Update and persist one existing Style world without replacing unrelated worlds.

## submit

- `submit_assets_for_review`(**asset_ids**, title, description, review_notes, allow_download, webhook_url, webhook_secret): Publish one or more project assets into a public client review room and return a share link.

## supervisor

- `supervisor_review_answer`(**flag_id**, **action**, value, scene_number): Answer one Script Supervisor question.
- `supervisor_review_list`(): List the Script Supervisor's open questions: omissions, removed claims or elements, uncertain classifications, and withheld synopses that verificatio…

## tasks

- `tasks_acknowledge`(**subscription_id**, **client_id**, **workflow_id**, **thread_id**, **event_id**): Acknowledge that the bound agent has accepted responsibility for a completed task.
- `tasks_batch_get`(**task_ids**): Get multiple PR0TA tasks in one MCP call for efficient generation polling.
- `tasks_cancel`(**task_id**): Cancel one queued or running PR0TA task.
- `tasks_completion_events`(**subscription_id**, cursor): Read completion receipts for recovery.
- `tasks_get`(**task_id**): Get one PR0TA task by id and return its canonical status/result.
- `tasks_subscribe`(**request**): Register a durable HTTPS completion receiver bound to one client/workflow/thread.
- `tasks_unsubscribe`(**subscription_id**): Disable completion delivery and pending email escalation for this subscription.
- `tasks_watch`(**subscription_id**, **task_ids**): Add task IDs to a completion subscription.

## transcription

- `transcription_get`(**asset_id**): Get stored transcript text, segments, and flattened word-level timing for a project asset.
- `transcription_start`(**asset_id**, model_id, language, diarization, timestamp_granularity, force): Start Scribe V2 transcription for a project audio or video asset.

## update

- `update_set_references`(**scene_number**, location, **looks**): Save or update production designer set references for a scene.

## video

- `video_cadence_check`(**asset_id**): Measure one video's motion cadence (free): duplicate frames, skipped frames and stalls, generation-chunk seams, post-cut settle jolts, camera wobble…
- `video_quality_control_analyze`(**asset_id**, **query**, fps, reasoning_effort, previous_task_id): Submit one project video asset to BytePlus Dola for asynchronous visual quality-control analysis.
- `video_stutter_repair`(**asset_id**, user_requested, force): Repair a video's motion cadence (free): inserts or drops frames at skips and stalls, smooths generation seams, trims a settle jolt at the head and st…

## voices

- `voices_clone`(**request**): Clone an ElevenLabs voice from project audio assets or sample URLs.
- `voices_design`(**request**): Generate ephemeral prompt-designed voice previews.
- `voices_design_commit`(**request**): Commit one prompt-designed voice preview as a permanent voice.
- `voices_list`(provider, search, page_size, include_live, include_custom): Browse searchable TTS voices by provider.
- `voices_speech_to_speech`(**request**): Transform project audio into a selected voice with speech-to-speech.

## world

- `world_generation_submit`(**request**): Submit a World Labs Marble text, single-image, multi-image, 360-panorama, video, or PR0TA depth-panorama world request and return the queued task.
