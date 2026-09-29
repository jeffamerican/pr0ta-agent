---
name: pr0ta-development
description: "PR0TA development from idea to approved direction: logline, treatment, beat sheet, writers' room, writing or importing a screenplay, drafting scenes from beats, revisions, publishing a locked draft, and the Producer/Director Creative Direction approval. Read when a production has a story, a script, or a script to write."
---

# PR0TA Development

A story becomes a production in PR0TA through its development pipeline. Each
stage feeds the next, and the platform's departments read what the earlier
stages approved:

**Logline → beat sheet → screenplay → publish → Creative Direction → Script Breakdown**

This skill takes a project to an approved Creative Direction. `pr0ta-prep`
continues from the breakdown. Use the pipeline instead of writing prompts
straight from a brief: the breakdown, casting, looks, sets, shotlists and
storyboards all come from the published screenplay and the approved direction.

Call `prep_production_capabilities` once in a new project for the page-to-tool
map, and `memory_context_pack` before creative work (see `pr0ta-api` →
"Project memory").

## Who decides

Approvals are the user's. At each gate, show the user what you propose, ask,
and call the approving tool only on their explicit instruction:

| Gate | Tool that records it |
|------|----------------------|
| Logline | `development_logline_set` with `approve: true` |
| Beat sheet | `beat_sheet_approve` |
| Publishing a draft (spends credits: starts the breakdown) | `screenplay_publish` |
| Creative Direction (spends credits: runs the departments) | `direction_approve` |

Working saves (a draft logline, an unapproved beat sheet, screenplay saves) need
no approval.

## The script library

A project holds a library of screenplays. The **primary** script is the
project's original screenplay. Each further script (a commercial spot, an
episode, an alternate version) has its own logline, beat sheet, revisions,
runtime and publish, and owns its own block of production scene numbers (the
primary 1-999, the next 1001-1999, and so on).

- `scripts_list` shows every script: `id`, `title`, `kind`, `blockStart`,
  `status`.
- A new spot, episode or alternate is a **new script**:
  `script_create(title, kind)` (`kind`: `spot`, `episode`, `alternate`,
  `short`, `feature`, `other`), then write it with
  `screenplay_save(script_id, content)`. Never overwrite the primary, or
  another script, with a different piece.
- One script per spot or episode. Three spots are three scripts, not one
  document holding all three.
- The logline, beat sheet, drafting, save, read and publish tools take an
  optional `script_id`. Without it they work on the script the chat is on:
  the primary, unless the Writers' Room is open on another script.
- A new script is an unpublished draft: only the Writer and Story Editor see
  it until it is published. It appears on the Screenplay page, where the user
  can open and edit it.
- Departments break down one production: every published script together, in
  block order, scene headings numbered by block. Publishing any script (the
  primary included) re-runs that breakdown over the whole production, so
  publish when a script is ready, not after every edit. Scene 1003 is scene 3
  of the script whose block starts at 1001.


## 1. Read where the project stands

`project_metadata_get` returns `developmentSettings` (the working
`activeLogline`, the `approvedLogline`, `approvedBeatSheet`,
`publishedScreenplay`) and the generated `beatSheet`.

`get_project_development_context` returns the same under
`development_settings`. Its top-level `logline`, `genre` and `tone` come from
the Producer read, not the working logline: read the logline from
`development_settings.activeLogline` or `approvedLogline`. Pass `script_id` to
read one library script's beat sheet and loglines; every read also lists the
library's `scripts` and the project's `campaign_sheet` (the arc over them).

`get_screenplay_text` pages the screenplay. By default it returns the latest
published revision (Fountain notes removed), and `not_published` before the
first publish. Pass `working_draft: true` to read the working draft; do that
before any revision or save. Pass `script_id` to read another library
script's working draft. `breakdown_status` tells you whether a draft has
been published and where its breakdown is. Continue from what exists; never
overwrite an approved stage without the user asking.

## 2. Logline

Draft two or three options in conversation. Save the chosen one with
`development_logline_set(logline)`; record it as approved with
`approve: true` once the user accepts it. The beat sheet and screenplay build on
the approved logline.

## 3. Treatment and source material

Treatments, outlines, research and reference scripts are project documents.
`document_add_text(filename, content)` adds `.txt`, `.md` or `.fountain` text;
`documents_list` shows what exists. PDFs and Final Draft files are uploaded
through the app or the REST documents route (see `pr0ta-api`).

