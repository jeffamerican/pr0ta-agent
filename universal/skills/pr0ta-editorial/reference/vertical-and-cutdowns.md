# Vertical, Social and Cutdowns

> **See also:** the parent `pr0ta-editorial` SKILL.md for the ship gate and the rewrite loop; `pr0ta-timeline` → "Sequences, Sources and Framing", "Text and Captions" and "The Verification Loop" for the mechanics.

Read this before cutting anything for a feed: Reels, Stories, TikTok, Shorts, a 6–60 second ad, or a shorter version of an existing piece.

## A Recut Is a New Film

A cutdown is not the long version with pieces removed. A 30-second Reel made from a 90-second 16:9 commercial has a different viewer (scrolling, sound off, one thumb from leaving), a different frame and a different clock. Write its own one-sentence spine before touching the timeline, for that length and that viewer. Then pick shots for the spine; most of the long version will not fit and that is correct.

The failure to avoid: a **highlights reel**, the best-looking shots of the original in their original order, cut shorter, with no story of their own. It reads as a trailer for something the viewer will never see. If your cut list is the original's shots in the original's order, stop and write the spine.

**Story beats for short ads** (time budgets are guides, not rules):

| Length | Beats |
|---|---|
| 6 s bumper | One idea: hook image → product or payoff → brand. No setup. |
| 15 s | Hook (0–2 s) → the problem or desire (2–6 s) → the product doing the one thing (6–12 s) → brand, offer, call to action (12–15 s). |
| 30 s | Hook (0–2 s) → tension (2–10 s) → turn: the product or idea (10–20 s) → proof or payoff (20–26 s) → end card (26–30 s). |
| 60 s | A short story with one character and one change; the brand lands inside the story by the midpoint and again on the end card. |

Each length is cut from its own spine. Never derive the 15 from the 30 by trimming; derive both from the brief.

## The First Two Seconds

The feed decides in about a second. The first frame is also the thumbnail.

- Open on the most arresting image you have: motion, a face looking at the lens, the payoff itself, a striking contrast. Never a logo, a slow fade-up, an establishing wide where nothing happens, or black.
- Put the hook in text too (a title or caption clip from frame 0), because most viewers start with the sound off.
- The first cut lands inside the first 1–2 seconds. A long first shot loses the scroll.
- Check it: `post_frames_get` at `times` `[0, 0.5, 1.0, 1.5, 2.0]` on the render. Would you stop scrolling on frame 0?

## Reframing for 9:16

Set the sequence to 1080×1920 before cutting. Probe every source (`assets_probe`): a 16:9 source in a 9:16 frame is letterboxed (`fit: contain`) and fills a third of the screen. For each shot, decide:

1. **Native vertical** material: use it.
2. **Cover and reposition**: `"fit": "cover"`, then `transform.positionX` to keep the subject in the window (about −1.08 to 1.08 pans the full width of a covered 16:9 source; positive shows more of its left side). Keyframe `positionX` to follow a subject that moves.
3. **Regenerate or re-shoot vertical** when the crop fails: subjects at opposite edges, important text or product at the side, a composition that only works wide. Generate the vertical shot (`pr0ta-video`) from the same references.

Never ship a contained 16:9 shot with bars in a vertical cut, unless it is a designed frame-in-frame with a deliberate background and text above and below. Look at every reframed shot with `post_frames_get` on the sequence; `analysis` flags each `letterboxed_source`.

## Safe Zones

Feed apps cover parts of a vertical frame with their own interface: the account line and buttons at the top, the caption, sound line and call-to-action buttons at the bottom, and the like/comment/share stack on the right. The areas vary by app and change over time, so keep everything that matters in the central band:

- Text, faces, product and logo stay out of the top 12–14%, the bottom 20–25%, and the right 15% of the frame.
- Caption clips with `safeArea` (the default) sit above the bottom 20%; raise `position` to `center` or move the caption up when the app's own caption or a call-to-action button will cover more.
- Nothing essential at the edges of a cover crop either: a viewer on a different phone may see slightly less.

## Captions and On-Screen Text

Assume the sound is off. Every spoken line is captioned (`text.role: "caption"`), and the message is on screen as text at the moments it matters.

- Captions are verbatim, one or two lines, short lines (about 32 characters or fewer), each on screen exactly while its words are spoken; time them from word timing (`transcription_get`), never by guess. Break lines at phrase boundaries.
- High contrast: white on the default dark box, or a bold color the brand allows. Never over a face, never over the product.
- On-screen titles carry the hook, the claim and the offer in a few words each; one idea per card. Read every card aloud, character by character, against the script.
- Caption clips also export as an SRT sidecar; upload it with the video where the platform accepts one.

## Pacing for 15–60 Seconds

- Cut fast early (a cut every 1–2 seconds in the opening), then let one or two key shots breathe; uniform two-second cuts read as a slideshow.
- One idea per shot. If a shot needs explaining, it is the wrong shot.
- The brand or product is visible by the midpoint, not only on the end card.
- Cut on beats of the music bed (`music_analyze` downbeats) and on the emphasis of spoken words.
- No consecutive slices of one take presented as separate shots: the cut is invisible and reads as a stutter (analysis flags `adjacent_same_source_slices`). Merge them or cut away between them.
- End on the end card: brand, offer, call to action, held long enough to read twice (about 2–3 seconds).

## Sound

Design for both sound-off and sound-on. With sound on, music carries energy and the voice carries the claim; mix to about −14 LUFS integrated with true peak at most −1 dBTP (the verification loop measures it). Link picture to its sound (`post_clips_link`) and switch off thin generated audio. A music sting on the end card helps memory.

## The Ship Gate for Short Ads

The seven criteria hold, read for the format:

1. The story reads **with the sound off** (captions and text carry it) and with it on.
2. Pacing: fast open, at least one held beat, no slideshow rhythm.
3. No reused footage and no same-take slices posing as separate shots.
4. No time-stretches; every source shortfall resolved.
5. Every cut hits a named beat.
6. The tail is the end card, held to be read.
7. For 15–30 s ads the end card (brand, offer, call to action) replaces the credits card; no credits card is required. Longer branded pieces and anything citing sources keep the credits rule.

Plus, before handoff: the first frame stops the scroll; no `letterboxed_source`, `no_on_screen_text` or `double_audio_risk` findings remain; loudness is on target; captions are inside the safe zones on the rendered frames.

Save the cut with `provenance.deliverable` naming the platform, shape and length (for example "Instagram Reel 9:16, ≤30 s") so the checks use the social targets, and `provenance.intent` stating its spine.

## Failure Modes

- **Highlights reel**: the original's shots, shorter, in the original order. Write the recut's own spine and cut from it.
- **Letterboxed widescreen**: 16:9 shots with bars in a 9:16 frame. Cover and reposition, or regenerate vertical.
- **Silent and uncaptioned**: the story lives in dialogue the viewer never hears. Caption it; put the message on screen.
- **Slow open**: a logo, a fade or a wide where nothing happens. Open on the hook.
- **Buried call to action**: the offer appears for half a second at the end. Hold the end card; show the brand earlier.
- **One take, three "shots"**: back-to-back slices of the same take. Merge or cut away.
