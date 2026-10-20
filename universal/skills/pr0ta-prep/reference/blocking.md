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
