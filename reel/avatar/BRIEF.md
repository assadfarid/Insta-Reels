# Avatar presenter reel: brief (handoff for a fresh session)

## Goal
A ~40 s vertical Reel (1080x1920) where a **male AI presenter built from the owner's own photos**
explains "How I built the Jorge Dan site", in the style of the reference reel
(talking head at a desk, floating screen cards above the head, word-by-word captions,
final CTA "Comment WORKFLOW").

## Reference reel (what to match)
- 720x1280, 53 s, loudness about -14 LUFS.
- Presenter at a wooden desk with a laptop, curtain backdrop, speaking to camera.
- Floating UI cards (website screenshots) appear above her head and swap as she explains.
- Bold word-by-word captions; the key word is set larger in a serif italic ("like *this*").
- Ends with "Comment <keyword>" and a pill-shaped keyword tag.

## Decisions made
- Presenter route: **AI avatar from photos** via the Creative Claw plugin (create-avatar, clone-voice / generate-voiceover),
  using only the owner's own likeness and voice. Photos are NOT committed to the repo; ask the owner to re-upload them.
- Topic: how the Jorge Dan site (https://jorgedan.launchforge.studio) was built.
- Best photos: the olive-tee selfies (best light); desk setup has a black/red GLOBAL gaming chair.

## Draft script (approve language EN/ES and check facts before generating)
1. "This luxury real-estate site took me days, not weeks. Here's the workflow."
2. "First, I start from the client's voice, not from a template."
3. "Then I design the sections: a manifesto, four projects and a private consultation form."
4. "I build it natively in WordPress, so the client can edit everything."
5. "Then I test it on a phone, because that's where buyers look first."
6. "Want the exact workflow? Comment WORKFLOW and I'll send it."
(Confirm the "days, not weeks" claim and workflow steps are accurate before publishing.)

## Plan
1. Sign in to Creative Claw (plugin Connectors tab). Network host app.creativeclaw.co is allowed in the `insta-reels` environment.
2. Create the avatar + character sheet from the photos; get approval; set voice (cloned with consent, or designed).
3. Generate the talking-head clip(s) per script line at 9:16.
4. Composite in Remotion (`reel/`): captions, floating site cards (captures in `reel/public/jd/`), CTA, music.
   Reuse `reel/src/jd/*`, `reel/audio/make_music.py` (original music), and the render notes in the repo.
5. Render with: REMOTION_BROWSER_EXECUTABLE=/opt/pw-browsers/chromium npx remotion render <Comp> out/<name>.mp4

## Environment notes
- Remotion cannot download its own Chrome here; use /opt/pw-browsers/chromium.
- Other plugin hosts (manymotions.com, mcp.aitopia.ai) are NOT allowed; add them only if needed.
