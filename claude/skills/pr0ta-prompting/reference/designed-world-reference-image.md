# Controlled Designed-World Reference Images

Use this contract when a generated image must preserve exact semantic screen
structure while translating it into a locked Production Designer world. The
canonical prompt profile is `designed_world_reference_image`.

## Contents

- Hard Contract
- Required Workflow
- Department Ownership
- Exact Prompt Shape
- Canonical Tool Call
- Acceptance Gate

## Hard Contract

- Prefer one first-class `guidance_package` containing exactly two coordinated,
  non-appearance image passes:
  - `Reference 1`: neutral `flat_structural` authority for camera, crop,
    silhouette, openings, boundaries, object placement, and relative scale;
  - `Reference 2`: `depth_normalized` data for near/middle/far ordering and
    occlusion only.
- Assign `Reference 3` to the first and only appearance authority. Use one
  user-approved story-world image with `guidance_kind: "appearance"`.
- Treat the flat/depth pair as indivisible. Both members must share
  `guidance_package_id`, resolution, and camera/frame identity. Select both or
  reject the package.
- The backward-compatible path remains valid: `Reference 1` is one
  `semantic_asset_id` structure pass and `Reference 2` is approved appearance.
- Keep all base assets different and keep their order fixed.
- Preserve active character, styling, prop, lighting, and action references as
  candidates. Mark visible cast and continuity-critical hero props `required`.
- `visible: true` and `continuity_critical: true` automatically make a candidate
  required; an explicit `required: true` does the same for another authority.
- Exclude inactive, rejected, and superseded references with an audit reason.
- Treat the Director's approved visual style and image language as authoritative.
- Treat the Production Designer's locked physical environment—location identity,
  architecture, set decoration, materials, fixtures, practical props, signage,
  terrain, and spatial relationships—as authoritative.
- Never give neutral-flat values, grayscale depth, or false-color semantic
  regions appearance authority.
- Never let the appearance image change camera, crop, screen geography,
  silhouettes, openings, occlusion, or the required action.
- Never mention an image that is absent from the submitted package.
- Depth normalization must use finite visible rendered pixels only, excluding
  sky/background/infinite Z, hidden, occluded, and out-of-frame geometry. Store
  near/far metres, percentile policy, `near_white_far_black`, explicit black
  background value `0`,
  occupied dynamic range, histogram bins, middle-tone fraction, and pass/fail QC.
- UI inspection may false-colour depth for humans, but the provider input must
  remain the registered grayscale `depth_normalized` asset.
- Reject before generation when depth metadata is missing or non-finite,
  `far_m <= near_m`, QC is binary/inadequate, package members disagree, either
  member is pruned, or the terminal prompt misstates authority.

With a first-class package, do not add beauty, legacy depth, normals, outline,
false-colour Asset-ID, or duplicate aligned structural passes. The legacy
single-structure path may still use one diagnosed fallback, but never stack
diagnostic passes.

## Required Workflow

1. Supply the complete current creative brief, binding authoritative overrides,
   and positive required story claims. The orchestrator builds one authority
   packet from those requirements, the declared reference roles, and filtered
   approved ProtaFilm|memory facts, active decisions, and continuity. Candidate,
   rejected, inactive, and superseded memory stays outside this packet.
2. Verify the neutral flat pass against the intended camera, crop, silhouette,
   openings, boundaries, object placement, scale, and action. Verify the depth
   pass has passing visible-pixel histogram QC and matching package identity.
3. Verify that the appearance image is approved and actually expresses the
   locked story world. Do not infer approval from its presence in the library.
4. Call `agent_chat_orchestrate_prompt` with
   `prompt_profile: "designed_world_reference_image"`.
5. Keep the default role chain: Director → Production Designer → Stylist →
   Propmaster → Storyboarder → Cinematographer. The configured Stylist and
   Propmaster are always consulted. When the submitted authority set has no
   cast/wardrobe or hero-prop subject, that department returns a typed
   `not_applicable` contribution.
