# Scoring to Picture

How a film composer decides what the music does, before any model is prompted. This holds for
every music route; how to say it to a particular model is in that model's guide (Suno:
`suno-v6.md`; ElevenLabs Music: `eleven-music.md`).

## Spot before you generate

A spotting pass decides where music plays, where it stops, and what each cue is for. Silence is
a choice: music everywhere becomes wallpaper and spends its power.

For each scene ask:

1. **Does this moment need music at all?** Strong dialogue, a natural soundscape or a silence
   that lands may serve better.
2. **What is the cue for?** Its function decides its shape (see "Cue types").
3. **What is under the action?** Score the subtext (what a character feels or hides), not what
   they do on screen. A man calmly packing a bag after a death is grief, not packing.
4. **Where does it start and stop?** Start on a cut, a look, a line's end or a beat of silence;
   never in the middle of a sentence. Stop on a cut, a hit, or under a sound that covers the
   exit.
5. **What must it hit?** A reveal, a door slam, a title, a cut to black: list the hit points
   with their times.
6. **How does it end?** Button, ring-out or fade (see "Endings").

Take timing from the locked cut when there is one (picture-first); otherwise from the cue
sheet's plan (`pr0ta-sync`).

## The cue sheet

Name cues by reel and order: `1M1` is reel 1, music cue 1. A short film or a spot with no
reels uses `1M1, 1M2…` throughout. Each cue records:

| Field | Example |
|---|---|
| Cue | 1M3 "Kitchen Confession" |
| In / out | 00:04:12:08 to 00:05:41:20 (and duration) |
| Starts on / stops on | "Mara sits down" / "cut to the hallway" |
| Function and type | Underscore bed under dialogue |
| Subtext | Guilt she will not name |
| Hit points | 00:05:02:10 she drops the cup |
| Ending | Ring-out under the cut |
| Theme | Mara's theme, fragment only |
| Usage | BI (background instrumental) |
| Source | Model, prompt and asset id of the circled take |

Usage codes, as they go on a performing-rights cue sheet: **BI** background instrumental,
**BV** background vocal, **VI** visual instrumental (performed on screen), **VV** visual vocal,
**MT** main title, **ET** end title, **Logo**.

## Cue types

| Type | What it is | Shape |
|---|---|---|
| Underscore | Score beneath a scene, often under dialogue | Sparse, steady, no lead melody under words |
| Bed | Sustained background under narration or voice-over | Level, loop-friendly, no surprises |
| Feature cue | Music that leads: montage, chase, reveal, title | Full arc, melody, hits |
| Source (diegetic) | Music the characters hear: radio, band, party | Played as a recording, period-true; it ignores the cut |
| Sting | A 1-5 s accent on a hit or reveal | One gesture, sharp attack |
| Bumper | A 3-10 s link between segments | Quick statement and button |
| Main title / end title | Credits music | A full piece; end titles often a song |
| Logo | A brand button at the end of a spot | 2-5 s, resolves |

## Under dialogue

The speaker is the soloist; the score accompanies.

- Speech intelligibility lives roughly between 1 and 4 kHz. Keep busy material out of that
  band: no lead melody, no bright solo instruments (violin, oboe, flute, lead guitar) while
  someone speaks. Write around the voice: a low pad or drone below it, a high shimmer above it,
  nothing moving in the middle.
- Match the voice: under a deep voice go light on cellos and low winds; under a high voice,
  avoid bright violins.
- Keep the level flat and the harmony slow. No builds, no accents landing on words, no
  crescendo into a line. Make musical moves in the gaps between lines.
- Rhythm, if any, is slower than the speech.
- Ducking (`pr0ta-timeline` → "Audio Mix") is the safety net, not the plan; a cue that only
  works ducked was the wrong cue.

## Hit points and tempo

To land a musical moment on a picture hit, choose the tempo so the hit falls on a bar line:

- One beat is 60 / BPM seconds; one 4/4 bar is 240 / BPM seconds.
- At 100 BPM a bar is 2.4 s, so a hit at 0:38.4 is the start of bar 17.
- Tempos that divide evenly into the frame rate keep beats on whole frames: at 24 fps, 60, 72,
  80, 90, 96, 120 and 144 BPM give 24, 20, 18, 16, 15, 12 and 10 frames a beat.

Plan the climax tag at the hit's bar, generate, then measure: `music_analyze` gives the real
tempo and downbeats; metering short windows of the take (`audio_meter`) shows where the peak
landed. Trim the head so the peak sits on the hit, or pick the take that lands closest.
Generated music drifts; two or three planned turns per cue survive better than ten.

Mickey-Mousing (music that mirrors every motion) suits comedy, animation and stylized moments;
elsewhere it reads as cheap. Counterpoint (music that ignores or opposes the image: cheerful
source music over violence) is a deliberate effect for irony or horror.

