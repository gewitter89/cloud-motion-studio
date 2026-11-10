# REQUIREMENTS: Two-Minute Cinematic Film "VOYAGER: The Loneliest Artifact"

## 1. Executive Summary
Produce a standalone 2-minute (120 seconds) high-retention cinematic science documentary film dedicated to Voyager 1 & The Golden Record. The entire creation and rendering pipeline must execute autonomously in the cloud (GitHub Actions + Cloud VPS 169.58.30.140) so that shutting down the user's local PC does not interrupt the process.

## 2. Functional Requirements (FR)
- **FR-1 [Cloud Autonomy]:** Pipeline runs in GitHub Actions (`.github/workflows/render-two-minute-film.yml`) and Cloud VPS. Process runs detached via background runner, writing state and delivering outputs directly to GitHub Releases and Telegram.
- **FR-2 [Duration & Resolution]:** Exactly 120.0 seconds (3600 frames @ 30 FPS), Full HD 1920x1080, H.264 High Profile, AAC 256 kbps.
- **FR-3 [Narrative Structure]:**
  - Act 1 (00:00 - 00:25): The Void & 24 Billion Kilometers (Atmosphere of unfathomable isolation).
  - Act 2 (00:25 - 00:55): 1977 & The Golden Record (Humanity's message: sounds, laughter, music, Bach).
  - Act 3 (00:55 - 01:25): Pale Blue Dot (The 1990 photo: Earth as a suspended dust mote in a sunbeam).
  - Act 4 (01:25 - 02:00): Eternal Silence & Immortality (Sensors fading in 2026, floating through the galaxy forever).
- **FR-4 [Audio & Voiceover]:**
  - High-fidelity Russian voiceover with flawless diction, accents, and timing.
  - Multi-layer cinematic sound design: Interstellar sub-bass drone, authentic NASA telemetry / radio pulsars, spatial stereo music bed, emotional crescendo.
  - Loudness normalized to -14 LUFS (broadcast standard).
- **FR-5 [Visual Quality & Motion]:**
  - Zero primitive stick figures, zero black bars, zero comic speech bubbles.
  - Authentic astronomical space art: Photorealistic Golden Record texture, Jupiter Great Red Spot storm turbulence, Saturn ice rings, Deep Space starfields, Pale Blue Dot sunbeam flare.
  - Dynamic camera kinematics: 2.5D multi-plane depth parallax, orbital drifts, anamorphic lens flares, cosmic dust micro-particles.
  - Kinetic typography: Subtle, elegant gold/white subtitles for mobile/desktop viewers.

## 3. Non-Functional Requirements (NFR)
- **NFR-1 [Zero PC Dependence]:** 0% CPU/GPU workload required on user's machine after trigger.
- **NFR-2 [Verifiability]:** Automatic contact sheet audit generation (12 frames sampled every 10s) to prove motion and visual consistency.
- **NFR-3 [Delivery]:** Automated push to GitHub Release `v2.0.0` and Telegram notification via bot `@prostov_shrink_bot`.
