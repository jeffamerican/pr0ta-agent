# Humanoid Motion Prompting

Text-to-motion is an exception to PR0TA's visual prompting house style. Image and video models render a world, so they benefit from subject, wardrobe, environment, lighting, camera, and mood. A motion model emits joint rotations for one skeleton. Give it only the body configuration and action it can represent.

## Prompt contract

- Use one actor, present tense, and **12–20 words**. HumanML3D training captions average approximately twelve words.
- Describe limb geometry, weight, direction, and the simplest body action.
- Omit objects and props, environment, clothing, multiple actors, camera moves, facial performance, and looping instructions. These are not represented by the output skeleton and often degrade the motion.
- When an action involves a prop, describe the body configuration the prop would produce, then delete the prop from the prompt.

**Bad — visual prose and an unrepresentable prop:**

> "She rides a skateboard forward at a steady cruise, front foot planted across the deck behind the front bolts, back foot near the tail."

**Good — 14 words of body geometry:**

> "A person crouches low, feet far apart, torso twisted sideways, gliding steadily forward."

The good prompt never mentions a skateboard. It describes the stance that a board would produce.

## Guidance and seeds

For Hunyuan motion, start with `guidance_scale` **4–5** and sample several seeds. Variety comes from the seed. Raising guidance on an off-distribution prompt can make the model commit more strongly to a bad interpretation.

Prefer several seeds at moderate guidance over one or two samples at high guidance. Change the prompt only when the measured body behavior shows that the intended geometry is absent.

## Measure before visual review

Do not approve motion from a still frame or overall silhouette. Measure the joint behavior first, then review it by eye:

- For a wide stance, measure average horizontal foot separation and foot-height difference.
- For percussion-like movement, measure wrist travel and whether the hands alternate.
- For locomotion, measure root travel, planted-foot drift, and the expected joint range.

A semantic impression such as "rides" or "drums" is not enough. The geometry must fit the intended production action.