6. For a location/environment-only request, set
   `subject_presence: {cast: false, wardrobe: false, hero_props: false}`. This is
   frozen context for the specialist agents; it does not elide their calls.
7. Poll the returned task with `tasks_get` and branch on `result.type`. A
   `generation_package` is ready for use. A `prompt_assessment` means the
   Cinematographer reports `needs_clarification` or `has_problems` for explicit
   review; read its questions or issues, do not assume
   `final_prompt` exists, and do not reconstruct a prompt from partial chat
   messages. Treat task failure, degraded required stages, and terminal
   validation errors as failure.
   A failed primary gets either one repair or one retry of the same configured
   department runtime. Orchestration never substitutes a hard-coded model.
   Exhausted attempts are not resumable. Call `agent_chat_resume` only when the
   failure supplies `error.details.retry_token`; its frozen checkpoint preserves
   completed typed stages. Confirm `error.details.target_generation` says
   `submitted: false` and `charge_incurred: false` before reporting that no
   target-generation charge occurred.
8. Only from a validated `generation_package`, inspect `generation_receipt`,
   confirm the provider order, normalization metadata, selected/excluded
   references, and QC, then generate one diagnostic image. QC flat structure,
   depth ordering, and appearance as separate dimensions.
9. Ask for explicit user approval before writing selected images into Production
   Designer reference slots, style packages, or project canon. Record accepted
   decisions in memory only after approval.

## Department Ownership

- Director: return `designedWorldDirector`; own story function, camera, screen
  geography, action, circulation, visual style, palette roles, weather, lighting,
  atmosphere, and practical shot choices.
- Production Designer: own physical location identity, architecture and built
  form, set decoration, materials and finishes, fixtures, practical props,
  signage, terrain, and spatial relationships without changing story, style, or
  shot intent. Return `designedWorldProductionDesign` as positive current-world
  facts covering location identity, architecture, set decoration, materials,
  fixtures, props, signage, spatial relationships, terrain, and depth context.
  Environmental set-dressing placement remains here; continuity-critical
  hero-prop identity and state belong to Propmaster.
- Stylist: own wardrobe, hair, makeup, and current character-look facts and
  recommend matching submitted references. Casting owns identity and provider
  tokens. Return `designedWorldStyling`, or `not_applicable`.
- Propmaster: own visible or continuity-critical prop identity, state, handling,
  and matching reference recommendations. Return `designedWorldProps`, or
  `not_applicable`.
- Storyboarder: return `designedWorldSections` with `exactFrame`,
  `designedWorldLock`, `appearanceContract`, and five to eight positive
  `validationAssertions`, plus `referenceBindings`, `excludedReferences`, and
  `missingAuthorities`. It must select or exclude every active candidate, keep
  the indivisible flat/depth pair first with appearance immediately after it,
  and select every required cast/prop authority. Binding `promptFacts` must be
  copied verbatim from submitted candidate metadata or validated Stylist and
  Propmaster handoffs; Storyboarder cannot author or paraphrase those facts. On
  the legacy path it keeps structure and appearance first.
- Cinematographer: perform the terminal suitability review and return
  `prompt_assessment` plus optional bounded `section_revisions`. It may revise
  exact frame, appearance contract, and validation assertions. It validates the
  final numbered reference order and the typed authority clause: flat controls
  structure; depth controls ordering only; grayscale is data and cannot become
  palette, material, lighting, weather, or atmosphere; appearance controls all
  visible appearance. A physical-world
  lock change routes to Production Designer, after which Storyboarder recomposes
  the typed sections before the next review. The platform renders the final prompt.

## Exact Prompt Shape

The platform renders each marker exactly once and in this order:

1. `REFERENCE CONTRACT.`
2. `EXACT FRAME.`
3. `DESIGNED-WORLD LOCK.`
4. `APPEARANCE CONTRACT.`
5. `FINAL VALIDATION:`

Use the sections as follows:

