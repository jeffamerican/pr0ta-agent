# PR0TA MCP tool catalog, part 1

Generated from the live MCP server; do not edit. The index is `mcp-tools.md`.

## agent

- `agent_chat_orchestrate_prompt`(**creative_brief**, topic, references, guidance_package, role_chain, optional_roles, target, prompt_profile, context_scope, memory_scope, authority_plan, subject_presence, reference_preflight_mode, workflow_key, timeout_seconds, request_id): Queue one isolated multi-department workflow that converts a creative brief and ordered references into a terminal Cinematographer provider-ready pro…
- `agent_chat_resume`(**retry_token**): Resume a retryable failed prompt-orchestration task from its preserved department checkpoint.
- `agent_chat_send`(**role**, **topic**, **message**, attachments, generation_mode, request_id): Send a project-scoped message to a PR0TA department agent using the same chat, project context, credits, persistence, and tool runtime as the app.

## assets

- `assets_annotations_batch_update`(**annotations**): Annotate up to 100 project assets in one call.
- `assets_annotations_update`(asset_id, url, tags, notes, labels, keywords, category, reference_type, character_name, set_name, prop_name, look_name, subject, scene_number, shot_number, take_number, auto_increment_take): Write tags, notes, labels, and semantic reference metadata to one project asset.
- `assets_download`(**asset_id**, as_attachment, artifact): Alias for assets_get_download_link.
- `assets_favorite_set`(**asset_id**, **favorite**): Favorite or unfavorite a project asset for Prep and Production curation.
- `assets_get_download_link`(**asset_id**, as_attachment, artifact): Get a signed/proxy download handoff for one asset.
- `assets_get_download_links`(**asset_ids**, as_attachment, artifact): Get signed/proxy download handoffs for multiple assets in one MCP call.
- `assets_import_url`(**url**, subject, category, labels, folder_path): Import a public image, video or audio file from a web address into the project as a ready asset (free): PR0TA downloads it server-side, so no upload…
- `assets_list`(offset, limit, kind, category, browser_category, reference_type, subject, source, task_id, q, favorite_only, asset_ids, folder_path, recursive, include_virtual_references, include_download, compact): List PR0TA project assets with simple filters.
- `assets_probe`(**asset_ids**, refresh): Measure video, image and audio assets (free): width, height, aspect_ratio, orientation, fps, duration_seconds, has_audio and codecs, read from each f…
- `assets_trim`(**asset_id**, **asset_type**, **in_point**, **out_point**, category, subject, idempotency_key, background): Trim a project audio or video asset into a new registered derivative.
- `assets_upload_batch_start`(**files**, folder_path): Create signed upload handoffs for multiple assets in one MCP call.
- `assets_upload_finalize`(**asset_id**, byte_size, checksum_sha256, duration_ms, metadata, category, subject, labels, status, folder_path): Finalize a signed upload after its PUT succeeds: verifies the stored object and marks the asset ready.
- `assets_upload_start`(**filename**, content_type, kind, folder_path, idempotency_key, checksum_sha256): Create an asset placeholder and signed upload handoff.

## audio

