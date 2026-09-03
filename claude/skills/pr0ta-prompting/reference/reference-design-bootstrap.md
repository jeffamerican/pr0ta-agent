# Reference-Design Bootstrap

Use `agent_chat_orchestrate_prompt` when the user needs a net-new character,
hero prop, or wardrobe reference and there is no approved image to attach yet.
The workflow returns a provider-ready **candidate** generation package; it does
not silently approve the design or generate media.

## Choose the profile

| Subject | `prompt_profile` | Required department chain |
|---|---|---|
| Character identity and look | `character_reference_design` | Director → Casting → Production Designer → Stylist → Propmaster → Storyboarder → Cinematographer |
| Hero prop or designed object | `prop_reference_design` | Director → Casting → Production Designer → Stylist → Propmaster → Storyboarder → Cinematographer |
| Wardrobe/look exploration | `wardrobe_reference_design` | Director → Casting → Production Designer → Stylist → Propmaster → Storyboarder → Cinematographer |

Do not override `role_chain` or `optional_roles` for these profiles. The server
supplies and validates the department-correct chain. All stages are consulted.
Director and Storyboarder must contribute; Casting, Production Designer,
Stylist, and Propmaster return `referenceDesignStatus: "not_applicable"` with
an empty `proposedPrompt` when the requested subject has no material decision
inside their authority. They must not invent unrelated characters, wardrobe,
props, or environments merely to make their stage nonempty.

Use `designed_world_reference_image` only when an existing controlled
composition has structural guidance and approved appearance authority. It is
not the bootstrap profile for a subject that has no references.

## MCP example: net-new hero prop

```json
{
  "creative_brief": "Design a near-future courier e-bike as a clean approval reference sheet. Show a three-quarter hero view plus readable side and detail views. It must feel repairable, lightweight, and built for wet coastal streets.",
  "prompt_profile": "prop_reference_design",
  "memory_scope": {"project_only": true},
  "authority_plan": {
    "required_claims": [
      "step-through frame",
      "removable cargo battery",
      "weathered but maintained"
    ]
  }
}
```

No `references` field is required. The profile defaults to
`model_id: "nano_banana_2"` and `modality: "text_to_image"`.

If inspirations exist, add ordered image references with a narrow declared
authority. Semantic aliases `character_reference`, `style_reference`,
`prop_reference`, and `wardrobe_reference` are accepted as `type`; the server
normalizes their media type to `image` while preserving the semantic type.

```json
{
  "references": [
    {
      "asset_id": "asset-uuid",
      "type": "prop_reference",
      "role": "cargo rack mechanism only",
      "authority": "mechanical construction, not colour or silhouette"
    }
  ]
}
```

With one or more references, the default modality becomes
`reference_to_image`. The aliases `ref_to_img` and `img_to_img` normalize to
that modality. A reference modality without references, or a text modality
with references, is rejected before task creation with an actionable 422.

## Complete the workflow

1. Call `memory_context_pack` for the relevant project, scene, character, or
   asset scope when established project facts may constrain the design.
2. Call `agent_chat_orchestrate_prompt` with the appropriate bootstrap profile.
3. Poll the returned task ID with `tasks_get` until it succeeds or fails.
4. Require `result.type == "generation_package"`,
   `result.approval_status == "candidate"`, and inspect the role contributions,
   validation, target model, modality, and final prompt.
5. Present the candidate to the user. Only after explicit approval, pass the
   returned prompt and target settings to `generation_submit`.
6. Poll the generation task with `tasks_get`, review the resulting asset, and
   record an accepted design decision in ProtaFilm|memory only when the user
   actually approves it.

If orchestration returns `prompt_assessment` or a failed task, do not call
`generation_submit`. Surface its diagnostics and revise the brief, authorities,
or references.

## REST shape

REST uses `POST /api/agent_chat/orchestrate_prompt` with the equivalent camelCase
fields: `projectId`, `creativeBrief`, `promptProfile`, `memoryScope`,
`authorityPlan`, `references`, and optional `target`. It returns a queued task;
poll through the project task API just as MCP uses `tasks_get`.
