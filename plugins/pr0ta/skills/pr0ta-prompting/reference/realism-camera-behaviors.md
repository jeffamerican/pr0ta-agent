# Realism: A Person Is Holding the Camera

Generated footage reads as fake when it is filmed like a robot: perfectly level, perfectly exposed, perfectly focused, the camera already pointing at the action before it happens. Footage reads as real when a person seems to be holding the camera and reacting late and imperfectly to what happens in front of it.

Use this reference when the look calls for footage someone captured: phone video, a consumer camcorder, found footage, documentary, mockumentary, a candid snapshot, a hidden observer. A polished cinematic look (dolly, crane, gimbal) is a different choice; the project's style decides which one applies. The techniques work on any image or video model. Per-model grammar still comes from the resolved model's reference (Seedance 2.5: `pr0ta-video/reference/seedance-2.5-prompt-craft.md`).

## Lead With the Capture Medium

The first sentence names how the picture was captured: the device, the lens, the viewpoint, and the framing flaws. It sets the whole look, so it comes before the subject.

Inside a project the server adds the scene's look line (Style page) to every prompt. When the whole project or scene is captured footage, the capture medium belongs in that look line: propose it (Reusing a Look below) instead of writing it into each prompt. Write a capture sentence into a single prompt only when that shot departs from the project's look (one phone clip inside a filmed scene), and make sure it does not contradict the look line.

| Capture medium | What the sentence names |
|---|---|
| Phone, rear camera, bystander | Arm's-length or chest-height handheld, normal field of view, autofocus and auto-exposure, phone HDR, slight motion blur |
| Phone, front camera, selfie | Ultra-wide front lens with barrel distortion at the edges, high angle from the outstretched arm, the arm entering the frame, a smudged lens |
| Consumer camcorder (2000s) | Low dynamic range, low-bitrate softness, blocky compression, interlaced motion artifacts, washed-out colour, a clumsy optical zoom |
| Disposable or point-and-shoot with flash | Harsh direct on-camera flash, a blown foreground, shadows falling off hard into black, red-eye glints, a tilted horizon |
| Skate camera | 12mm fisheye from knee or pavement height, curved edges, a crooked horizon, the subject looming toward the lens |
| Hidden observation | Filmed through a door gap or from behind cover, dark foreground edges, the subjects unaware of the camera |
| Documentary handheld | Shoulder-height handheld, available light, framing that corrects after the action starts |

For stills, write one sentence each in the order **camera, tone, light, texture**: camera (medium, lens, viewpoint, framing), tone (the feeling, as if caught by a passerby), light (the actual sources), texture (two or three physical qualities that interact with the light). For video, put the capture sentence at the top of the camera or visual-style section, then the operator behavior below.

## Prompt the Imperfections

Name the imperfections the medium produces: film grain, sensor noise in the shadows, JPEG or MPEG compression, blown highlights, flash falloff, chromatic fringing, a crooked or off-centre frame, a subject half out of frame, motion blur from a rocking train. Use only the ones that fit the medium and the scene, and leave out "8K", "masterpiece", and "ultra-detailed": they pull the image back toward a polished render.

The imperfections belong in the prompt. Choosing a lower output resolution is a separate decision; for video, finish the approved draft as usual (`pr0ta-video/reference/draft-to-final.md`), and compare the finished take with the draft when the look depends on rawness.

## Operator Behaviors

Write each behavior as a chain: **what happens in the scene → what the camera does wrong → one correction → the settled final frame.** Give a shot one behavior, follow it once, and finish on its clear result. Say how the camera physically moves, because zoom, pan, and walking look alike to a model unless the prompt separates them.

| Behavior | Write |
|---|---|
| Handheld reaction | Continuous small, irregular hand tremor. At the event, the operator flinches back and the frame rolls slightly; the operator then re-centres the subjects. The shot never becomes smooth or stabilized. |
| Crash zoom | The operator's feet stay planted and only the lens zooms: the background magnifies without the camera travelling forward. A short radial smear, a slight overshoot, a moment of soft focus, then focus returns on the subject. |
| Whip pan | A sound makes the operator turn. One rapid horizontal rotation; objects between smear sideways; the frame overshoots the target, corrects once, and settles. It is a physical turn in the same space, not a cut. |
| Walking backward | The subject walks toward the lens while the operator retreats. Each step adds vertical bob and a small roll; nearby objects slide past faster than the background; the subject's size stays roughly steady. It is neither a zoom nor a smooth tracking rig. |
| Peek from cover | The operator is hidden behind a door edge or a pillar, with dark cover filling the foreground. The camera leans out just enough to reveal the action, then pulls back. The subjects never notice the camera. |
| Foreground obstruction | Someone crosses close to the lens. Autofocus grabs the near object and the subject goes soft; once the object clears, focus snaps back onto the subject's eyes and the operator reframes slightly. |
| Exposure adaptation | Moving from a dark interior into sunlight washes the frame nearly white; automatic exposure then lowers the brightness until the subject is readable. |
| Focus hunt | During a fast, slightly clumsy zoom, focus slides past the subject once, then snaps back sharp on the subject's expression. |
| Handover | The shot starts steady, the camera changes hands, and it finishes handheld. |

Combining two or three behaviors across a sequence (a whip pan in one shot, a focus recovery in the next) sells realism better than piling them into one shot.

## Keep the Camera Out of Its Own Picture

- The operator stays unseen and the recording device stays outside its own field of view. The operator's hands stay out of frame unless the medium is a selfie.
- Recording looks invite on-screen graphics. State the clean picture first ("a clean full-frame recording image"), then exclude the overlays the model would otherwise add: REC indicator, timestamp, battery icon, focus brackets, viewfinder grid, border, subtitles. Use the route's `negative_prompt` field where it has one; on Seedance 2.5, write the exclusions in the prompt (`pr0ta-prompting` → Technique 4).
- Say where the imperfection comes from: it comes from the camera's movement, focus, or exposure, not from graphics on the picture.
- A date stamp or a REC icon that the story needs is on-screen text: specify it exactly (`pr0ta-video/reference/generative-typography.md`).

## Sound for Captured Footage

Match the sound to the device: a raw phone or camcorder microphone, wind noise, mic distortion on loud moments, room tone, and the action's own sounds, cut abruptly at each hard cut. Bystander reactions can be wordless (gasps, laughter, screams). When someone speaks, require intelligible words: laughter accompanies the line rather than replacing it. When the camera turns away from a speaker, the voice continues off screen from where the speaker stands. `pr0ta-video/reference/native-audio.md` covers dialogue fields.

## Make the Image Worth Looking At

Realism makes an image believable; contrast makes it worth watching, especially in spots and social pieces. Raise contrast one level at a time:

1. **Expected:** the subject in the place it belongs (a robot in a factory).
2. **Unexpected situation:** the same subject somewhere it does not belong (the robot slumped beside a car charger at night).
3. **Unexpected styling:** an attitude or styling that gives the subject personality.
4. **Feeling:** a pairing that makes the viewer feel something (hard metal powered down among soft flowers).

Use this while developing ideas with the person; it does not override an approved script.

## Reusing a Look

When the person likes a still or take and wants its capture look again, distil its capture sentence and two or three texture qualities into a proposed update to the style world's look text (`pr0ta-prep` → style worlds), so every later prompt starts from the same medium. Agree the wording with the person before saving it, and never approve a look yourself.

## QC

PR0TA's QC treats camera motion as creative and never flags shake. When the shot plan or look calls for captured footage, the planned focus hunting, exposure pumping, flash blowout, grain, and compression are part of the look, not faults. QC findings are flags; the person decides.
