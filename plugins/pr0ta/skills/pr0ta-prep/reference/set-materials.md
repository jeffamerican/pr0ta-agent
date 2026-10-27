# Premium set builds: geometry, materials and lighting

`blender_job_submit` builds a set at one of two quality tiers, named in the
request's `quality_tier`.

- **`blockout`** (the default, unbilled) is the reference build: primitives
  with flat colours, rendered on EEVEE at up to 1280x720 and 64 samples. Use it
  for layout, scale, blocking, cameras, animatics and anything a video model
  only takes staging from.
- **`premium`** (priced in credits) is a photoreal build. It unlocks
  everything below and path-traces beauty renders in Cycles with denoising, at
  up to 3840x2160 for stills and 1920x1080 for video. Use it when the person
  asks for a finished or photoreal set, for an approved set's hero stills, or
  when a render itself is the deliverable.

A blockout request that uses a premium field is refused, and the error names
each field. Ask the person before you switch a build to premium, because it
spends credits. The Operator quotes it before it runs, and `tasks_get` shows
the quote in `metadata.cost_estimate`. A delivered build is charged the worker
time it used, never more than the quote. A failed job is never charged. A
premium job reserves its worker time: the build, plus a path-tracing budget shared
across its beauty frames (the beauty pass and each `shot_cameras` still). Each
frame stops on time and is denoised, so a premium job always finishes. When a
job asks for more frames than the budget holds, the error says how many fit.
Render the rest in further premium jobs on the saved `.blend`
(`source_asset_id`, no `objects`), which reserve a short load-and-save
instead of a build. A premium
video path-traces at most 48 frames (2 s at 24 fps) per job on the CPU worker,
so render a moving premium shot in 2 s pieces, or keep video in blockout and
make the premium stills. Premium `render.samples` is a ceiling
(default 1024): adaptive sampling stops clean pixels early. `render.exposure_ev`
sets the camera exposure in stops. A `clay` render or an animatic is always a
blockout.

## Real-time asset (the Space app)

Every premium build also bakes the set into a real-time asset, and that asset
is the build's main deliverable when the person wants to see the set in the
ProtaFilm|maker Space app (RealityKit on iPhone) or any real-time viewer:

- **Files.** `set_environment_realtime.usdz` (`model/vnd.usdz+zip`, for the
  Space app and Quick Look) and `set_environment_realtime.glb` (unlit glTF), both
  role `realtime_model` on the set. Publish them with `review_submit_assets`;
  the Space app opens them from the review room with no other steps.
- **Look.** Cycles bakes the set's own light (sun, sky, portals, practicals,
  bounce and shadows) and its materials into texture atlases, denoised and
  tone-mapped like the stills. The material is unlit (glTF) or emissive on
  black with no specular (USD), so the phone's light does not light the set a
  second time. Glossy reflections are baked as seen straight on: metals keep
  their colour, but mirrors and polished floors do not reflect as you move.
  Glass and water stay see-through, let the sun and sky through into the bake
  (a room lit by a skylight or windows bakes as bright as it renders), and are
  lit by the phone. Figures are left out.
- **Texel density.** The set's surfaces are grouped by area into up to four
  atlases (`realtime_asset.max_atlases`, up to 6) of at most 4096 px
  (`texture_size`), at one density of at most 256 px/m.
  `scene_inventory.quality.realtime.atlases[]` reports each atlas's size,
  area and `px_per_m`. When fewer than 16 samples would fit the bake's time, the
  atlases shrink first, and the receipt shows the lower `px_per_m`.
- **Scale and placement.** Real meters, Y-up; the origin sits on the floor
  under the centre of the set's footprint (`origin_offset_m` is the shift from
  the build's world).
- **iPhone budgets.** At most 1,000,000 triangles by default
  (`realtime_asset.max_triangles`, up to 1,500,000; denser sets are decimated
  before the bake) and at most 150 MB per file.
