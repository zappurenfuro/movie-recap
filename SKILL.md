---
name: movie-recap
description: Create a full narrated movie recap and a short Instagram Reel from a user-supplied local film or episode, including subtitles, thumbnails, and upload copy. Use when asked to run movie-recap or produce these recap packages from local footage.
---

# Movie recap

## Invocation and default scope

Claude Code: `/movie-recap Lucky`.
Codex: `$movie-recap Lucky` (or select this skill in the host's skill picker).
A quoted video path or folder also works. Read the title/path and optional scope from the invocation message. Claude Code arguments: $ARGUMENTS. If that token is not expanded by the host, use the user's actual message, not the literal token as a filename.

Default: finish BOTH the full recap and the Reel, including the files below. Treat this as an instruction to execute the work, not just write a script, outline, or editing plan. Full-only or Reel-only applies only when the user explicitly requests it. Do not start rendering merely because someone asks to inspect, install, explain, or modify this skill.

This file contains both current recap templates, consolidated without obsolete preference history. Full-only editing rules must never leak into the Reel. Explicit current user instructions override these defaults. Do not change the source templates or other movie projects during a normal run.

## Resolve the input

1. Start in the user's selected project folder. Search for supplied local video files (`.mkv`, `.mp4`, `.mov`, `.m4v`, `.webm`, `.avi`) and sidecar subtitles. Prefer an explicit supplied path. For a title such as Lucky, match filenames and relevant subfolders, ignoring punctuation/case and common release suffixes.
2. Exclude previous recap exports, trailers, samples, thumbnails and temporary work from source selection. Probe candidate media before choosing; do not pick a file merely because it is longest. Verify identity from footage, credits and subtitles.
3. If there is exactly one plausible source for the requested title, proceed without asking. If Lucky matches multiple episodes, or two different films remain plausible, ask one concise question identifying the candidates. Do not silently combine episodes or select an arbitrary one. With no title, use the sole clear source; otherwise ask. If no source exists, report where you looked and request its path. Do not download a film automatically.
4. Keep the source unchanged. Create new `<Title>-Full-Recap` and `<Title>-Reel-Recap` folders beside the source. If either already exists, choose a consistent unused `-Edit-2`, `-Edit-3`, etc. pair rather than overwriting previous work. Use the episode identifier in names when applicable.
5. Create a scoped task work folder outside the final folders. Read applicable project instructions, but keep the two mode contracts separate. Do not overwrite an unrelated existing AGENTS.md. If project instructions need persisting, keep them at the source root or within a separate task workspace, not among lean final outputs.

## Tools, voice and actual execution

### Automatically installed runtime

Before searching global tools, read `runtime.json` next to this installed SKILL.md. Follow its `manifest_path` and reread the shared manifest; require `status: ready`. Use its absolute `python`, `ffmpeg`, `kokoro_model`, `kokoro_voices`, `source_whisper_model` (multilingual source-film recognition), and `whisper_model` (English narration alignment) paths. These paths remove any need for users to activate a virtual environment or locate models manually. Use PyAV from this Python environment for probing; the installer does not provide a separate ffprobe executable. Prefer CPU by default and only use an available GPU after verifying it works.

If the pointer is absent, also check `~/.movie-recap/runtime-v1/runtime.json`, then perform the portable discovery below. If the shared manifest is absent, stale, or not ready, explain the actual setup error and direct the user to run this repository's `python install.py --target claude` or `--target codex` (with `--update` when replacing a skill). If the user has asked you to set up dependencies and the repository is available, run the installer yourself. Do not report a successful setup merely because a manifest file exists; check the referenced executables/models. Never include runtime.json in a public repository because it contains machine-specific paths.

This is an agent workflow, not a standalone video-rendering program. Use available shell/file tools to author and run the needed editing code. Discover FFmpeg/ffprobe (or PyAV probing), Python, a TTS engine and ASR/alignment tools. Probe a short encode before committing to a long render. Use compatible CPU encoding if NVENC is unavailable. Never claim a completed video when only text instructions were produced.

Default narrator: local Kokoro `am_michael`, English, synthesized at 1.00x. Full: apply exactly one `atempo=1.10` adjustment. Reel: prefer 1.00x, shorten the script before considering up to 1.30x. Do not silently switch voices between outputs or claim an exact Instagram voice. Reuse installed models; ask before paid services. If required local execution or a usable voice is unavailable, report the specific blocker without pretending a standalone SKILL.md installs those capabilities. The repository installer provides automatic setup.

Portable dependency discovery:
- Locate Python and FFmpeg/ffprobe from the active environment or user-supplied paths. If installed, `imageio_ffmpeg.get_ffmpeg_exe()` can locate an FFmpeg binary.
- Locate the Kokoro ONNX model and voice data from the user's installed TTS environment. Do not assume a particular username, download folder or operating system. If the files are missing, report the required assets and ask for their paths or permission for setup as needed.
- Look for cached faster-whisper models in the current user's Hugging Face cache or a user-specified model directory. Probe CUDA support and fall back to CPU when needed.
- Discover equivalent local tools on each machine. Do not package model weights, API credentials, or film footage with this skill.

## Shared production workflow

1. Probe source streams, duration, active dimensions, frame rate, audio language and subtitles. Read dialogue and sample the entire story including its ending. Use local ASR if usable subtitles are missing; visually verify important actions rather than trusting ASR guesses. Distinguish dreams, flashbacks, legends and uncertain outcomes from actual events. Web research may corroborate film identity/year; never replace footage analysis with a plot guess.
2. Write plain, specific English narration with accurate cause and effect. Avoid AI slogans, stacked dramatic fragments, invented dialogue and repetitive filler. Build a source-time map with exact passages for each narrated event. Full covers the complete story. Reel establishes context and stops at the beginning of the climax, with its own script and spoiler cutoff.
3. Synthesize complete paragraphs or natural sentences, not short display-caption fragments. Join them into continuous narration with natural breathing pauses. Measure the actual adjusted speech, then build the picture timeline. Preserve syllables and don't stretch audio to fit arbitrary shot durations.
4. Align words to the generated voice. Audit omissions, proper names and unexpected speech. With faster-whisper, avoid supplying the entire expected script as `initial_prompt`; it can hallucinate words or skip openings. If audio decoding fails because of a PyAV API mismatch, use FFmpeg to decode mono 16 kHz PCM and pass a NumPy array to Whisper. Inspect low-confidence results instead of accepting fabricated word timestamps.
5. Keep a temporary edit manifest containing source in/out, output start/end, narration phrase anchors, freeze points and transforms. Place named actions at their spoken phrase or slightly before. Inspect intermediate action frames and rendered shot boundaries. Never cover 'they kiss' with a frozen hug or 'searching CCTV' with an unrelated shot until several seconds later.
6. Render the full recap using Part A, then the Reel using Part B. Reuse source analysis, not the full recap's transformed picture. Keep timing frame-accurate with a consistent CFR, explicit frame counts and concat durations. Check cached renders against current script, source selection and settings; invalidate changed clips instead of reusing stale files.
7. Mix clear narration with a quiet separate appropriate bed. A restrained original synthesized underscore is acceptable. Do not add Undertow automatically. Explicit audio mapping must exclude all film audio from the full export. Use H.264 High, yuv420p, CFR, square pixels, AAC-LC stereo (48 kHz is suitable), and MP4 faststart for both modes.
8. Generate natural-phrase TTS SRT and short display SRT independently from the same narration words and measured timings. Use the shared subtitle rules from Part A for both; its no-original-audio/full-only export restrictions do not override Part B. Preserve every word, punctuation and order. Supply upload copy and thumbnails as specified.
9. Validate complete decoding, expected frame count/duration, dimensions, codec profile, audio headroom, nonoverlapping SRT timing and exact script reconstruction. Audit every full clip's total duration and noncontinuous source selection. Compare the two Reel picture streams/timings. Inspect thumbnails and selected narrated actions. Review representative motion with audio when available; stills and metadata alone do not prove smooth playback. Report any unavailable normal-speed listening/watch pass honestly.
10. Only after verification, clean task-generated temporary files using an explicitly verified path within the task project. Preserve sources, previous edits, shared tools/models, instructions and deliverables. Do not remove shared caches. If cleanup is blocked by the host, do not retry through another shell or language to bypass the block; report the retained location and reason. Never publish, upload or dispute claims without explicit authorization.

## Final package contract

Replace `<Title>` with the verified film/episode label. Default delivery has THREE MP4s total: one full and two Reel versions.

```text
<Title>-Full-Recap/
  <Title>-recap-with-narration.mp4
  <Title>-narration-TTS.srt
  <Title>-captions-display.srt
  youtube-upload.txt
  thumbnails/
    thumbnail-01.png
    thumbnail-02.png
    thumbnail-03.png
<Title>-Reel-Recap/
  <Title>-recap-with-narration.mp4
  <Title>-recap-without-narration.mp4
  narration.txt
  <Title>-narration-TTS.srt
  <Title>-captions-display.srt
  instagram-copy.txt
```

Do not create a full-recap no-narration video or empty original-audio SRT. Full upload copy is mandatory in this combined workflow, not optional. Do not add a logo, watermark or channel branding unless the user explicitly requests it and supplies the asset. A single SKILL.md carries all editorial instructions; locally available rendering and voice tools are still needed.

## Part A — Full recap

## Default full-recap style: clean noncontinuous editing

- Apply the clean noncontinuous editing rules below to full recaps only. The Reel uses its own picture and pacing rules.
- Each visual clip must be at most 3.00 seconds in total, INCLUDING its moving footage, end-frame freeze and zoom. Three seconds is a ceiling, not a requirement to make every shot exactly three seconds.
- Use genuinely noncontinuous excerpts from the scene relevant to the narration. For example, a 60-second narrated section about a ten-minute film scene should draw short excerpts from separated moments of that scene, not sixty consecutive seconds disguised as adjacent three-second cuts. Keep the cause and effect understandable, and show each named action when it is narrated; do not insert unrelated footage just to create a gap.
- Add occasional purposeful hard-zoom freezes, with no shake. Preserve natural source colors and exclude all frying effects. Mute all original-film audio in the final export.
- Keep the existing minimum ten-minute duration, 1.10x narrator rate, final centered 1.10x crop and whole-video flip, one narrated export, useful separate subtitles, thumbnails and upload package unless explicitly changed by the user.

## Inputs and output location

- Identify the actual movie from the supplied footage, credits, and available subtitles. Do not rely on a filename alone or confuse similarly titled films.
- Preserve the source media unchanged.
- Create a new, clearly named output subfolder inside the movie's source folder. Do not overwrite a previous edit without instruction.
- Reuse available local tools and models. Ask before incurring new paid service charges.
- Do not edit standing preferences during an ordinary render. If the user requests a preference change, update this skill and any installed copies you can verify, plus explicitly linked project templates where applicable. Preserve unrelated instructions.

## Duration and pacing: mandatory

- The finished recap must be AT LEAST 10:00 long. Ten minutes is a floor, never a target or upper limit.
- Prioritize clear, relaxed narration and enough time to understand each scene. A 15-, 20-, or 30-minute recap is acceptable when the story needs it.
- Use the required 1.10x narration rate; do not accelerate further, rush cuts, remove necessary context, or compress the ending to fit ten minutes.
- Do not pad the runtime with repetition, dead air, or irrelevant footage. Expand useful explanation and allow purposeful pauses.
- Keep delivery natural at the required 1.10x narration rate, with clear phrasing and breathing pauses. Do not force an identical words-per-minute rate across sentences.
- Keep narration relaxed while covering each idea with relevant noncontinuous clips of at most three seconds each. Do not speed up speech to fit a single clip; use additional relevant excerpts. Choose understandable moments rather than cutting mechanically every second.

## Narration and audio speed: mandatory

- Every speech/audio speed adjustment must remain between 0.90x and 1.10x, inclusive, relative to the original generated or recorded audio.
- The cumulative effective speed must also remain within that range. Never stack compliant-looking operations to exceed the limit.
- Full-recap narration must use a cumulative effective speed of 1.10x relative to the unadjusted generated voice. Generate naturally at 1.00x and apply one 1.10x tempo adjustment, or an equivalent single adjustment; never stack beyond 1.10x. This replaces the previous preference for 1.00x or slower narration. Original-film audio is excluded from the exports.
- If narration outlasts a clip, extend the narration window and cover it with more relevant noncontinuous clips, each within the three-second limit. Do not force the voice to fit.
- Never trim spoken words or final syllables to meet a timestamp. Measure actual audio lengths and leave natural breathing room.
- Keep voice identity, rate, loudness, and delivery consistent. Use punctuation and deliberate pauses for expression.
- Verify and record any applied speed changes, including synthesis rate and postprocessing. When available, audit generated speech for omitted words and pronunciation problems.
- Use quiet appropriate music below the narrator. Keep music separate from the voice while working, but remove temporary stems after verification unless requested as deliverables.
- Exclude ALL original-film audio from the final export: dialogue, music, ambience, screams and sound effects. Do not insert original-audio breaks or leave silent interludes intended for them. The narrated export contains narration plus the separate music bed. This replaces all earlier original-audio quotas.

## Final deliverables: one narrated video and a lean folder

- Deliver exactly ONE final MP4: `<Movie>-recap-with-narration.mp4`, with finished picture, narration and quiet separate music. No original-film audio.
- Do not generate or retain a no-narration MP4, preview, standalone picture export, alternate resolution or duplicate final video unless explicitly requested.
- Keep only useful final assets: the narrated MP4, narration-TTS.srt, captions-display.srt, youtube-upload.txt (including chapters, optional music credit and thumbnail source notes), and three thumbnail pictures. Keep project AGENTS.md at the source-project root rather than duplicating it inside the deliverable folder.
- Do not deliver an empty original-audio SRT, original-audio timing file, redundant narration TXT, separate chapter file, audio stems, render scripts, debug logs, contact sheets, intermediate videos or duplicate reports by default. The narration-TTS SRT already preserves the script. Put any necessary brief verification/usage notes in the handoff or clearly separate editing notes inside the upload package.
- Use a clearly scoped temporary work directory during creation. After the final export and useful assets have passed verification, remove task-generated temporary clips, audio, caches and other unnecessary work files. On Windows, verify the resolved absolute cleanup target is inside this task's project directory before using native PowerShell Remove-Item with -LiteralPath. Preserve source media, the project instructions, useful final assets, previous user edits and unrelated files. Do not clean other projects without authorization.
- This lean-output rule applies to full recaps only. Reel deliverables continue to follow the separate Reel template.

- No burned-in captions. Do not add logos, watermarks, branding, decorative title cards, persistent chapter headers or presentation-style text without a request.
- Export editor-compatible MP4: H.264 High, 8-bit yuv420p (4:2:0), constant frame rate and AAC-LC stereo. Explicitly set the pixel format; do not deliver H.264 High 4:4:4. Verify the encoded format as well as successful decoding.
- Final full-recap videos must be exactly 1920 x 1080 (16:9 canvas). Preserve the footage's proportions: apply the established picture crop/zoom and whole-video flip to the active image, then fit it inside the canvas with black letterbox bars above/below when needed. For 1920 x 804 footage, use 138-pixel black bars at both top and bottom. Never stretch the picture or crop it to fill 16:9. These bars are for aspect-ratio preservation, not a separate caption band. Reels and standalone thumbnail rules are unchanged.

## TTS-first SRT for Subtitle Edit / EdgeTts

- Supply one complete, valid, UTF-8 `.srt` file, sequentially numbered, containing the full authored narration in the original speaking order.
- Preserve exact wording; do not omit or summarize text while creating subtitles.
- Prefer complete sentences or natural speaking phrases. Split long sentences only at logical breathing points where each segment sounds natural independently.
- Never fragment a sentence into individual words or disconnected short clauses. Combine very short complete sentences with neighboring narration when appropriate.
- Aim for roughly 2–7 seconds per entry; longer entries are acceptable for natural delivery. Do not enforce display-caption character limits or frequent line breaks.
- Use punctuation to guide intonation. Keep each speaker separate; do not mix speakers in a cue.
- Base timings on actual generated audio where available. Before synthesis, use a realistic relaxed reading-rate estimate with breathing time; revise the timeline after synthesis rather than forcing audio into estimates.
- Keep ordinary continuous-speech gaps approximately 0–200 ms. Use longer gaps only for deliberate narration pauses and transitions, not original-audio breaks.
- Require positive cue durations, sequential timestamps, and no overlaps. Check that reconstructing all SRT text reproduces the entire narration exactly.
- Do not include effect labels, music labels, or original-film dialogue in the narrator's TTS SRT. Do not reserve gaps for original-film audio.
- Explain when relevant that a different EdgeTts voice can change durations; recheck alignment. Do not create an unrequested no-narration export.

## Story and visual editing

- Ground the script in the supplied film's subtitles, dialogue, and actual footage across the full story, including the ending. Check critical actions visually and distinguish interpretation from explicit plot events.
- Use plain, specific sentences. Avoid generic dramatic slogans, manufactured suspense, vague chapter names, repeated rhetorical questions, and documentary-style filler.
- Match footage to the narration. Preserve comprehensible chronology and identify characters clearly without overloading listeners with names.
- Narration-to-picture synchronization is mandatory. When a person, object, location, or action is mentioned, show the relevant image at that phrase or just before it; do not reveal it three to five seconds later. For example, show the CCTV monitors/search footage when the narrator describes searching the cameras, rather than holding an unrelated reaction shot until afterward.
- Select and inspect exact source in-points, not approximate scene timestamps. Align important reveals/actions to spoken phrase timings, including within a sentence. Audit concrete visual references throughout the edit and correct delayed or mismatched shots before delivery.
- Show the actual action stated by the narration, not merely the same people or a nearby moment. If the narration says an embrace turns into a kiss, the kiss itself must play at that phrase; a frozen hug is not an adequate match. Apply this to every concrete event, including falls, discoveries, attacks, object use and escapes.
- Inspect the progression through each action, not just first/last frames. Map the action's source timestamp to its spoken phrase and show the decisive action within the three-second clip before cutting or freezing. Never freeze a lead-in frame so that the narrated event never appears. Choose a better source passage, adjust picture timing or revise inaccurate narration when needed; keep the scene's cause and effect understandable.
- Inspect the actual rendered first and last frames of important shots, including any held frame. A source reverse-angle cut can occur a fraction of a second after the chosen in-point; first look for a relevant moving passage of at most three seconds or another suitable shot. If neither covers the narration, a selective freeze before the reverse cut may keep the named person or object visible. Do not hold a blank transition or an overexposed flash.
- Edit all source clips in their normal, unmirrored orientation, including cuts, freezes, pans, zooms and cropping; retain source colors. Do not selectively flip individual clips during this stage.
- Full recaps require one additional, constant 1.10x centered picture zoom across the entire assembled edit, before the final horizontal flip. Enlarge width and height uniformly to 110% and crop equally from opposing edges back to the original output dimensions. Keep the center fixed, preserve aspect ratio, and do not animate this global zoom or add shake. This is picture magnification, independent of narration speed.
- Apply this global zoom exactly once, identically to the final video, on top of any deliberate per-shot edits. Account for its crop when choosing shots so important faces, objects, and narrated actions remain visible. Audio, duration, subtitle timing, and standalone thumbnail framing are unaffected. Treat it as editorial styling, not copyright protection; it does not prevent claims, blocks, or strikes.
- After all clips are merged and the complete edit is finished, apply ONE horizontal flip to the entire assembled movie picture before letterbox padding. Flip every movie frame, including screens, signs, timers and documents, even when their text becomes reversed. There are no text-readability exceptions for source footage.
- Apply the same final whole-video flip to the final video, preserving identical picture timing, audio, and separate SRT files. Remove any inherited per-clip mirroring before this final flip so that double flipping does not restore some shots to their original orientation.
- Use noncontinuous moving excerpts and occasional end-frame freezes with a pronounced hard zoom. Do not freeze every clip or routinely hold a frame through an entire narration paragraph.
- A freeze is appropriate when narration about a specific person, object or action lasts longer than the useful footage showing it, or when a particular moment benefits from emphasis. Let the useful action play first, choose a clear relevant frame, and hold only as long as needed within the same three-second total clip limit. Cover any remaining narration with another relevant noncontinuous excerpt. Preserve phrase-to-picture alignment and natural narration pacing; do not speed up the voice to avoid a necessary hold.
- Prefer moving footage within the three-second limit when a freeze adds nothing. Use freezes selectively for emphasis or to keep a relevant subject visible; never to pad the ten-minute minimum. These edits are styling, not copyright protection.
- For selected freeze frames, use a clear hard zoom toward the relevant person or object, for emphasis on the selected subject. A roughly 1.65x close-up and brief end hold are useful references, not quotas. Keep the subject visible after the final crop; use a stable focal point without shake or oscillation. The moving portion, freeze and zoom together must stay within three seconds.
- Never add shake, jitter, vibration, wobble, random offsets, or repeated back-and-forth movement to freeze frames or other footage. The owner finds the shaking in the delivered recap dizzying. Keep a stable focal point and a continuous smooth motion path; a fully static hold is preferable to unstable movement.
- Prevent rendering-induced jitter as well as intentional shake. Use a rendering method with smooth subpixel interpolation or sufficient oversampling; do not accept visible pixel stepping or alternating crop positions during zooms. Review representative rendered freeze/pan/zoom passages in motion at normal playback speed, including entry and exit. Still-frame contact sheets alone cannot verify motion smoothness. Correct any visible jitter before delivery.
- Preserve the film's source colors and clean image. No added frying effects: noise/grain, RGB separation, pixelation, aggressive sharpening, randomized hue/saturation/contrast shifts or compensating gamma treatments. Retain the established centered 1.10x crop and final whole-video horizontal flip. Never claim these edits prevent copyright claims, blocks or strikes.
- Keep source aspect ratio and important subjects intact. Allow stronger focused zooms while retaining the subject and necessary scene context; avoid indiscriminate heavy cropping and excessive color changes.

## Separate visual-caption SRT: mandatory

- Deliver two useful subtitle files: `<Movie>-narration-TTS.srt` for voice generation and `<Movie>-captions-display.srt` for readable narrator captions.
- Shorten the visual caption cues without changing the narration script, generated audio, delivery rate, or pauses. Never use the short display-caption file as the TTS input.
- Use short readable phrases, generally about 4–9 words per cue and at most two lines, aiming for around 32–42 characters per line. Prefer one line when feasible. Do not show whole long narration sentences as a bulky three-line block.
- Split at natural phrase boundaries, sentence endings, and speaker changes. Preserve every spoken narration word in order; do not join different speakers or unrelated sentences.
- Align display cues to actual spoken words, not merely proportional sentence duration. Avoid overlap, flashing single words, and captions that remain far beyond their spoken phrase.
- SRT carries text and timings, not reliable styling. Recommend bold outlined sans-serif text directly over the footage; do not add black text bands or shrink the picture. Leave the final video free of burned-in captions unless explicitly requested.

## Verification and handoff

- Verify the final MP4 duration is at least 600 seconds and that picture, narration and subtitle timing match.
- Verify the final video is exactly 1920 x 1080 with square pixels, correct source proportions and centered black padding where necessary.
- Verify the constant 1.10x centered zoom covers every frame in the final export, with equal opposing-edge crops and unchanged output dimensions/aspect ratio. Check representative shots and hard-zoom freezes for lost subjects and ensure the global zoom was not applied twice.
- Verify the horizontal flip was applied once to the entire completed picture in the final export, with no per-clip exceptions or double flips. Compare representative final frames, including text-bearing shots and freezes, against the unflipped assembled edit.
- Verify exactly one narrated final video deliverable, no burned-in captions, valid picture/audio streams, successful decoding, and reasonable loudness/peak levels.
- Inspect representative frames, hard-zoom freezes and transitions. Check speech pacing and sync with available tools; disclose if no full listening pass was performed.
- Review freeze placement and duration across the full edit: each hold should solve a specific timing or emphasis need, rather than being a default applied to every shot. Replace unnecessary holds with suitable moving footage and check that necessary holds end when the narration moves to the next idea.
- Validate SRT numbering, timings, wording preservation, and speed-limit compliance, including the required cumulative 1.10x narration rate. Base the edit and subtitle timings on the measured adjusted narration.
- Provide links to the narrated video, both useful SRT files, upload package and thumbnail options, with actual duration, file size and concise verification notes. Verify that no unnecessary files remain in the final folder.
- Audit every rendered clip: moving footage plus any freeze/zoom must total at most three seconds. Inspect source in/out points to confirm successive excerpts are genuinely noncontinuous, rather than adjacent pieces of the same passage. Verify the final mix has no source-film audio.
- Do not upload, publish, dispute claims, or send messages without explicit authorization.

## Thumbnail stills: mandatory for full recaps

- Extract three distinct, interesting frames as thumbnail picture options for every full recap. Save them as `thumbnails/thumbnail-01.png`, `thumbnail-02.png`, and `thumbnail-03.png` in the output folder.
- Use actual source-film frames and deliver upload-ready YouTube thumbnails in exact 16:9 dimensions. Default to 1280x720 pixels for these film-frame exports; use a larger 16:9 size when useful source detail supports it. Crop and, when needed, zoom/reposition around the main subject before resizing. Do not stretch the image or retain cinematic black bars; keep faces and essential action inside the crop.
- Keep each thumbnail below 2 MB for compatibility with mobile uploads. Use optimized PNG, or high-quality JPG if necessary to meet that size; reflect the actual extension in the handoff. Verify dimensions, aspect ratio, file size, image decoding and the final composition for all three options.
- Keep source orientation and colors for the standalone thumbnails; the final whole-video flip rule applies to the videos. Do not add text, captions, branding, composites, or generated imagery unless requested. This thumbnail sizing rule supersedes the earlier native-resolution/native-aspect-ratio requirement and applies only to full recaps.
- Choose visually clear, compelling moments with readable expressions, an important object, or a distinctive situation. Provide meaningfully different options rather than three adjacent frames of the same shot. Prefer frames without motion blur, blinks, transitions, credits, embedded subtitles, or excessive gore.
- Inspect all three extracted images before delivery. Record their exact source timestamps and short descriptions in the thumbnail notes section of `youtube-upload.txt`; recommend one option and provide links or inline previews. Do not create a redundant thumbnail-options text file.
- These three images are supporting deliverables and do not change the one-final-video requirement. This requirement applies only to full recaps, not Reels.

## YouTube upload package template

Always provide and save `youtube-upload.txt` containing:

1. One recommended accurate, compelling title and three alternatives. Keep titles under 100 characters and avoid misleading events, invented stakes, or unrelated film names.
2. A copy-ready description with a specific premise, film name/year, full-spoiler notice, verified chapter timestamps from the final edit, and a brief relevant subscription invitation.
3. A relevant comma-separated tag list within YouTube's 500-character tag budget. Do not pad it with unrelated popular titles.
4. Three short thumbnail-text options and one concrete visual concept without excessive gore.
5. One pinned comment asking a specific story question.
6. Appropriate category, language, audience setting, playlist suggestion, subtitle upload reminder, and end-screen suggestion. Base audience/age decisions on the actual material; do not promise ad suitability.
7. Any music attribution actually required by the assets used. Do not add fictitious credits or imply that a copyright disclaimer grants permission.

Chapter timestamps must come from the delivered edit. Update them whenever the edit timing changes.

## Optional Undertow music credit: full recaps only

- The owner plans to manually add "Undertow" by Scott Buckley. Always include a separate, copy-ready optional music-credit block in `youtube-upload.txt`, labeled for use when the owner adds the track. Do not insert the song into the exports automatically or claim it is already present.
- Supply this credit for the YouTube video description:

```text
Music: "Undertow" by Scott Buckley.
Released under CC BY 4.0.
https://www.scottbuckley.com.au/library/undertow/
https://creativecommons.org/licenses/by/4.0/
```

- If the owner trims, loops, or otherwise modifies the music, include a brief accurate changes statement with the credit; do not invent changes. Keep this optional block separate from credits for assets actually present in the delivered edit.
- This is licensed music requiring attribution, not a promise of no Content ID claims. Keep claim-release guidance in handoff notes when needed, not in the public description: https://www.scottbuckley.com.au/library/copyright-claims-release/
- This preference applies only to full recaps. Do not change Reel instructions or rebuild existing exports for this documentation update.

## Part B — Short recap for Instagram Reels

Only this part governs the Reel. Full-only duration, speed, clip ceiling, whole-picture zoom/flip and canvas rules do not apply.

## Hard duration and story structure
- EVERY final video must be at least 45.000 seconds and at most 75.000 seconds, inclusive, including all pauses, audio tails, transitions and closing frames. Aim for 45.5–74.5 seconds to leave encoding margin. This is a runtime requirement, separate from TTS playback speed.
- Write a concise recap that establishes the protagonist, situation, threat and escalation, then stops at the beginning of the climax.
- Do not show or narrate the climax's outcome, resolution, final defeat, survival outcome or ending.
- Open immediately with a concrete, accurate hook from the film. Avoid generic scene-setting and misleading invented stakes.
- Build curiosity through a specific unresolved decision or danger. A genuine prediction question is welcome. Do not promise a second part when none is planned.
- Use few character names and plain, natural sentences. Remove secondary plots rather than packing the entire film into rushed narration.

## Voice and timing
- Use the user's selected consistent voice when provided. Otherwise use the established local narrator, Kokoro am_michael, without asking again. Disclose it as a local voice, not an exact Instagram-provided voice. If that voice is unavailable, report the missing dependency and ask only if a materially different substitute is needed.
- Generate and measure narration BEFORE final picture editing.
- TTS may be accelerated to 1.20x or 1.30x when useful. Maximum cumulative effective speed is 1.30x; record synthesis and postprocessing rates and never stack beyond the cap.
- Retain natural punctuation and brief breathing pauses. Never cut words or final syllables to meet the limit.
- Favor a slightly calmer delivery and an enjoyable watch over maximum information density. Speed increases are optional, not a target. Shorten the script and remove secondary details before accelerating speech or adding rapid cuts; use the available 45–75-second window for clear phrasing and breathing room.
- Adjust the script and edit to fit the 45–75-second runtime. If too short, add useful setup or escalation before the climax, not filler or dead air. If too long, tighten the script without revealing the resolution. Keep the existing 1.30x maximum cumulative TTS speed.
- Keep narration clear above quiet music. Original-film audio moments are optional; no long-form ten-break quota applies.

## Picture
- Preserve the source aspect ratio; the user will reframe for Instagram. Do not crop to vertical or add a vertical canvas.
- Default to original orientation and source colors. No mandatory horizontal flip or color grade.
- Match every concrete spoken reference to the relevant shot at the phrase or slightly before it, including within-sentence changes.
- Inspect exact source in-points and rendered shot boundaries. Avoid delayed reveals, blank frames, unrelated reverse angles and accidental spoilers.
- Prefer purposeful moving footage. Optional smooth holds/pans/zooms must not shake, wobble or jitter.
- Minimize end-frame freezes. Let relevant source footage continue naturally for most of each shot; do not routinely play a fraction of a second and freeze the remainder of a narration segment. Use a brief freeze only when it serves a specific emphasis or transition, and avoid repeated freezes across consecutive shots.
- Slow the visual pace slightly. Let viewers recognize the setting, follow the action and digest each idea before changing scenes. Generally favor several seconds of continuous, relevant footage (often about 3–6 seconds, longer when useful), without enforcing a fixed shot length. Avoid habitual one-second cuts or rapid jumps between locations; brief cuts should be motivated by a specific action or reveal.
- Choose source passages that remain relevant for the intended hold, including any cuts already inside the film. If a passage becomes unrelated or blurry, find a better continuous passage rather than routinely solving it with a long freeze. Preserve precise phrase-to-picture matching by simplifying narration and choosing shots that cover the whole idea; do not delay a required reveal to slow the cut rate.
- Keep important subjects visible for later reframing. No decorative cards or burned-in captions unless requested.

## Deliverables and verification
- Deliver exactly two final MP4s: with narration, and identical picture/timing without narration. Retain music and selected original audio in the latter.
- Keep intermediate videos inside _work.
- Supply narration.txt, natural-phrase narration-TTS.srt and compact captions-display.srt. Preserve every narration word in both SRTs.
- Align display captions to spoken words, split at natural phrases, use at most two short lines, avoid word-by-word flashing.
- Verify both final media durations satisfy 45.000 <= duration <= 75.000 seconds, their pictures/timing match, all streams decode, sound has headroom, and SRT timestamps are sequential with no overlap.
- Verify the final shot and final narrated line stop before the climax's outcome or resolution.
- Review pacing at normal playback speed where supported: check that footage mostly keeps moving, freezes are brief and occasional, and scene changes allow comprehension. Inspect internal source cuts as well as edit boundaries. Revise rushed sequences instead of treating duration compliance as proof of an enjoyable pace; disclose if normal-speed playback review was unavailable.
- Report runtime, voice/rate, relevant limitations, and file links. If replacing narration using the no-narration export, recheck duration and alignment.
- Reuse local tools; ask before paid services. Do not upload or publish without authorization.

## Instagram description and optional on-screen hooks
- Include instagram-copy.txt with every Reel delivery.
- Begin the copy-ready post caption with the film title and verified year, for example: "🎬 Colony (2026)". Follow it with a fuller story description in two or three natural paragraphs, roughly 120–200 words when useful.
- Match the user's reference through specific plot context, character motivations, escalating danger and an unresolved dilemma. Avoid generic promotional filler.
- Preserve the Reel's spoiler cutoff in the description too: no climax outcome, resolution or ending. Do not reveal additional late twists just to lengthen it.
- Include a short relevant hashtag line and an optional genuine discussion question.
- Separately supply 4–6 optional on-screen hooks for manual placement, with one recommended option and both statement and question variants. Aim for roughly 6–12 words, readable in one or two lines.
- Hooks should be specific, accurate and intriguing, like the headline above the footage in the examples. Avoid generic "you won't believe" copy, invented stakes, ending spoilers or false part-two promises.
- Suggest a two-line break for the recommended hook and bold readable sans-serif text with strong contrast near the top, clear of faces and subtitles. The user chooses the final canvas and may use a header area.
- Keep hooks separate from narration and SRTs. Do not burn them in, add a header band, resize footage or change the videos unless explicitly requested.

## Installation and invocation reference

The installed skill folder must be named `movie-recap` and contain `SKILL.md`. No logo asset is bundled or required. In the GitHub source repository, `README.md` explains setup and `install.py` installs this file into that folder.
- Claude Code personal installation: `~/.claude/skills/movie-recap/`; project installation: `<project>/.claude/skills/movie-recap/`. Invoke `/movie-recap Lucky`.
- Codex personal installation: `~/.agents/skills/movie-recap/`; project installation: `<project>/.agents/skills/movie-recap/`. Invoke `$movie-recap Lucky`, or select the skill in the picker. A custom slash command is not registered in Codex simply by naming a skill.
- Open the folder containing the source film as the project, or pass its explicit path. Reopen the session if the installed skill does not appear. Local filesystem installation does not automatically install it into Claude's cloud/Cowork environments.
- Copy the whole folder or extract its ZIP to move it to another machine. Models and runtimes are not included in the ZIP; run the repository installer to download and verify them on that machine. Changes to an installed copy do not automatically update another copy.

Host syntax references: https://code.claude.com/docs/en/skills and https://learn.chatgpt.com/docs/build-skills
