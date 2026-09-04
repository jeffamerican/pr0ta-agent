# Reference Plate Authoring

The reference image is the strongest control SwitchX has. It decides what the regenerated region contains and how the kept subject is relit. Treat it as a plate that must physically agree with the source camera, not as a mood board.

## Contents

- Geometry alignment rules
- Workflow
- Lighting as the relighting decision
- Using a SwitchX still pass
- QC before the video pass

## Geometry Alignment Rules

- Same lens feel: match focal length, horizon height, and camera height. A reference shot from standing height cannot back a plate shot from a low tripod.
- Same subject scale: the environment's floor, doorways, and furniture must be plausible for the subject's size and position in the plate.
- Same frame: build the reference at the plate's aspect ratio and composition; PR0TA rescales it to the prepared source size but cannot recompose it.
- Same coverage: everything the matte regenerates must exist in the reference, including the ground the subject stands on.

## Workflow

1. Extract the plate's first frame with the Video Editor's frame tools or `saveFreezeFrame`, and use it as the edit source so the geometry is inherited.
2. Edit the frame into the target world with an image edit model from `pr0ta-image`, holding the camera and subject placement and changing only the environment. Nano Banana 2 is the default; use Seedream or GPT Image 2 when adherence to a supplied location still matters.
3. When an approved location still exists, attach it as a reference to the edit and give it appearance authority only; when a Marble world exists, shoot the reference from the matching camera in the world viewer and use the capture as the structure source, as described in `reference/world-anchored-references.md`.
4. Fan out three to five candidates and pick the one whose light direction, horizon, and scale agree with the plate. Reject candidates that moved the camera.
5. Save the chosen reference as a project asset, tag it with `assets_annotations_update` as a location reference, and record it in memory once approved.

## Lighting as the Relighting Decision

SwitchX restyles the kept subject to match the reference's lighting. Decide the light before generating the reference:

- Key direction and elevation must be plausible for the plate; a subject lit from camera left cannot be relit convincingly by a reference keyed from camera right.
- Color temperature and contrast in the reference become the subject's new grade.
- Practical lights in the reference create the new contact shadows and reflections; include them where the plate needs them.

Describe the same lighting in the prompt so the text and the image agree.

## Using a SwitchX Still Pass

`beeble/switchx-image` can build the reference plate itself: send the extracted frame as `image_asset_id`, an approved location still as `reference_image_asset_ids[0]`, and `alpha_mode: "auto"`. The result keeps the subject pixels and regenerates the background from the location still, which is usually closer to the final video look than a generic image edit. Iterate on stills until the look is right, then run the video route with the approved still as the reference.

## QC Before the Video Pass

- Overlay the reference on the plate frame and check horizon, floor line, and subject footprint.
- Confirm the reference contains nothing that contradicts the matte, such as an object where the kept subject stands.
- Confirm the reference's light direction matches the prompt.
- Keep the reference free of text, watermarks, and letterboxing; they propagate.
