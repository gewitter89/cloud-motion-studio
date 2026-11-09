---
name: visual-physics-audit
description: Visually inspect storyboards and rendered animation frames for anatomy, geometry, perspective, physics, lighting, legibility, and continuity, then provide concrete fixes before delivery.
---

# Visual / physics QA

Generate a contact sheet of source frames and sample keyframes at the beginning, midpoint, and end of every shot, plus both sides of every cut. Do not evaluate the code alone.

## Reject/fix if
- Characters' limbs have inconsistent articulation, feet float or pass through ground, hands detach, relative scale changes accidentally.
- A beam of light is disconnected from its emitter, points backwards, moves independently from emitter, or fails to form a plausible illuminated target.
- Props, falling items, floating money or particles have no defined origin, path or explanation; collisions and relative positions contradict the story.
- Depth and occlusion conflict, horizons change arbitrarily, perspective lines don't converge coherently, foreground/background sizes contradict the camera model.
- Objects intersect unintentionally, text collides/clips, parts of main action are off-screen, labels are too small for phone viewing.
- The viewer cannot answer in 2-3 seconds: 'Where am I? What is happening? Why does it matter to the narration?'
- The shot stays compositionally stagnant >8-10 seconds with no meaningful new information, unless explicitly editorially justified.

## Geometry specification per shot
In the shot/asset config declare: `{world_width,world_height,ground_y,camera,vanishing_point,light_sources,character_scale,character_skeleton_zones,prop_anchor_points,z_order,collision_surfaces}`. Use consistent local coordinates; measure positions instead of scattering magic numbers. For 2D, 3D fields can be `not_applicable` rather than fake values.

Use an explicit character rig with torso, shoulders, elbows, hips, knees, and feet. Walking requires alternating support feet with at least one grounded contact; jumps require take-off, ballistic arc, landing. If the scene is iconic/stylized, preserve internal consistency rather than demand photorealistic physics.

## Report format
For every issue: `timestamp -> visible defect -> impact on viewer -> exact asset/layer/coordinate/timing fix -> screenshot path -> severity (blocker/major/minor)`.
Use verdict PASS only when visually verified, not inferred from logs. Score framing, legibility, physical coherence, continuity, narrative clarity and motion quality from 0 to 10. Final release: all blockers fixed, category scores >= 8 or explicitly documented exception approved by user.
