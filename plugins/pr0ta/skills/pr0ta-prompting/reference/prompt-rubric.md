# Prompt Self-Check

Grade every video prompt against this list before you submit it. It holds for any model; the model's own reference wins where it says something different. Image prompts use the same list without the time and camera items.

## Grades

- **A:** every item passes. Submit.
- **B:** the route is right, every input is attached, nothing contradicts, but a craft item fails. The take may work; it is less likely to. Fix and regrade.
- **C:** the wrong route, an input named but not attached, or a contradiction. Fix that first.

Submit only an A. An item the route cannot support (no such field) passes; say why in your reasoning. Items 1 and 2 are the exception when the shot keeps a recorded performance or recorded speech: then a request with no way to keep it fails them. A shot that keeps neither passes both.

The grade is for the prompt and request. A take that keeps a recorded performance is called kept only after it has been checked against the source (item 15), never on the prompt's word.

## The Checklist

**Route and fields**

1. **The route and inputs can keep what must survive.** A recorded performance that must reach the cut (the actors' faces and likeness, gestures, lip movements and timing, the source's framing and cuts) needs a request that edits the plate:
   - a Seedance 2.5 edit (a video-edit route, or Omni with `omni_reference_task_type: "edit"`) with the plate as its only video, at 720p or more when faces matter, and a prompt that locks the faces, performance and timing (`pr0ta-video/reference/seedance-2.5-prompt-craft.md` → "Replace the World Around Live Action");
   - or SwitchX with a matte, or a matte composite, when the plate's pixels must come through exactly.

   A reference, text- or image-to-video request regenerates the performance and fails this item. Prose cannot turn one into an edit: "Video 1 is the sole action timeline" earns nothing on its own (`pr0ta-hybrid/reference/route-selection.md` → "Keep a Performance: Seedance Edit or SwitchX").
2. **Recorded dialogue stays recorded.** Generated speech never replaces recorded speech in a hybrid. On the video-edit routes send `generate_audio: false` (keeping the source's sound with it is verified only there), and lay the source's soundtrack back under the take if it drifted. On any other route, including an Omni edit (`byteplus/seedance-2.5`, or MuAPI Omni, which always generates sound), plan that re-lay in Post before you submit.
3. **Settings are fields, not prose.** Audio (`generate_audio: false` keeps a source's sound; `keep_source_audio` works only on the dedicated edit routes), duration, resolution, aspect ratio and negative prompt go in the request fields the route exposes. Prose may repeat a setting once; it never replaces the field. On an edit, extend or first-frame job, write no ratio in prose; set the field to `adaptive` or the source's ratio where the route exposes one.

**Inputs**

4. **Every input is attached and named in the model's syntax,** in final upload order: `Video 1` / `Image 1`, `@image1`, `<IMAGE_0>` (`pr0ta-prompting` → "Reference Syntax Is Per Model"). Never "the attached image" or "the approved portrait".
5. **Each input has one job and a limit.** "Image 1 is the approved setting: environment and light only, never the people." On an edit, the source is the only video: the model blends the action and sound of every attached video, so an earlier take rides as a still (its last frame) for continuity, never as a second video. A submit or quote result's `request_advisories` flags this.

**Picture**

6. **Self-contained.** A stranger could picture the shot from the prompt alone. No "same as before", no pronouns that point at other shots; descriptors copied word for word from the prompt bible.
7. **Visible, not abstract.** Things a camera sees: faces, hands, the blanket, "dappled warm sunlight from camera left". Not "authority for identity and lens perspective", "cinematic", "dramatic lighting".
8. **Time is explicit.** For more than one beat, use whole-second ranges with no gaps or `Shot N` blocks; a single-beat clip needs only the action and a visible end state. On an edit, say which seconds change and which stay.
9. **Light comes from sources.** Direction, quality and warmth. When people move into a new world: bounce, contact shadows, edge light.
10. **One camera behavior per beat,** described physically ("slow push-in", "handheld, drifting left"), or "exactly as recorded" on an edit.

**Exclusions**

11. **Wanted states are written positively.** Exclusions are short, each paired with what it protects, and only for problems seen or invited (`pr0ta-prompting` → Technique 4).
12. **The unwanted state is never named as a fact.** "Studio-filmed footage" anchors the studio look; "a small hand mismatch" invites a redraw of the hands. Say the result: "the action continues straight through the 2-second mark in one take".

**Fit**

13. **Nothing contradicts.** One camera path, one ratio, roles that do not overlap, action that fits the duration.
14. **Shortest prompt that passes 1-13,** within the model's prompt limit.
15. **You know how you will check the take.** Say what you will compare, and against what:
    - faces, hands and the ground against the source, with the same `post_frames_get` `times` or `frames` on both;
    - the take's QC review;
    - the soundtrack and lip sync against the source (`audio_align`);
    - the length against the plan.

## Example

The prompt behind the "Replace the World Around Live Action" recipe (`pr0ta-video/reference/seedance-2.5-prompt-craft.md`), a 480p edit of the picnic plate, graded B under the earlier rubric; at 480p with faces that must hold, it now fails item 1 (C). Its inputs were attached, but it also wrote "Output 16:9" on an edit (3), called Image 1 "the attached image reference" (4), listed abstractions (7), implied the change instead of timing it (8), relit thinly (9), and named "studio-filmed footage" and a hand mismatch (12). The recipe's worked example is the A rewrite. It also locks the faces, names the grass in the keep-list and renders at 720p or 1080p: fixes aimed at that picnic edit (C010), which redrew both faces and turned the grass to gravel, not yet tested in a rerun.

The Lago di Como hybrid chunk (2026-10-28) self-graded A and was a C: a Seedance 2.5 Omni edit with the source and the preceding generated take as two videos (1, 5), on a route that generates its soundtrack (2). Its prose ("Video 1 is the sole action timeline", "Video 2 is visual continuity only", "the original soundtrack remains the editorial authority") changed none of that: the take replayed the earlier take's action and its sound did not match the source. The A version is a Seedance edit of the source as its only video: the video-edit route with `generate_audio: false` (or Omni edit with the source soundtrack laid back in Post), the earlier take's last frame as an image, and the recipe's face and performance lock, checked against the source before it is called kept. SwitchX with a custom matte is the alternative when the plate's pixels must come through exactly.
