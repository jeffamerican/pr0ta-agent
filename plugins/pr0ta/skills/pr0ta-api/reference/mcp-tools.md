# PR0TA MCP tool catalog

Generated from the live MCP server; do not edit. Every project-scoped tool also
takes `project_id`. Arguments in **bold** are required. For which tools serve
which page, call `prep_production_capabilities`; for a tool's full schema, see
the tool listing in your MCP client.

The catalog is split into parts that each fit one read. Find the tool's group
below, then read the part named beside it (another reference file of this skill).

## Tools by group

- **agent** (`mcp-tools-1.md`): agent_chat_orchestrate_prompt, agent_chat_resume, agent_chat_send
- **assets** (`mcp-tools-1.md`): assets_annotations_batch_update, assets_annotations_update, assets_download, assets_favorite_set, assets_get_download_link, assets_get_download_links, assets_import_url, assets_list, assets_probe, assets_trim, assets_upload_batch_start, assets_upload_finalize, assets_upload_start
- **audio** (`mcp-tools-1.md`): audio_analyze, audio_meter, audio_stem_separate
- **beat** (`mcp-tools-1.md`): beat_sheet_approve, beat_sheet_generate
- **blender** (`mcp-tools-1.md`): blender_job_submit
- **breakdown** (`mcp-tools-1.md`): breakdown_element_review_decide, breakdown_rerun, breakdown_status
- **bug** (`mcp-tools-1.md`): bug_report_create
- **cast** (`mcp-tools-1.md`): cast_list_get, cast_list_save
- **casting** (`mcp-tools-1.md`): casting_avatar_demo_generate, casting_character_sheet_prompt_resolve, casting_descriptive_prompt_generate, casting_portrait_prompt_write, casting_read_generate, casting_voice_design, casting_voice_sample_generate
- **character** (`mcp-tools-1.md`): character_consistency_get
- **consistency** (`mcp-tools-1.md`): consistency_resources_create, consistency_resources_delete, consistency_resources_get, consistency_resources_list, consistency_resources_update
- **cut** (`mcp-tools-1.md`): cut_quality_review
- **department** (`mcp-tools-1.md`): department_heads_get, department_heads_save, department_read_generate
- **development** (`mcp-tools-1.md`): development_logline_set
- **direction** (`mcp-tools-1.md`): direction_approve
- **director** (`mcp-tools-1.md`): director_read_generate
- **document** (`mcp-tools-1.md`): document_add_asset, document_add_text, document_read
- **documents** (`mcp-tools-1.md`): documents_list
- **enable** (`mcp-tools-1.md`): enable_studio_mode
- **generation** (`mcp-tools-1.md`): generation_batch_submit, generation_submit
- **get** (`mcp-tools-1.md`): get_breakdown_element_review, get_character_references, get_review_annotations, get_scene_breakdown, get_scene_shotlist, get_screenplay_text, get_set_references, get_shot_assets
- **grounded** (`mcp-tools-1.md`): grounded_web_search
- **hybrid** (`mcp-tools-1.md`): hybrid_generation_capabilities, hybrid_sequences_apply_setup, hybrid_sequences_approve, hybrid_sequences_create, hybrid_sequences_generate, hybrid_sequences_get, hybrid_sequences_job, hybrid_sequences_list, hybrid_sequences_update, hybrid_shot_generate, hybrid_shots_create, hybrid_shots_get, hybrid_shots_list, hybrid_shots_update
- **memory** (`mcp-tools-1.md`): memory_claim_update, memory_claims_list, memory_conflicts_list, memory_context_pack, memory_get_confirmation, memory_graph, memory_ingest_app, memory_overview, memory_propose_alternate, memory_propose_change, memory_record_decision, memory_record_note, memory_report_conflict, memory_request_confirmation, memory_search, memory_source_create, memory_source_process, memory_sources_list
- **models** (`mcp-tools-1.md`): models_get_defaults, models_list, models_preferred
- **music** (`mcp-tools-1.md`): music_analyze
- **narration** (`mcp-tools-1.md`): narration_materialize_to_post, narration_timeline_get
- **post** (`mcp-tools-1.md`): post_clip_slow_motion, post_clips_link, post_export_start, post_frames_get, post_render_start, post_sequence_analyze, post_sequence_debug_report, post_sequence_get, post_sequence_save
- **prep** (`mcp-tools-1.md`): prep_production_capabilities
- **producer** (`mcp-tools-1.md`): producer_read_generate
- **production** (`mcp-tools-1.md`): production_context_get, production_queue_analyze, production_queue_asset_create, production_queue_asset_delete, production_queue_asset_update, production_queue_character_elements_get, production_queue_component_selection_set, production_queue_list, production_queue_prompt_set, production_queue_refresh, production_queue_regenerate, production_queue_regenerate_batch, production_queue_take_favorite, production_queue_take_select, production_queue_upload_retry
- **project** (`mcp-tools-1.md`): project_metadata_get, project_metadata_patch
- **read** (`mcp-tools-1.md`): read_pr0ta_skill, read_web_page
- **review** (`mcp-tools-1.md`): review_submit_assets
- **save** (`mcp-tools-1.md`): save_scene_shotlist
- **screenplay** (`mcp-tools-1.md`): screenplay_draft_beats, screenplay_import, screenplay_publish, screenplay_save
- **script** (`mcp-tools-1.md`): script_create, script_supervisor_read_generate
- **scripts** (`mcp-tools-1.md`): scripts_list
- **set** (`mcp-tools-1.md`): set_environment_asset_link, set_environment_collider_materialize, set_environment_upsert, set_environments_get
- **shot** (`mcp-tools-1.md`): shot_performances_list, shot_quality_review
- **shotlist** (`mcp-tools-2.md`): shotlist_generate, shotlist_generate_batch, shotlist_scene_chat, shotlist_scene_descriptions_generate
- **storyboard** (`mcp-tools-2.md`): storyboard_chunks_list, storyboard_first_frame_propose, storyboard_generate, storyboard_generate_batch, storyboard_pdf_export, storyboard_reference_sheet_generate, storyboard_reference_sheets_list, storyboard_sequences_get, storyboard_sequences_save
- **style** (`mcp-tools-2.md`): style_candidates_generate, style_package_get, style_package_save, style_world_assign_scenes, style_world_create, style_world_delete, style_world_update
- **submit** (`mcp-tools-2.md`): submit_assets_for_review
- **supervisor** (`mcp-tools-2.md`): supervisor_review_answer, supervisor_review_list
- **tasks** (`mcp-tools-2.md`): tasks_acknowledge, tasks_batch_get, tasks_cancel, tasks_completion_events, tasks_get, tasks_subscribe, tasks_unsubscribe, tasks_watch
- **transcription** (`mcp-tools-2.md`): transcription_get, transcription_start
- **update** (`mcp-tools-2.md`): update_set_references
- **video** (`mcp-tools-2.md`): video_cadence_check, video_quality_control_analyze, video_stutter_repair
- **voices** (`mcp-tools-2.md`): voices_clone, voices_design, voices_design_commit, voices_list, voices_speech_to_speech
- **world** (`mcp-tools-2.md`): world_generation_submit


## MCP-only tools

External MCP clients also have these.

- **create** (`mcp-tools-3.md`): create_project
- **get** (`mcp-tools-3.md`): get_project_development_context, get_project_metadata, get_workspace_snapshot
- **list** (`mcp-tools-3.md`): list_project_assets, list_projects
- **operator** (`mcp-tools-3.md`): operator_mission_control, operator_mission_get, operator_mission_review, operator_mission_send, operator_mission_start, operator_missions_list
