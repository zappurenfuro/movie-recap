# Reusing production tools and overlapping work

Before writing editing code, inspect available general-purpose helpers and their input schemas. Reuse compatible probing, extraction, voice, alignment, subtitle, render, mixing, thumbnail and verification code. Remove hardcoded movie data from an adapter rather than copying a previous movie's analysis. Keep project-specific manifests outside the skill. Do not publish user assets or paths.

The bundled `scripts/run_jobs.py` schedules existing commands; it is not a turnkey movie renderer. The agent still analyzes footage, writes fresh scripts and supplies compatible media helpers. It uses only Python's standard library. Use the installed runtime's Python to invoke it.

## Job manifest

Write JSON with an absolute `cwd` for the task workspace and a `jobs` array. Each job has a unique safe `id`, an `argv` list, optional `needs` job IDs, optional exclusive `resources` names, and optional `timeout_seconds` (default 3600, maximum 86400). Use absolute executable/helper paths. Paths with spaces are single list elements; do not use shell quoting, redirection, pipes or shell command strings.

Example structure, to adapt to actual inspected helpers:

```json
{
  "cwd": "/absolute/current-task",
  "jobs": [
    {"id": "source-transcript", "argv": ["/absolute/python", "/absolute/analyze.py", "transcribe"], "resources": ["gpu"]},
    {"id": "source-survey", "argv": ["/absolute/python", "/absolute/analyze.py", "survey"], "resources": ["cpu-heavy"]}
  ]
}
```

Invoke:

```text
<runtime-python> <skill-folder>/scripts/run_jobs.py <task>/jobs.json --output <task>/logs-analysis-01 --workers 2
```

The output directory must not already exist. Commands run with `shell=False`; manifests execute local code and must be reviewed before running. No command is skipped because an old output exists. The runner validates dependencies before starting, records stdout/stderr in per-job logs, and writes `timings.json`. A zero exit code means the command completed, not that its editorial output passed review. Include actual verification commands where appropriate.

If a job fails, no new jobs are scheduled; already-running jobs finish (or reach their configured timeout), and remaining jobs are marked skipped. Fix the issue before submitting a new manifest in a new logs directory. There are no automatic retries. Use directly invoked commands rather than detached services or shell wrappers: timeouts control the direct child, not arbitrary grandchildren. Preserve logs until diagnosis is complete.

## Stage boundaries

1. Start an end-to-end timer before inspecting the source. Reuse models/tools but create new analysis from source footage and source-provided subtitles. Transcription and visual surveys can overlap if hardware allows.
2. Review story events and the ending. Write new scripts for the requested formats. Lock natural paragraphs before synthesizing them. Estimate duration from measured voice behavior, then measure the actual generated voice; do not pad an underlength Reel.
3. Keep one voice model loaded across natural paragraphs. While it generates approved material, inspect relevant source actions and thumbnail candidates. Do not render final picture timing until the adjusted voice and phrase anchors are measured. Overlapping work can be done by a single agent with background processes; it does not require subagents.
4. Build the edit manifest from current-run evidence and narration. Validate scene references before encoding. Use bounded workers and explicit resource labels for heavy work. A job may claim several resources; jobs sharing any name cannot overlap. Resource names are user-defined, not automatic GPU/CPU detection.
5. Render independent batches once with compatible settings, then stream-copy assembly. Use the same encoded Reel picture for both audio variants. A changed batch need not force other unchanged same-run batches to render again. Recompute downstream timing when voice or duration changes.
6. Complete decoding, subtitle, audio and visual checks. Review representative motion with audio; report unavailable review. Preserve all quality settings and deliverables. Record both wall time and per-stage times; overlapping times are not additive. Include manual review, corrections and failed attempts in the overall report.

## Cache boundary

Reuse code and installed models across movies. For a fresh production, do not reuse previous movie analysis, generated transcripts, scripts, shot manifests or narration. Within a run, retain intermediates only with matching source identity, helper version and relevant settings. Explicitly requested revisions may reuse unaffected results. The runner deliberately implements no automatic content cache: the agent must validate any resume decision and invalidate dependent outputs. Cleanup must preserve shared helpers, models and previous deliverables.
