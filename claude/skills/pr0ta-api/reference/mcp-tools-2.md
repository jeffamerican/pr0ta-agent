# PR0TA MCP tool catalog, part 2

Generated from the live MCP server; do not edit. The index is `mcp-tools.md`.

## production

- `production_context_get`(scene_number, shot_number, character_names, include_provider_guidance): Fetch existing PR0TA screenplay breakdown, casting, set, prop, look, and approved reference context for a scene or shot.
- `production_queue_analyze`(**asset_uids**, asset_contexts): Queue Cinematographer or Composer analysis and return a task id.
- `production_queue_asset_create`(**asset**): Create a manual Production Queue item using the same schema as the Queue UI.
- `production_queue_asset_delete`(**asset_uid**): Delete or exclude one Production Queue item.
- `production_queue_asset_update`(**asset_uid**, **updates**): Update a Production Queue item's description, prompts, modality, model, analysis, labels, or saved render settings.
- `production_queue_character_elements_get`(**asset_uid**): Resolve cast and reference elements for one Queue shot before character-consistent generation.
- `production_queue_component_selection_set`(**asset_uid**, image_take_id, audio_take_id): Set the selected image and audio component takes for a composite Queue item.
- `production_queue_list`(include_hidden, offset, limit): List one bounded page of the synthesized Production Queue, including prompts, generated takes, selections, and status.
- `production_queue_prompt_set`(**asset_uid**, **generation_prompt**, component, trim_config, modality): Set a component prompt, trim configuration, or modality for one Queue item.
- `production_queue_refresh`(**asset_uids**, reset_analysis, full_reconstruct): Refresh Queue items from Storyboarding, optionally resetting analysis or reconstructing the full queue.
- `production_queue_regenerate`(**asset_uid**, **generation_params**, generation_prompt, batch_id, batch_label): Queue generation or regeneration for one Production Queue row and return a task id.
- `production_queue_regenerate_batch`(**asset_uids**, **generation_params**): Queue generation or regeneration for several Production Queue rows (each as production_queue_regenerate does).
- `production_queue_request_preview`(**asset_uid**, generation_params): Show what production_queue_regenerate would render for one row, without rendering or storing anything: the row it reaches, the prompt, model, modalit…
- `production_queue_take_favorite`(**asset_uid**, **take_id**, favorite): Favorite a generated take for one Queue item, or remove the favorite with favorite=false.
- `production_queue_take_select`(**asset_uid**, take_id, take_type): Select or clear a generated image, video, or audio take for one Queue item.
- `production_queue_upload_retry`(**asset_id**): Retry permanent-storage recovery for one failed Production Queue asset.

## project

- `project_metadata_get`(keys, lightweight): Read full project metadata or selected top-level keys.
- `project_metadata_patch`(**updates**): Merge top-level project metadata updates with editor authorization.
- `project_rename`(**name**): Rename the project (its display name; the project id, slug and files stay).

## qr

- `qr_code_generate`(data, url, error_correction, dark, light, scale, size, border, version, micro, svg, subject, folder_path): Make a real, scannable QR code as a project image asset (free, no credits, no model): a PNG (optionally also an SVG), read back before it is saved so…
- `qr_code_verify`(**asset_id**, expected_payload, times, count, record): Scan check (free): does an image asset, or sampled frames of a video asset, carry a QR code that actually decodes, and to the expected payload?

## read

- `read_pr0ta_skill`(name, section, reference, offset): Read the PR0TA production playbook.
- `read_web_page`(**url**, max_chars): Open one web page in a browser and return its text as Markdown, after its scripts have run.

## references