## Endings

- **Button:** a hard final chord or hit on a downbeat, then silence. Spots, stings, bumpers,
  comedy.
- **Ring-out:** the last chord decays naturally under the cut. Most score.
- **Fade:** only for source music, montages and end credits. Never to hide a cue that has no
  ending; fade after the last musical event, never through it.
- A cue that must continue past a cut either crosses it on a held note or hands off to the next
  cue in the same key.

For a spot, make each length its own edit (60, 30, 15, 6 s) with its own hook and an earlier
resolution, not a shortened 60.

## Beds and loops

A loop starts and ends on the same harmony and pulse, with no intro and no ending. Trim the
intro and the tail off a longer cue at matching points, crossfade the seam by about half a
second, and listen to the seam twice before using it. Build a long bed from one loop and vary
it with the mix (layers in and out), not with new generations.

## Themes and the score bible

A score holds together through a few recurring ideas, not through every cue sounding alike.

- Keep a **score bible** for the project (`score_bible_get` / `score_bible_save`): the concept,
  the style core every prompt starts from, the exclude core, the palette, key centers, the
  tempo family, how music sits under dialogue, and the themes with the cue that states each.
- A **theme** belongs to a character, place or idea. Write it first, as a short cue with a
  clear, simple melody. Once the person approves it, record it in the bible with its asset id.
- Later cues **vary** the theme: a fragment under a scene, the full statement at a turning
  point, a new orchestration for a new mood (sad, triumphant, menacing). Derive them from the
  theme cue where the model can (Suno: Cover keeps the melody), and listen for the melody before
  calling it the theme.
- Keep key relationships simple: the theme's key or a near one (relative minor, a fifth away).
- Update the bible when a decision changes, and record a decided theme or rule in project
  memory too (`memory_record_decision`).

## From emotion to music

Starting points, not rules. Combine with the score bible's palette.

| Scene | Tempo | Harmony | Palette | Texture and arc |
|---|---|---|---|---|
| Tension, thriller | 60-90, or a 120-140 pulse with slow harmony | Minor, Phrygian, pedal tones, minor seconds | Low string ostinato, pulsing synth bass, ticking percussion, muted brass swells | Restrained, slowly tightening, no release |
| Grief | 50-70 | Aeolian, suspended chords, slow changes | Solo cello or felt piano, soft string pad | Intimate, fragile, space, unresolved |
| Romance | 66-90 | Major with a borrowed minor iv, warm 7ths and 9ths | Piano, warm strings, acoustic guitar, solo clarinet | Tender, gently swelling, understated |
| Comedy | 100-140 | Major, chromatic passing notes | Pizzicato strings, bassoon, clarinet, glockenspiel | Bouncy, staccato, light; Mickey-Mousing allowed |
| Action | 130-170 | Minor, driving ostinati | Taiko and hybrid percussion, low brass, spiccato strings, synth bass | Relentless, escalating, hard stops |
| Wonder, awe | 70-100 | Lydian, open fifths, bright major | Celesta, harp, high strings, wordless choir, shimmering pads | Luminous, rising, airy |
| Horror | Free or under 60 | Atonal, clusters, tritones | Bowed metal, col legno strings, prepared piano, sub drone, breath textures | Unsettling, sparse, sudden silences |
| Uplifting spot | 100-124 | Major, I-V-vi-IV | Piano eighths, plucks, claps, light kit, warm pad | Optimistic, building, clean button |
| Period piece | Of the era | Of the era | The era's instruments, named | A believable ensemble in a believable room |
| Trailer | 90-130 | Minor turning major at the climax | Hybrid orchestra, risers, braams, impacts, choir | Three acts, gaps for the editor, escalate then stop |

Modes as colors: **Lydian** (raised fourth) floats and wonders; **Dorian** (minor with a raised
sixth) is hopeful minor; **Phrygian** (flat second) is menace; **Aeolian** is melancholy;
**Mixolydian** is rootsy swagger; whole-tone and clusters are instability.

## Temp tracks and references

A temp track (or a reference the person names) describes a tone, not a melody to copy. Turn it
into words: tempo, instruments, texture, harmony, energy, production. Never put a real artist,
composer, film or song name in a prompt, and never aim to reproduce a recognizable piece.

## Before you generate a cue

1. Function and type.
2. The emotion under the action.
3. Is anyone speaking? Then the dialogue rules.
4. In, out and duration; hit points and their bars at the chosen tempo.
5. The ending.
6. A theme statement, a variation of a theme, or neither.
7. The style core and exclude core from the score bible, plus this cue's specifics.
8. Then write the model's request from its guide, generate, and measure the takes.
