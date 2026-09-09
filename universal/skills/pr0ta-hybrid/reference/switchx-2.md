# SwitchX 2.0: workflow and API availability

Verified 2026-09-09 against Beeble's [2.0 announcement](https://beeble.ai/research/switchx-2-0) and [live API schema](https://api.beeble.ai/developer-api-docs/openapi.json).

## Availability boundary

Beeble announced SwitchX 2.0 in its cloud app. PR0TA's `beeble/switchx`
and `beeble/switchx-image` use the developer API, which still documents
720/1080 output and 240 video frames. The schema exposes no model-version
selector, Finish operation, or 10-bit output selection. Do not claim PR0TA,
MCP, Resolve, or Premiere is running 2.0 based on the product announcement.
Recheck the provider contract and PR0TA model defaults before submitting.
Do not send guessed 2.0 parameters or substitute an upscale for native Finish.

## Using 2.0 in Beeble's cloud app

1. Keep the original full-resolution plate, its native frame rate, the matte,
   and the approved look reference. The 480-frame ceiling means 20 seconds
   at 24 fps, 16 seconds at 30 fps, or 8 seconds at 60 fps; it is not a universal
   20-second allowance. Split at editorial cuts before processing.
2. White matte regions retain source geometry and performance while receiving
   the reference lighting. Black regions are generated. Design the reference
   for the actual lens, horizon, environment, and light direction.
3. Iterate at 720p, or 1080p when necessary to judge detail. Improved camera
   and fast-motion tracking are model capabilities, not documented API flags.
   Review pans, parallax, lip sync, fast gestures, hair, and occlusion against
   the original footage before approving a take.
4. Use Beeble's Finish workflow on the selected take for native 4K. Finish
   returns to the original source for detail. A new generation with a similar
   prompt, an enlarged draft, or a repeated seed is not evidence of finishing
   the selected take. Retain its identity and inputs for provenance.
5. Download the 10-bit MOV for grading; the MP4 download is 8-bit. Confirm the
   downloaded stream's actual dimensions, bit depth, frame count, frame rate,
   and color metadata before delivery. Do not infer bit depth from `.mov` alone.

## Resolve and Premiere handoff

Until the developer contract supports 2.0, generation through either PR0TA
plugin follows the existing API limits in [switchx.md](switchx.md).
For a separately authorized Beeble cloud workflow, export the trimmed original
plate plus its matte and reference from the NLE, process in Beeble, then import
the downloaded 10-bit MOV into the original sequence at the plate's in-point.
Keep the original audio and timing, compare an overlay against the source, and
check color-management interpretation in the host before grading. This is a
manual handoff, not a PR0TA plugin Finish command.

## Pricing and implementation status

The announcement's two-week 50% offer does not establish API pricing or exact
account eligibility. Query the relevant live price before paid work; do not
apply the cloud offer to PR0TA's API cost calculation without confirmation.

The repository implementation checklist is
`Documentation/switchx_2_api_readiness.md`. Full integration remains pending
the provider's 2.0 developer contract and end-to-end verification.
