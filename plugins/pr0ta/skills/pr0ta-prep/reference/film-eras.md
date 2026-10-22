# Film eras: scenes, age stages and their cast members

A film that spans periods changes everything with the period. The Director
decides the eras and each recurring character's ages in its read, and the
person (or you) approves them with Creative Direction (`pr0ta-development` →
"Creative Direction"). Prep then works from the approved plan. A single-period
film has one era and none of this applies.

## Scenes

Every scene in `get_scene_breakdown` carries `era_id` once the film has two or
more eras. The tag is deterministic: a scene listed by two eras belongs to the
one listing fewer scenes, and a scene no era lists belongs to the first main
era. A flashback era with `parentEra` keeps its own id, so its characters get
the right age there. `parentEra` records that it belongs to another era's
design; styles, sets, looks and props do not follow it automatically yet, so
keep its style world and Prep references in step yourself.

## Stage members

The character's existing cast member keeps its name and everything approved on
it (portrait, sheets, voice) and plays the stage marked `main`, plus every
scene no other stage member plays. Once it has an approved portrait, sheet or
voice it stays at the age it was approved at: if the main mark later moves to
another age, that age is cast as its own member and the Creative Direction page
says so. Approvals never move between ages.

A cast member approved before the era plan existed has no recorded age: its
`age_stage` says `unresolved`, with a `likely_stage_id` and a question. Until
someone marks `castAt: true` on the stage its approvals were made at (in the
Director read, approved with Creative Direction), it plays every scene as
before and no other age is cast. Ask the user which age it is; the likely one
is only a guess from its prompt. A `castAt` answer can be corrected later (move
the mark); an age recorded from an approval cannot be moved this way.

Casting gives every other stage marked `distinctActor` (and the main stage
when the existing member stays at another age) its own cast member, named
`CUE · year · age` (for example `ANGELA · 2000 · 55`). Its record holds:

- `same_person_as`: the base member it is linked to
- `stage_id`, `era_id`, `era_ids`
- `stage_age`, `stage_period`
- `stage_scenes`: the scenes it played when cast, as ranges (routing reads the
  approved era plan, so a scene added later still reaches the right member)

A stage the same actor plays gets no member; its `ageNote` says how the age
shows (makeup, grey hair).

Cast and approve each stage member like any principal:

- A portrait at that age and period that keeps the base member's lasting
  features (eyes, bone structure, ethnicity, marks).
  `casting_portrait_prompt_write` already knows the stage.
- A voice designed as the same person's voice at that age. Until it has an
  approved voice of its own, the table read and references use the base
  member's approved voice.

Rules:

- Approvals are bound to stage ids. Keep a stage's id when you edit its age or
  scenes. A stage is its scenes: an age edit, even two stages swapping ages,
  corrects that stage, and its approvals stay on it. Approvals move only by an
  explicit `castMember` or `castAt` answer. A stage moved to eras it did not
  share is a new age there (a new id). A stage member whose stage is gone
  is kept with its media and plays nothing until someone sets `castMember` (its
  name) on the stage it should play; nothing is reassigned by guesswork.
  `castMember` on a stage that has its own member replaces that member there
  (it is kept with its media, unused; removing the `castMember` restores it).
  `castMember` naming a member that plays another age moves it off that age,
  which gets a new member; removing the `castMember` sends it back home
  (unless that age changed since: then it is kept, unused, to reassign).
  `castMember` changes nothing on the stage the base member plays, on a
  stage without `distinctActor`, or when it names another character's member;
  one member plays one stage (the first stage naming it). The approval's
  `eraNotes` say when an answer changes nothing or moves a member.
- Give new stages new ids. Ids of dropped stages stay reserved in the
  Director read's `retiredStages`: never reuse one (only the same character
  coming back at about the same age gets it back). On a Director re-read an id
  keeps a stage while its age agrees, or is only reworded (30 -> 30s, late
  30s -> 40) on the same scenes or era; ages that do not even meet (10 -> 45,
  child -> teen) are a new stage, and the person's `castAt`/`castMember`
  answers stay with the stage at the age they were given for (`eraNotes` say
  when one was dropped).
  Ages agree when two
  numbers are within two years, a number sits inside a span away from its
  edges, or two spans share at least half (toddler 1-3, child 4-11, tween
  10-12, teen 13-19, young adult 18-25, adult 18-64, 50s, early twenties
  20-23, 70+, months 0-1; "child" and "tween" do not agree). An age on one
  side only, or words that are not ages, never agree. Write ages as numbers or
  ranges. A retired stage member or a switched-off base pin comes back only
  at an age that agrees; otherwise it is asked about (or `castMember`).
- Approved media is anchored at the age it was approved at (`approved_age` on
  stage members, `age_stage.approved_age` on the base member). A re-read never
  moves it; when a stage's age no longer agrees with it, `age_conflict` (and
  the approval's `eraNotes`) says so and the member keeps playing until the
  person decides: `keepCast: {"member": NAME, "age": AGE}` on the stage keeps
  exactly that member for that age (the anchor moves on approval; a bare
  `true` means the member playing it now, at its age now), or recast. The person's age corrections move the
  anchor too. These stage fields are the server's: saves never change them.
- Never rename a stage member or merge it into its base: shot lists, the table
  read and references find it by name and stage.
- A stage the approved plan drops keeps its member if it carries approved
  media or a hand-edited prompt. It is marked `stage_retired` and plays no
  scene (references never list it). One from before Casting recorded its own
  prompt is kept too, marked `legacy_kept`: ask the user whether to delete it.
  A casting read
  that does not cover the character leaves its stage members as they are.
- Shot lists, the table read, storyboard frames, the voice lock and the
  reference resolver keep the screenplay cue (ANGELA). Each scene routes the cue
  to the stage member who plays it there. Pass `metadata.scene_number` with
  speech requests: without it the cast member's own voice is used and the task
  says so (`voice_lock_note`). A stage member named directly without an
  approved voice of its own speaks with its base member's.
- Era ids and stage ids are kept across re-reads (cast records name them).

## Casting

`cast_list_get` lists stage members with the rest of the cast, cast numbers
after the existing ones. Make each one's references as for any principal
(Portrait, Face Turnaround, Outfit; `pr0ta-consistency` → "Ages Across Eras").
