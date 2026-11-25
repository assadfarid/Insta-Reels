# The Robot That Learned to Lie - running the project on your PC

## 1. Get the code (GitHub)
Open PowerShell (or Git Bash) in the folder you want, e.g. `D:\ClaudeDesignPro\AI Video Editor`:

    git clone https://github.com/assadfarid/Insta-Reels.git "The Robot That Learned to Lie"
    cd "The Robot That Learned to Lie"
    git checkout ccr-b636e929-ljheeo
    cd story

## 2. Add the media (not in Git - too large)
Download the three zip files from the Claude chat and extract **all three into the `story` folder**
(choose "Extract here" so the `assets` folder merges):

- `robot_media_1_images.zip`      -> assets/img (the 55+ illustrations)
- `robot_media_2_clips_audio.zip` -> assets/clips, assets/lines (voices), assets/audio_raw (music), assets/fonts, assets/refs
- `robot_media_3_retimed.zip`     -> assets/retimed (slowed, interpolated clips)

## 3. Install the tools (once)
    winget install Python.Python.3.12
    winget install Gyan.FFmpeg
    pip install -r requirements.txt

Close and reopen the terminal afterwards so `python` and `ffmpeg` are found.

## 4. Rebuild audio, then render
    python sfx.py
    python mix_audio.py
    python render_quick.py all        # full render in 30-second pieces -> out/The_Robot_That_Learned_to_Lie_1080p.mp4

Small changes later: `python render_quick.py 170,190` re-renders only 2:50-3:10 and rebuilds the video.
After changing a clip: `python retime.py s14` first, then the quick render for its time range.

## 5. Working with Claude Code on the PC
Open the Claude desktop app > Code, choose this local folder, and ask for changes as before.
Commit and push from there (`git add`, `git commit`, `git push`) - media stays out of Git (see .gitignore).
