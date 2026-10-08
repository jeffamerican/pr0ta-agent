# PR0TA MCP tool catalog, part 3

Generated from the live MCP server; do not edit. The index is `mcp-tools.md`.
External MCP clients have these tools; they take `project_id` where a project applies.

## create

- `create_project`(**name**, description, slug): Create a new PR0TA project for the authenticated user and return its project_id.

## get

- `get_project_development_context`(script_id): Get PR0TA development context including logline, beat sheet, screenplay status, and development settings, for one script in the project's library (sc…
- `get_project_metadata`(): Get high-level project metadata summary (logline, genre, tone, cast, scene count).
- `get_workspace_snapshot`(session_id): Get the latest structured frontend workspace snapshot for a project, optionally scoped to a session_id.

## list

- `list_project_assets`(asset_type, category, limit): List project assets with optional modality/category filters.
- `list_projects`(): List PR0TA projects accessible to the authenticated user.

## operator

- `operator_mission_control`(**mission_id**, **action**, client_id, completion_subscription_id): Pause, resume, cancel, archive, or unarchive a mission.
- `operator_mission_get`(**mission_id**, after): Read a mission: status, summary, checkpoint (plan, draft artifacts), pending actions awaiting approval, usage, and events after the cursor.
- `operator_mission_review`(**mission_id**, **effect_id**, **decision**, client_id, completion_subscription_id): Approve or reject one action a mission is holding for review (see effects with status pending in operator_mission_get).
- `operator_mission_send`(**mission_id**, **text**, mode, client_id, completion_subscription_id): Send direction to a mission: mode steer changes the current work, follow_up queues a next request after it.
- `operator_mission_start`(**objective**, title, scene_numbers, character, shot_number, client_id, completion_subscription_id): Hand a goal to the PR0TA Operator as a durable mission that runs inside PR0TA with its own tools, project permissions, and credit budget.
- `operator_missions_list`(archived): List your Operator missions in this project with status and summary.