- `audio_analyze`(sequence_id, from_time, to_time, windows, track, tracks): Predict timeline audio levels for one range or multiple windows.
- `audio_meter`(asset_id, sequence_id, from_time, to_time, windows, track, tracks, allow_long, timeout_seconds): Run actual LUFS/true-peak metering for one short range or multiple short windows of a sequence.
- `audio_stem_separate`(**asset_id**, model_id, prompt, options): Separate a project audio or video asset into stems (paid: Fal's price for its length): Demucs splits music into vocals, drums, bass and other, so you…

## beat

- `beat_sheet_approve`(structure, beats, script_id): Record a script's beat sheet as approved so screenplay drafting follows it.
- `beat_sheet_generate`(**prompt**, structure, logline, template, quality_gate, script_id): Queue the Story Editor to write a script's beat sheet; returns a task to poll with tasks_get.

## blender

- `blender_job_submit`(**request**): Build or revise a canonical set in the isolated Blender worker, optionally starting from an existing self-contained .blend, GLB, or FBX asset.

## breakdown

- `breakdown_element_review_decide`(**scene_number**, **fingerprint**, **version**, **mention_id**, **action**, target_id): Decide one element mention in a scene's element review: link it to target_id, keep it separate, leave it unresolved, or exclude it.
- `breakdown_rerun`(scenes, force): Rerun the breakdown of the published screenplay.
- `breakdown_status`(): Report the published screenplay's breakdown: each stage's status (producer, director, script_supervisor, casting, production_designer, stylist, propm…

## bug

- `bug_report_create`(**title**, **description**, severity, steps_to_reproduce, expected_behavior, actual_behavior, error_messages, screenshot_url, additional_context): Create an internal bug report for the PR0TA developer team.

## cast

- `cast_list_get`(): Load the Casting-page cast list with enriched portrait, character-sheet, and voice fields.
- `cast_list_save`(cast_members, reconcile_existing, merge): Atomically persist the Casting-page cast list to castingRead, castingIndex, and cast CSV.

## casting

- `casting_avatar_demo_generate`(**request**): Queue an avatar performance demo from a cast portrait and voice sample.
- `casting_character_sheet_prompt_resolve`(**character**, portrait_asset_id, portrait_url, casting_prompt, voice_prompt, sample_line): Resolve the app's cinematic character-design-sheet brief for a cast member.
- `casting_descriptive_prompt_generate`(image_asset_id, image_url, character, current_prompt): Generate a detailed casting prompt from an approved portrait image.
- `casting_portrait_prompt_write`(**character**, direction, save): Have the Casting Director write a character's portrait prompt and save it to the cast record, where Casting shows it (Portrait tab).
- `casting_read_generate`(**script**, **producer_analysis**, **director_analysis**, script_supervisor_characters): Run and persist the Casting breakdown and canonical cast list; returns a task for polling.
- `casting_voice_design`(**request**): Design and persist a MiniMax/Fal voice for one project cast member.
- `casting_voice_sample_generate`(**request**): Generate or queue a named cast-member voice sample.

## character

- `character_consistency_get`(character_id, name): Resolve the complete provider-ready consistency bundle for a character by id or name.

## consistency

- `consistency_resources_create`(**resource_type**, **resource**): Register a trained Seedance Character or Kling Element with project references.
- `consistency_resources_delete`(**resource_type**, **resource_id**): Delete one stored Seedance Character or Kling Element record.
- `consistency_resources_get`(**resource_type**, **resource_id**): Get one stored Seedance Character or Kling Element.
- `consistency_resources_list`(**resource_type**): List stored Seedance Characters or Kling Elements for the project.
- `consistency_resources_update`(**resource_type**, **resource_id**, **updates**): Update references, labels, metadata, name, or archive state for a consistency resource.

## cut

- `cut_quality_review`(asset_id, render_task_id, intent, force): QC verdict for an assembled cut (free).

## department

- `department_heads_get`(start_scene, end_scene, include_bootstrap): Load production-design, character-look, and prop Prep data using the same partitioned storage as the Locations, Looks, and Props pages.
- `department_heads_save`(**department**, **scenes**, breakdown, library, authoritative_scene_numbers): Persist Locations, Looks, or Props page data through the authoritative department-head partitioned-storage workflow.
- `department_read_generate`(**department**, **scenes**, **producer_analysis**, **director_analysis**, item_id): Generate and persist Locations, Looks, or Props department reads for one or more scenes.

## development

- `development_logline_set`(**logline**, approve, script_id): Save a script's working logline; with approve=true also record it as the approved logline the beat sheet and screenplay build on.

## direction

- `direction_approve`(producer_read, director_read): Approve Creative Direction: accept the Producer and Director reads (optionally edited) and let the Script Supervisor and departments run.

## director

- `director_read_generate`(**script**, **producer_analysis**): Run and persist the Director breakdown for a screenplay; returns a task for polling.

## document

- `document_add_asset`(**asset_id**, filename): Add an attachment to the documents.
- `document_add_text`(**filename**, **content**): Add a text document (treatment, outline, research, or a .fountain/.txt screenplay) to the project's documents.
- `document_read`(asset_id, filename, offset, max_chars): Read a document's text.

## documents

- `documents_list`(): List the project's development documents (treatments, outlines, uploaded screenplays).

## enable

- `enable_studio_mode`(): Enable Studio mode for the current project so review-room tools can create submissions, review rounds, and public share links.

## generation

- `generation_batch_submit`(**requests**): Submit up to ten PR0TA generation requests, including speech, sound effects, music, 3D, and Lipsync jobs, and return queued tasks.
- `generation_submit`(**request**): Submit one PR0TA generation request, including image, video, motion, 3D, lipsync, speech, sound effects, or music, and return the queued task.

## get

- `get_breakdown_element_review`(**scene_number**, offset, limit): Read saved, source-cited element types, presence, identity suggestions and reviewer decisions for a scene.
- `get_character_references`(**character_name**): Retrieve character reference data: portrait URLs, physical description, voice configuration, wardrobe notes, and look timeline from casting read.
- `get_review_annotations`(submission_id, review_round_id, resolution_status): Retrieve client review comments, decisions, annotations, and time-coded feedback for the project.
- `get_scene_breakdown`(**scene_number**, scene_range_end): Retrieve the script supervisor's scene breakdown for one or more scenes.
- `get_scene_shotlist`(**scene_number**, offset, compact): Retrieve the director's shot list for a scene, including shot number, size, angle, lens, aspect ratio, movement, duration, description, action, and c…
- `get_screenplay_text`(scene_number, offset, limit, include_workspace_context, working_draft, script_id, workspace_session_id): Retrieve the screenplay.
- `get_set_references`(scene_number, location): Retrieve production design reference images and descriptions for a location or scene.
- `get_shot_assets`(**scene_number**, **shot_number**): Retrieve generated media assets (video takes, audio takes, storyboard frames) for a specific shot identified by scene and shot number.

## grounded

- `grounded_web_search`(**query**, max_results): Search the web with your model provider's search and return an answer with its sources.

## hybrid

- `hybrid_generation_capabilities`(): Read Hybrid Studio supported operations, models, and reference roles without generating.
- `hybrid_sequences_apply_setup`(**sequence_id**, **request**): Explicitly apply a representative background/settings to selected matching-continuity shots.
- `hybrid_sequences_approve`(**sequence_id**, **request**): Record user approval of a reviewed current-revision result.
- `hybrid_sequences_create`(**request**): Import an edited project video and start non-generative cut/coverage analysis.
- `hybrid_sequences_generate`(**sequence_id**, **request**): Spend credits on remaining shots in an approved representative's continuity state.
- `hybrid_sequences_get`(**sequence_id**): Read the sequence revision, exact frame cuts, coverage setups, approvals and batch plans.
- `hybrid_sequences_job`(**sequence_id**, **request**): Prepare reviewed cuts as individual shot assets, or assemble approved outputs in original order with source audio.
- `hybrid_sequences_list`(): List project Hybrid Production sequences in Post.
- `hybrid_sequences_update`(**sequence_id**, **request**): Save reviewed cuts, coverage membership, representatives and continuity states.
- `hybrid_shot_generate`(**shot_id**, **request**): Submit a saved immutable Hybrid shot revision through unified generation.
- `hybrid_shots_create`(**request**): Create saved Hybrid Studio shots.
- `hybrid_shots_get`(**shot_id**, revision): Get saved Hybrid Studio shots.
- `hybrid_shots_list`(): List saved Hybrid Studio shots.
- `hybrid_shots_update`(**shot_id**, **request**): Update saved Hybrid Studio shots.

## memory

- `memory_claim_update`(**claim_id**, **status**, supersedes_claim_id): Approve, reject, supersede, or return a memory claim to candidate status; supply supersedes_claim_id for an exact replacement.
- `memory_claims_list`(status, department, scope_type, scope_id, include_system_claims, offset, limit): List memory claims with the same filters as the Memory workspace.
- `memory_conflicts_list`(): List unresolved and historical conflicts detected in ProtaFilm|memory.
- `memory_context_pack`(task_intent, scope): Get the current, role-scoped ProtaFilm|memory snapshot for this agent.
- `memory_get_confirmation`(): Resolve the latest eligible explicit user approval for a durable memory write in this role's global project chat.
- `memory_graph`(lens, scene, department, offset, limit): Get a curated ProtaFilm|memory graph lens.
- `memory_ingest_app`(): Ingest current application state into ProtaFilm|memory claims.
- `memory_overview`(): Get the complete ProtaFilm|memory overview and status counts.
- `memory_propose_alternate`(**statement**, semantic_key, department, scope_type, scope_id, evidence, task_id, memory_snapshot_id): Preserve a creative option without making it current production authority.
- `memory_propose_change`(**statement**, semantic_key, replaces_claim_id, department, scope_type, scope_id, evidence, task_id, memory_snapshot_id, expected_head_ids, relationship_hint): Propose evidence-backed current project knowledge without rewriting history.
- `memory_record_decision`(**decision**, department, scope_type, scope_id, source_claim_id, approved_asset_id, semantic_key, replaces_claim_id, memory_snapshot_id, expected_head_ids, user_confirmation_ref): Record a durable user production decision in Current ProtaFilm|memory.
- `memory_record_note`(title, **body**, department, scope_type, scope_id): Propose an unconfirmed agent observation for later review without making it Current.
- `memory_report_conflict`(**statement**, semantic_key, department, scope_type, scope_id, evidence, task_id, memory_snapshot_id, expected_head_ids): Report evidence that may contradict current project memory for internal review.
- `memory_request_confirmation`(**decision**, **semantic_key**, **approved_asset_id**): Ask the connected authenticated user to approve one exact Project Bible decision, then return a short-lived confirmation token.
- `memory_search`(query, department, scope_type, scope_id, limit): Search ProtaFilm|memory claims for the current project.
- `memory_source_create`(**source**): Register a source that ProtaFilm|memory can process into claims.
- `memory_source_process`(**source_id**): Process one registered source into memory claims.
- `memory_sources_list`(): List uploaded, manual, and application-derived memory sources.

## models

- `models_get_defaults`(**model_id**): Get PR0TA parameter schema and compatible generation request defaults when available.
- `models_list`(generator, image_kind, search, offset, limit, curated_only, modality): Search the complete PR0TA model and provider-tool catalog with optional category filters.
- `models_preferred`(modality): Get the model to use for a modality: the user's Settings → Tools default, else the admin's top pinned model.

## music

- `music_analyze`(**asset_id**, min_bpm, max_bpm, beats_per_bar, include_transients, include_beats, include_downbeats): Start or return cached beat/downbeat/transient analysis for a music audio asset.

## narration

- `narration_materialize_to_post`(sequence_name, base_version, lock_token): Materialize narration cuts into the post-production sequence.
- `narration_timeline_get`(): Load the complete narration timeline for a project.

## post

- `post_clip_slow_motion`(clip_id, sequence_id, **engine**, quote_only, confirm_credits, idempotency_key, lock_token, asset_id, source_in, source_out, speed, fps): Make smooth slow motion for a slowed clip (|speed| < 1): interpolated frames, not repeated ones.
- `post_clips_link`(**video_clip_id**, **audio_clip_ids**, sequence_id, mute_video_audio, lock_token): Link a video clip to its sound on an audio track so they move and trim together.
- `post_export_start`(export_request, sequence_id): Start an async final master export of a saved sequence (free, no credits).
- `post_frames_get`(asset_id, sequence_id, times, count, detail, region): Look at frames (free, no credits): a contact sheet of up to 12 frames, filed as an image asset and shown to you.
- `post_render_start`(render_request, sequence_id): Start an async preview render of a saved sequence.
- `post_sequence_analyze`(sequence_id): Analyze a saved sequence before rendering or calling it done (free).
- `post_sequence_debug_report`(sequence_id): Render-risk report for a saved sequence (free): retimed clips, source shortfalls, media gaps, audio track summary, and one warnings[] list (code, sev…
- `post_sequence_get`(sequence_id): Load a saved post-production sequence.
- `post_sequence_save`(**timeline**, sequence_id, merge_existing, lock_token, provenance): Save or patch a post-production sequence.

## prep

- `prep_production_capabilities`(): List the MCP tools that map to every PR0TA Prep and Production page.

## producer

- `producer_read_generate`(**script**): Run and persist the Producer breakdown for a screenplay; returns a task for polling.

## production

- `production_context_get`(scene_number, shot_number, character_names, include_provider_guidance): Fetch existing PR0TA screenplay breakdown, casting, set, prop, look, and approved reference context for a scene or shot.
- `production_queue_analyze`(**asset_uids**, asset_contexts): Queue Cinematographer or Composer analysis and return a task id.
- `production_queue_asset_create`(**asset**): Create a manual Production Queue item using the same schema as the Queue UI.
- `production_queue_asset_delete`(**asset_uid**): Delete or exclude one Production Queue item.
- `production_queue_asset_update`(**asset_uid**, **updates**): Update a Production Queue item's description, prompts, modality, model, analysis, or labels.
- `production_queue_character_elements_get`(**asset_uid**): Resolve cast and reference elements for one Queue shot before character-consistent generation.
- `production_queue_component_selection_set`(**asset_uid**, image_take_id, audio_take_id): Set the selected image and audio component takes for a composite Queue item.
- `production_queue_list`(include_hidden, offset, limit): List one bounded page of the synthesized Production Queue, including prompts, generated takes, selections, and status.
- `production_queue_prompt_set`(**asset_uid**, **generation_prompt**, component, trim_config, modality): Set a component prompt, trim configuration, or modality for one Queue item.
- `production_queue_refresh`(**asset_uids**, reset_analysis, full_reconstruct): Refresh Queue items from Storyboarding, optionally resetting analysis or reconstructing the full queue.
- `production_queue_regenerate`(**asset_uid**, **generation_params**, generation_prompt, batch_id, batch_label): Queue generation or regeneration for one Production Queue item and return a task id.
- `production_queue_regenerate_batch`(**asset_uids**, **generation_params**): Queue generation or regeneration for multiple Production Queue items.
- `production_queue_take_favorite`(**asset_uid**, **take_id**, favorite): Favorite a generated take for one Queue item, or remove the favorite with favorite=false.
- `production_queue_take_select`(**asset_uid**, take_id, take_type): Select or clear a generated image, video, or audio take for one Queue item.
- `production_queue_upload_retry`(**asset_id**): Retry permanent-storage recovery for one failed Production Queue asset.

## project

- `project_metadata_get`(keys, lightweight): Read full project metadata or selected top-level keys.
- `project_metadata_patch`(**updates**): Merge top-level project metadata updates with editor authorization.

## read

- `read_pr0ta_skill`(name, section, reference, offset): Read the PR0TA production playbook.
- `read_web_page`(**url**, max_chars): Open one web page in a browser and return its text as Markdown, after its scripts have run.

## review

- `review_submit_assets`(**asset_ids**, title, description, review_notes, allow_download, webhook_url, webhook_secret, recipient_emails): Publish assets to a PR0TA public client review room.

## save

- `save_scene_shotlist`(**scene_number**, stylistic_approach, **shots**): Save or update the director shotlist for a specific scene.

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
- `set_environment_upsert`(**variant_id**, scene_number, status, build_brief, revision_notes, render_settings, metadata): Create or revise the 3D environment contract for a canonical Production Design set variant.
- `set_environments_get`(scene_number, include_superseded): List canonical 3D set environments, their Production Design variants, assigned scenes, render contract, and linked Blender, runtime, world, still, vi…

## shot

- `shot_performances_list`(shot_uid, scene_number, shot_number, kinds, limit): List the performances filed on a shot, newest first: human takes recorded in Human Performances, dialogue takes, and camera takes.
- `shot_quality_review`(**asset_id**, force): QC verdict for one generated take (video, still or audio).
