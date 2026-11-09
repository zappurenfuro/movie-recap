# Movie Recap

[Download the latest release](https://github.com/zappurenfuro/movie-recap/releases/latest)

A skill for Claude Code and Codex that turns a local movie or episode into a full narrated recap and a short Instagram Reel, with separate subtitles, thumbnail frames, and upload copy.

```text
Claude Code: /movie-recap Lucky
Codex:       $movie-recap Lucky
```

The agent reads the footage, writes the scripts, generates voiceovers, edits the videos, and checks the outputs. The installer sets up the skill, an isolated Python environment, FFmpeg, and local voice/recognition models automatically. This is an agent workflow, not a standalone rendering application; Claude Code or Codex must still perform the editing.

## Install

Requires 64-bit Python **3.11, 3.12, or 3.13**, internet access for initial setup, and Claude Code or Codex. Git is only needed for the clone option. On systems where Python is named `python3`, substitute it for `python` below. No administrator access or GPU is required for the default CPU runtime.

Clone this repository and run the installer:

```sh
git clone https://github.com/zappurenfuro/movie-recap.git
cd movie-recap
python install.py --target both
```

Or download and extract the repository ZIP, open a terminal in the extracted folder, and run the last command. Choose one app if preferred:

```sh
python install.py --target claude
python install.py --target codex
```

The installer creates a shared runtime in `~/.movie-recap/runtime-v1`, installs the Python dependencies, downloads Kokoro and Whisper models, and generates a short narrated test video. It installs the skill only after runtime checks pass, and places a `runtime.json` beside each installed `SKILL.md` so the agent knows the exact executable and model paths. It does not modify system PATH, install CUDA drivers, upload your films, or start a movie recap.

Allow roughly **3 GB of free space** for setup, plus separate space for movie editing. Models total approximately 650 MB; package downloads add more. Download size varies by platform. Completed downloads are reused. Interruptions may require restarting a partial file; rerun the same command to continue setup.

| App | Personal install destination | Invocation |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/movie-recap/SKILL.md` | `/movie-recap Lucky` |
| Codex | `~/.agents/skills/movie-recap/SKILL.md` | `$movie-recap Lucky` |

These are the documented [Claude Code](https://code.claude.com/docs/en/skills) and [Codex](https://learn.chatgpt.com/docs/build-skills) skill locations. Reopen your session if the skill does not appear. Codex does not register a custom `/movie-recap` slash command merely from this filename; use `$movie-recap` or its skill picker. Local installation does not automatically install the skill into cloud/Cowork sessions.

For installation in one project only:

```sh
python install.py --target both --project "/path/to/movie-project"
```

To preview destinations without downloads or writes, add `--dry-run`. The installer leaves identical skills unchanged and refuses to overwrite a different skill unless you pass `--update`; updates keep a timestamped backup. Normal runs reuse the runtime, verify model hashes and rerun the smoke checks.

Optional flags:

```sh
# Choose another disk for the shared runtime.
python install.py --target both --runtime-dir "/path/to/movie-recap-runtime"

# Advanced: install only instructions and supply your own tools/models.
python install.py --target both --skill-only
```

`--skill-only` does not verify or remove an existing runtime pointer. A default installation runs the checks again and refreshes it.

### Install through your coding agent

You can also give Claude Code or Codex this installation prompt:

```text
Install https://github.com/zappurenfuro/movie-recap for both Claude Code and
Codex, including all media dependencies and voice/recognition models.
Clone it into an unused local folder, read README.md, and inspect install.py
and runtime_setup.py. Use a supported 64-bit Python 3.11–3.13 interpreter
to run: python install.py --target both
Do not use --skill-only. Run the installer's end-to-end checks and confirm
that both installed skills have a valid runtime.json. If an existing skill
needs updating, use --update to preserve a backup. Do not render a movie yet.
```

For only one app, replace `--target both` with `--target claude` or `--target codex`.

The agent still needs permission to access the repository and write to the relevant skill directory. A GitHub upload alone does not install the skill for other users.

## What setup installs

- An isolated Python virtual environment, separate from global/user packages.
- FFmpeg through the platform-specific `imageio-ffmpeg` wheel; PyAV supplies media probing, so a separate `ffprobe` executable is not required or installed.
- NumPy, Pillow, PyAV, ONNX Runtime, kokoro-onnx, faster-whisper and Hugging Face download support. Primary versions are in `requirements-runtime.txt`; resolved versions are recorded in `runtime.json`.
- The Kokoro v1.0 ONNX model and voice data, with `am_michael` selected by the skill. Both downloads have pinned SHA-256 checksums.
- A pinned multilingual Whisper base model for source-film dialogue and an English base model for narration alignment. The default narration is English. Speech-recognition results still need checking against the actual footage and available subtitles.

The installer checks TTS output, H.264/AAC encoding and decoding, English word timing, and multilingual-model loading with an English test sentence. It records successful setup in `runtime.json`; it does not claim to test every language.

Use a local agent session with shell execution and access to the movie folder. A GPU is optional; CPU processing is slower but requires no CUDA setup. The skill must use the installed runtime paths rather than asking you to activate its environment manually. Paid services are not used by this installer.

### Platform notes and troubleshooting

End-to-end setup has been tested on Windows x64 with Python 3.13. The installer uses portable Python code and dependency wheels for other supported platforms, but macOS and Linux have not been end-to-end tested here. Unsupported architectures or missing dependency wheels produce an installation error instead of a false success.

- If Python is missing or outside 3.11–3.13, install a supported 64-bit Python first. The installer cannot install the interpreter that runs it.
- If Linux reports that `venv`/`ensurepip` is missing, install your distribution's Python venv package, then rerun. No privileged OS-package changes are attempted automatically.
- If GitHub, PyPI or Hugging Face downloads fail, check your connection/proxy and rerun the same command. A failed runtime check prevents this run from changing installed skills; completed files remain available for retry.
- If an existing skill differs, use `--update` to preserve a backup and install the new version.
- Keep the shared runtime folder in place after installation. Moving it makes its saved paths stale; rerun with the desired `--runtime-dir` to install and register that location.
- If you installed only a standalone `SKILL.md` through another tool, rerun this repository's installer for automatic dependency setup.

Models and binaries are downloaded from their upstream sources; they are not bundled into this repository. Their respective licenses apply. Source references: [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx), [Kokoro model](https://huggingface.co/hexgrad/Kokoro-82M), [faster-whisper](https://github.com/SYSTRAN/faster-whisper), [Whisper base](https://huggingface.co/Systran/faster-whisper-base), and [imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg).

## Use

Open your movie project in the app, for example:

```text
movie-project/
  Lucky.mkv
  Lucky.en.srt   # optional source subtitles
```

Then enter `/movie-recap Lucky` in Claude Code or `$movie-recap Lucky` in Codex. You can also supply a quoted full video path. If several episodes match the title, the agent asks which episode rather than choosing arbitrarily.

Both formats are generated by default. To request only one:

```text
/movie-recap Lucky full only
/movie-recap Lucky reel only
```

Use `$movie-recap` for the equivalent Codex requests. The source stays unchanged, and another run uses new output folders rather than overwriting a previous edit.

## Fresh content and reusable production code

Each new recap uses fresh source analysis, newly written scripts and newly generated narration. The workflow reuses compatible production code, installed models and tools rather than rebuilding them for every movie. An explicitly requested revision may retain unaffected content.

Independent work can overlap: transcription with visual sampling, approved narration synthesis with shot inspection, and thumbnails or draft upload copy with rendering. Picture timing still follows measured speech. Same-run retries may reuse verified unchanged results; previous movie analyses, scripts and voices are not a shortcut for a fresh run.

The installer includes `scripts/run_jobs.py`, a dependency-aware command runner with bounded concurrency, exclusive resource labels, logs and timings. See [production guidance](references/production.md) for its manifest and limitations. It schedules media helpers supplied by the agent; it is not a complete automatic editor. Existing compatible media helpers should be reused before writing missing logic. Export settings, narration pacing and verification requirements are preserved; no fixed production time is promised.

## What you get

**Full recap:** at least ten minutes, complete story coverage, measured 1.10x narration, 1920 x 1080 output, noncontinuous clips of at most three seconds, occasional stable hard-zoom holds, and no original-film audio. Default picture styling includes a final centered 1.10x zoom and horizontal flip. These are editing choices, not copyright clearance. No logo or burned-in captions.

**Reel:** 45–75 seconds, calmer moving shots, original aspect ratio and orientation, consistent narration, and a cutoff before the climax's outcome. Includes matching versions with and without narration. No promised second part.

```text
Lucky-Full-Recap/
  Lucky-recap-with-narration.mp4
  Lucky-narration-TTS.srt
  Lucky-captions-display.srt
  youtube-upload.txt
  thumbnails/
    thumbnail-01.png
    thumbnail-02.png
    thumbnail-03.png

Lucky-Reel-Recap/
  Lucky-recap-with-narration.mp4
  Lucky-recap-without-narration.mp4
  narration.txt
  Lucky-narration-TTS.srt
  Lucky-captions-display.srt
  instagram-copy.txt
```

TTS subtitles use natural speaking phrases; display subtitles use short readable cues without changing the narration. YouTube copy includes titles, description, chapters, tags, and thumbnail notes. Instagram copy includes a description, hashtags, and optional on-screen hooks. Thumbnails are three actual film frames cropped to 1280 x 720.

Quiet separate music may be included. The optional Undertow credit block is supplied for users who manually add that song; the song itself is not bundled or automatically inserted.

## Updating and customization

After reviewing a newer revision:

```sh
git pull --ff-only
python install.py --target both --update
```

Edit `SKILL.md` to change the workflow and rerun the installer with `--update` to synchronize installed copies. Edit the full and Reel sections separately so settings do not leak between formats. Keep your media and generated exports outside this repository.

The agent verifies decoding, timing, subtitle preservation and sampled scene alignment, and reports any review limitations. Review the final videos before publishing. This skill does not automatically upload videos or submit copyright disputes.

## Repository contents and testing

Publish `SKILL.md`, `README.md`, `install.py`, `runtime_setup.py`, `requirements-runtime.txt`, `.gitignore`, `scripts/`, `references/`, and `tests/`. The installer copies the skill and its scripts/references into each selected app. Do not upload your installed runtime, runtime.json, models, media, or Python cache files.

Run the offline installer checks with:

```sh
python -m unittest discover -s tests -v
```

The normal installer performs the separate real model-download, narration, encoding, decoding and recognition checks. Tests that mock downloads are not a substitute for that end-to-end setup.