- **Time.** On the CPU worker the bake has 900 s in a build that renders no
  stills (`render.passes []`, no `shot_cameras`), 480 s when the build also
  path-traces stills (which then share 420 s), and about 1,100 s in a re-bake of
  a saved `.blend`. Every premium job reserves the same 1,200 worker seconds.
  The density the bake reaches on CPU depends on the set's surface area: the
  17-object test arcade (about 1,400 m² of surface) baked at about 1 cm a texel.
  For the best asset, build with `passes []` and render stills in a later job.
- **When the bake cannot finish.** The build is still delivered (`.blend`,
  runtime GLBs, stills), `scene_inventory.quality.realtime.error` says why, and
  the task message says so. Finish it with a re-bake: a premium job on the saved
  `.blend` (`source_asset_id`, no `objects`, `realtime_asset: {enabled: true}`,
  `render.passes []`). `realtime_asset: {enabled: false}` skips the bake on a
  render-only job. A blockout never bakes.
- **One at a time.** One premium job runs at a time across the platform while
  premium runs on the CPU worker. A second one is refused with a retryable
  message that says how many minutes to wait; nothing is charged. Blockouts
  are not limited by it.

After the job, `scene_inventory.quality` reports the engine, the samples
ceiling, each frame's time limit and the seconds each still took. It also lists
what every object was given (cutouts, modifiers) and credits each library file
the build used. Look at the stills before you call a set finished.

## Shapes

Each `scene_plan.objects` entry takes exactly one shape: a `primitive`, an
`asset_id`, a `sweep`, a `lathe` or `coffers`. Premium cylinders, cones and
spheres use 64 segments (`segments` sets 3–256). Sweeps, lathes and coffers are
built in real meters: `dimensions` is ignored and `transform.scale` multiplies
the meters.

**Sweeps** (`sweep`) run a moulding profile along a path: cornices, skirting,
chair and picture rails, archivolts, handrails, frames and kerbs.

- **Profile.** Give `profile` (a name below, scaled by `profile_size_m` =
  [projection, height] in meters) or `profile_points`, your own closed outline
  in meters (x out from the wall, y up). `flip` mirrors it.
- **Path.** Give `path` (points in the object's meters, with `closed: true` to
  run it round a room) or `arc` (`radius_m`, `start_deg`, `end_deg`, and
  `plane` `xz` for a vertical arch about the object's location or `xy` for a
  curve in plan).
- **Direction.** On a path, the profile projects to the right of travel seen
  from above, so walk a room's walls clockwise to face the mouldings inward. On
  an arc, it projects outward from the radius and toward -y, out of a wall
  whose face looks toward -y.
- Corners are mitred. UVs are in meters along the path.

Sweep profiles: `rect`, `round`, `half_round`, `cove`, `ovolo`, `ogee`,
`cyma_reversa`, `torus`, `astragal`, `bead`, `baseboard`, `chair_rail`,
`picture_rail`, `crown`, `cornice` (a classical cornice: bed moulding, corona
with drip, cyma recta).

**Lathes** (`lathe`) turn a profile about the object's z axis: columns,
balusters, urns, domes and finials.

- **Profile.** Give `profile` (scaled by `radius_m`, the lower shaft radius,
  and `height_m`) or `profile_points` as [radius, height] pairs from bottom to
  top. A radius of 0 closes the shape on the axis.
- **Turn.** `segments` sets the smoothness. An `angle_deg` under 360 turns
  only part of the profile, for example a half dome against a wall.
- **Square section.** `section: "square"` runs the profile round a square
  instead of a circle, for piers and pedestals. A pilaster is a square-section
  column with `section_depth` about 0.25, set against the wall.

Lathe profiles: `column_tuscan` (a whole Tuscan column: base, shaft with
entasis, astragal, echinus and abacus; the base and abacus reach 1.25 x
`radius_m`), `column_shaft`, `column_base`, `column_capital`, `baluster`,
`urn`, `vase`, `dome` (a shell), `finial`, `bowl`, `pedestal_round`.

**Coffers** (`coffers`) are a slab with a grid of stepped recesses on its
underside, built as clean quads. Use them for coffered ceilings and soffits.

- **Size.** `width_m` runs along x and `depth_m` along y. `thickness_m` sets
  the slab, and `cells` [x, y] the number of coffers.