- `REFERENCE CONTRACT.` On the preferred path, state that Reference 1 controls
  flat structure only, Reference 2 controls spatial ordering/occlusion only,
  grayscale is data with zero appearance authority, and Reference 3 controls all
  visible appearance. Each selected additional reference controls only its
  declared shot-specific subject. On the legacy path, Reference 1 controls
  structure and Reference 2 appearance.
- `EXACT FRAME.` State the exact camera, crop, screen geography, silhouettes,
  openings, occlusion, scale, circulation, and action.
- `DESIGNED-WORLD LOCK.` State the authoritative Production Designer location,
  architecture, set decoration, materials, fixtures, signage, terrain, and
  spatial relationships.
- `APPEARANCE CONTRACT.` State the Director-approved palette, print or surface
  texture, lighting, atmosphere, weather, and image language expressed by
  Reference 2.
- `FINAL VALIDATION:` State five to eight positive assertions covering the
  highest-risk story, geography, physical-design, and appearance requirements.

Use literal numbered `Reference N` labels in the image prompt; do not substitute
`@imageN`. The terminal package performs provider-specific binding and carries
approved Seedance character tokens forward separately.

## Canonical Tool Call

```json
{
  "creative_brief": "Describe the exact shot, locked location, required action, and known risks.",
  "prompt_profile": "designed_world_reference_image",
  "guidance_package": {
    "guidance_package_id": "shot-c-guidance-v1",
    "camera_frame_id": "camera-frame-shot-c",
    "resolution": {"width": 1280, "height": 720},
    "passes": [
      {
        "asset_id": "flat-pass",
        "guidance_kind": "flat_structural",
        "flat_mode": "neutral_clay"
      },
      {
        "asset_id": "depth-pass",
        "guidance_kind": "depth_normalized",
        "depth_convention": "near_white_far_black",
        "normalization": {
          "source": "visible_rendered_pixels",
          "near_m": 0.72,
          "far_m": 21.4,
          "near_percentile": 2,
          "far_percentile": 98,
          "background_value": 0
        },
        "depth_qc": {
          "passed": true,
          "effectively_binary": false,
          "occupied_bins": 96,
          "middle_tone_fraction": 0.61,
          "occupied_dynamic_range": 0.94
        }
      }
    ]
  },
  "references": [
    {
      "asset_id": "approved-appearance-reference",
      "type": "image",
      "guidance_kind": "appearance",
      "role": "appearance only",
      "authority": "palette, texture, light, atmosphere, material expression"
    },
    {
      "asset_id": "current-character-portrait",
      "type": "image",
      "guidance_kind": "character_identity",
      "role": "Bug identity",
      "authority": "casting identity only",
      "subject_id": "bug",
      "subject_name": "Bug",
      "provider_token": "@omni-character:bug-v2",
      "visible": true
    },
    {
      "asset_id": "hero-skateboard-reference",
      "type": "image",
      "guidance_kind": "prop_identity",
      "role": "hero skateboard",
      "authority": "prop identity and state only",
      "continuity_critical": true
    }
  ],
  "authority_plan": {
    "requiredClaims": ["locked location identity", "required action"]
  }
}
```

The profile defaults to `muapi/seedream-5.0-pro-edit` with
`reference_to_image`. Override technical parameters only when the selected
model's live schema requires it; never invent provider fields.

Blender-worker outputs store the same package metadata in each asset's
`designed_world_guidance` labels. For external uploads, attach those labels to
each pass through the normal asset upload/finalize metadata surface; the
orchestrator resolves project asset IDs and treats stored guidance metadata as
authoritative over caller restatements.

## Acceptance Gate

Reject the package unless the prompt contains the five ordered markers, names
every selected reference and no excluded reference, includes five to eight
positive validation assertions, preserves the Production Designer lock, keeps
authorities separate, retains both flat/depth members in deterministic order,
selects all required cast and hero-prop references, and fits the provider
reference limit. The receipt must list selected and excluded authorities with
reasons, package/camera lineage, depth normalization and QC, validation results,
and final provider order. A successful task
proves prompt construction only; it does not prove that an image was generated,
saved, approved, or added to canon.
