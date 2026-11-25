---
name: moonlite-animation
description: End-to-end workflow for turning a written story into a narrated, illustrated, animated YouTube film (watercolour storybook style, narrator + character voices, speech bubbles, karaoke subtitles, AI video clips from Gemini/Veo, Flow or Kling, 1080p/4K render, brand kit, thumbnail and YouTube launch). Use this skill whenever the user wants to make an animated story, bedtime story, kids story, short film, story video or "BBC-style" narrated animation from a story or script — or is in the middle of one and asks for clip prompts, speech-bubble fixes, re-renders, watermark removal, thumbnails, channel branding, Shorts, or YouTube upload settings for it — even if they don't say "skill" or name the steps.
---

# Moonlite Animation

This skill captures a pipeline that produced an 11-minute animated film ("The Robot That Learned to Lie",
reference implementation in `story/` of the Insta-Reels repo) from a plain story text. The user drives the
creative choices and generates AI video clips in their own Gemini/Flow/Kling accounts; you do everything else
locally with Python, OpenCV, PIL and ffmpeg.

Read the reference file for the phase you are in — don't load all of them up front:

| Phase | Read |
|---|---|
| Script, voices, timeline, rendering, re-rendering, file formats | `references/pipeline.md` |
| Writing prompts for AI clips / start & end frames, handling refusals | `references/clip_prompts.md` |
| Checking a render, fixing what the user reports | `references/qa_checklist.md` |
| Thumbnail, channel brand kit, title/description, upload, Shorts | `references/youtube_launch.md` |

## The phases (in order)

1. **Agree the brief.** Story text, aspect ratio (16:9 for YouTube), language, narrator + character voices,
   visual style (calm watercolour storybook works well), target audience age. Ask once, then go.
2. **Script.** Split the story into scenes `sNN`; each line is `(scene, speaker, text-with-voice-tags, hud)`.
   Chapter cards are silent (the user disliked a narrated "Chapter One").
3. **Illustrations.** One key image per scene from a shared character reference sheet so faces stay consistent.
4. **Voices.** One take per chapter and speaker (cheaper and more consistent), split back into line files.
   A deep, calm narrator voice was the user's preference.
5. **Timeline.** Lines → timed shots, with emotional pauses kept, a 5-second **hook** (the story's central
   question) before the title, short chapter-title overlays, a separate "The End" card, then rolling credits.
6. **First render** with only stills + motion (camera moves, parallax, breathing, blinks, light effects,
   particles, environment motion, sound effects). Show stills before long renders.
7. **AI clips.** Give the user one start picture + one copy-paste prompt per scene (see `clip_prompts.md`),
   most emotional scenes first. When clips arrive: inspect frames, remove watermarks, sync the key action to
   the narrated phrase, retime so the clip fills its scene playing forward only, place speech bubbles, quick
   re-render the affected 30-second pieces.
8. **QA loop.** The user watches and reports problems; fix them in batches (see `qa_checklist.md`).
9. **Masters.** 1080p master, a <500 MB HQ copy for chat delivery, 4K upscale (HEVC) split into ~300 MB parts
   with a `copy /b` join command and SHA-256 checksum.
10. **Launch.** Brand kit, thumbnail options, title/description/tags, audience settings, Shorts.

## Working agreements that mattered to this user

- **Be careful with their usage.** Each render and image check costs. Batch changes, re-render only the
  affected 30-second pieces (`render_quick.py`), spot-check a few frames instead of full contact sheets unless
  asked, and keep replies short. Long encodes run in the background; tell the user the honest ETA.
- **Show before rendering.** For visual decisions (bubbles, fonts, title cards) render 2–6 stills or an
  options sheet and let the user pick; they often reject the first design ("I didn't like the font").
- **No credits to third-party generators unless asked.** The user generates clips/images in their own tools;
  you write prompts and process what they send back.
- **Story logic beats pretty pictures.** Every clip must match what the narrator says at that moment
  (action timing, who is in the room, what objects exist yet). Reject or trim clips that contradict the story
  and say why.
- **Honesty in credits and metadata.** Credit real roles once (the user disliked their name repeated); don't
  invent team members. Removing the word "AI" from credits is fine, but the YouTube "altered content" box and a
  line in the description keep the disclosure honest. "Made for kids" is a legal audience setting, not a growth
  lever — set it by the real audience, and explain what it disables (comments, end screens, bell).
- **Deliver files the user can actually get.** Files only live in the cloud session; send them in chat
  (<500 MB, ~450 MiB fails), commit code to git, keep media out of git, and give exact PowerShell commands for
  their Windows folder.
- **Commit and push after each change** to the working branch; media/outputs go in `.gitignore`.

## Quick rules of thumb

- Bubble placement: anchored to the speaker's mouth, beside the face on the side they face, never covering any
  face, never nearer another character than the speaker, short slim tail pointing down to the mouth.
- Clips never freeze or rock back and forth: retime forward-only with motion-interpolated in-between frames.
- Ducking: music dips under speech, but from "The End" on hold it steady and only fade at the very end.
- Title cards and end cards sit over softly blurred moving video, never a still.
- Thumbnails: big emotional faces + a short curiosity hook; the title should add what the thumbnail doesn't say.