- **Coffers.** `rib_m` is the rib width, `recess_m` the depth (less than the
  thickness), and `steps` (1–3) the number of stepped stages.
- **Barrel vault.** Add a `bend` modifier of 180 degrees about `x`. Make
  `depth_m` the arc: the span x pi / 2. Place the object at the crown height,
  which is the springing height plus span / 2.

## Openings (`cutouts`)

Exact boolean cuts through a primitive, sweep, lathe or coffer slab, applied
before its modifiers so an `array` repeats them. The result is cleaned: welded
vertices, no slivers, coplanar faces merged.

- **Shape.** `shape` is `box`, `cylinder` (axis along the object's y: an
  oculus through a wall lying in x-z), `arch` (round-headed: its height
  runs from sill to crown and includes the half-round head) or `sphere`
  (niches).
- **Placement.** `location` is the opening's centre in the object's own
  meters, measured from the object's centre before its rotation. Make the
  depth (y) larger than the wall is thick.
- **Repeat.** `repeat: {count: [x, y, z], spacing_m: [...]}` cuts a row or
  grid of openings (up to 256): an arcade's arches, or a wall of windows.

## Modifiers (`modifiers`, up to 8, in order, live in the saved .blend)

- `bevel` (`width_m` 0.0005–0.5, `segments` 1–8, `angle_deg`): no real edge is
  knife-sharp. Bevel stone blocks, plinths, furniture and walls by 5–20 mm with
  2–3 segments.
- `array` (`count` 2–64, `offset_m` centre to centre in the object's meters, or
  `relative_offset` in multiples of its size, `merge`): colonnades, arcades,
  balusters and steps. Copies across all of an object's arrays are capped at
  1024.
- `subdivision` (`levels` 1–3, `simple` keeps the shape and only adds
  density): smooth organic forms, or density for displacement.
- `solidify` (`thickness_m`, `offset`): gives a thin surface a thickness.
- `mirror` (`axes`): builds a symmetric half once.
- `bend` (`angle_deg`, `axis` `x` or `y`): curls the horizontal extent across
  the axis down about it, keeping the crown at the object's location. It needs
  density across the bend: coffers have it, and a plain slab needs a `simple`
  subdivision first.

Premium shading (`shading: auto`) smooths curved surfaces and keeps edges
sharper than 30 degrees crisp, with weighted normals on flat faces. Use
`smooth` or `flat` to force either.

## Materials (`material`)

Give one of `library`, `preset` or `image_asset_id`. Without one, the
blockout fields `color`, `roughness` and `metallic` apply.

- **`library`** is a CC0 PBR texture set (Poly Haven, ambientCG), baked into the worker.
  It is box-projected in object meters, so primitives need no UVs and the
  texel density stays real. `texture_scale_m` sets the width of one repeat
  (the default is the texture's measured size, below). `texture_rotation_deg`
  turns the grain. Sweeps, lathes and coffers default to `projection: uv`,
  which keeps their metric UVs. A wood `cube` that is a member (one side at
  least 1.5 times the next and at most 1 m across: a post, beam, rafter, rail,
  leg or table top) gets metric UVs with the grain along its length, so its
  planks never cross it; the job's quality receipt marks it `grain`. Floors,
  walls, planes and round shapes keep the box. `projection: box` or a non-zero
  `texture_rotation_deg` keeps the box on a member too.
- **`weathering`** (0–1; library default 0.3, else 0) adds grime where
  surfaces meet and uneven roughness. Set 0 for showroom-new surfaces, and
  0.6–1 for old courtyards.
- **`displacement_m`** turns the height map into real relief where the mesh is
  dense (a `simple` subdivision first, levels 2–3) and bump elsewhere. Typical
  values: 0.005–0.02 for cobbles, rubble walls and rough plaster.
- **`tint`** multiplies a library or preset colour. **`emission_strength`**
  makes it glow in the tint or colour: lamp shades, lit windows and screens.
- **`image_asset_id`** stretches a project image over the object's UVs.
  Use it for paintings, posters and signage: put it on a `plane` sized to the
  image's aspect and rotated upright. Frame it with a closed sweep (an
  `astragal` or `bead` with a `gilt` preset).

