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

