---
name: pr0ta
description: "PR0TA (ProtaFilm|maker, app.pr0ta.com) orchestration hub for AI film and video production: script to screen, from logline and screenplay through breakdown, casting, shot lists and storyboards to image, video, voice and music generation, editing and export. Read first for any PR0TA production, then load the one companion skill for the next step."
---

# PR0TA production hub

PR0TA is a script-to-screen studio. It develops a story, breaks the screenplay
down with AI department heads, prepares every character, place and shot, then
generates, edits and delivers the film. This hub picks the path and routes to
the companion skill that owns each step. Read only the companion you need next.

## First moves

1. **Connect.** Use the PR0TA MCP connector (`https://app.pr0ta.com/api/mcp/mcp`,
   OAuth in the browser). If `list_projects` is not callable, the connector is
   not authenticated in this session: connect it in your host's MCP settings and
   start a new session. REST with a personal access token (`pat_...`, Settings →
   General → API Keys, kept in `$PR0TA_PAT`, never pasted into prompts) is the
   fallback for routes MCP does not expose. See `pr0ta-api`.
2. **Pick the project.** `list_projects`, or `create_project(name)`. Every
   project tool takes `project_id` explicitly.
3. **Map the project.** `prep_production_capabilities` returns every page and
   its tools. `breakdown_status` and `project_metadata_get` show how far the
   project has come.
4. **Load memory.** `memory_context_pack(task_intent, scope)` before creative
   work; it cites the project's approved decisions, which outrank everything
   else. Record accepted decisions with `memory_record_decision` and notes with
   `memory_record_note` (arguments and confirmation: `pr0ta-api` → "Project
   memory").

## Choosing models

Never pick a model from memory or from these skills. The project's admin pins
models per modality and each user may override them in Settings → Tools.

- Call `models_preferred(modality)` and put its `model_id` in the request.
  Modalities include `image_model`, `image_edit_model`,
  `reference_to_video_model`, `video_model` (text-to-video), `video_edit_model`
  (image-to-video), `video_extend_model`, `lipsync_model`, `dialogue_model`
  (speech), `music_model`, `sfx_model`.
- If `model_id` is null, choose with `models_list(modality)` (pinned first) and
  tell the user which you chose.
- If the user names a model or a capability only one model has, use it.
- Then read the model's reference in `pr0ta-video`, `pr0ta-image` or
  `pr0ta-audio` before writing its prompt, and check its modes and limits with
  `models_get_defaults(model_id)`. Prompt grammar is not portable between models.

## Two paths

**A story (characters, scenes, dialogue): the script-to-screen pipeline.**

| Stage | Skill |
|-------|-------|
| Logline, beat sheet, screenplay, publish, Creative Direction | `pr0ta-development` |
| Breakdown, review queues, style, casting, sets, looks, props, shot lists, storyboards, Production Queue | `pr0ta-prep` |
| Recurring characters and places across shots | `pr0ta-consistency` |
| Generating the scripted shots: through the Production Queue | `pr0ta-prep` |
| Model grammar and prompts for those shots | `pr0ta-image`, `pr0ta-video`, `pr0ta-prompting` |
| Dialogue, narration, voices | `pr0ta-audio` |
| Score and sound effects | `pr0ta-music` |
| Cut, mix, review, export | `pr0ta-timeline`, `pr0ta-editorial` |

**A short piece with no story (promo, montage, title card, music video):** plan
timing with a cue sheet (`pr0ta-sync`), write prompts (`pr0ta-prompting`),
generate ad hoc, outside the Production Queue (`pr0ta-image`, `pr0ta-video`,
`pr0ta-audio`, `pr0ta-music`), then cut (`pr0ta-timeline`, `pr0ta-editorial`).

Footage or a 3D world as the source: `pr0ta-hybrid`. Downloads: `pr0ta-downloading`.
Raw routes, schemas, limits and the full tool catalog: `pr0ta-api`.

**Long or unattended work:** hand it to PR0TA's own Operator as a mission
(`pr0ta-operator`); you get a receipt when it stops.

## Rules that hold everywhere

1. **The user decides.** Approving a logline or beat sheet, publishing a
   script, approving direction, answering review questions, and approving
   held actions are the user's calls. Propose, ask, then act on their word.
   Rights, clearance and legal review are the user's too: never run or
   delegate one unasked. The project's Legal settings set the rights policy,
   and PR0TA enforces it when a job is submitted.
2. **Prep before generation.** Read `production_context_get` for the scene or
   shot, and reuse approved casting, looks, sets and references before making
   new ones. Recurring characters need consistency resources
   (`pr0ta-consistency`); free-text prompts alone drift.
3. **Every prompt is self-contained.** Models see only the prompt and the
   attached references. `pr0ta-prompting` owns the technique.
4. **Generation returns tasks.** Poll `tasks_get` with backoff or subscribe
   with `tasks_subscribe`; never assume a task finished. Keep parallel
   submissions within the limits in `pr0ta-api`.
5. **Draft video before finishing it.** When the chosen video model offers
   draft mode (`draft_mode` in `models_get_defaults`), generate a low-cost
   draft, review it with the user or against the shot's intent, and finish only
   the approved draft; the final keeps the draft's prompt, references, seed and
   duration. Iterate at draft cost (`pr0ta-video` → `reference/draft-to-final.md`).
6. **Audio is indexed before it is cut.** PR0TA indexes generated and uploaded
   audio in the background; check the index before starting another
   (`pr0ta-audio` → "Time-indexing").
7. **Edit on the PR0TA timeline.** It is the shared editing surface with the
   user. Snapshot before large passes, preview key segments before export
   (`pr0ta-timeline`).
8. **A cut is not done until it passes the editorial gate.** Every asset used
   once, the story reads the way the piece intends, seven ship criteria
   (`pr0ta-editorial`).
9. **Curate as you go.** Tag keepers and rejects with
   `assets_annotations_update` and record choices in memory, so the next agent
   and the user can find them.
10. **Read the QC verdict before using a take.** Every generated take
   (storyboard frames aside) and every full render or export is reviewed
   automatically and free, story and continuity first; a speech take is
   also compared with the speaker's approved voice.
   `shot_quality_review` (a take) or `cut_quality_review` (a render) returns
   the verdict: `pass`, `repair` (usable; its faults are repaired once the user
   keeps it), `fixable` (needs a new take; with a revised prompt), `fail` or
   `uncertain`, judged against the project's delivery target. Never present a
   take that did not pass as good; say what the review found (`pr0ta-video` →
   "Automatic QC of Every Take").

## Local ledger

For multi-shot work, keep a small local `assets.json` mapping readable shot keys
to PR0TA asset ids, the prompt, the model and where each asset is used. Update
it after every successful generation. The edit itself lives on the PR0TA
timeline, versioned with timeline snapshots, not in local folders.