## 4. Beat sheet

`beat_sheet_generate(prompt, structure?, logline?, template?)` queues the Story
Editor and returns a task; wait for it with `tasks_get`. Put the treatment or
story notes in `prompt`, pass the approved logline, and name a structure
(for example "Save The Cat", the default). A `template` is the list of beats
the sheet must cover, as `{name, description?, children?[]}`.

The finished sheet is saved as `beatSheet`. Review it with the user. Edit by
passing `structure` and `beats` to `beat_sheet_approve`, which saves the edited
sheet and approves it together; with no arguments it approves the saved sheet.

For notes and rewrites, talk to the Story Editor: `agent_chat_send(role:
"story_editor", topic, message)`. It reads the same project context and
answers on a task.


## 5. Screenplay

Three ways in, all ending in one working draft:

- **Import** an existing script: upload it as a document (app or REST), then
  `screenplay_import(filename?)` makes it the primary script's working draft
  (it cannot import into another library script; save that one's text with
  `screenplay_save(script_id, content)`). It returns no
  script text; read the result with `get_screenplay_text(working_draft: true)`.
  Text scripts can be added with `document_add_text` first.
- **Write**: `screenplay_save(content)` saves the whole script. Always send the
  complete text in Fountain or standard screenplay format; it replaces the
  working draft. `new_revision: true` starts a new revision when the text
  changed instead of overwriting the current one.
- **Draft from beats**: read the draft with `get_screenplay_text(working_draft:
  true)` and pass it as `content` to `screenplay_draft_beats(content,
  budgets?)`, which asks the Writer to draft a scene for every approved beat
  the script does not cover yet. The drafted scenes arrive on the finished
  task's `result_refs.scenes` (`{beatId, beatName, text}`; beats it could not
  draft are in `result_refs.failed` and `result_refs.notReached`) and are not
  placed in the script: show them to the user, merge the accepted ones into the
  full text, then `screenplay_save`. `budgets` sets page length per beat id in
  eighths.

Revise with the Writer through `agent_chat_send(role: "writer", ...)`, then
save the result. Before every revision or save, read the current draft with
`get_screenplay_text(working_draft: true)` and change that text. Each save is
the complete current draft. Never save the published text (the default read)
over a newer working draft: it would discard the unpublished changes.

## 6. Publish

Publishing locks the working draft as a revision (colored revision pages after
the first), renders the PDF, and starts its breakdown. The Producer and
Director reads run first; the breakdown then waits for Creative Direction.

`screenplay_publish(title?, actual_length_eighths?)` returns an
`analysis_task_id` and `analysis_deduplicated` (true when the task returned
is a breakdown run already in progress). Publish only when the user asks.
Republishing a changed script reruns what the changes affect.

## 7. Creative Direction

When `breakdown_status` shows the producer and director stages done and
direction waiting for approval:

1. Read the reads: `project_metadata_get` returns `producerRead` (logline,
   genre, tone, audience, scope) and `directorRead` (stylistic approach, visual
   genre, palette, style worlds, main cast).
2. Present them to the user as a brief. Discuss changes; the Producer and
   Director can be asked through `agent_chat_send(role: "producer" | "director")`.
3. On the user's approval, `direction_approve(producer_read?, director_read?)`
   records it. Pass edited reads to approve them as edited; the departments
   read the approved versions. Approval lets the Script Supervisor and the
   departments run.

`direction_approve` fails with a conflict when the screenplay changed after the
reads (they are being read again) or when the Director read is not ready.

## 8. Hand-off

Direction approved, the breakdown runs on its own. Continue in `pr0ta-prep`:
follow `breakdown_status`, work the review queues, then style, casting, looks,
sets, props, shotlists and storyboards.

## Tasks and waiting

`beat_sheet_generate` and `screenplay_draft_beats` return `{task,
deduplicated}`: the task id is `task.id`, and a second request while one is
running returns that running task with `deduplicated: true`.
`screenplay_publish` returns `analysis_task_id` (see Publish). Poll
`tasks_get(task_id)` with backoff, or subscribe (`tasks_subscribe`) and wait
for the completion event.

## Handing the whole stage to the Operator

For long development work (a full draft from a beat sheet, a rewrite pass
across many scenes), `operator_mission_start` hands the goal to PR0TA's own
Operator, which works inside the app with these tools and stops for the user's
approvals. See `pr0ta-operator`.