Library textures (name, what it is, and the real width of one repeat):

**marble and travertine**: `marble_white_polished` polished white Carrara marble, grey veins (2 m); `marble_black` polished black marble, white veins, Nero Marquina (2 m); `marble_cream` polished cream marble, Botticino (2 m); `marble_rose` polished rose marble with red veins (2 m); `marble_beige_tiles` honed beige marble wall and floor tiles (1.5 m); `marble_floor_tiles` large marble floor tiles with grout lines (2 m); `marble_mosaic` small marble mosaic tiles (2 m); `travertine` pale honed travertine (1.2 m); `travertine_banded` banded travertine, warm grey and cream (1.2 m).

**stone**: `granite_floor_tiles` speckled granite floor tiles (2.3 m); `terrazzo` terrazzo floor tiles (2 m); `stone_floor_flagstones` worn monastery flagstone floor (1.8 m); `sandstone_blocks` large dressed sandstone blocks, an ashlar wall (3 m); `pale_stone_ashlar` pale cut-stone bricks, limestone look (2 m); `stone_wall_rubble` old rubble stone wall (2 m); `castle_stone_white` whitewashed castle stone blocks (2.5 m); `slate_floor` dark slate floor slabs (2.29 m); `cobblestone` cobblestone street (1 m).

**plaster**: `plaster_white` clean white interior plaster (1 m); `plaster_painted` painted plaster wall, light texture (2 m); `plaster_ochre` Italian ochre lime plaster (2 m); `plaster_worn` worn, patched plaster wall (1.8 m); `stucco_white` white exterior stucco (2 m); `plaster_red_weathered` weathered red/terracotta plaster (2 m).

**concrete**: `concrete_floor` smooth concrete floor (2 m); `concrete_wall` cast concrete wall (2 m); `concrete_brushed` brushed concrete (2.5 m).

**ceramic and brick**: `terracotta_floor_tiles` square terracotta (cotto) floor tiles (2.08 m); `terracotta_patterned_tiles` patterned terracotta tiling (2.15 m); `roof_tiles_clay` clay barrel roof tiles (4 m); `ceramic_wall_tiles` glazed interior wall/floor tiles (1.9 m); `checkered_floor_tiles` black and white checkered tiles (2 m); `brick_red` red brick wall (3 m); `brick_herringbone_paving` herringbone brick paving (1.8 m).

**wood**: `parquet_herringbone` herringbone parquet floor (3.4 m); `wood_floor_boards` clean wooden floorboards (1.7 m); `wood_floor_old` old worn floorboards (3 m); `oak_veneer` oak veneer, furniture and panelling (1.83 m); `walnut_veneer` walnut veneer, furniture and panelling (1.8 m); `wood_planks_dark` dark stained planks (2 m); `wood_planks_weathered` grey weathered exterior planks (2 m); `wood_planks_white_painted` white painted planks (1.8 m); `tree_bark` brown tree bark (1 m).

**metal**: `metal_plate` treadplate steel (0.5 m); `metal_rusty` rusted steel sheet (1 m); `corrugated_iron` galvanised corrugated iron (1.12 m).

**fabric**: `velvet` velour velvet upholstery (0.28 m); `linen` rough linen (0.27 m); `denim` denim twill (0.1 m); `leather_brown` brown leather (0.4 m); `jacquard_quatrefoil` quatrefoil jacquard, drapes and upholstery (0.28 m); `wool_boucle` wool boucle upholstery (0.31 m).

**ground**: `gravel` loose gravel (2.25 m); `asphalt` road asphalt (3 m); `grass` grass with leaves (2 m); `dirt` packed dirt (2.07 m); `sand` coastal sand (15 m); `rock_face` natural rock face (2.38 m).

