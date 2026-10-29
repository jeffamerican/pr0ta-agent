# Seedance 2.5 Prompt Craft

How to write a Seedance 2.5 prompt that the model follows. `seedance-2.5.md` owns routes, request fields, durations, and reference limits; this file owns the writing. The authority is ByteDance's Dreamina Seedance 2.5 prompt guide on BytePlus (https://docs.byteplus.com/en/docs/modelark/seedance-2-5-prompt-guide, updated 2026-10-16; rendered by JavaScript, so read it in a browser), plus production experience. Where the two differ, the provider guide wins. Grade every prompt with `pr0ta-prompting/reference/prompt-rubric.md` before you submit it.

## Shape of a Prompt

The provider's recommended order is:

1. **One-sentence summary:** subject, location, event, genre or style, camera.
2. **Detailed plot:** segment the clip by timestamps or by `Shot N`, and give each segment its visuals, camera movement, action, dialogue, and sound.
3. **Additional notes:** what must stay constant throughout (camera angle, environment, sound, atmosphere).

Timestamps are whole seconds. Use continuous ranges with no gaps (`0-3s`, `3-7s`, `7-15s`), time points ("at the 5-second mark, …"), or relative time ("after 3 seconds, …"). If a range holds too little, the model improvises; if it holds too much, it adds cuts or drops part of the plot. Do not time high-frequency actions ("shakes his head three times per second").

## Sectioned Template for Complex Shots

Use labelled sections when a shot has several characters, dialogue, or several references. Each section has one job, which keeps the model from mixing them:

- **Generation goal:** one sentence saying what the clip is and what it must demonstrate, plus the picture's frame (a clean full-frame image, no added interface).
- **Reference asset roles:** one line per asset, in upload order, each saying what it supplies and what it must not contribute (see Reference Roles).
- **Subjects and relationships:** the exact on-screen cast count, who is who, who holds which prop, and who operates the camera if anyone does (see Cast and Identity).
- **Event script:** the action in chronological order, from where it begins to a clear, visible final state.
- **Camera and sound:** one camera behavior described physically, then the dialogue and the sound.
- **Maintain consistency:** one closing sentence that restates cast count, identities, wardrobe, prop ownership, room geography, and action direction, and repeats the exclusions.

