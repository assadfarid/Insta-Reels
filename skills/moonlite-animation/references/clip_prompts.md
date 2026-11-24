# Prompts for AI clips (Gemini / Veo, Google Flow, Kling)

## Deliver them so the user can copy them
The user often works on a phone. Put each prompt in its own fenced code block (copy button), send the start
picture as a file with the scene name, and say where to use it. Number prompts in story order; tell them how to
name the result (`sNN.mp4`) and to send a batch in one message.

## Prompt template (worked best)
```
A gentle watercolour illustration comes to life: <one or two concrete actions, in order, with who does what>;
<one environmental motion: light flicker, dust, wind, birds, sparks>. <Continuity constraints: who is NOT
there, objects that must stay where they are, robot has no antennas, etc.> Keep the exact hand-drawn
watercolour storybook style and the same characters. Slow, subtle motion, static camera, no text, no new
characters, no scene change.
```
- Say "metal helper" instead of "robot" and avoid film-like phrasing: fewer refusals.
- One clear direction of movement ("moves only toward the girl, never away") prevents sloppy wrong-way steps.
- For fast action ask for it explicitly ("runs fast, leaning forward, arms swinging"); otherwise you get a stroll.
- For scenes seen from behind: "only the plain back of the helper's round head, no face and no eyes".

## Pick scenes in this order
1. Scenes that are still pictures and carry the biggest emotional beats (the lie, the confrontation, the
   sacrifice, the goodbye, the reunion).
2. Long still scenes.
3. Redos of clips with continuity errors (object in the wrong place, extra character, wrong design).

## Fix the start picture before prompting
Animation copies whatever is in the first frame. Check it against the story moment: who is in the room, where
props are (e.g. a drawing taped on the chest, not on a door), faces drawn on the back of heads, scale of
characters. Edit with PIL/OpenCV (crop someone out, move/resize an object, paint over a face) or ask the user
to regenerate it. If the edit leaves a smeared patch, use another scene's picture of the same moment instead.

## Start + end frame (Kling)
Write an image-edit prompt for the end frame from the start picture ("Edit this exact image… change only
this…"), then the video prompt. Gemini/Flow take only a start picture.

## Refusals ("third-party content providers")
Gemini sometimes blocks a robot picture as resembling a known character, and keeps refusing in that chat.
In order: new chat → simpler, gentler prompt → closer crop of the picture → **Flow** (accepted the same
pictures) → wait a day. Don't burn the user's usage retrying the same chat.

## Inspecting returned clips
Common problems seen: a second copy of the girl in the background, a shadowy figure in a doorway, a door
opening behind someone, props appearing a scene early (microphone), the robot gaining antennas, the head
turned backwards while walking, a background turning into a different room after 2 s, the camera zooming in
hard. Decide per clip: use, trim, crop/paint out, or reject with a precise redo prompt.