Procedural presets (no image files; `color` drives the ones marked *):
`gold_polished` polished gold; `gilt` gilded leaf, slightly worn (frames,
mouldings); `brass_aged` aged brass with soft tarnish; `copper` copper;
`bronze_patina` bronze with green verdigris in the hollows; `steel_brushed`
brushed stainless steel; `chrome` mirror chrome; `iron_wrought` dark wrought
iron (railings, grilles); `glass_clear` clear window glass; `glass_frosted`
frosted glass; `mirror` silvered mirror; `water_still` still water surface;
`marble_veined`* veined marble in any colour; `paint_gloss`* glossy paint;
`paint_matte`* flat matte paint; `ceramic_glazed`* glazed ceramic with
clearcoat; `plastic`* smooth plastic; `rubber`* matte rubber;
`fabric_plain`* plain woven fabric with sheen; `paper`* matte paper.

## Light (`scene_plan.world`, lights)

- **World.** `world` takes an `hdri` (below) or a physical `sky`.
  `sky` takes `sun_elevation_deg`, `sun_azimuth_deg` (counter-clockwise from
  +x seen from above, so 90 is +y), `sun_size_deg` (larger means softer
  shadows), `air_density` and `dust_density` (haze). `strength` scales it.
  The sky is real daylight, stops brighter than exposure 0 expects: expose it with
  `render.exposure_ev` about -5 at `strength` 1 (about -5 - log2(strength):
  -3.75 at 0.42, -4 at 0.5). At -1 an 18% grey card renders almost white and
  dark timber turns pale and grey, so judge colour only at a sky exposure.
  `rotation_deg` turns an HDRI. `background_visible: false` lights the set
  with the sky but shows `world_color` to the camera.
- **Portals.** For an interior lit through windows, add one AREA light per
  opening with `size` x `size_y` matching it, `portal: true` and `energy` 0,
  rotated to point into the room. A portal adds no light of its own: it guides
  the sky's light through the opening, so the interior clears faster and with
  less noise.
- **Practicals.** Lamps, sconces and candles are ordinary lights, plus an
  emissive material on the shade or flame.

HDRIs (CC0, Poly Haven): `sky_midday_partly_cloudy` midday sun, partly cloudy
sky; `sky_clear_midday` clear midday sky, hard sun; `sky_overcast` soft
overcast sky, no sun; `sky_morning` low morning sun, clear sky; `sky_sunset`
warm sunset sky; `sky_dusk` blue-hour dusk after sunset; `sky_night` night sky
with moonlight; `venice_sunset` Venetian lagoon city at sunset (buildings and
water show); `studio_soft` small photo studio with soft boxes.

## Recipe: an arcade under a coffered barrel vault

A gallery 6 m wide runs along x, with an arcade wall at y = 3.2, a back wall at
y = -3.1, and bays every 2.8 m.

1. **Arcade wall.** A `cube` 18 x 0.6 x 4.6 at z 2.3, `library
   plaster_ochre`. Give it one `arch` cutout 2.0 x 1.4 x 3.9, repeated `[5, 1,
   1]` every 2.8 m, and a 15 mm `bevel`.
2. **Archivolts.** A `sweep` with `profile ogee`, `profile_size_m` [0.22,
   0.12] and `arc` `radius_m` 1.0 from 0 to 180, placed at the first arch's
   springing on the wall face. Give it an `array` of 5 every 2.8 m.
3. **Columns.** A `lathe` `column_tuscan` of radius 0.2 and height 2.95 in
   front of the piers, `library marble_white_polished`, with an `array` of 6.
4. **Pilasters.** The same lathe with `section: square` and `section_depth`
   0.3 on the back wall.
5. **Cornices.** A `sweep` with `profile cornice`, `profile_size_m` [0.32,
   0.4], along each wall at the springing height (4.2).
6. **Vault.** `coffers` with `width_m` 18, `depth_m` 9.42 (3 x pi),
   `cells` [16, 7], `rib_m` 0.14 and `recess_m` 0.18. Give it `bend` 180
   about x and place it at z 7.6 (4.6 + 3). Use `stucco_white` with
   `weathering` 0.6.
7. **Floor and light.** `terracotta_floor_tiles` on the floor. Use a `sky`
   with the sun low across the arcade (elevation 28, azimuth 70), and a
   17 x 3.9 portal across the arches.
