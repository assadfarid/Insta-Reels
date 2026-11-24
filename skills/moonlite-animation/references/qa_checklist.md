# QA checklist (what the user actually caught, so check it first)

## Story continuity
- Does each shot show what the narrator says right now? Action lands on the phrase, not before.
- Who is in the room? (She calls "Echo?" → he must not be visible. He sits down → don't cut back to him standing.)
- Props in the right place and only after they exist (drawing taped on chest after "Now we're a family").
- No extra/duplicate characters or shadows; no new rooms mid-clip.
- Character design consistent (antennas, head shape); faces never drawn on the back of a head.

## Bubbles
- Every bubble belongs to the speaker: beside their face on the side they face, never nearer another character.
- Never covers any face; tail short, slim, points down to the speaker's mouth; nothing cut off at screen edges.
- Off-screen voices (radio) come from the device.

## Motion
- No frozen first/last frames, no back-and-forth rocking, camera always drifts a little.
- Slowed clips: check fast movements for interpolation smear.
- Title, chapter, end and credits cards over moving blurred video.

## Sound
- Music ducks under speech; no rise after "The End" into the credits; fade only at the very end.
- Sad chapters use a sadder theme; check levels by measuring RMS per 2 s around transitions.

## Branding and text
- Watermarks of every generator removed (Veo text, Gemini sparkle) — scan the corners of every clip.
- Fonts: show options sheets; this user chose Amatic SC golden brush for thumbnails/brand, Fredoka for bubbles.
- Title on one line, vertically centred; spacing between title and tagline.
- Credits: name once, real roles only.

## How to check cheaply
- Render 4–12 stills at the exact times (`render.py 0 1 --stills ...`) and tile them; read the tile once.
- For the finished file, grab frames with ffmpeg `-ss` from the HQ/4K output, not from test renders.
- Report honestly what was and wasn't checked.
