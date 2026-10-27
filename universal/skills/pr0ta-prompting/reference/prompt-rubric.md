# Prompt Self-Check

Grade every video prompt against this list before you submit it. It holds for any model; the model's own reference wins where it says something different. Image prompts use the same list without the time and camera items.

## Grades

- **A:** every item passes. Submit.
- **B:** the route is right, every input is attached, nothing contradicts, but a craft item fails. The take may work; it is less likely to. Fix and regrade.
- **C:** the wrong route, an input named but not attached, or a contradiction. Fix that first.

Submit only an A. An item the route cannot support (no such field) passes; say why in your reasoning.

## The Checklist

**Route and fields**

1. **The route keeps what must survive.** A recorded performance that must reach the cut needs a plate-preserving route; a generative edit redraws the actors (`pr0ta-hybrid/reference/route-selection.md` → "Keep the Plate or Re-render It").
2. **Settings are fields, not prose.** Audio (`generate_audio: false` keeps a source's sound; `keep_source_audio` works only on the dedicated edit routes), duration, resolution, aspect ratio and negative prompt go in the request fields the route exposes. Prose may repeat a setting once; it never replaces the field. On an edit, extend or first-frame job, write no ratio in prose; set the field to `adaptive` or the source's ratio where the route exposes one.

**Inputs**

3. **Every input is attached and named in the model's syntax,** in final upload order: `Video 1` / `Image 1`, `@image1`, `<IMAGE_0>` (`pr0ta-prompting` → "Reference Syntax Is Per Model"). Never "the attached image" or "the approved portrait".
4. **Each input has one job and a limit.** "Image 1 is the approved setting: environment and light only, never the people."

**Picture**

5. **Self-contained.** A stranger could picture the shot from the prompt alone. No "same as before", no pronouns that point at other shots; descriptors copied word for word from the prompt bible.
6. **Visible, not abstract.** Things a camera sees: faces, hands, the blanket, "dappled warm sunlight from camera left". Not "authority for identity and lens perspective", "cinematic", "dramatic lighting".
7. **Time is explicit.** For more than one beat, use whole-second ranges with no gaps or `Shot N` blocks; a single-beat clip needs only the action and a visible end state. On an edit, say which seconds change and which stay.
8. **Light comes from sources.** Direction, quality and warmth. When people move into a new world: bounce, contact shadows, edge light.
9. **One camera behavior per beat,** described physically ("slow push-in", "handheld, drifting left"), or "exactly as recorded" on an edit.

**Exclusions**

10. **Wanted states are written positively.** Exclusions are short, each paired with what it protects, and only for problems seen or invited (`pr0ta-prompting` → Technique 4).
11. **The unwanted state is never named as a fact.** "Studio-filmed footage" anchors the studio look; "a small hand mismatch" invites a redraw of the hands. Say the result: "the action continues straight through the 2-second mark in one take".

**Fit**

12. **Nothing contradicts.** One camera path, one ratio, roles that do not overlap, action that fits the duration.
13. **Shortest prompt that passes 1-12,** within the model's prompt limit.
14. **You know how you will check the take.** What to compare and against what: faces and hands against the source, the soundtrack against the source, length against the plan.

## Example

The prompt behind the "Replace the World Around Live Action" recipe (`pr0ta-video/reference/seedance-2.5-prompt-craft.md`) graded B: a Seedance edit is defensible for a 480p look draft (a final would call for SwitchX), and its inputs were attached, but it wrote "Output 16:9" on an edit (2), called Image 1 "the attached image reference" (3), listed abstractions (6), implied the change instead of timing it (7), relit thinly (8), and named "studio-filmed footage" and a hand mismatch (11). The recipe's worked example is the A rewrite.
