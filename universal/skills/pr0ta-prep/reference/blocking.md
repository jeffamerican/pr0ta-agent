# Blocking a sequence chunk

Block each sequence chunk before it renders, on the Blocking page's plan:
`blocking_get(scene_number)` reads the scene's approved set, its cast as
figures (body, height, approved rig) and its chunks (the queue's chunking,
with shot numbers and seconds); `blocking_save` keeps the cast and each
chunk's figures (start place, then keys, a walk/run path or a motion clip over
the chunk's seconds; grips for held props), the props its action needs and
staging notes; `blocking_animatic_render(scene_number, chunk_id)` renders the
chunk's animatic on the approved set: one low-sample grey clay video (no
textures or colours, so the video model takes camera and staging, not the
set's look) cut between the
shot list's setups on its durations, each pushing in, pulling out or
following as its shot's `movement` says. Put each beat where its shot is on
screen, then read the cut check (`scene_inventory.cut`, `coverage`) and fix
the blocking for cuts that will not play. An animatic is a render, never a
set build: its figures and props exist only in it. Its outputs are stored
under `blocking/scene-NNN/chunk-K/` and filed in the asset library under
Blocking/Scene N/Chunk K, named for their scene, chunk (and shot) and time.

Turn the chunk's words into blocking without guessing where it matters and
without inventing what nobody wrote. Read the screenplay's action for the
chunk, its shot list (size, angle, subject, movement, duration) and the cast:
- **Take** what they state: who is in each shot, where they are, which way
  they face and look, the props named, each shot's framing, move and length.
- **Infer, and say so** in the staging notes: heights and bodies from the
  cast, everyone standing at the start, people in an exchange facing each
  other, the camera on one side of the line, lens from shot size.
- **Leave out** what nothing states: no invented walks, gestures, business or
  camera moves. A figure the words keep still stays still.
- **Ask the person** only when a frame cannot be judged without it (two
  people with no stated placement, a shot with no framing): one review card,
  at most five questions, each with your proposed answer as the default.
Coordinates you place are a first guess: render, read `scene_inventory`
(figures' grounding and contact, each shot's framing receipt) and the stills,
and correct people that overlap, float or stand inside the set before calling
the chunk blocked.

A shot can follow an operator's recorded move instead of its composed setup:
the person records it on a phone from the Blocking page (the capture stands
where the animatic's camera opens, on the set, with the blocked figures
playing) and picks the take; the next animatic follows it. The person approves
the animatic; never approve it yourself. Once approved, the queue sends it with
the chunk whose shots it cuts exactly, as its first reference video (ledger
kind `blocking`), with the instruction that its grey figures are placeholders:
Seedance takes camera, moves, cuts and timing from it, not the mannequins'
look or motion.

## Props that move, and riding

Props in a chunk's `objects` can move over the chunk's seconds:
- **`keys`**: where the prop is at given times (eased between them).
- **`fall`**: it tips over in place, pivoting on its base edge toward a direction, and ends on its
  side (a knocked bottle, a toppled bike). It does not drop: something let go in mid-air needs a key
  on the floor.
- **`ride`**: it travels with a figure, on the body (a skateboard under a skater, a bicycle under a
  rider) or in a hand (`hand_l`, `hand_r`: a bag, a phone, a gun). Set `until` to let go: the prop
  stays where it was, then its keys or fall move it. A bail: the board rides until the let-go, then
  keys roll it on and a fall tips the bike. A drop or a throw: keys carry it to where it lands.
- A prop a hand grips (`left_hand_grip`/`right_hand_grip`) moves with the hand, so give it no ride,
  keys or fall. Keys, falls and let-gos must fall inside the render.
- A rider stays on the board or bike when its path ends. A figure has a path or keys, not both, so
  stepping off is the next chunk's blocking.

Built-in kits need no model: `primitive: "skateboard"` and `primitive: "bicycle"`. A kit riding under
its rider is sized to the rider (a bike for a 1.5 m rider is smaller), so leave its scale alone. A project 3D model
(`asset_id`, e.g. an approved prop from Prep) works too; it is scaled to the prop's dimensions.

A figure rides on its path: `gait: "skate"` stands sideways on the deck (`stance` regular leads with the
left foot, goofy the right; `push_until` keeps the back foot pushing until then), and `gait: "bike"`
sits on the saddle pedalling at the speed's cadence. Give the skater a skateboard and the rider a
bicycle that `ride` them; the kit sits where its rider needs it. For a chase, put the riders on paths
with their gaps in time (`start_time`) and speeds, and follow them with `follow` setups.

## Everyday performance: walking, running, sitting, idling, talking

- **Walk and run** on a path (`gait: "walk"` 1.4 m/s, `"run"` 3.6 m/s, or set `speed`); the figure
  settles into `end_pose` when the path ends. Stagger entrances with `start_time`.
- **Idle** is automatic in a video: a figure holding a pose or between keys breathes, shifts its weight
  and lets its gaze drift, out of step with everyone else. Set `idle: "still"` only for a freeze (a
  held breath, a body, a statue).
- **Talk and listen**: add `talk` spans to the figure, timed from the dialogue in the shot list
  (about 2.5 words a second, a beat of 0.3 s between lines):
  `{"start": 1.2, "end": 3.8, "kind": "talk", "energy": "normal"}`. Talking nods the head on the
  stresses, turns into the line and gestures with the right hand (both for `energy: "animated"`, the
  free one when a hand holds something; `hands` overrides). Give the person spoken to a `listen` span
  over the same seconds: slow nods, head tipped. Pair it with `look_at` on each other; nods ride on
  the gaze. Walk-and-talk works on a path (the head talks, the arms keep the stride). Spans must not
  overlap, and a motion clip carries its own performance.
