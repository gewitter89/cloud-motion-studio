# ARCHITECTURE & DESIGN: Two-Minute Cinematic Film "VOYAGER"

## 1. Cloud Architecture

```
[Local / Agent]
     │
     ├─► Push Code & Workflow to GitHub (origin/main)
     ├─► Trigger GitHub Actions (`.github/workflows/render-two-minute-film.yml`)
     └─► Deploy & Trigger Cloud VPS Daemon (`169.58.30.140`)
              │
              ▼ (Fully Autonomous Execution in Cloud)
      ┌──────────────────────────────────────────────────┐
      │ 1. Voiceover Synthesis & DSP Normalization       │
      │ 2. Spatial Ambient SFX & Music Synthesis         │
      │ 3. Keyframe Rendering & Kinematic 2.5D Parallax  │
      │ 4. Particle Engines (Stars, Dust, Lens Flares)   │
      │ 5. FFmpeg H.264/AAC Mastering (1920x1080@30FPS)  │
      │ 6. Automated Audit Contact Sheet                 │
      └──────────────────────────────────────────────────┘
              │
              ├─► Attach to GitHub Release `v2.0.0`
              ├─► Direct Deploy to Cyberdeck Public Web CDN
              └─► Push Notification & Video to Telegram Bot
```

## 2. Audio Pipeline Design
- Script text divided into 4 chapters matching the timeline.
- Narration synthesis with edge-tts / high-quality neural voice (ru-RU-DmitryNeural / ru-RU-SvetlanaNeural with adjusted pitch/rate for cinematic gravity).
- Procedural multi-layer sound design:
  - Deep space low-frequency hum (40-65 Hz continuous drone).
  - NASA pulsar radio clicks & Golden Record needle crackle.
  - Ambient orchestral drone bed (C minor / D minor ambient pads).
  - Climax emotional swell at 01:20 (Pale Blue Dot revelation).
- Audio mixing via FFmpeg `amix` + `loudnorm` filter (-14 LUFS, -1.5 dBTP).

## 3. Visual Engine Design
- **Renderer:** Python + OpenCV + PIL + NumPy vector particle system.
- **Visual Layers per Shot:**
  1. Base cosmic background (Deep starfield with multi-spectral nebulae).
  2. Hero celestial bodies (Voyager probe with parabolic dish, Golden Record, Jupiter clouds, Saturn rings, Earth pale blue dot).
  3. Dynamic volumetric lighting (Solar beam scattering, engine telemetry pulses).
  4. Floating stellar dust particles (3D depth-projected points).
  5. Kinetic subtitle overlay with gold keywords.

## 4. Delivery & Verification Protocol
- Automated QC script generates `voyager_120s_audit_sheet.jpg` sampling 12 keyframes.
- Check black bar ratio < 5%, motion delta > 10.0 across all shots.
- Release created via GitHub CLI (`gh release create v2.0.0`) with release notes.
