---
name: voice-director
description: Select and direct a professional Russian or Ukrainian narration voice for short video, create A/B voice tests, synchronize it with the storyboard and measure final sound loudness.
---

# Voice director

## Do not guess from audio metadata
Technical analysis of bitrate/sampling/loudness does not reveal accent, realism or emotional quality. Listen to actual A/B voice samples and verify pronunciations before rating them. If your environment can't listen to audio, report that limitation and ask the user to judge the shortlisted examples.

## Process
1. Recover exact verified narration from project source (script/subtitle/transcript). Mark emphasis, pauses, factual words, named entities and difficult pronunciations.
2. Use the same 15-25-second speech excerpt to generate three alternatives, with consistent loudness: A neutral warm low/mid male documentary narrator, B energetic but controlled explanatory narrator, C familiar but credible and conversational. Adapt language to source script. Do not change words across alternatives.
3. If API configured, evaluate Gemini TTS or ElevenLabs; do not pretend to have API access. Gemini voice auditions could start with `Charon` (informative), `Iapetus` (clear), `Orus` (firm), but evaluate accent and gender in the chosen language rather than assuming the voice name guarantees any trait.
4. Direct performance: natural Russian/Ukrainian pronunciation, deliberate phrase stress, stable voice identity and room tone, 125-155 spoken words/minute where comfortable, pauses 150-350ms between thoughts and longer at scene changes as needed. Do not enforce exact numerical speed if it harms naturalness.
5. Compare A/B/C blind at matched loudness, choose one, then render the whole narration in coherent segments. Fix incorrect pronunciation; no random speaker switches.
6. Mix and QC with FFmpeg. Integrated target approximately -16 LUFS for finished voice-forward stereo video, true peak <= -1.5 dBTP; voice can remain mono inside final stereo mix. If music present, duck it under speech and check intelligibility on phone speaker.
7. Export final narration, its associated transcript, per-segment timestamps, and a short voice settings log. Mark if evaluation was purely technical and no actual auditory listening was performed.

## Narrator instruction template
'Professional male narrator for a clear modern short educational documentary. Confident but human, warm medium-low register, crisp consonants without artificial booming bass, restrained expressivity, no advertisement or announcer intonation. Speak fluent [LANGUAGE] in a neutral natural accent. Put expressive emphasis on scientific/conceptual contrasts, vary phrasing gently, pause after important ideas and before consequences. Do not shout, imitate famous speakers, or change persona between clips.'