- **Sit down / stand up**: a `sit` key's location is where the hips land on the seat (the feet rest
  about 0.3 m in front). Key `stand` 0.3 m further forward, facing away from the seat, then `sit` at
  the seat 1.0 to 1.4 s later, so the feet stay put (reverse it to stand up). The body hinges forward
  over the feet on the way. The seat's front edge belongs under the knees.
- Seated figures talk with their hands too; lying figures only breathe.


## The motion check: block, check, fix, render

`blocking_check(scene_number, chunk_id)` renders nothing and answers in well under a second for most chunks. It solves every figure
frame by frame (after the chunk's actions expand) against the approved set build's objects and the other
figures, and returns issues grouped by check and figure:

| Check | Means | Typical fix (the hint says it in metres or seconds) |
|---|---|---|
| `set_penetration` | a body part inside a set object or prop (not the seat it sits on, legs under a table, stairs it stands on, or a room it is in) | move the key or path point by the push-out the hint gives |
| `people_overlap` | two bodies inside each other (hands may touch) | move one figure apart |
| `floating` / `sinking` | the lowest point off what the figure stands on | lower or raise the key's location z |
| `foot_slide` | a planted figure glides between two keys of the same pose | give the move a walk path, or keep the location |
| `reach` | a hand misses its declared target | move the figure toward it, or the target nearer |
| `pop` | a joint jumps in one frame | give the change more time, or add a key between |
| `path_blocked` | a path line runs through an object | insert the detour point the hint gives |

Each issue names its `cause` (e.g. `figures[Kai].keys[2]→[3] (1.5–2.1 s)`), `worst_time` and `severity`.
`beats` lists which shot each key lands in, to check beats against the notes. Pass `chunk: {figures,
objects, actions}` to check a candidate before saving. The loop: fix the worst error, check again, render
once the errors are gone. A chunk may render with open issues (they ride on the response and the Blocking
page shows them); the person decides. It is an approximation on mannequin capsules and object bounds; the
animatic is the authority.

### The render's own QA (on the meshes)

Every animatic render measures its figures again on their real meshes and rigs against the set's own
geometry (not boxes): `set_penetration`, `people_overlap`, `floating`/`sinking` and `reach`, written to
the render's `scene_inventory.motion_qa` and shown under the animatic on the Blocking page. It also makes
small fixes and lists them in `motion_qa.fixed`: feet settled onto what is under them (up to 12 cm off)
and a hand or forearm eased out of a surface it went up to 5 cm into (when no target puts it there).
Anything bigger is reported, never moved: fix it in the blocking. Read `motion_qa` with the cut check
when the render finishes; an approved animatic with open errors shows an amber ring on its chunk.

## Action skills (`actions` on a chunk)

Write intent; each skill expands into keys, paths, talk spans and props before the check and the render
(`include_expanded: true` on blocking_check shows the result). They run in order, so later skills build on
earlier ones. A figure is keyed or on a path within a chunk; a skill that needs the other says so (end a
line with a bail, then key the figure in the next chunk). Numbers may be ranges, `{"range": [0.5, 1.5]}`:
the check tries values across each range and keeps the one with the fewest issues (`actions.chosen`).

| Skill | Arguments | Expands to |
|---|---|---|
| `skate_line` | figure, points, speed?, start_time, stance, push_until?, board?, dismount | a skate path plus a skateboard that rides it |
| `bike_ride` | figure, points, speed?, start_time, bike?, dismount | a bike path plus a bicycle that rides it |
| `walk_to` / `run_to` | figure, points (from where it stands), speed?, start_time, end_pose | a walk or run path |
| `ollie` | figure, at [x,y], height 0.35, length 1.4 | a hop in the skate line over that spot (kerbs, gaps) |
| `bail` | figure, time?, land | the line ends at `time`; the rider pitches over and lands lying; the board rolls on 1.5 m (a bike tips over) |
| `chase` | pursuer, target, gap s, offset m, gait?, speed? | the target's line, coming from `gap` seconds back along it, `offset` to its left; a kit if it rides. Give an offset (or end the target's line with a bail) or the pursuer runs into a stopped target |
| `fight_exchange` | attacker, defender, time, punches, interval, hand, hit | squared-up guards, punches at the head, hits rocking the defender back |
| `shoot` | shooter, target (figure or point), time, shots, interval, gun?, hit | the pistol comes up 0.5 s before, recoil per shot; a hit figure falls |
| `take_cover` | figure, behind (object), threat, time | a run to the far side of the object, crouched by `time` |
| `fall` | figure, time, toward (forward, back, left, right, or a world direction [dx, dy]), distance | stumble then lie (face down forward, on the back backward) |
| `sit_down` / `stand_up` | figure, seat (object or point), time, duration, facing? | the planted sit-down and stand-up keys |
| `conversation` | lines [{figure, words or seconds, energy}], start, gap, listeners | talk and listen spans timed from the words; still figures look at each other |
| `knock_over` | figure, prop (a chunk prop), time | a reach to the prop and its tip-over away from the hand |

Example, a chase that ends in a bail:

```json
"actions": [
  {"skill": "skate_line", "figure": "Kai", "points": [[0,0,0],[14,0,0]], "stance": "goofy"},
  {"skill": "ollie", "figure": "Kai", "at": [4,0]},
  {"skill": "chase", "pursuer": "Dez", "target": "Kai", "gait": "bike", "gap": {"range": [0.6, 1.4]}, "offset": 1.0},
  {"skill": "bail", "figure": "Kai", "time": 3.0}
]
```

For a performance the procedural skills cannot give (a kickflip, a choreographed fight, a stunt fall),
generate a clip with text_to_motion and give the figure `motion` instead; the check skips clips and the
animatic shows them.
