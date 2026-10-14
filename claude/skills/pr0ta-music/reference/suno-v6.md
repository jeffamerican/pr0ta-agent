# Suno v6 on PR0TA

Read this before writing any request for a Suno route (`muapi/suno-v6`, `muapi/suno-v6-wild`,
`muapi/suno-v6-mini`). Facts marked **(probed)** were measured on PR0TA's own Suno route; the
rest is Suno's documentation or widely reproduced community practice. Suno publishes no tag
specification: tags and descriptors are strong hints, not commands, so every cue is judged by
measuring its takes, never by its prompt.

For what the music should do (spotting, cue types, hit points, themes, palettes), read
`scoring-to-picture.md` first. This file is how to say it to Suno.

## The three routes

| Route | Use it for | Notes |
|---|---|---|
| `muapi/suno-v6` | Every keeper: score, songs, final cues | The most literal reading of the style text. |
| `muapi/suno-v6-wild` | Exploring when v6 comes back flat, genre blends, alternate ideas | Strays further from the prompt. Take the idea it finds back to v6 (rewrite the style text from what you heard, or Cover the take on v6). |
| `muapi/suno-v6-mini` | Cheap sketches, lyric and structure tests | **(probed)** Leaked a wordless choir into an instrumental and cut its ending off where v6 rang out cleanly. Never deliver a Mini take without checking it. |

All three cost the same per request and always return **two takes**; both are saved. Never
pick between models by price.

## What a request carries

`generation_submit` with `generator: "music"`, `mode: "txt_to_music"`, the Suno model, and:

