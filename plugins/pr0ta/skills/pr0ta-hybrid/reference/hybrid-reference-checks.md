# Check hybrid references and the resulting picture

Read before preparing continuity packets, transforming matte utilities, or
summarizing whether a hybrid reconstruction preserved its source. These checks
support the chosen workflow; they do not authorize generation, repairs or spending.

## Framing is four separate checks

Compare matched source/candidate frames for **subject scale, frame placement,
camera angle and left-to-right order**. Record each result separately. A take can
restore body order while making the people larger, moving them left and showing
more of their backs. Summarize partial adherence directly: “Order matches;
subjects are larger and farther left; camera angle differs.” A QC statement that
a framing image was followed is not proof that all four components match.

## Budget useful continuity coverage before submission

For deliberately requested multi-chunk Omni reconstruction, inspect the previous
accepted video's actual camera-angle coverage. Preserve the user's requested
duration or angle criterion; do not replace a multi-angle video with one endpoint
still or a tiny single-angle tail without a revised plan. For example, a request
for at least 20 seconds **or** two useful angles can be met by a shorter excerpt
only when those two angles are actually present. This is a user-directed recipe,
not a universal provider minimum or a proven quality improvement.

Probe the actual source and continuity assets before constructing the request.
List each input's duration, audio-stream presence and reference role; total all
video durations and any audio counted by that route's aggregate limit. Check
per-file minima, per-file maxima and aggregate limits independently against the
current route contract or an explicit provider validation receipt. Requested
output duration is a separate quantity. Leave margin for measured/container
rounding. Where the limit remains unconfirmed, retain the measured packet and
state that uncertainty rather than inventing a bound or repeatedly submitting it.

**MuAPI Seedance 2.5 Omni:** support inspected the C019 failures on 5 November 2026
and confirmed a **30-second combined input-video limit**. The 29.988-second source
plus 2.002/3.003-second continuity exceeded it, despite the provider's misleading
minimum-duration error. PR0TA measures the final video list before task creation
and refuses packets over 30 seconds or with an unmeasurable video. It never trims
inputs automatically. This confirmation does not establish another route's limit,
an audio-duration rule, or the cause of a different packet below 30 seconds.

Allocate the continuity coverage first, then fit smaller contiguous incoming
source chunks into the remaining budget, preserving every original performance
frame and its sound in the sequence. If a packet does not fit, explain the split;
do not silently drop an angle, cut off source material or shorten continuity
below the user's requirement. A generic “video could not be processed” error
does not establish a minimum duration. Even an explicit minimum-duration error
can conflict with measured provider-hosted bytes; preserve that discrepancy.

Keep the **performance source's original audio** when the chosen reconstruction
needs it. Remove audio only from the separate style/continuity derivative.
`assets_trim` with `asset_type: "video"`, `remove_audio: true`, `in_point: 0` and `out_point` equal to the
probed full duration makes a whole-video, picture-copy derivative without audio
streams. Retain the original and probe the returned derivative. A muted render
may still contain silent AAC: silent loudness is not `has_audio: false`.
If an older client omits `remove_audio` from its tool schema, refresh its tool
catalog rather than substituting mute for audio removal.
Describe the prior video as atmosphere/geography/light context, never footage
to prepend, an old performance to replay, or dialogue to mix into the new take.

## Inspect utilities before transforming holdouts

A nominally white utility can contain a dark perimeter. Inspect all four native
decoded borders before translating, rotating or joining it into a protection
matte; those operations can move the perimeter into the actor region. Check the
rendered joins at native scale and at the source's first/last frames before paid
compositing. Filename, thumbnail and “white” prompt wording do not prove a flat
constant value. Use a verified borderless utility when available. If exact
constant/feathered utility creation is unavailable, say so and obtain a suitable
source rather than claiming a generated image is mathematically constant.
Judge a matte for coverage, edges and timing, not finished-scene colour or sound.

## Separate compatibility from creative verification

A successful revised packet proves compatibility for that packet. If source
length, continuity length, angle coverage and wording changed together, it does
not establish which change cured an earlier provider failure.

Check performance, framing, dialogue/sync, cadence, facial light and environmental
motion separately. A passed request or QC verdict can coexist with weak breeze,
late-only moving shadows, changed gestures or missing dialogue. When the primary
performance source was unavailable to QC, state that exact preservation remains
unverified and compare the source directly before claiming it. A still establishes
neither moving dapple nor wind over the whole shot. Report the temporal range and
surfaces actually checked, retaining unresolved findings.

For requested changes, pair the observed source deficiency with its visible
target, then scope preservation around it: `route-selection.md` → “Explicit
source-to-target changes”. Clear wording directs the model; it does not prove
the delivered effect.
