# Workflow gates

PR0TA stops some steps until a creative, quality or approval condition holds:
an approved first frame, an approved voice, an audited script, a prompt
that fits the world's look. Each such stop is a **workflow gate**. You may pass one on your own
judgment, explicitly: the gate's error names it, you retry with

```json
{"workflow_bypasses": ["<gate>"], "bypass_reason": "<one honest sentence>"}
```

and PR0TA records a receipt (`workflow_bypass_receipts`: the gate, your
reason, who and when, and the risk it protects) on the task, the tool result
or the mission. Pass a gate only after it refused, only the gate it named, and
only when you judge its risk acceptable for this request. Tell the user what
you passed and why. Unknown names are refused.

Money, rights and access are never workflow gates. Credit ceilings, mission
allowances and budgets, paid confirmations, quotes, draft finishing, billing,
model-rights policy and team read-only access refuse exactly as before, and no
bypass reaches them; their errors say what the user changes (an allowance,
Settings, a card in the app).

## The gates

| Gate | Where you pass it | What it protects | Reasonable to pass |
| --- | --- | --- | --- |
| `style_change` | `generation_submit` (Prep references), `casting_character_sheet_prompt_resolve`, `storyboard_generate(_batch)`, `shotlist_generate(_batch)` | A prompt that contradicts the world's look line, or a Casting brief drafted under an earlier look, renders off-look | A deliberate scene exception (a dream, a flashback insert), or you checked the old prompt still fits |
| `first_frame_approval` | `storyboard_reference_sheet_generate` | A sheet built on unapproved first frames repeats their flaws in every shot | Rough previs; otherwise approve the frames |
| `set_approval` | Blocking animatic render, Camera Performance | Blocking and camera work on an unapproved build are redone if another build is chosen | A rough pass on the newest build |
| `approved_voice_lock` | `generation_submit` speech, Production Queue `generation_params` | Another voice than the approved Casting voice breaks voice continuity | A different voice is intended (a flashback, a disguise, a temp narrator) |
| `voice_reference_policy` | `generation_submit`, `voices_clone` request, dialogue, Production Queue `generation_params` | A generated, mixed, short or unapproved clip used as a voice drifts the voice | The clip is known clean and the speaker's own |
| `dialogue_audit` | `agent_chat_orchestrate_prompt` | Dialogue the Script Supervisor did not audit may not match the screenplay | Silent previs, or you checked the lines yourself; never a final dialogue take |
| `character_tokens` | `agent_chat_orchestrate_prompt` | Omni character tokens that do not match bound references swap or blend identities | The token names an approved character not yet in the snapshot |
| `prompt_sections` | `agent_chat_orchestrate_prompt` | A prompt missing required sections drops camera, action or continuity facts | The content is there under another structure |
| `reference_ambiguity` | `agent_chat_orchestrate_prompt` | Several references for one character blend a face or build | The candidates are near-identical (the first required one is kept) |
| `reference_preflight` | `agent_chat_orchestrate_prompt` (or `reference_preflight_mode: "shadow"`) | An image whose pixels do not support its claimed role misleads the render | The flagged issue does not matter for this shot |
| `native_voices` | `agent_chat_orchestrate_prompt` | A speaker with no approved Casting voice is voiced by the video model; that voice is provisional and will not match their other takes | Previs, a provisional experiment, or a one-off speaker (a crowd, a voice heard once) |
| `character_visual_references` | `agent_chat_orchestrate_prompt` | A visible character with no selected portrait or turnaround is drawn from the prompt alone (no turnaround is generated) and drifts from other shots | Previs, or a background or once-seen figure |
| `reference_limits` | `agent_chat_orchestrate_prompt` | References dropped to fit the image slots or the 15-second reference-audio budget (lowest priority first) no longer guide the render | The dropped references are minor (it keeps required plates, then portraits, then turnarounds, and the voices with the most lines) |
| `cinematographer_readiness` | Production Queue `generation_params` | A sequence chunk rendered before `production_queue_analyze` lacks camera and continuity facts | The row's own prompt and model already state them |
| `reference_gaps` | Production Queue `generation_params` | A subject with no approved reference is invented and will not match its other shots | The subject does not recur (an insert, a background extra) |
| `qc_still_stop` | The in-app Operator's mission checkpoint; "Keep as is" on a QC card (`operator_mission_review`) needs no bypass and is receipted with your note | A still QC flagged becomes the source of later shots | Exploratory stills nothing builds on yet, or you checked the findings |
| `scope_guard` | The tool's arguments, inside a mission | Work on scenes outside the mission's focus touches material not handed to it | The scene is plainly part of the job (shared continuity) |

A stale reference ledger, the provider's character limit, another project's
data and tools a worker lacks are not gates.
Neither is a missing face or outfit sheet: those sheets are never required,
nothing stops on them, and the portrait and character sheet stand in
(`pr0ta-consistency` → "Face and Outfit Sheets"). Make the missing sheet from
the approved portrait instead of passing anything.

## Approving yourself

Approval steps may be yours when you have looked and judge the result right.
Each is recorded and shown as approved by agent, distinct from the user's
approval, and the user can change it. Pass an `approval_reason`: why it is
right (or that the user asked).

| Approval | Call |
| --- | --- |
| A storyboard first frame | `storyboard_first_frame_propose(..., approve: true, approval_reason)` |
| A set build | `set_environment_upsert(status: "approved", approval_reason, approved_revision?)`; it does not renew the build budget |
| A Casting voice | `cast_list_save(approve_voices: [{character, voice_id, sample_asset_id}], approval_reason)` |
| A first-frame or Casting-voice review card | `operator_mission_review(..., decision: "approve", note)`; the note is your reason |
| A logline | `development_logline_set(logline, approve: true, approval_reason)` |
| A beat sheet | `beat_sheet_approve(approval_reason, structure?, beats?)`; drafting from beats needs one |
| Creative Direction | `direction_approve(approval_reason, producer_read?, director_read?)` after reading both reads; `breakdown_status` names it while the direction waits. The department reads it starts spend credits through the usual checks |

Never replace an approval the user made (a first frame, a set build, a
logline, a beat sheet, the direction) or discard their unapproved edits to the
direction unless they asked for it: then pass `replace_person_approval: true`
(their draft is archived, not deleted). Without it the call is refused and
names the flag. Approving the same content the user approved leaves it theirs,
and an agent-answered review card leaves a frame the user approved as it is.

Cards that finish drafts spend credits: only the user approves them, in the
app. Publishing a screenplay stays the user's (`pr0ta-development` → "Who
decides").

`validation_overrides` (REST `validationOverrides`) on prompt orchestration is
the older spelling of `native_voices`, `character_visual_references` and
`reference_limits`. It is still accepted and receipted the same way; prefer
`workflow_bypasses` with a `bypass_reason`.
