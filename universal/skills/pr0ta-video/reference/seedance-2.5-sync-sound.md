# Seedance 2.5 sung-performance reference workflow

This recipe applies to `muapi/seedance-2.5-omni-reference`, mode
`ref_to_vid`, `omni_reference_task_type=reference`. It is an empirical
production workaround, not a guarantee of exact music reproduction or lip sync.
Read [the route contract](seedance-2.5.md) first. MuAPI's
[current family documentation](https://muapi.ai/seedance-2.5) describes up to
30 images, 10 videos and 10 audio files, with output up to 30 seconds.
The installed route's audio-array preflight separately enforces a 15-second
combined audio duration. The demonstrated 30-second video carrier does not
remove other reference limits or authorize longer output.

## Choose the sound authority before preparing references

Ask which reference supplies the intended music and which videos supply only
picture continuity. Disclose that an audible continuity video can compete with
the song even when prose calls it “visual only.” Do not silently mute every
video: its sound may be intentional authority.

1. Establish the continuous master song and its transcript first. Keep source
   asset IDs, exact excerpt ranges, lyrics, phrase timings and musical boundary
   context with the production receipt.
2. For continuity-only video, create a separate silent derivative and verify
   that it contains no audio stream or that its decoded audio is silent.
3. For the demonstrated 30-second case, render the intended song excerpt into
   a black-picture video at normal speed. Verify duration and decoded audio
   timing against the source. Black picture is a container, not visual intent.
4. Attach video assets in order: **silent continuity, black song carrier**.
   Supply no separate audio references in this configuration. Preserve the
   ordered asset IDs and each reference's purpose, source range and audio policy.
5. Include exact lyrics in order and relative phrase timings. Specify melody,
   key, tempo, swing, arrangement, vocal character, breaths and syllable lengths.
   Direct the full duration with a few concrete timed picture beats and a final
   landing state. Narrow continuity authority to the beginning when intended.
6. Keep accepted picture paired with its native generated sound through the
   timeline handoff. Never blindly overdub the master onto a different visible
   performance. Preserve source provenance in the asset/sequence notes.
7. Review one canary before expanding. Compare every word, late-phrase timing,
   melody/timbre, visible mouths, instrument attacks, picture continuity and joins.
   Keep insert ambience beneath the continuous song; check for music replacement
   or vocal ducking. Native sound and matching transcripts do not prove sync.

Suggested role wording:

> The first video is silent and supplies visual continuity for the beginning
> only. It establishes the initial cast, wardrobe and setting; the following
> timed directions govern how the world develops. The second video has black
> picture carrying the intended song. Its audio is the sole musical authority
> throughout; the black picture is only a transport container.

## Preparing the derivatives

Make the silent continuity derivative and the black-picture song carrier in Post (or any editor), export them, and upload them as project assets. Before submission verify: the continuity file has no audio stream or decodes to silence; the carrier's duration and decoded audio match the source excerpt at zero lag. Record each derivative's source asset id, range, and audio policy with the returned asset ids, and attach them in the order above. AAC is lossy; keep the master for the final mix.

## Recorded evidence and its limits

Report `a9036186-ea23-4c0d-aa9b-5010a783247c`, My Own Ship, September 7, 2026:

| Test | Configuration | Observed result |
| --- | --- | --- |
| A | Ordinary 15s audio reference plus lyrics | Wrong opening; phrase drift around 1–2s |
| B | 30s black song video plus audible continuity video | Later lyrics recovered; opening contaminated |
| C | B with a muted continuity derivative | 58/58 words; ASR onset median 20ms, maximum 180ms |
| D | Muted continuity and carrier, dynamic timed camera directions | 58/58 words; median 21ms, maximum 740ms near ending |

C is a near-controlled single run: muting also re-rendered at 24fps and dropped
roughly one tail frame. A/B also changed duration. Sampling variation and
conditioning causality remain unresolved. D was creatively accepted, but also
partly replayed the opening, appeared to change the singer's face, and produced
three ships instead of four. Report the worst drift with the median.

The carrier's measured decoded correlation was 0.996689 with 0.375ms lag; the
muted input's decoded peak was zero. These are source-integrity measurements.
ASR word-onset differences are not audiovisual sync measurements. Reliable-sync
claims require replicated provider evaluations and actual audiovisual review.
Do not label this workflow “perfect sync” or generalize to other Seedance routes.
