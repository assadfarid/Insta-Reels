# Pipeline (reference implementation: `story/` in the Insta-Reels repo)

Read `story/HANDOVER.md` there for the current state. Reuse the scripts rather than rewriting them; for a new
story copy `story/` to a new folder and replace `script.py`, the images, voices and clips.

## Contents
1. Files and formats
2. Voices
3. Timeline
4. Rendering engine
5. AI clips: install, sync, retime
6. Speech bubbles and subtitles
7. Quick updates and full renders
8. Masters and delivery

## 1. Files and formats
- `script.py` — `LINES = [(scene, speaker, text, hud_or_None), ...]`. Scenes `sNN`; chapter markers `tN`
  (silent). Speakers e.g. `N` (narrator), `MIA`, `ECHO`. Voice tags in brackets: `[softly]`, `[crying]`,
  `[pause]`, `[long pause]`, `[whispers]`. `hud` = robot diagnostic overlay text with `\n`.
- `assets/img/sNN.png` — one illustration per scene (2720x1536 worked well). Keep `_orig` copies before edits.
- `assets/lines/NNN.wav` — one file per line index (chapter markers have none).
- `assets/clips/sNN.mp4` — AI clip for a scene; originals kept as `raw_sNN.mp4`, rejected ones renamed.
- `faces2.json` — per scene, head boxes `{SPEAKER: [x0,y0,x1,y1]}` as fractions of the frame.
- `mouths.json` — `"sNN:SPEAKER": [x, y, facing]` (facing +1 right, -1 left).
- `timeline.json` — generated; shots, lines, huds, chapters, music segments, total.

## 2. Voices
Group lines by (chapter, speaker), join with `[long pause]`, generate one take per group, then split on the
pauses (`split2.py`: silence detection + text-length scoring to assign segments to lines). One take per group
keeps tone consistent and is far cheaper than one call per line. Character FX in the mix: radio band-pass,
recorded voice with room echo, robot with a light metallic echo.

## 3. Timeline (`timeline.py`)
- Hook (~5 s): the central question + answer (here "Is Mommy coming home tomorrow?" / "Yes, Mia. Tomorrow."
  with the WARNING HUD) over the relevant scene, then the main title.
- Gaps: ~0.35–0.4 s around narration, ~0.2 s between characters, ~0.7 s after emotional lines, +0.25 s on a
  scene change. Tight pacing was requested; don't let chapter cards run long (2.6 s overlay on the first shot).
- The final "The End." line becomes its own end card after the last picture holds ~2.6 s.
- Rolling credits shot (~21 s) after the end card; last ~6.5 s is a still card for YouTube end-screen elements.
- Music per chapter (`gentle`, `hopeful`, `sad`), merged into segments.
After any timing change re-run: `timeline.py`, `word_times.py`, `sfx.py`, `mix_audio.py`, `make_srt.py`.

## 4. Rendering engine (`render.py`, `effects.py`, `captions.py`)
- 1920x1080, 24 fps, 0.9 s crossfades. Camera: Ken Burns + push-ins on key emotional lines + handheld float;
  gentle drift (zoom 1.00→1.035) even on video shots so nothing ever stops.
- Still-scene effects: eye glow/blink/dim, red alarm flicker, hologram, screens, headlights, light rays,
  dust/pollen/embers, sparks, foliage/sky/water/waterfall displacement, scarf flutter, birds, depth parallax,
  breathing, power-cut blackout.
- Title/end/credits cards over a softly blurred, slowly moving clip frame; a signature ornament (gold line
  drawing outward, emblem in the middle) on title and chapter cards.
- Clip colour match: Lab mean/std transfer toward the scene's illustration at ~0.75 strength.

## 5. AI clips: install, sync, retime
1. Look at a frame strip (`select='not(mod(n,24))',tile=6x2`) before using a clip: check characters, extra
   people, objects, continuity, watermark.
2. Watermarks: Veo text bottom-right (1920 clips: `delogo=x=1856:y=1034:w=50:h=30`; 1280 clips:
   `x=1236:y=690:w=36:h=20`); **Gemini sparkle** sits higher (1920 clips: about `x=1692:y=852:w=98:h=98`).
   Locate unknown marks by finding pixels that are bright and static across all frames.
3. Register in `render.py`: `CLIP_SPEED[name]='h'`, `SYNC[name]=(phrase, seconds_into_clip_of_key_action)`,
   clip duration in `_cdur`.
4. `python retime.py sNN` writes `assets/retimed/sNN.mp4`: the clip slowed (ffmpeg `minterpolate`
   mci/aobmc) to exactly fill its scene with the key action on the phrase. `RUSH` entries keep a fast action
   at real speed (e.g. a character running in) and slow the rest.
5. Fixes that don't need a new clip: crop out an unwanted figure (zoom crop), paint out a static object with
   per-frame inpaint, trim a clip before it goes wrong, darken the start for a "lights go out" moment.

## 6. Speech bubbles and subtitles (`captions.py`)
- Narrator: Fredoka subtitle at the bottom, words fill yellow as spoken (per-word times from `word_times.py`),
  one subtitle at a time.
- Bubbles (style chosen by the user: white rounded pill, coloured name tag per character, soft shadow,
  pop-in). Placement search scores candidates: hard penalties for covering any face, being nearer another
  character than the speaker, the tail crossing another face, sitting on the HUD; prefers the facing side.
  Tail: short and slim, scaled to the bubble, always pointing down to the mouth.
- When a clip moves or zooms, set per-scene boxes from a gridded still of the clip; `FACES_LINE` /
  `MOUTH_LINE` override a single line.
- Audit script idea: for every character line compute distance from bubble centre to own face vs nearest other
  face; review the worst ratios.

## 7. Quick updates and full renders
- `python render_quick.py 170,190;300,320` re-renders only the 30-second pieces covering those ranges and
  joins all pieces (no re-encode) with the current `assets/mix.wav`. Minutes instead of ~35 minutes.
- `python render_quick.py all` after timeline changes; `python render_quick.py assemble` after audio-only
  changes. `render.py 0 1 --stills t1,t2` for check frames.
- Never run two quick updates at once (they write the same output).

## 8. Masters and delivery
- HQ chat copy: x264 slow, crf 19, maxrate 5.6M → ~410 MB for 11 min.
- 4K: `scale=3840:2160:flags=lanczos,unsharp=5:5:0.45`, libx265 crf 21 `-tag:v hvc1` (~870 MB) →
  `split -b 300M`; user joins with `cmd /c copy /b a.part0 + a.part1 + a.part2 out.mp4` and checks
  `Get-FileHash`. Tell them HEVC may need the free Windows HEVC extension or VLC.
- A tail clip (credits) can be appended with ffmpeg concat `-c copy` only if encoded identically — but audio
  fades at the old ending make joins audible; prefer re-rendering the whole 4K.
- Review copy for other AIs: 720p, crf 28, ~60 MB.