| Field | Where | What it is |
|---|---|---|
| `prompt` | top level | Suno's **style text**, up to 1,000 characters (longer is cut at a word boundary). |
| `duration` | top level | Seconds, 30 to 360 honored; shorter requests are generated at 30 s and trimmed. |
| `lyrics` | `parameters` | The lyrics field: words with `[Section]` tags for a song, or tags alone for an instrumental. Up to 5,000 characters. |
| `instrumental` | `parameters` | `false` for a sung cue. Without lyrics and without `instrumental: false`, the cue is instrumental. |
| `title` | `parameters` | Up to 80 characters. |
| `negative_tags` | `parameters` | Things to keep out (Suno's Exclude field). |
| `vocal_gender` | `parameters` | `male` or `female`; a nudge for sung cues. |
| `style_weight`, `weirdness_constraint` | `parameters` | 0 to 1. See "Sliders". |
| `audio_weight` | `parameters` | 0 to 1: how much the source music or the singing voice weighs (Cover, Extend, voices). |
| `singing_voice_id` | `parameters` | A ready project singing voice (`music_singing_voices_list`). |
| `operation` | `parameters` | `create` (the usual), `cover`, `extend` or `sound`. See "Operations". |
| `audio_asset_id` | top level | The source music for `cover` and `extend`. |
| `video_asset_id` | top level | A clip to score from (create only). |
| `output_format` | top level | `wav` for WAV takes (adds $0.01 a take); otherwise 48 kHz MP3. |

A request with `instrumental: false` and no lyrics lets Suno write the words; it then ignores
the duration and picks its own length, so write the lyrics yourself whenever length or words
matter.

REST: `POST /api/v2/projects/{project_id}/generate` with the same `request` body.

## Writing the style text

The style text sets the whole track's identity. Order matters: the first words weigh most.

1. **Genre and era first**, specific beats general: "1970s Italian crime-film funk" beats
   "funk"; "minimal ambient film underscore" beats "cinematic".
2. **Mood and energy**: Suno defaults to upbeat and bright when no mood is given.
3. **Tempo as a BPM number** ("72 BPM") plus feel ("half-time", "rubato", "driving 8ths").
   **(probed)** Asked tempos landed within 2 BPM.
4. **Two to four named instruments or textures**: "felt piano, upright bass, brushed snare,
   tape-warm Rhodes". Concrete nouns survive best; generic adjectives drift most.
5. **Vocal identity** for a song: gender plus one or two qualities ("breathy female alto,
   close-miked"). Leave it out of an instrumental entirely.
6. **Production feel tied to genre and era**: "lo-fi", "vinyl crackle", "80s gated reverb
   drums", "dry and intimate". Abstract engineering words ("wide stereo", "sidechain",
   "high quality", "radio-ready", "reverb 30%") do nothing reliable.
7. **The arc and the ending**: "sparse verses, full band from the first chorus, piano-only
   bridge, ends on one held chord then silence".

Length: for a sketch, 4 to 7 comma-separated descriptors. For a keeper, write instructions,
not adjectives: say what each instrument and the singer do in each section. Without them v6
tends to thin the band when a vocal enters. Avoid stacking contradictions ("dark, joyful,
aggressive, gentle"); keep genre blends to two or three, dominant first.

Never name an artist, band, composer, producer, film, song or album: Suno rewrites or blocks
names, and a soundalike is a rights risk. Describe the sound instead: genre and era, the
signature instruments, the vocal character, the production, the tempo and groove.

Do not write "no X" in the style text: a negated word puts the thing in play ("no humming"
produced more humming). Say what is there ("solo nylon guitar only") and put exclusions in
`negative_tags`.

Key ("in D minor") is guidance at best; treat the key as unverified until you hear it.

Examples:

- Sketch: `90s trip-hop, melancholic, 84 BPM half-time, dusty breakbeat, upright bass, Rhodes, vinyl crackle, breathy female vocal, sparse verses, fuller chorus`
- Keeper: `Slow country ballad, 72 BPM. Female lead sings close and soft in the verses and opens up on the last word of each chorus line. Brushed snare in the verses, full kit from the first chorus. Upright bass walks into each chorus. Pedal steel answers the vocal between lines. Bridge is piano and voice only. Final chorus a cappella, then one sustained steel chord and silence.`

## Exclusions

`negative_tags` takes 3 to 8 comma-separated category nouns: `vocals, humming, choir, drums,
trap hi-hats, risers`. Mirror each with a positive instruction in the style text ("strings and
piano only"). Exclusion is a nudge: it cannot beat a style text or a tag that implies the
excluded thing ("anthem", "gospel", "chant" and `[Choir]` invite group vocals). **(probed)** A
dialogue bed with `piano` excluded still brought piano in both takes when the style text said
"intimate and uneasy"; the palette word that pulls the model must go, not just be excluded.

## The lyrics field

Section tags go in square brackets, one per line, before their section. They are
case-insensitive. A malformed tag (missing bracket, prose inside it) gets sung.

```
[Intro - solo piano, 4 bars]

[Verse 1 - close, soft]
Streetlights hum a tune I used to know
Every window holds a different glow

[Chorus - full band, belted]
Carry me home (carry me home)
Over the wire, over the stone

[Instrumental Break - guitar solo]

[Bridge - piano and voice only, whispered]
If the night forgets my name

[Final Chorus - bigger harmonies]
Carry me home (carry me home)
Over the wire, over the stone

[Outro - band drops out, last line held, then stop]
Home
[End]
```

- **Structure tags**, most to least reliable: `[Verse]`, `[Chorus]`, `[Intro]`, `[Outro]`,
  `[Pre-Chorus]`, `[Bridge]`; then `[Post-Chorus]`, `[Hook]`, `[Final Chorus]`; then
  `[Instrumental Break]`, `[Interlude]`, `[Solo]`, `[Guitar Solo]`, `[Breakdown]`, `[Build]`,
  `[Drop]` (Build and Drop work best in electronic genres). `[Silence]`, `[Stop]`,
  `[Key Change]`, `[Tempo: slow]` are unreliable.
- **Number repeated sections** (`[Verse 1]`, `[Verse 2]`) when they should differ, and
  **write every chorus out in full**; "repeat chorus" or "(x2)" is unreliable.
- **Direction inside a tag**: one or two audible changes after a dash or colon
  (`[Chorus - wider, full release]`). Say the same instruction in the style text too; the
  two agreeing is what makes it stick.
- **Vocal delivery**: `[Whispered]`, `[Spoken Word]`, `[Rap]`, `[Belted]` are reliable;
  `[Falsetto]` about half the time (add "falsetto" to the style text). `[Male Vocal]` and
  `[Female Vocal]` work when the style text names the gender too. `[Harmonies]`, `[Choir]`,
  `[Call and Response]`, `[Duet]` are usable; label duet lines `[Male]`, `[Female]`, `[Both]`.
- **Parentheses** after a line are backing vocals or echoes, "(carry me home)". Never put
  directions in parentheses; they get sung.
- **Lines**: 6 to 10 syllables, steady within a section. Crowded lines get rushed or spoken.
  Make the chorus look different on the page (shorter lines). Stretch a held vowel in the
  spelling ("go-o-one").
- **Instrumental section inside a song**: `[Instrumental Break]` or `[Interlude - piano and
  strings]` with no lyric lines under it. `[Instrumental Bridge]` holds better than a bare
  `[Bridge]`, which may get sung or collapse into a verse.
- **Endings**: `[End]` is a soft hint. Describe the ending in the outro tag and the style text
  ("band drops out, last line held, then stop"; "one sustained chord, then silence"). A bare
  `[Outro]` invites vamping; give it a length ("2-bar outro").
- **Pronunciation**: write numbers and dates as spoken ("twenty twenty-six"), acronyms
  spelled out ("A-I", "N-Y-C"), hard names by sound ("Shiv-awn"). Respell only the word that
  fails, and keep one spelling for the whole song. Swap homographs (live, read, lead).
- **Language**: write the lyrics in the target language and script, name it in the style
  text ("Spanish-language vocals"), keep one language per section. Write the style text itself
  in English.

## Instrumentals

The reliable stack: no sung lines, an instrumental flag (the default), no vocal-implying words
in the style text, and `negative_tags: "vocals, humming, choir, backing vocals, chant"`.

Section tags still shape an instrumental: PR0TA sends the tags in `lyrics` and keeps the track
instrumental. **(probed)** The same trailer style with tags kept its asked-for piano-and-drone
opening and ended in silence; without them one take dropped the opening and drifted into four-
on-the-floor in another key. Give every instrumental cue its arc in tags:

```
[Intro: lone piano motif over low drone]
[Build: spiccato strings ostinato, percussion grows, riser]
[Climax: full orchestra, taiko, relentless]
[Final Hit: massive impact, then silence]
[End]
```

For a solo-instrument piece, tag every section with the instrument, state it positively
("solo fingerstyle guitar only"), exclude drums, bass, pads and vocals, and end on "single
ringing chord, then silence".

## Length, tempo and timing

- **(probed)** Requests of 30 s and more came back within about a second of the duration
  (30, 60, 90 and 120 s; a sung 120 s song too). A 15 s request came back at 9 and 15 s in
  different styles: for anything under 30 s, use `operation: "sound"` or generate 30 s with the
  ending where you want it and trim.
- **(probed)** Tempo held within 2 BPM of the number in the style text; Cover keeps the
  source's tempo whatever the style text says.
- Every take is trimmed to the requested duration when it runs over (the asset metadata
  records the trim); end the arc where you want the cut, or the trim lands mid-phrase.
- Quality falls off in the back half of long generations. Keep a single generation under about
  three minutes; build longer cues with Extend or overlapping sections crossfaded on the
  timeline.
- To land a climax on a picture hit, choose the tempo so the hit falls on a bar line (one 4/4
  bar is 240 / BPM seconds; `scoring-to-picture.md` → "Hit points"), put the climax tag at that
  bar, generate, then measure where each take's peak landed and trim the head so it lines up.

## Sliders

`style_weight` (Suno's Style Influence) is how closely the take follows the style text;
`weirdness_constraint` (Weirdness) is how far it may wander; `audio_weight` (Audio Influence)
is how much the source music or singing voice weighs. Starting points, then change one thing at
a time:

| Goal | `style_weight` | `weirdness_constraint` | `audio_weight` |
|---|---|---|---|
| Score and beds that must follow the brief | 0.75-0.85 | 0.2-0.35 | - |
| Strict genre adherence | 0.85-0.9 | 0.25-0.4 | - |
| A song with a stable hook and some life | 0.65-0.8 | 0.35-0.5 | - |
| An adventurous alternate take | 0.5-0.65 | 0.55-0.7 | - |
| Cover that restates a theme closely | 0.6-0.75 | 0.2-0.35 | 0.75-0.9 |
| Cover that only borrows the theme's feel | 0.6-0.75 | 0.4-0.55 | 0.3-0.5 |
| A singing voice that must sound like its owner | 0.65-0.8 | 0.25-0.4 | 0.7-0.85 |

High weirdness with a high style weight on an overloaded brief gives confused arrangements. The
sliders cannot fix an arrangement; the style text and tags do. Suno's app also has a Variety
setting that rewrites the style text; PR0TA's route does not expose it, so concrete genre and
instrument nouns are your protection against drift.

## Operations

### Cover: derive a cue from a theme

`operation: "cover"` with `audio_asset_id` restyles the source music: new instrumentation,
mood and production, same melody. **(probed)** Four orchestral covers of a simple solo-piano
theme all kept the melody, the harmony and the tempo (at `audio_weight` 0.5 and 0.9); covers of
a busy trailer cue with no clear melody kept nothing of it. So write theme cues to carry a
clear, singable melody, and derive later cues from the theme cue, not from busy ones.

The leitmotif workflow:

1. Write the theme as its own short cue (30 s): one instrument, a simple four-bar melody stated
   twice, plain harmony, the key and tempo the score bible names.
2. When the person approves it, record it in the score bible (`score_bible_save`, theme with
   `asset_id` and `status: "approved"`).
3. For each later appearance, Cover the theme cue with the scene's style text, its tags and a
   duration. Measure the result, and listen for the melody before calling it the theme.

Cover takes `lyrics` too: a sung cover of an instrumental theme puts words on its melody.

### Extend: continue a cue

`operation: "extend"` with `audio_asset_id` and `parameters.continue_at` (seconds into the
source) continues the music from that point with a new style text and tags. **(probed)** The
take holds the source up to `continue_at` followed by the continuation (a 60 s source extended
from 45 s came back 107 and 126 s long), and `duration` is ignored. Use it to lengthen a cue
that ends too soon, to add a coda, or to turn a cue in a new direction at a picture change.
Start the extension's tags with the section it begins ("[Coda: solo piano restates the
motif]"). Sources over two minutes may be refused; trim the source first (`assets_trim`).
Place the take on the timeline from `continue_at` on, or use it whole in place of the source.

### Sound: stings, logo buttons, loops and one-shots

`operation: "sound"` makes two short takes from up to 500 characters of prompt, priced at
$0.02 (any Suno model may be named; Sound runs on Suno's sound model). Optional
`parameters.sound_loop` (true for a loop), `sound_tempo` (BPM) and `sound_key` (`C`, `F#`,
`Am`, `Any`). **(probed)** A logo sting came back 3 and 5 s; a horror loop 15 and 18 s. Check a
loop's seam before relying on it (the end must flow into the start); one loop take faded out
instead of looping.

### Scoring from a video

On create, `video_asset_id` (a clip up to about four minutes) lets Suno read the picture's mood
and pacing. Lyrics cannot be written in this mode and the duration is Suno's: **(probed)** one
take matched the 25 s clip, the other ran 113 s. It is a mood reference, not sync: plan hits
yourself and trim.

### WAV delivery

`output_format: "wav"` converts both takes to WAV after they are made ($0.01 a take). If the
conversion fails, the MP3 takes are saved instead and the asset metadata says so.

### Not available on PR0TA's Suno route

Replace Section, plain-language section edits, Remaster and Max Mode are app-only. Edit a take
on the timeline instead (trim, crossfade, split), or regenerate the section and crossfade it in.
Separate stems with `audio_stem_separate` (Demucs); word timing of a sung take with
transcription (`pr0ta-audio`).

## Singing voices

A singing voice is a person's own voice, cloned for Suno songs. Only the person can make one:
in the Music editor they upload or record about ten seconds of clean voice, then read aloud a
phrase Suno picks, within minutes (the phrase proves the voice is theirs; an unfinished clone
expires and must be started again). Agents never make, approve or change a voice.

`music_singing_voices_list` lists the project's voices; a `ready` voice sings a cue with
`parameters.singing_voice_id` plus lyrics. Raise `audio_weight` (0.7 to 0.85) when the take
does not sound like its owner. A voice belongs to the project it was made in and to the
person who made it; never use one for anyone else's part.

REST: `GET /api/v2/projects/{project_id}/music/singing-voices` lists them. Making a voice
(`POST /api/v2/projects/{project_id}/music/singing-voices`, then `/confirm`) needs a person
signed in to the app; tokens get `403 singing_voice_requires_user_session`.

## Judging the takes

Never call a cue right on its prompt. For each take:

1. `music_analyze(asset_id)`: tempo against the asked BPM, where the downbeats fall, whether
   the grid is reliable.
2. `audio_meter` with the take's `asset_id` and short windows (two seconds each across the
   take): where the loudest moment (the climax) lands, and whether a bed stays level.
3. Listen for what the prompt cannot guarantee: stray vocals or humming in an instrumental, a
   melody under dialogue, the ending type, the theme's melody in a cover, the words of a song.
4. Pick the take whose hits land and whose ending is right; say why in one line.
5. Fix with the cheapest edit: trim the head to land a hit, trim the tail at a phrase end and
   fade, strip a stem (`audio_stem_separate`, then mute the melodic `other` or the `vocals`
   stem). Regenerate only when the arrangement itself is wrong, changing one thing.

## When it goes wrong

| Symptom | First fix | Then |
|---|---|---|
| Genre drift | Primary genre first; cut to genre, groove, 2-3 instruments, vocal | Raise `style_weight`; use v6, not Wild |
| Unwanted instrument | Remove the palette word that implies it; add it to `negative_tags` | Strip its stem |
| Vocals or humming in an instrumental | No sung lines, no vocal-implying words, exclude vocals and humming | Strip the vocal stem; regenerate on v6 if Mini |
| A melody under dialogue | Pads and drones only; no piano or solo instrument in the palette | Strip the `other` stem; regenerate |
| Band disappears under the vocal | State per section that the riff continues under the verse | Same instruction in the style text and the tag |
| Singer speaks or raps instead of singing | Fewer syllables, stretched vowels, shorter chorus lines | Change the genre word that carries the melody |
| Repeated or missing verses | Write every section out; shorten the lyrics | Rewrite the crowded section |
| Endless outro | Bar-counted outro plus "then stop" | Trim at a phrase end and fade |
| Cut-off last line | Shorter lyrics; a short final landing line | Extend from before the cut with an outro |
| Long intro | "Cold open, vocal on beat one" or "4-bar intro" | Trim the head |
| Tag text gets sung | Fix the brackets; shorten the tag; move prose to the style text | |
| Prompt refused | An artist, song or brand name, or flagged lyrics | Describe the sound; rewrite the line |

## Worked requests

Dialogue underscore, 90 s (score the subtext; nothing moves under the words):

```json
{"generator": "music", "mode": "txt_to_music", "model": "<Suno model from models_preferred>", "duration": 90,
 "prompt": "ambient drone bed for dialogue, warm low string pad and soft analog synth drone only, one sustained chord at a time changing every eight bars, D dorian, 60 BPM, the same quiet level throughout, nothing rises, intimate and uneasy",
 "parameters": {"lyrics": "[Intro: drone already sounding]\n[Bed: sustained pad, slow chord change]\n[Bed: same level, new chord]\n[Outro: thins to one low note]\n[End]",
  "negative_tags": "vocals, humming, choir, piano, guitar, drums, percussion, risers, impacts",
  "style_weight": 0.85, "weirdness_constraint": 0.2}}
```

Trailer build, 60 s with a final hit at 0:54 (100 BPM, bar 23):

```json
{"generator": "music", "mode": "txt_to_music", "model": "<Suno model>", "duration": 60,
 "prompt": "hybrid orchestral trailer, sparse piano and low drone opening, ticking pulse, rising spiccato strings, taiko and hybrid percussion, low brass braams, D minor, 100 BPM, three-act escalation, abrupt hard stop on a final hit",
 "parameters": {"lyrics": "[Act 1 Intro: lone piano motif over low drone]\n[Act 2 Build: spiccato strings ostinato, percussion grows, riser]\n[Act 3 Climax: full orchestra, taiko, relentless]\n[Final Hit: massive impact, then silence]\n[End]",
  "negative_tags": "vocals, choir, EDM drop, rock guitar, fade out", "style_weight": 0.8, "weirdness_constraint": 0.25}}
```

Theme restated heroically (Cover of the approved theme cue):

```json
{"generator": "music", "mode": "txt_to_music", "model": "<Suno model>", "duration": 30, "audio_asset_id": "<theme cue>",
 "prompt": "heroic orchestral restatement of the theme, french horns carry the melody, full strings, timpani, A minor, 80 BPM, triumphant, ends on a held tonic chord",
 "parameters": {"operation": "cover", "lyrics": "[Theme: horns state the melody over strings]\n[Theme: full orchestra, melody again]\n[Ending: held tonic chord]\n[End]",
  "negative_tags": "vocals, choir, synth", "style_weight": 0.8, "weirdness_constraint": 0.2, "audio_weight": 0.75}}
```

Logo button for a spot:

```json
{"generator": "music", "mode": "txt_to_music", "model": "<Suno model>",
 "prompt": "bright corporate logo sting, piano chord and bell hit with a shimmering tail, confident resolve",
 "parameters": {"operation": "sound", "sound_tempo": 120, "sound_key": "C"}}
```

End-credits song, 2 minutes, in the theme's key:

```json
{"generator": "music", "mode": "txt_to_music", "model": "<Suno model>", "duration": 120,
 "prompt": "cinematic indie folk ballad, warm intimate female vocal, fingerpicked acoustic guitar, piano, swelling strings in the final chorus, 76 BPM, E major, bittersweet and hopeful. Verses sparse and close; chorus opens up with full strings. Ends on a held piano chord, then silence.",
 "parameters": {"instrumental": false, "vocal_gender": "female", "title": "Till the Long Night Ends",
  "lyrics": "[Intro - solo piano, 4 bars]\n\n[Verse 1 - close, soft]\nThe porch light flickers on the old road home\nYour coat still hanging where you left it on its own\n\n[Chorus - full band, strings swell]\nAnd I will wait for you\nWhere the river bends\nI will wait for you\nTill the long night ends\n\n[Outro - piano alone, last line held, then stop]\nTill the long night ends\n[End]",
  "negative_tags": "male vocals, autotune, trap hi-hats, EDM drop, rap", "style_weight": 0.75, "weirdness_constraint": 0.3}}
```

**(probed)** This song came back word for word, 120 s long, with a clean ending.

## Rights

Suno's output on PR0TA is cleared for commercial use under the model's license record
(`models_get_defaults` shows it); it is not exclusive, and soundalike prompts are the main
risk, which is why names never go in a prompt. Do not start legal or clearance checks on your
own; the project's legal settings decide how much scrutiny a piece gets.