- `references_resolve`(**asset_uid**, model): Read the references a Production Queue row's render sends (its reference ledger), without rendering or saving anything: each image, video and audio f…
- `references_settle_in_frame`(**asset_uid**, model): Settle who is in frame for a shot written before the shot list recorded it: one billed classification call whose answer is saved on the shot list (ch…

## review

- `review_submit_assets`(**asset_ids**, title, description, review_notes, allow_download, webhook_url, webhook_secret, recipient_emails): Publish assets to a PR0TA public client review room.

## save

- `save_scene_shotlist`(**scene_number**, stylistic_approach, shots, replace, revision, refresh_scene_context): Save or update the director shotlist for a specific scene.

## score

- `score_bible_get`(): Read the project's score bible: the musical concept, the style core and exclude core every cue's prompt starts from, palette, key centers, tempo fami…
- `score_bible_save`(concept, style_core, exclude_core, palette, key_centers, tempo_family, dialogue_strategy, themes, notes): Save score bible fields.

## screenplay

- `screenplay_draft_beats`(**content**, budgets, script_id): Queue the Writer to draft a scene for every approved beat the script does not cover yet; returns a task.
- `screenplay_import`(filename, asset_id, force): Make a screenplay the PRIMARY script's working draft.
- `screenplay_publish`(title, actual_length_eighths, script_id): Publish the working screenplay as a locked revision and start its breakdown: the Producer and Director reads run, then the breakdown pauses for Creat…
- `screenplay_save`(**content**, new_revision, script_id): Save the complete working draft of one script in the project's library.

## script

- `script_create`(**title**, kind): Create a new, empty script in the project's library and return it (id, title, kind, blockStart).
- `script_supervisor_read_generate`(**script**, **producer_analysis**, **director_analysis**, casting_analysis): Run and persist normalized Script Supervisor scenes, characters, locations, and continuity; returns a task.

## scripts

- `scripts_list`(): List the project's screenplay library: id, title, kind (feature, episode, spot, short, alternate, other), blockStart (its first production scene numb…

## set

- `set_environment_asset_link`(**environment_id**, **asset_id**, **role**, modality, status, pass_type, metadata): Attach an existing project asset to a 3D set environment with a typed role, modality, technical pass, and approval state.
- `set_environment_collider_materialize`(**environment_id**, **world_asset_id**): Download a World Labs Marble world's collider mesh, register it as a project GLB asset, and link it to a 3D set environment as the Blender source so…
- `set_environment_upsert`(**variant_id**, scene_number, status, approved_revision, approval_reason, replace_person_approval, build_brief, revision_notes, render_settings, metadata): Create or revise the 3D environment contract for a canonical Production Design set variant.
- `set_environments_get`(scene_number, include_superseded): List canonical 3D set environments, their Production Design variants, assigned scenes, render contract, and linked Blender, runtime, world, still, vi…

## shot

- `shot_performances_list`(shot_uid, scene_number, shot_number, kinds, limit): List the performances filed on a shot, newest first: human takes recorded in Human Performances, dialogue takes, and camera takes.
- `shot_quality_review`(**asset_id**, force): QC verdict for one generated take (video, still or audio).

## shotlist

- `shotlist_generate`(**scene**, **producer_analysis**, **director_analysis**, workflow_bypasses, bypass_reason): Generate and durably save a Director shot list for one scene; returns a task for polling.
- `shotlist_generate_batch`(**scenes**, **producer_analysis**, **director_analysis**, workflow_bypasses, bypass_reason): Generate and save Director shot lists for multiple scenes in one background task.
- `shotlist_scene_chat`(**scene**, **messages**, producer_analysis, director_analysis): Ask the Director agent to revise or discuss one scene.
- `shotlist_scene_descriptions_generate`(**script_supervisor_data**, producer_analysis, director_analysis): Generate concise Director scene descriptions for Shotlisting; returns a task for polling.
- `shotlist_shots_move`(**from_scene**, **to_scene**, **shot_uids**, dry_run, spanning_sequences): Move shots from one scene's saved shot list to another scene, for coverage filed under the wrong scene (a breakdown re-run that split a scene).

## storyboard

- `storyboard_chunks_list`(scene_number, scene_range_end, max_duration_seconds): List Seedance-ready storyboard beat chunks assembled from screenplay, shotlist, storyboard prompts, and approved references.
- `storyboard_first_frame_propose`(**scene_number**, **shot_number**, **asset_id**, approve, approval_reason, replace_person_approval): Put a ready storyboard image on a shot as its first-frame candidate (the take Storyboarding shows selected).
- `storyboard_generate`(**scene**, **director_shotlist**, **producer_analysis**, **director_analysis**, workflow_bypasses, bypass_reason): Generate and durably save storyboard prompts for one scene; returns a task for polling.
- `storyboard_generate_batch`(**scenes**, **director_shotlists**, **producer_analysis**, **director_analysis**, workflow_bypasses, bypass_reason): Generate and save storyboard prompts for multiple scenes in one background task.
- `storyboard_pdf_export`(scene_number, scene_range_end, scene_numbers, layout, paper, approved_only, skip_empty, fields, include_cover, scene_breaks, title, subtitle, orientation, cover_notes, panels): Export the storyboard as a printable PDF (free) and file it as a project document.
- `storyboard_reference_sheet_generate`(**chunk_id**, variation_count, quality, model, reference_asset_ids, reference_image_urls, include_chunk_reference_urls, storyboard_sheet_prompt, workflow_bypasses, bypass_reason): Generate a GPT Image 2.5 Sunburst optimized Seedance storyboard reference sheet for one beat chunk.
- `storyboard_reference_sheets_list`(chunk_id, limit, offset, include_download): List generated Seedance storyboard reference sheet assets.
- `storyboard_sequences_get`(): List the manual and generated Storyboarding sequence records used by the Storyboarding and Queue pages.
- `storyboard_sequences_save`(**sequences**, replace_scene_numbers): Update Storyboarding sequence records (selected sheets, prompts, references).

## style

- `style_earlier_look_list`(): List the approved pictures made with an earlier look than their style world has now: cast portraits and character sheets, Prep sets, wardrobe looks a…
- `style_package_get`(include_assets): Load the project's style worlds: each world's look line (stylePrompt, compiled from lookSlots), scene assignments, client references and previews.
- `style_package_save`(**styles**, asset_annotations): Persist several style worlds at once and annotate their assets.
- `style_preview_generate`(**style_id**): Render one preview of a Style world's look line on a real moment from its scenes, with the project's default image model.
- `style_restyle`(**key**, again): Restyle one approved picture listed by style_earlier_look_list toward its world's current look: one paid image edit that keeps its people, place and…
- `style_world_assign_scenes`(**style_id**, **scene_numbers**): Replace one alternate Style world's screenplay-scene assignments.
- `style_world_create`(**name**, style_id, scope, look_slots, style_prompt, typography_prompt, usage_notes, scene_numbers, is_default): Create and persist one new Style-page world without replacing existing worlds.
- `style_world_delete`(**style_id**): Delete one Style world while preserving at least one world and a valid default.
- `style_world_update`(**style_id**, name, scope, look_slots, style_prompt, typography_prompt, usage_notes, client_references, match_client_references, make_default): Update one existing Style world without replacing the others: its look (look_slots, compiled into the look line every generation gets), name, scope,…

## submit

- `submit_assets_for_review`(**asset_ids**, title, description, review_notes, allow_download, webhook_url, webhook_secret, recipient_emails): Publish one or more project assets into a public client review room and return a share link.

## supervisor

- `supervisor_review_answer`(**flag_id**, **action**, value, scene_number): Answer one Script Supervisor question.
- `supervisor_review_list`(): List the Script Supervisor's open questions: omissions, removed claims or elements, uncertain classifications, and withheld synopses that verificatio…

## tasks

- `tasks_acknowledge`(**subscription_id**, **client_id**, **workflow_id**, **thread_id**, **event_id**): Acknowledge that the bound agent has accepted responsibility for a completed task.
- `tasks_batch_get`(**task_ids**, detail): Get multiple PR0TA tasks in one MCP call for efficient generation polling.
- `tasks_cancel`(**task_id**): Cancel one queued or running PR0TA task.
- `tasks_completion_events`(**subscription_id**, cursor): Read completion receipts for recovery.
- `tasks_get`(**task_id**, detail): Get one PR0TA task by id and return its canonical status/result.
- `tasks_subscribe`(**request**): Register a durable HTTPS completion receiver bound to one client/workflow/thread.
- `tasks_unsubscribe`(**subscription_id**): Disable completion delivery and pending email escalation for this subscription.
- `tasks_watch`(**subscription_id**, **task_ids**): Add task IDs to a completion subscription.

## transcription

- `transcription_get`(**asset_id**): Get stored transcript text, segments, and flattened word-level timing for a project asset.
- `transcription_start`(**asset_id**, model_id, language, diarization, timestamp_granularity, force): Start Scribe V2 transcription for a project audio or video asset.

## update

- `update_set_references`(**scene_number**, location, **looks**): Save or update production designer set references for a scene.

## video

- `video_cadence_check`(**asset_id**): Measure one video's motion cadence (free): duplicate frames, skipped frames and stalls, generation-chunk seams, post-cut settle jolts and single-subj…
- `video_quality_control_analyze`(**asset_id**, **query**, fps, reasoning_effort, previous_task_id): Submit one project video asset to BytePlus Dola for asynchronous visual quality-control analysis.
- `video_stutter_repair`(**asset_id**, user_requested, force, stabilize): Repair a video's motion cadence (free): inserts or drops frames at skips and stalls, smooths generation seams and trims a settle jolt at the head, sa…

## voices

- `voices_clone`(**request**): Clone an ElevenLabs voice from project audio assets or sample URLs.
- `voices_design`(**request**): Generate ephemeral prompt-designed voice previews.
- `voices_design_commit`(**request**): Commit one prompt-designed voice preview as a permanent voice.
- `voices_list`(provider, search, page_size, include_live, include_custom): Browse searchable TTS voices by provider.
- `voices_speech_to_speech`(**request**): Transform project audio into a selected voice with speech-to-speech.

## world

- `world_generation_submit`(**request**): Submit a World Labs Marble text, single-image, multi-image, 360-panorama, video, or PR0TA depth-panorama world request and return the queued task.
