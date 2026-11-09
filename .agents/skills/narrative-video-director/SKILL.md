---
name: narrative-video-director
description: Design, storyboard, time, render and quality-check a professional 2-minute narrative explainer or motion-graphic video with geometrically coherent scenes.
---

# Narrative video director

## Required workflow
1. Inspect repo and current video. Identify the existing renderer, voice engine, project format, assets and screenplay. Write `production/TECH_AUDIT.md` with verified facts and gaps; never assume the script if audio cannot be transcribed.
2. Write `production/BEAT_SHEET.csv` with `start_s,end_s,exact_narration_text,scene_goal,visual_action,assets,geometry_rules,sfx,review_status`. Each row should be an understandable visual statement, not vague 'show a cool abstract animation'.
3. Write `production/STYLE_BIBLE.md`: fixed palette, typography, character proportions, 2D/2.5D perspective model, world-to-screen coordinates, stroke widths, lighting, icon semantics, and transition grammar. Reuse identical character components and shape primitives.
4. Write a `production/STORYBOARD.md` showing for each beat: initial frame, final frame, change or consequence, camera framing, and exactly which spoken words it supports.
5. Produce an animatic/low-res render (first 15-25 seconds first for high-risk scenes). Extract contact sheets and inspect original frames. Mark each shot as PASS/FIX. Fix layout before full render.
6. Generate/replace voice only with the voice-director procedure. Align timings to the selected final waveform; use timestamps rather than guessing. If transcription exists, verify it with the original script.
7. Render complete MP4 at 1920x1080 30fps and ensure 120 +/- 5s if the user expects a two-minute video. Validate using ffprobe/FFmpeg and `tools/video_audit.py`.
8. Emit final `production/QA_REPORT.md`: shot-by-shot defects, improvements, unresolved issues, audio stats, final output files and exact render command.

## Visual storytelling rules
- Subject first: one primary object, clear actor/cause/action/effect sequence.
- Remove clutter, decorative filler, random coins/laser lines, ambiguous background marks.
- Design for phone: avoid tiny distant figures occupying <15% of the visible scene. For scenes focused on characters, frame them prominently enough to recognize actions.
- When a scene is an abstract metaphor, make its meaning explicit with a title, comparison, label, or unambiguous transformation.
- Every scene transition must indicate passage of time, shift of location, changed scale, or new argument; preserve overall style.
- Keep notes of known scene continuity: camera direction, light direction, ground line, object size and location, color identity and who is speaking.

## Rendering choice
First identify the current rendering stack. Improve it if viable. For code-based editorial motion design, Remotion + SVG or canvas is a strong default; read official Remotion skills. For mathematical diagrams use Manim if suited. Blender/3D physics only for shots that require real depth or simulation. FFmpeg is for audio/video engineering and QA, not an animation art director. Avoid rewriting the whole production stack without a reason.
