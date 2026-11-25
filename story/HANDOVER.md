# Handover - The Robot That Learned to Lie (Moonlit Tales)

State: film finished (10:57, rated 9.8/10), uploaded-ready. This file tells a new Claude session where things are.

## Pipeline (all in story/)
- script.py            - every line: (scene, speaker, text with voice tags, HUD text)
- timeline.py          - builds timeline.json (shots, lines, HUDs, music, hook, chapter overlays, The End card)
- word_times.py        - per-word timing for the karaoke subtitles
- sfx.py / mix_audio.py- procedural sound effects; final mix -> assets/mix.wav (music tracks: gentle / hopeful / sad)
- render.py            - frame renderer: camera moves, AI clips, colour match, effects, captions, title cards
- captions.py          - narrator subtitles + speech bubbles (placement rules, faces2.json / mouths.json)
- retime.py            - makes forward-only slowed copies of each clip that fill its scene (assets/retimed/)
- render_quick.py      - renders 30 s pieces (out/chunks/) and joins them: `python render_quick.py 170,190`
- make_srt.py          - subtitles + YouTube chapter times
- brand/               - Moonlit Tales logo, banner, intro/end cards, thumbnails (make_brand2.py, make_thumb2.py)

## Media (not in Git - from the 3 zips)
assets/img (illustrations), assets/clips (AI clips s01..s56), assets/lines (voices), assets/audio_raw (music),
assets/retimed (slowed clips). assets/mix.wav and sfx.wav are rebuilt by sfx.py + mix_audio.py.

## Typical changes
- New clip for scene sNN: put it in assets/clips/sNN.mp4 (remove watermarks first: Veo text bottom-right,
  Gemini sparkle at about x1692 y852 98x98 on 1920 clips), add/adjust SYNC in render.py, then
  `python retime.py sNN` and `python render_quick.py <start>,<end>` for its time range.
- Bubble in the wrong place: edit faces2.json / mouths.json for that scene (fractions of the frame), quick render.
- Timeline/script change: python timeline.py, word_times.py, sfx.py, mix_audio.py, make_srt.py, then
  `python render_quick.py all`.
- 4K: ffmpeg upscale of out/The_Robot_That_Learned_to_Lie_1080p.mp4 (lanczos + light unsharp, HEVC crf 21).
