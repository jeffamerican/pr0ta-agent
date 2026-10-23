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

Publishing a draft is the user's: it spends credits and starts the breakdown,
so publish only on their explicit instruction. The other approvals may be
yours once you have read the material and judge it right: pass an
`approval_reason`. Each is recorded and shown as approved by agent, distinct
from the user's approval, and the user can change it. When the user is around
or the call is contested, show what you propose and ask first. Replacing the
user's approval, or their unapproved edits to the direction, is refused unless
they asked and you pass `replace_person_approval: true`.

| Gate | Tool that records it | Whose |
|------|----------------------|-------|
| Logline | `development_logline_set` with `approve: true`, `approval_reason` | yours or the user's |
| Beat sheet | `beat_sheet_approve(approval_reason)` | yours or the user's |
| Publishing a draft (spends credits: starts the breakdown) | `screenplay_publish` | the user's |
| Creative Direction (starts the department reads; they spend credits through the usual checks) | `direction_approve(approval_reason)` | yours or the user's |

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
`approve: true` once the user accepts it or you judge it right (with an
`approval_reason`). The beat sheet and screenplay build on
the approved logline.

## 3. Treatment and source material

Treatments, outlines, research and reference scripts are project documents.
`document_add_text(filename, content)` adds `.txt`, `.md` or `.fountain` text;
`documents_list` shows what exists. A file the user attaches (PDF, Final Draft,
Highland, Fountain, Word .docx, RTF, text) arrives as an asset: read it with
`document_read(asset_id)` (scanned PDFs are OCR'd; long files come in pages,
continue with `offset: next_offset`) and add it to the documents with
`document_add_asset(asset_id)`. `document_read(filename)` reads a document
already in the list.

## 4. Beat sheet

`beat_sheet_generate(prompt, structure?, logline?, template?)` queues the Story
Editor and returns a task; wait for it with `tasks_get`. Put the treatment or
story notes in `prompt`, pass the approved logline, and name a structure
(for example "Save The Cat", the default). A `template` is the list of beats
the sheet must cover, as `{name, description?, children?[]}`.

The finished sheet is saved as `beatSheet`. Review it with the user. Edit by
passing `structure` and `beats` to `beat_sheet_approve`, which saves the edited
sheet and approves it together; with no arguments it approves the saved sheet.
Approve when the user accepts the beats or you judge them right (pass an
`approval_reason`); `screenplay_draft_beats` drafts only from an approved sheet.

For notes and rewrites, talk to the Story Editor: `agent_chat_send(role:
"story_editor", topic, message)`. It reads the same project context and
answers on a task.


## 5. Screenplay

Three ways in, all ending in one working draft:

- **Import** an existing script: `screenplay_import(asset_id)` for an attached
  file, or `screenplay_import(filename?)` for a project document, makes it the
  primary script's working draft (it cannot import into another library
  script: read that file with `document_read` and save its text with
  `screenplay_save(script_id, content)`). It returns no script text; read the
  result with `get_screenplay_text(working_draft: true)`. Only import when the
  user wants the file to become the working draft; to pick or study scenes,
  `document_read` is enough. Text scripts can be added with `document_add_text`
  first.
- **Write**: `screenplay_save(content)` saves the whole script. Always send the
  complete text in screenplay format ("Screenplay format" below); it replaces the
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

### Screenplay format

Every script, spots and commercials included, is a standard screenplay in
Fountain. The breakdown, shot lists and the Writers' Room read it that way.

- **Title page**: `Title:`, `Credit: Written by`, `Author:`, `Draft date:`.
  Put the deliverable and target length in `Notes:` (for example
  `Notes: 9:16 social spot, about 43 seconds`), never as a body line.
- **Scene headings**: one per place, `INT. STUDIO - DAY` with a hyphen. A
  passage across several places is `INT./EXT. VARIOUS - DAY` followed by
  `MONTAGE:` (or `SERIES OF SHOTS:`) and one `-- ` line per image.
- **Action** is only what we see and hear, in present tense. Instructions to
  the editor or crew, references, rationale and timing go in `[[notes]]`,
  which publishing strips. Never timecodes at the start of action.
- **On-screen text** is its own line: `SUPER: AN IDEA ISN'T A FILM.`, then a
  blank line. An app or device screen is `INSERT - <SCREEN>` on its own line,
  a blank line, then what it shows.
- **Dialogue**: character cue in caps, `(V.O.)` or `(O.S.)` extensions, short
  parentheticals. A character's first appearance in action is in caps.
- `>` marks a transition only (`> CUT TO:`); end with `FADE OUT.` or
  `CUT TO BLACK.`

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
   genre, palette, style worlds, main cast, eras and character stages).
2. Present them to the user as a brief. Discuss changes; the Producer and
   Director can be asked through `agent_chat_send(role: "producer" | "director")`.
   Review the eras with the rest: they are the Director's stylistic call and
   shape the film. Each era has an id, name, period, `kind` (main, frame,
   flashback, montage, insert), an optional `parentEra` (a short flashback
   that belongs to another era's design), `scenes` as ranges ("1-5, 107-149") and a
   one-line palette, texture, lens and wardrobe identity. A scene listed by two
   eras belongs to the one listing fewer scenes; an unlisted scene belongs to
   the first main era. One era means a single-period film and changes nothing.
   `characterStages` lists each character seen at clearly different ages under
   one cue: per stage its eras (or scenes), age, `year` (the year the stage is
   first seen; it names the stage's cast member), evidence, `distinctActor`,
   reason and `ageNote` (how the age shows when the same actor plays it).
   Exactly one stage per character is `main`: the character's existing cast
   member, with every approval, plays it. Check the ages against the script and
   the main stage against the user's casting.
3. On the user's approval, or when you judge both reads right for the film,
   `direction_approve(producer_read?, director_read?, approval_reason?)`
   records it (yours shows as approved by agent). Pass edited reads to approve them as edited; the departments
   read the approved versions. Approval lets the Script Supervisor and the
   departments run. Eras and stages are edited the same way (or on the
   Creative Direction page). Approving an edit that touches only the era plan
   reruns little: era names and reasons rerun nothing; scene ranges, kinds and
   `parentEra` re-tag the scenes without a model; a changed period or visual
   identity (or scenes moved to an era that looks different) reruns Sets, Looks
   and Props for those scenes only (every scene when it is the main era, which
   unlisted scenes belong to); a change to a character's stages (eras,
   scenes, ages, `distinctActor`, `main`, `castAt`, `castMember`) reruns
   Casting. While the Script Supervisor is still reading (or waits for the
   approval) and Casting, Sets, Looks and Props have not started, these era
   edits rerun nothing: the Supervisor's handoff starts them with the
   direction approved at that moment, and its era tags follow the approved
   plan. Any other Director read edit, or an era edit while the Director is
   still reading or a department has started, reruns the
   Script Supervisor and every department. The Creative Direction page says
   which before you approve. Batch
   era edits into one approval. A cast member approved before the era plan
   keeps every scene until someone marks `castAt: true` on the stage its
   approvals were made at (its `age_stage.conflict` asks; ask the user unless
   the script settles it). A `castAt` or `castMember` answer that changes
   nothing comes back in the approval's `eraNotes`, with the reason.

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
