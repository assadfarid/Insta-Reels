# The Robot That Learned to Lie: illustrated story video pipeline

Builds a ~12-minute 16:9 narrated storybook film from `script.py`.

| Step | File | What it does |
|---|---|---|
| Script | `script.py` | Every spoken line: scene id, speaker, text (with ElevenLabs v4 audio tags), optional Echo HUD text |
| Scene art | `scenes.py` | Image prompts for the 55 scenes (Seedream 5.5, character reference sheet for consistency) |
| Voices | `groups.py` | Groups lines per chapter and speaker; each group is one TTS take with `[long pause]` separators |
| Split | `split2.py` | Cuts each take back into single lines (silence detection matched to text length) |
| Timeline | `timeline.py` | Lays out lines, shots, chapter cards, HUD overlays and the music plan into `timeline.json` |
| Audio | `mix_audio.py` | Places dialogue, adds radio/recording FX, loops and ducks the score, loudness-normalises (-16 LUFS) |
| Video | `render.py` + `effects.py` | Ken Burns motion with handheld float, per-scene living effects (glowing/blinking eyes, light flicker, sparks, particles, light rays, hologram, headlights), crossfades, title cards, typed HUD readouts, vignette and grain at 1920x1080/24fps |

Render: `python3 timeline.py && python3 mix_audio.py && for p in 0 1 2; do python3 render.py $p 3 & done; wait`,
then concatenate `out/part_*.mp4` and mux with `assets/mix.wav`.

Voices (ElevenLabs): narrator Tom (deep, caring), Mia Emmaline, Echo Sigma Centauri, Dr. Elena Lulu, radio operator Liam, technician Jason.