For a fast compilation or montage, give the cast a short continuity block (each character's fixed outfit and one defining trait), a rhythm rule ("each clip shows one action from its start to its impact, then hard-cuts; no build-up, no aftermath"), and then timed shot blocks such as `[SHOT 3 | 3-4.5s] … HARD CUT.` Keep the shot count low enough that each block gets its action.

## Reference Roles

- Number assets by upload order (Image 1, Video 1, Audio 1) and bind every asset in the prompt. Never rely on a name written on the image ("JOHN" lettered on a portrait): it causes confusion and duplicated characters.
- When PR0TA builds the prompt package (`agent_chat_orchestrate_prompt`, the Production Queue), it compiles the numbered role declarations from the reference plan; use the same numbering and names in the body. When you submit a prompt directly, write the declarations yourself, one line per asset in upload order ("Image 1 is MARA's approved portrait: face and hair only.").
- With several subjects, list the mapping one by one ("Images 1-2 are Mara and correspond to Audio 1; Image 3 is Theo").
- Say which part of an asset to use: "use Video 1 only for the orbiting camera move", "use Image 4 for lighting and grade". A role line does not reliably keep a reference video's action and dialogue out of the take, so attach a video only when its motion belongs in the result.
- When a reference is accurate, tell the model to follow it instead of re-describing it ("follow the actions and camera movement of Video 1 in order").
- Seedance 2.5 accepts multi-view sheets as subject references (2.0 did not). A character's packet is split by job (`pr0ta-consistency` → "Face and Outfit Sheets"): the **face sheet** (a six-angle head turnaround) for the face, the **portrait** for the canonical likeness, the **outfit sheet** (front and back, no face) for the clothes only, and in wide shots, when the slots allow, the full-body **character sheet** for build and proportions. Tight on slots: drop the body sheet first, then the portrait, never the face sheet.
- Give each sheet its one job in its role line, and say that every view shows the same person and that the sheet's grid, studio light and background are not copied ("Image 1 is MARA's face turnaround: all six views are her; take only her face and head. Image 3 is her outfit sheet: take only the clothes, not a face or a mannequin."). PR0TA writes these role lines when it builds the package. Then describe the scene's own setting and light in the body: the face sheet's even studio light is there to show the face, not to light the shot; the face holds under hard or low-key light because the sheet shows it from every side.
- Use simple line-art or stick-figure storyboards with 15 panels or fewer and little text. A multi-panel storyboard guides the plot, not the exact frames; use first/last or keyframe references when strict alignment matters.
- Resize a high-resolution generated reference image to no larger than the output resolution. Large references can stamp fingerprint-like patterns into dense textures such as grass and foliage.

## Cast and Identity

Identity leaks between characters when the cast is vague. Write:

- the exact cast on screen: "exactly one Mara, one Theo, and one older woman with short silver curls";
- each supporting character with a clearly different face, hair, and wardrobe from the referenced lead;
- that the lead's wardrobe belongs only to the lead, and that the lead's reference never supplies another character's face or clothes;
- prop ownership and handovers ("the bouquet belongs to Theo until he hands it to Mara").

## Negatives and Exclusions

Seedance 2.5 has no `negative_prompt` field. The provider guide recommends positive descriptions wherever possible and documents negative control for subtitles and audio. Its own examples also use short negatives for preservation, reference limits, and artifacts:

| Use | Example |
|---|---|
| Subtitles | "No subtitles." |
| Audio | "No BGM; generate only environmental sounds and action sounds." / "No audio." |
| Preservation in an edit | "Keep the original audio unchanged. Do not change the shot structure or add new shots." |
| Reference limits | "Use the clay-render video only for camera movement and blocking; do not take its visual content." |
| Known artifacts | "Natural skin texture, no excessive beautification or skin smoothing." / "No stuttering, no flickering." |
| Recording overlays | "A clean full-frame recording image; no REC indicator, timestamp, viewfinder grid, or subtitles." |

Pair each negative with the positive it protects, and list only problems you have seen or that the look invites. Write the action you want positively (`pr0ta-prompting` → Technique 4), because a positive end state also tells the model what to show. A small 12-draft A/B at 480p (a waiter carrying a tall stack of plates, a boy holding a balloon in strong wind, a man on a bench seen from behind) found no penalty for negation: "He does not drop the plates", "He does not let go of the balloon" and "He never turns around" never rendered the forbidden action. Neither did the positive phrasings, so those scenes never provoked the failure and the test does not prove negation safe where the model leans toward the forbidden action (shattering, falling). If a take shows the forbidden action, rewrite that line positively first.

### When an exclusion does not hold

| Symptom | Repair |
|---|---|
| Background music despite "No BGM" | Say the audio keeps character voices and action sounds only and that no music track of any kind is generated. Enumerate the synonyms (music, background music, BGM, score, instrumental, melody, synth effects, ambient pad), and repeat the audio constraint at the start and end of the prompt. Otherwise remove it in post with `audio_stem_separate`, which also removes the sound effects. |
| Subtitles despite "No subtitles" | Do not repeat dialogue words after a line, and do not attach tone or action notes to individual words. Give each line one speaker mapping with its delivery note in front: `MARA (whispering): "Not here."` Make sure no reference video carries subtitles; a subtitled reference can override the instruction. This can still happen occasionally, so check every take. |
| Glowing or lit-up eyes on strong emotion | Make "normal human eyes; no glowing eyes" the top-priority constraint, keep environmental light on the facial contours, and replace intense emotion words ("fanatical", "extremely shocked") with neutral ones ("amazed"). |

## Dialogue

- Map every line to its named speaker (the platform's writers already require `NAME: "exact line"`).
- Require intelligible spoken words: laughter accompanies a line rather than replacing it.
- When the camera turns away from a speaker, the voice continues off screen from where the speaker stands.
- Give a non-human speaker a voice that is distinct from the human cast's, and a visible cue in time with its speech (a visor that flickers, a speaker grille that pulses).
- Keep one featured speaker per beat when you can, and synchronize every visible speaking mouth.

## Editing and Extension

State the scope and the change from A to B, and keep the rest: "From 4-6s in Video 1, change the man's action from drinking coffee to mopping the floor; leave the rest unchanged." Open with an edit word (edit, replace, add, remove, change to) so the model treats the clip as source, not as a loose reference. To change the aspect ratio of an existing clip, a Reference task with a detailed shot-by-shot timeline holds the content better than an Edit, which invents imagery to fill the new canvas.

The provider guide's edit advice: sources of 20 seconds or less are more stable; one to five reference images work best; one change per pass. A job that needs a new element and a new motion path at once goes better as two passes (a Reference task makes the element, then an Edit puts it in the clip).

### Replace the World Around Live Action

A Seedance 2.5 edit can keep a recorded performance while it changes the world, the light, the wardrobe or the style. That means the actors' faces and likeness, gestures, lip movements, timing, framing, camera and cuts. It does so when the request and the prompt are built for it. It redraws every pixel, so the prompt and the inputs earn the preservation, and a check of the take against the source proves it. The route itself never rules it out. SwitchX is the other route, for a plate whose pixels must come through exactly (`pr0ta-hybrid/reference/route-selection.md`).

**Omni Reference is equally first-class for hybridization and excels across edited
sequences.** Properly prompted, reference mode is fully capable of maintaining
actor identities and performances. Bind the source edit to the performance,
camera, timing and cuts; bind stills to appearance. Native drafts are a useful
review workflow: approve the actual native draft, then finish that draft at the
delivery resolution (`draft-to-final.md`). The following request recipe describes
the dedicated edit operation; it does not require switching a sequence-source
Omni Reference workflow to edit mode.

#### Set up the request

- **For the dedicated edit operation**, use `byteplus/seedance-2.5-video-edit`, or the MuAPI video-edit routes for 4K (a real-person refusal on ModelArk falls back to MuAPI by itself; do not resubmit). Omni with `omni_reference_task_type: "edit"` also edits. Reference mode reconstructs from the source and can preserve the performance when its prompt assigns the source that authority; it also supports native drafts, unlike edit/extend.
- **The source is the only video.** With several videos, the guide says, "the model determines which video to edit based on the prompt"; the others act as references. A previous take sent as Video 2 "for continuity only" replayed its action and lines in a hybrid chunk (bug d7aee401). Carry an earlier take as a still of its last frame. A submit or quote result's `request_advisories` flags a second video. For sequence-source Omni Reference reconstruction, also keep the source as the sole video: it already carries the performance. Add a previous take as a continuity video only in a deliberately chosen generation/continuation workflow (`pr0ta-video` → "Continuity Workflows").
- **Resolution that holds a face.** Render a take whose likeness matters at 720p or 1080p. At 480p faces and hands soften most. The 480p picnic edit (C010, 2026-10-27) redrew both faces and turned the grass under the blanket to gravel. Edits cannot draft, so to save cost try the prompt on a trimmed slice that holds the hardest face moment (`assets_trim`) before the whole plate.
- **Length and format.** Per the guide, a source of 20 s or less is more stable. Edit a longer plate in chunks, each its own single-source edit. A source with 8n+1 frames (161) comes back at exactly its length, and the guide recommends `output_format: "mov"` for edits.
- **References.** One to five images work best (guide), each with one job: setting, light, a wardrobe change. Resize generated stills to no larger than the output resolution, or dense grass and foliage can pick up fingerprint-like patterns (guide). Two things are untested in PR0TA: a clean frontal still of each actor cut from the plate itself, as an identity reference, is the next thing to try when a face drifts, and a portrait from other footage can pull the face away from the recording.

#### Write the prompt

1. **Open with the edit and the lock.** Start with an edit trigger ("Video edit of Video 1:"), then one sentence that preserves the recording. The guide's own edit example opens "Preserve the composition, camera position, lighting, and performance rhythm of @Video 1", then says "Only modify" and names the change. Drop "lighting" when the light changes.
2. **Number every input and give it one job.** "Video 1 is the source." "Image 1 is the approved setting: environment and light only, never the people."
3. **Lock list in things a camera sees.** Identify each person by position and wardrobe from frames you have looked at (`post_frames_get` on the source), not from a summary. Then lock their faces and identity, expressions, lip movements, gestures, eyelines, hair, wardrobe, props and positions. Lock the ground or surface they sit or stand on, the framing, the camera move and the timing too. Whatever you neither lock nor name as kept is open to change, and "everything around the people" includes the ground under them. Concrete nouns hold; abstractions ("sole authority for recorded identities") give the model nothing to look at.
4. **Describe only the change, from A to B.** Make one change per pass; the guide splits complex jobs into passes. Describe the new world in detail. Describe the people only enough to identify and lock them, and give them no style words ("cinematic", "beautiful", a film stock): community editing guides report that describing what should stay invites the model to alter it (unverified here).
5. **Scope by time.** Use whole-second ranges that cover the clip with no gaps, each with its job: "0-2s: leave unchanged." "2-15s: replace everything behind the people with …".
6. **Keep the people's light, or relight them on purpose.** Keeping their recorded light and choosing a setting whose key direction and warmth match it carries the least identity risk. To relight, give:
   - the key light's direction, quality and warmth;
   - bounce from the ground, walls or greenery;
   - contact shadows under bodies, hands and props;
   - edge light on hair and shoulders against a bright background.

   State persistent light requirements in every relevant beat, then check skin highlights, clothing shadows, hair/rim light and environmental shadows separately at the opening, cuts, close views and ending. Bright surroundings or hair alone do not prove direct sunlight on faces; repetition is direction, not a guarantee. Retain accepted pictures with disclosed findings.

   Studio-lit people in a sunlit world look pasted on. Community tests report that warm directional daylight holds faces better than night or neon (unverified here).
7. **Close by restating the fragile locks.** End with "Face and identity unchanged; lips match the recorded dialogue exactly." The guide's edit example ends on identity ("without drifting or changing identity"), and community footage prompts repeat the face lock at the end (no A/B in PR0TA yet). Short negatives work on 2.5: "Do not re-frame, re-time or re-cut; add no new shots." "Natural skin texture, no smoothing."
8. **Say the continuity, not the defect.** "The action continues straight through the 2-second mark in one take: no repeated gesture or word, no cut, no zoom or reframing." Never describe a flaw in the source ("a small hand-position mismatch at the boundary"): the model redraws what you point at.
9. **Audio by the flag.** Send `generate_audio: false` to keep the recorded sound; prose alone sets nothing. `keep_source_audio: true` does the same, but only on the dedicated edit routes (`byteplus/seedance-2.5-video-edit` and the MuAPI video-edit routes); on `byteplus/seedance-2.5` it does nothing. The MuAPI Omni routes have no `generate_audio` at all: an Omni edit always generates its soundtrack, so when recorded speech must survive, plan to lay the source's soundtrack back under the take in Post, or use the video-edit route. Say it once in the prompt as well. Finish an accepted native draft through `finalize_draft` or the draft-finish card (`draft-to-final.md`), preserving its native workflow. For a separately requested re-edit of a standalone preview or take without native finish support, choose the video-edit route of that resolution with `generate_audio: false` from the start. An Omni edit's generated soundtrack recreates the source's recorded dialogue, and the provider can refuse the whole take for it: `InputVideoSensitiveContentDetected.PrivacyInformation`, "the output audio may be related to copyright restrictions" (bug e9a6e90c, a 29 s 1080p Omni re-edit). The message identifies a generated-audio check; it does not establish a real-person violation or prove that unseen picture passed every check. PR0TA re-runs such a refused MuAPI Omni edit once, on the same task and quietly, on the video-edit route of its resolution with `generate_audio: false`, when it sends one video, no audio and no request for generated sound. Do not resubmit. If that is refused too, the message still does not establish which track caused the refusal; for a user-approved picture-only retry, edit a copy of the source without its audio track and lay the recording back in Post. Providers keep source audio inconsistently even with the flag. PR0TA flags a checked take whose soundtrack changed; otherwise compare the take with the source yourself (`audio_align`, `pr0ta-audio`). When the take drifted, lay the original track back under the picture in Post. A shot that keeps no recorded speech keeps generated sound by default.
10. **Frame and length from the source.** Write no ratio in the prompt. ModelArk edit routes force `aspect_ratio: adaptive` and `duration: -1` themselves. MuAPI edit routes default to 16:9 and 5 s, so send `aspect_ratio: "adaptive"` and an explicit whole-second `duration` from 4 to 30, rounding the measured source length up (28.064 s -> 29). `-1` is only a ModelArk value; MuAPI rejects it. Inputs are billed separately, each rounded up.

Worked example, 15 s, two people filmed in a studio and moved to a lakeside picnic, the first 2 s already showing the new setting (bracketed parts come from the frames you looked at):

```text
Video edit of Video 1: two people picnic on a blanket on a sunlit lakeside meadow, one continuous take, the camera exactly as recorded.
Preserve the people, performance rhythm, composition and camera movement of Video 1; only change the world around them and its light.
Video 1 is the source: the woman on the left in [her wardrobe] and the man on the right in [his wardrobe] keep their faces and identity, expressions, lip movements, gestures, eyelines, hair, wardrobe, the blanket, the props and their positions exactly as recorded, at the original pace and length.
Image 1 is the approved setting: use it for the environment and light only, never for the people.
0-2s: leave unchanged; it already shows the finished setting.
2-15s: replace everything behind the people with the setting from Image 1: short green grass under and around the blanket, the lake and the same shoreline seen in 0-2s. Relight both people to match 0-2s: dappled warm sunlight from the same direction, soft bounce from the grass, contact shadows under the blanket, hands and props, warm edge light on hair and shoulders.
The action continues straight through the 2-second mark in one take: no repeated gesture or word, no cut, no zoom or reframing.
Keep the recorded dialogue and sound unchanged; add no music.
Face and identity unchanged; lips match the recorded dialogue exactly; natural skin texture, no smoothing.
```

Fields: `generate_audio: false`, `resolution: "1080p"` (or `"720p"`) and `output_format: "mov"` on ModelArk. On MuAPI, pick the `-1080p` route and also send `aspect_ratio: "adaptive"` and a whole-second `duration` from 4 to 30 that holds the source.

#### Check the take before calling anything kept

- Pull the same moments from the source and the take: `post_frames_get` with the same `times` (or `frames`) on each, at the hardest face moments (a turn toward camera, mid-line, a close moment). Use `detail: "full"` and a `region` to read a face. Compare faces, hands, wardrobe, the ground and the framing.
- Read the automatic QC review of the take. Compare the soundtrack and lip sync with the source (`audio_align`).
- First compare the submitted beat instructions with source pictures: remove invented gestures or cuts before attributing departures to the model. A global preservation instruction does not cancel conflicting local action.
- If the user requests a correction after reviewing a drifted face, propose one change per authorized rerun:
  1. raise the resolution;
  2. add what drifted to the lock list;
  3. shorten the source;
  4. try an identity still from the plate (untested).

  Offer SwitchX when its pixel-preserving method addresses the observed problem. Tell the person what you compared, retain accepted takes and findings, and obtain their decision before rerunning or changing routes. QC evidence alone does not authorize new generation.

Avoid the anti-patterns this recipe replaces: `pr0ta-prompting/reference/anti-patterns.md` #12 and #13, then grade with `pr0ta-prompting/reference/prompt-rubric.md`.

#### Sources for this recipe

- Official: ByteDance's Seedance 2.5 prompt guide (https://docs.byteplus.com/en/docs/modelark/seedance-2-5-prompt-guide, read 2026-10-28). It covers locked edit tasks, the choice among several videos, edit triggers, the "Preserve … Only modify …" edit example, the 20 s and one-to-five-image recommendations, splitting complex jobs, 8n+1 frames, MOV output and fingerprint textures.
- Official API guides from hosts: Runware's Seedance 2.5 editing guide (https://runware.ai/docs/models/bytedance-seedance-2-5/guides/editing). It covers edit triggers, naming what stays, A-to-B changes, a single source clip, face and wardrobe as reference images, "Keep the audio unchanged", and a clean, evenly lit backdrop separating best.
- Community, with shown examples, untested by PR0TA:
  - Higgsfield's Seedance 2.0 4K footage VFX posts (https://higgsfield.ai/blog/vfx_4k, 2026-06-29). They open with a full lock list, add "Face and identity unchanged", "exact lip-sync" and "Do not re-frame, re-time, re-angle or re-cut", and claim (no side-by-side) that faces hold better at 4K than at 1080p.
  - The open `seedance-footage-vfx` skill (https://raw.githubusercontent.com/ShahriarArabpour/Algoticlab-Skills/main/skills/claude/seedance-footage-vfx/SKILL.md). It says to lock, then change one thing; describe the source from extracted frames; repeat the face lock at the end; keep the subject's light for the lowest identity risk; and that warm directional daylight is safer than night or neon.
- PR0TA's own results:
  - Picnic C010 (480p edit: faces redrawn, grass to gravel; SwitchX kept the actors).
  - Bug d7aee401 (two videos: the earlier take's action replayed).
  - A rerun of C010 with this recipe has not been done yet.

Seedance 2.5 and 2.0 render the same prompt and reference in visibly different styles. Do not mix their takes in one sequence without checking. To keep a 2.0 look in 2.5 work, extend the 2.0 clip on 2.5 with MOV output.

## Realism

For footage that should look captured by a person (phone, camcorder, found footage, documentary), lead with the capture medium and give the camera one operator behavior: `pr0ta-prompting/reference/realism-camera-behaviors.md`.
