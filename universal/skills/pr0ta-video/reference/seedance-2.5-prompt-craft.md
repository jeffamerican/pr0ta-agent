# Seedance 2.5 Prompt Craft

How to write a Seedance 2.5 prompt that the model follows. `seedance-2.5.md` owns routes, request fields, durations, and reference limits; this file owns the writing. The authority is ByteDance's Dreamina Seedance 2.5 prompt guide on BytePlus (updated 2026-10-16), plus production experience. Where the two differ, the provider guide wins. Grade every prompt with `pr0ta-prompting/reference/prompt-rubric.md` before you submit it.

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
- Say which part of an asset to use: "use Video 1 only for the orbiting camera move", "use Image 4 for lighting and grade".
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

A Seedance edit redraws every pixel, the actors included, and faces and hands soften most at 480p. To keep a recorded performance and change only its world, choose the route first: `pr0ta-hybrid/reference/route-selection.md` → "Keep the Plate or Re-render It". Use this recipe when a Seedance edit is the right call: a look draft, a stylized world, or a person who accepts re-rendered actors.

1. **Open with the edit and the shot.** One sentence: "Video edit of Video 1:", who, where, and the camera.
2. **Number every input and give it one job.** "Video 1 is the source." "Image 1 is the approved setting: environment and light only, never the people."
3. **Keep-list in things a camera sees.** Name the people, faces, gestures, eyelines, wardrobe, props, positions, framing and camera move. Concrete nouns hold; abstractions ("sole authority for recorded identities, lens perspective and camera trajectory") give the model nothing to look at.
4. **Scope by time.** Whole-second ranges that cover the clip with no gaps, each with its job: "0-2s: leave unchanged." "2-15s: replace everything behind and around the people with …".
5. **Relight the people for the new world.** Studio-lit people in a sunlit world look pasted on. Give:
   - the key light's direction, quality and warmth, matched to the setting (or to the part of the clip that already shows it);
   - bounce from the ground, walls or greenery;
   - contact shadows under bodies, hands, blankets and props;
   - light wrap and edge light on hair and shoulders against a bright background.
6. **Say the continuity, not the defect.** "The action continues straight through the 2-second mark in one take: no repeated gesture or word, no cut, no zoom or reframing." Never describe a flaw in the source ("a small hand-position mismatch at the boundary"): the model redraws what you point at.
7. **Audio by the flag.** Send `generate_audio: false` to keep the recorded sound; prose alone sets nothing. `keep_source_audio: true` does the same, but only on the dedicated edit routes (`byteplus/seedance-2.5-video-edit` and the MuAPI video-edit routes); on `byteplus/seedance-2.5` it does nothing. Say it once in the prompt as well. Providers keep the source audio inconsistently even with the flag: PR0TA flags a checked take whose soundtrack changed, and otherwise compare the take with the source yourself (`audio_align`, `pr0ta-audio`). Lay the original track back under the picture in Post when it drifted.
8. **Frame and length from the source.** Write no ratio in the prompt. ModelArk edit routes force `aspect_ratio: adaptive` and `duration: -1` themselves. MuAPI edit routes default to 16:9 and 5 s, so send `aspect_ratio: "adaptive"` and `duration: -1` (PR0TA renders the whole seconds that hold the source and trims the take back to it).

Worked example, 15 s, two people filmed in a studio and moved to a lakeside picnic, the first 2 s already showing the new setting:

```text
Video edit of Video 1: two people picnic on a blanket on a sunlit lakeside terrace, one continuous take, the camera exactly as recorded.
Video 1 is the source: keep both people exactly as recorded (faces, performance, gestures, eyelines, wardrobe, blanket, props, positions, framing and camera movement) at its original pace and length.
Image 1 is the approved setting: use it for the environment and light only, never for the people.
0-2s: leave unchanged; it already shows the finished setting.
2-15s: replace everything behind and around the people with the setting from Image 1: its terrace, the lake and the same shoreline seen in 0-2s. Relight both people to match 0-2s: dappled warm sunlight from the same direction, soft bounce from the ground and greenery, contact shadows under the blanket, hands and props, warm edge light on hair and shoulders.
The action continues straight through the 2-second mark in one take: no repeated gesture or word, no cut, no zoom or reframing.
Keep the recorded dialogue and sound unchanged; add no music.
```

Fields: `generate_audio: false`; on MuAPI also `aspect_ratio: "adaptive"` and `duration: -1`. Then check faces, hands and lip sync against Video 1, and the soundtrack as in step 7.

Avoid the anti-patterns this recipe replaces: `pr0ta-prompting/reference/anti-patterns.md` #12 and #13, then grade with `pr0ta-prompting/reference/prompt-rubric.md`.

Seedance 2.5 and 2.0 render the same prompt and reference in visibly different styles. Do not mix their takes in one sequence without checking. To keep a 2.0 look in 2.5 work, extend the 2.0 clip on 2.5 with MOV output.

## Realism

For footage that should look captured by a person (phone, camcorder, found footage, documentary), lead with the capture medium and give the camera one operator behavior: `pr0ta-prompting/reference/realism-camera-behaviors.md`.
