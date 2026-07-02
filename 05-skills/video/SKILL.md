---
name: video
description: Video production pipeline command. `status` reports the phase of each video project (orphaned, pre-production, needs transcript, ready for selects, ready for polish, in finishing, ready for upload, done). `new` bootstraps a new video project with a short Q&A intake and writes task-list.md. `record` runs a live on-set producer that holds the script and interviews you one question at a time while you record talking-head takes, surfacing verbatim lines and logging coverage + approved takes to recording-aids/. `selects` runs the post-recording chain (transcribe, /associate-producer, then a Buttercut rough-cut timeline that references the raw) for a slug; pass `--clips` to also splice per-clip mp4s. `remap` relinks a Descript-polished edit (DaVinci Resolve XML) back to the original raw footage, mapping the cuts to raw timecodes. `assets` reads producer/animation-ideas.md and generates Remotion overlays + Replicate B-roll into assets/ for the finishing pass. `lay-in` generates a DaVinci-importable full-stack timeline (xmeml) that keeps your remapped edit on V1 and places the MMSS-named overlays and cards onto tracks above it. `upload` drafts AI metadata, generates SRT captions and thumbnail variants, then publishes to YouTube as unlisted behind an approval gate. Triggers on "/video status", "/video new", "/video record", "/video selects", "/video remap", "/video assets", "/video lay-in", "/video upload", "video status", "new video", "record video", "be my producer", "interview me while I record", "on-set producer", "prompt me while I record", "make selects", "cut selects", "remap descript to raw", "relink descript to raw", "link descript export to raw", "generate assets", "make assets", "render overlays", "lay in graphics", "lay graphics onto timeline", "place graphics on timeline", "publish video", "upload to youtube", "where are my videos", "video pipeline status".
triggers: /video status, /video new, /video record, /video selects, /video remap, /video assets, /video lay-in, /video upload, video status, new video, record video, be my producer, interview me while I record, on-set producer, prompt me while I record, make selects, cut selects, remap descript to raw, relink descript to raw, link descript export to raw, generate assets, make assets, render overlays, lay in graphics, lay graphics onto timeline, place graphics on timeline, publish video, upload to youtube, bootstrap video, where are my videos, video pipeline status
---

# /video

Multi-action commands for the video production pipeline. This segment implements `status`, `new`, `record`, `selects`, `remap`, `assets`, `lay-in`, and `upload`. The `polish` action will be added in a later session.

## Actions

| Action    | Status           | Purpose                                                                  |
| --------- | ---------------- | ------------------------------------------------------------------------ |
| `status`  | ✅ Implemented   | Scan project folders, report each video's phase                          |
| `new`     | ✅ Implemented   | Bootstrap a new video project with a Q&A intake                          |
| `record`  | ✅ Implemented   | Live on-set producer: interview the user one question at a time, log coverage |
| `selects` | ✅ Implemented   | Transcribe raw, run /associate-producer, assemble a Buttercut rough-cut timeline (raw-referencing); `--clips` also splices per-clip mp4s |
| `remap`   | ✅ Implemented   | Relink a Descript-polished edit (xmeml) back to the original raw footage |
| `assets`  | ✅ Implemented   | Generate Remotion overlays + Replicate B-roll from animation-ideas.md    |
| `lay-in`  | ✅ Implemented   | Build a DaVinci-importable full-stack timeline: remapped edit on V1 + MMSS overlays/cards on tracks above |
| `polish`  | ⏳ Not yet built | Hand off to finishing                                                    |
| `upload`  | ✅ Implemented   | Draft metadata, generate captions + thumbnails, gated publish to YouTube |

## status

Invoked as `/video status` or `/video status <slug>`.

### What it does

Scans two parallel project trees:

- **Working files:** `/Users/jashia/Documents/1_Projects/videos/`
- **Meta docs:** `/Users/jashia/Documents/3_Resources/Obsidian/Second Brain/2 Systems/content-production/projects/`

For each `videoNN-slug` folder it finds in either tree, it infers the production phase from which files exist and prints a markdown table.

### Phase detection

The script walks the pipeline backwards and returns on the first match. This means "later" phases win — if a video has both a transcript and a selects manifest, it's reported as the more advanced phase.

| Detection                                      | Phase             | Next action           |
| ---------------------------------------------- | ----------------- | --------------------- |
| `retrospective.md` exists                      | done              | (none)                |
| `finals/` populated                            | ready for upload  | `/video upload`       |
| `rough-cuts/` populated                        | in finishing      | open in DaVinci       |
| `producer/selects-manifest.json` exists        | ready for polish  | `/video polish`       |
| `transcripts/` populated                       | ready for selects | `/associate-producer` |
| `raw/` populated                               | needs transcript  | run transcribe        |
| Has `script.md`, `task-list.md`, or `brief.md` | pre-production    | record                |
| Otherwise                                      | orphaned          | bootstrap or archive  |

### How to invoke

Run the bundled Python script via Bash and pass through its output verbatim:

```bash
python3 /Users/jashia/Documents/1_Projects/ai-system/.claude/skills/video/scripts/scan-projects.py
```

For one video in detail:

```bash
python3 /Users/jashia/Documents/1_Projects/ai-system/.claude/skills/video/scripts/scan-projects.py video04-ai-video-pipeline
```

Print the script's stdout directly. Do not summarize, reformat, or add commentary unless the user asks a follow-up question. The script's table is the deliverable.

## new

Invoked as `/video new`.

Bootstrap a new video project: run a short Q&A intake, derive a slug, create both folder trees, and write a recording-ready `task-list.md` to the Obsidian folder. The user dictates answers with voice, so expect stream-of-consciousness and shape it as you fill the template.

### Workflow

```
Task Progress:
- [ ] Step 1: Q&A intake (5 questions, one at a time)
- [ ] Step 2: Derive slug, confirm with user
- [ ] Step 3: Create both folder trees
- [ ] Step 4: Write task-list.md
- [ ] Step 5: Print confirmation and stop
```

### Step 1: Q&A intake

Ask these five questions **one at a time**. Wait for the user's answer to each before asking the next. Do not batch. Do not summarize until you have all five.

1. "What are you building or showing in this video?"
2. "Who's it for, and what do they walk away knowing?"
3. "Target runtime? (default 12-15 min)"
4. "Which pillar? building-in-public, ais, psa, aifc"
5. "Anything you already know you want to demo or show on camera? List a few bullets, riffable."

Answers will be voice-dictated and loose. Shape them into the artifact, do not transcribe verbatim. If an answer is genuinely missing or vague, ask one sharp follow-up before moving on.

### Step 2: Derive slug, confirm with user

Numbering and folder creation are delegated to the shared bootstrap helper (the same one `/story-development` uses, so numbering lives in one place). Build a kebab topic from Q1 (lowercase, dashes, no spaces, no punctuation, trim filler words), then peek at the slug the helper would assign without creating anything. The helper scans both project trees for the highest `videoNN-` and increments, zero-padded:

```bash
HELPER="/Users/jashia/Documents/1_Projects/ai-system/.claude/skills/video/scripts/bootstrap-video-project.sh"
"$HELPER" "<kebab-topic>" --dry-run --json
```

Confirm the printed `slug` with the user, for example: `"Slug will be video10-build-pipeline. OK?"`. Wait for yes. If the user adjusts the slug, pass their full `videoNN-...` slug to the helper in Step 3 (it accepts an explicit slug verbatim).

### Step 3: Create both folder trees

Run the helper for real with the confirmed slug (or the same kebab topic). It creates the Documents subfolders (`raw/`, `transcripts/`, `rough-cuts/`, `finals/`) and the Obsidian subfolders (`producer/`, `recording-aids/`), and refuses to clobber an existing slug (exit 3):

```bash
"$HELPER" "<confirmed-slug>" --json
```

Capture `meta_dir` from the output; `task-list.md` is written there in Step 4. The Obsidian `producer/` subfolder gets created so the Associate Producer has somewhere to write later. `recording-aids/` is the per-video paste-fodder location for "primes" used in fresh Claude Code sessions during build-along recording segments. Convention is documented in `workflow-state.md`. Leave the Documents subfolders empty until recording day. If the helper exits 3 (slug collision), stop and ask the user how to proceed.

### Step 4: Write task-list.md

Canonical template: `/Users/jashia/Documents/3_Resources/Obsidian/Second Brain/2 Systems/content-production/projects/video04-ai-video-pipeline/task-list.md`. Read it once to keep the exact section headings and tone in sync.

Write to: `/Users/jashia/Documents/3_Resources/Obsidian/Second Brain/2 Systems/content-production/projects/<slug>/task-list.md`.

**Variable parts (fill from Q&A):**

- Frontmatter: `slug`, `title`, `pillar`, `secondary_pillar` (optional, only include if Q4 names a clear secondary, e.g. a build-in-public video whose subject matter is AIS), `target_runtime`, `created` (today's date).
- `## Topic + angle`: synthesize from Q1 (topic). One or two sentences. Plain English.
- `## The takeaway`: synthesize from Q2 (audience + walk-away). One sentence on what the viewer leaves understanding.
- `## Hook (riff in the moment, do not lock)`: propose one angle drawn from topic + takeaway. Loose. Two short paragraphs max. Optionally drop in an alt angle prefixed with "Alt angle if the first one doesn't land on take 1:".
- `## Bullets to hit (rough order, riffable)`: scaffold the standard sub-sections below. Pre-fill the demo segments with the user's bullets from Q5 where they map. If Q5 had fewer than three demo bullets, leave the rest as empty placeholders the user can fill in later.

**Standard parts (verbatim from template):**

Use exactly this frontmatter shape (substituting variable values):

```yaml
---
slug: <slug>
title: <title>
pillar: <pillar>
secondary_pillar: <secondary_pillar> # optional, omit the line entirely if not given
format: walkthrough
target_runtime: <runtime>
status: draft
created: <today YYYY-MM-DD>
approval_keywords: ["that's the one", "moving on from that", "print that one"]
---
```

`format` is always `walkthrough`. `status` is always `draft`. `approval_keywords` is always the standard three.

Scaffold the bullets section with these sub-sections, in this order, with the same checkbox format the template uses:

```
### Setup (~1 min)
- [ ] Who I am, what this is, what we're building. Layout: `talking-head`
- [ ] (frame the take-away upfront so viewers know what they'll walk away with)

### Context / the gap (~2 min)
- [ ] (the gap this video closes, why it matters, what the viewer already knows)

### Demo segment 1 (~3-4 min)
- [ ] (pre-fill from Q5 bullets if applicable)

### Demo segment 2 (~3-4 min)
- [ ] (pre-fill from Q5 bullets if applicable)

### Demo segment 3 (~3-4 min)
- [ ] (pre-fill from Q5 bullets if applicable)

### Outro (~1 min)
- [ ] CTA, riffable (subscribe / comment / AI Office Hours link in description)
- [ ] Next-video tease
```

Use 3 demo segments by default. If the user gave 4-5 demo bullets in Q5 that clearly map to separate segments, use 4 or 5 instead. Cap at 5.

Then append, verbatim:

```
## Demo prep (do before hitting record)
- Obsidian sidebar narrowed to relevant folders, key reference doc open in a tab
- `.claude/skills/` (or relevant repo) open in Windsurf
- Terminal in the right project root, ready for command runs
- Browser closed, DnD on, clipboard cleared
- No client names / personal info on screen
- Pull a recent dictation note or rough idea to riff from in the cold open if needed

## Approval keywords (say on camera after a take you like)
- "that's the one"
- "moving on from that"
- "print that one"

## Hand-off
Once raw footage is in `~/Documents/1_Projects/videos/<slug>/raw/`, run `/video selects` (or the existing chain: transcribe, `/associate-producer`, splicer).
```

Substitute `<slug>` in the hand-off path. Do not add scene cues, verbatim lines, or Remotion slots: `task-list.md` is a riff-from artifact for solo walkthroughs, not the locked-down `script.md` that `/story-development` produces.

### Step 5: Print confirmation and stop

Print exactly:

```
task-list.md drafted at /Users/jashia/Documents/3_Resources/Obsidian/Second Brain/2 Systems/content-production/projects/<slug>/task-list.md. Folder structure ready at /Users/jashia/Documents/1_Projects/videos/<slug>/. Read it, edit anything that doesn't fit, then run /video record when ready.
```

Use full absolute paths so they're cmd-clickable. Do not invoke any other skill. Stop.

### Constraints specific to `new`

- **One question at a time.** Voice dictation breaks if questions are batched.
- **Confirm the slug before creating folders.** Folder names are hard to change later.
- **No em dashes anywhere in the output.** Use periods, commas, colons, parens.
- **Do not chain.** Emit the file and stop. The user decides when to record.
- **If `task-list.md` already exists at the target path** (somehow the slug collides), stop and ask the user how to proceed rather than overwriting.

## record

Invoked as `/video record <slug>`.

Turn **this** conversation into a live on-set producer for a recording session. You hold the video's script and interview the user one question at a time while they record talking-head (or walkthrough) takes. The user performs well when prompted and gets lost when they have to invent the content and the next question at once, so your job is to hold the questions. You ask, they riff to camera, they paste the transcribed take back, you register what landed and ask the next single question. The live conversation is ephemeral. The only artifact is a coverage + takes log written to `recording-aids/` at wrap, which `/associate-producer` can read later.

This action does not run a script or touch any external service. It is a guided interview. The full behavior lives in the playbook reference; load it before the first question.

### Workflow

```
Task Progress:
- [ ] Step 1: Resolve the slug and the script
- [ ] Step 2: Parse the script into ordered sections
- [ ] Step 3: Load the on-set producer playbook
- [ ] Step 4: Orient the user, confirm record is rolling, ask the first question
- [ ] Step 5: Run the one-question-at-a-time turn loop until wrap
- [ ] Step 6: Write the session log, print the wrap summary, stop
```

### Step 1: Resolve the slug and the script

If no slug was given, run `python3 .../scripts/scan-projects.py` (see the `status` action) and offer the videos in `pre-production` or `needs transcript` phase. If exactly one fits, confirm it. Otherwise ask which slug.

Resolve the script by checking these absolute paths in order. The **first one that exists wins**. Scripts do not always live in Obsidian. video06 and video07, for example, keep theirs in the working-files folder.

1. `/Users/jashia/Documents/3_Resources/Obsidian/Second Brain/2 Systems/content-production/projects/<slug>/script.md`
2. `/Users/jashia/Documents/1_Projects/videos/<slug>/script.md`
3. `.../projects/<slug>/outline.md`
4. `/Users/jashia/Documents/1_Projects/videos/<slug>/outline.md`
5. `.../projects/<slug>/task-list.md`
6. `/Users/jashia/Documents/1_Projects/videos/<slug>/task-list.md`
7. `.../projects/<slug>/brief.md`
8. `/Users/jashia/Documents/1_Projects/videos/<slug>/brief.md`

Set `meta_dir` to the directory of whichever file matched. The session log writes to `<meta_dir>/recording-aids/`. If nothing matches, stop and tell the user to run `/story-development` or `/video new` first. Do not invent a script.

### Step 2: Parse the script into ordered sections

Read the resolved script end to end. Build an ordered section list, capturing per section: title, layout tag (`talking-head` / `screen-demo` / `pip-*`), the spoken topic-boundary callout (`SAY: "..."`), the riff points, any `SAY EXACTLY` verbatim line, any `CLOSE (read for VO)` line, and the script's own riff prompt. Also read any "How to use this script" and "Recording checklist" sections and honor their instructions (they outrank your defaults). Read `approval_keywords` from the frontmatter; default to `["that's the one", "moving on from that", "print that one"]`.

### Step 3: Load the on-set producer playbook

Read `references/on-set-producer.md` in this skill folder and hold it for the whole session. It defines the persona, the turn loop, question craft, how to surface verbatim lines and callouts, control phrases, coverage tracking, and the exact session-log format. Follow it.

### Step 4: Orient, confirm rolling, ask the first question

Give the user a 2 to 3 line orientation: what you are shooting today, and the loop ("press record on the camera and the transcription app, riff your answer, then paste the take back to me and I'll ask the next one"). Remind them of the first topic-boundary callout if the script opens with one. Then ask the **first single question**, usually seeded from the cold open / hook riff prompt. Stop and wait.

### Step 5: Run the turn loop

Follow the playbook's turn loop exactly: one short line of register, an optional cue when a verbatim line or callout is due, then **exactly one question**. Treat pasted prose as a take, recognized phrases as control. Track coverage as you go. Never batch questions. Keep every turn short. The goal is to maximize how much the user records.

### Step 6: Wrap, log, stop

On a wrap signal (or when the script is fully covered), stamp the date with `date +%F`, then write or append the coverage log to `<meta_dir>/recording-aids/record-log.md` using the exact shape in the playbook (`mkdir -p` the folder first; append a new dated session if the file exists, never overwrite). Print a short wrap summary (covered / blessed / pickups needed) with the absolute log path, then stop.

### Constraints specific to `record`

- **One question per turn. Never batch.** This is the user's explicit choice and the entire point of the action.
- **Keep your turns short.** Brief register, optional cue, one question. No analysis, no reading the take back. Every word you spend is a word the user is not recording.
- **Verbatim is verbatim.** Surface `SAY EXACTLY` and `CLOSE (read for VO)` lines word for word from the script. Never paraphrase or invent them.
- **Do not transcribe or edit footage.** The full video transcript is the real record. You only keep questions coming and track coverage.
- **Off script is welcome.** Follow a tangent that serves the story. Track coverage by substance not sequence, judge when the gist the video needs is captured, and say so plainly instead of padding to fill bullets.
- **The log is the only artifact.** The conversation is ephemeral.
- **Do not chain.** `record` ends at the log and the wrap summary. The user runs `/video selects` later, when ready.
- **No em dashes anywhere.** Use periods, commas, colons, parens.
- **All paths are absolute.** Print full `/Users/jashia/...` paths so they are cmd-clickable.

## selects

Invoked as `/video selects <slug>`.

Thin wrapper that runs the post-recording chain for a single video: transcribe any raw files that don't have transcripts yet, hand off to `/associate-producer` (which writes coverage, the story brief, and the selects manifest), then export a rough-cut NLE timeline via Buttercut. The rough cut is a single XML that references the **original raw footage** by absolute path, with every select pre-assembled on the spine in narrative order (no media is duplicated or re-encoded). This is the default output. The per-clip splicer (individual `selects/*.mp4` files) is opt-in via `--clips`. Stops after the export. The wrapper does not auto-chain to `/video polish`.

### Workflow

```
Task Progress:
- [ ] Step 1: Pre-flight checks (preflight-selects.py)
- [ ] Step 2: Handle existing manifest (re-run prompt or proceed)
- [ ] Step 3: Transcribe missing raw files
- [ ] Step 4: Invoke /associate-producer (respects its own review gate)
- [ ] Step 5: Export the rough-cut timeline via Buttercut (default); also splice per-clip files if --clips
- [ ] Step 6: Print confirmation and stop
```

### Step 1: Pre-flight checks

Run the bundled preflight script:

```bash
python3 /Users/jashia/Documents/1_Projects/ai-system/.claude/skills/video/scripts/preflight-selects.py <slug>
```

The script emits a JSON payload on stdout and uses its exit code as a signal:

- **Exit 2 (failed):** one or more required inputs are missing. The JSON's `errors` array lists each problem with the absolute path involved and a one-line fix. Print the errors verbatim to the user, then stop. Do not continue to Step 2.
- **Exit 1 (rerun_prompt):** all inputs are present, but `producer/selects-manifest.json` already exists from a previous run. Proceed to Step 2 (handle re-run).
- **Exit 0 (ready):** all inputs are present, no existing manifest. Skip to Step 3.

What it checks:

1. `raw/` exists at `/Users/jashia/Documents/1_Projects/videos/<slug>/raw/` and contains at least one `.mp4` or `.mov` file.
2. The Obsidian meta folder exists at `/Users/jashia/Documents/3_Resources/Obsidian/Second Brain/2 Systems/content-production/projects/<slug>/`.
3. At least one of `task-list.md`, `brief.md`, or `script.md` exists in that Obsidian folder.

The JSON also reports `raw_files` (absolute paths), `missing_transcripts` (raw files with no matching `transcripts/<name>.json`), `manifest_path`, and `selects_dir`. Hold onto this payload for the rest of the workflow.

### Step 2: Handle existing manifest

Only reached if Step 1 returned exit code 1.

Ask the user, verbatim:

```
selects-manifest.json already exists. Re-run? (y/n)
```

Wait for the answer. On `y`, continue to Step 3. On `n`, print `Exiting. No changes made.` and stop. Treat any other response as the user wanting to think about it: print the same line and stop.

### Step 3: Transcribe missing raw files

For each absolute path in `missing_transcripts` from the preflight payload, run:

```bash
/Users/jashia/Documents/1_Projects/ai-system/connectors/speech-to-text/venv/bin/python3 \
  /Users/jashia/Documents/1_Projects/ai-system/connectors/speech-to-text/transcribe_video.py \
  <raw-file> \
  -o /Users/jashia/Documents/1_Projects/videos/<slug>/transcripts/<raw-stem>.json
```

Use the venv interpreter shown above, not a bare `python3`. `mlx_whisper` is installed only in `connectors/speech-to-text/venv` (the isolated MLX Whisper venv). A bare `python3` raises `ModuleNotFoundError: No module named 'mlx_whisper'`.

`<raw-stem>` is the raw filename without its extension. The transcriber writes both `.json` and `.md` alongside the `-o` path, so the markdown lands in `transcripts/` automatically.

If `missing_transcripts` is empty, skip this step.

Run transcripts sequentially (MLX Whisper holds the GPU). For each, surface the transcriber's final stderr line (duration / segments / words) to the user so they can see progress.

If a transcription fails, stop the workflow, print the stderr from the failing run, and do not proceed to the associate producer.

### Step 4: Invoke /associate-producer

Invoke `/associate-producer` for this slug via the Skill tool. The associate producer reads `script.md` / `task-list.md` / `brief.md` from the Obsidian folder and the transcripts from the Documents folder, then produces:

- `producer/coverage.md`
- `producer/story-brief.md`
- `producer/selects-manifest.json`

**Critical:** `/associate-producer` has its own review gate (Step 6 of its workflow): it shows you `coverage.md` and `story-brief.md` and waits for you to say "ship it" before emitting the manifest. The `/video selects` wrapper must not bypass that gate. If the associate producer pauses for review, surface that state to the user explicitly:

```
/associate-producer is waiting on the coverage + story-brief review gate. Review producer/coverage.md and producer/story-brief.md, then say "ship it" to resume. /video selects will pick back up from there.
```

Do not loop, sleep, or otherwise wait silently. The user controls when the gate releases.

When `/associate-producer` finishes and `producer/selects-manifest.json` exists on disk, continue to Step 5. If for any reason the manifest is not produced, stop and report what happened.

### Step 5: Export the rough-cut timeline via Buttercut (default)

Buttercut reads the manifest produced in Step 4 and writes a single NLE timeline XML that references the **original raw footage** by absolute path, with every select on the spine in narrative order. No media is duplicated or re-encoded, and every cut stays re-trimmable in the editor. This is the default output of `/video selects`.

First create the rough-cuts folder (the exporter does not create it):

```bash
mkdir -p /Users/jashia/Documents/1_Projects/videos/<slug>/rough-cuts
```

Then run the exporter. Default editor is `fcp7` (the legacy xmeml `.xml` that DaVinci Resolve and Premiere import, matching the user's DaVinci pipeline). Override with `--editor fcpx` for Final Cut Pro X only if the user asks:

```bash
ruby /Users/jashia/Documents/1_Projects/ai-system/connectors/buttercut-export/export.rb \
  /Users/jashia/Documents/3_Resources/Obsidian/Second Brain/2 Systems/content-production/projects/<slug>/producer/selects-manifest.json \
  --editor fcp7
```

The exporter writes to `/Users/jashia/Documents/1_Projects/videos/<slug>/rough-cuts/rough-cut_<slug>_<editor>.<ext>` (`.xml` for fcp7, `.fcpxml` for fcpx) and prints the clip count and total timeline duration. Capture both for the confirmation.

Dependency: the `buttercut` Ruby gem (Ruby 3.x). If the exporter fails with a missing-gem error or `LoadError`, print the fix and stop: `gem install buttercut`. If it exits non-zero for any other reason, print its stderr and stop. Either way, do not print the success confirmation.

**Opt-in per-clip files (`--clips`):** only if the user passed `--clips` to `/video selects`, also run the splicer to produce individual `selects/*.mp4` files alongside the rough cut. Dry-run first to sanity-check timestamps, then the real pass:

```bash
python3 /Users/jashia/Documents/1_Projects/ai-system/connectors/splicer/splice.py \
  /Users/jashia/Documents/3_Resources/Obsidian/Second Brain/2 Systems/content-production/projects/<slug>/producer/selects-manifest.json --dry-run
python3 /Users/jashia/Documents/1_Projects/ai-system/connectors/splicer/splice.py \
  /Users/jashia/Documents/3_Resources/Obsidian/Second Brain/2 Systems/content-production/projects/<slug>/producer/selects-manifest.json
```

The splicer reads `output_dir` from the manifest (the associate producer sets it to `<docs-folder>/selects`) and writes per-clip `{id}.mp4` files there. Do not pass `--reel` or `--reencode` from the wrapper. Without `--clips`, do not run the splicer at all.

### Step 6: Print confirmation and stop

On success, print exactly (substituting the resolved slug, editor, and extension):

```
Rough cut ready at /Users/jashia/Documents/1_Projects/videos/<slug>/rough-cuts/rough-cut_<slug>_<editor>.<ext>. It references the original raw footage by absolute path, every select on the spine in narrative order, fully re-trimmable. Manifest at /Users/jashia/Documents/3_Resources/Obsidian/Second Brain/2 Systems/content-production/projects/<slug>/producer/selects-manifest.json. Import it into your NLE (in DaVinci Resolve: File > Import > Timeline), then run /video polish when ready.
```

If `--clips` was passed, append a second line:

```
Per-clip selects also written to /Users/jashia/Documents/1_Projects/videos/<slug>/selects/.
```

Use full absolute paths so they are cmd-clickable. Do not invoke `/video polish` or any other downstream skill. Stop.

### Constraints specific to `selects`

- **Default output is the raw-referencing rough cut, not per-clip files.** The Buttercut XML in `rough-cuts/` is the deliverable. Only produce `selects/*.mp4` when the user passes `--clips`.
- **Default editor is `fcp7`** (DaVinci Resolve / Premiere xmeml). Use `--editor fcpx` only if the user asks for Final Cut Pro X.
- **Pre-flight failures must be loud.** Print the exact `errors` array from the preflight payload. The user should know which path is missing and what to do about it.
- **Do not bypass the associate producer's review gate.** If the producer pauses for the coverage + story-brief review, surface it. Do not poll, sleep, or auto-continue.
- **Do not modify `status` or `new` actions.** This wrapper composes existing skills.
- **No auto-chain to `polish`.** Wrapper stops after Step 6.
- **No em dashes anywhere.** Use periods, commas, colons, parens.
- **All paths are absolute.** Print full `/Users/jashia/...` paths so they are cmd-clickable.

## remap

Invoked as `/video remap <slug>`.

Relink a Descript-polished edit back to the original raw footage. This is the "Descript-in-the-middle" finishing path: you render the Buttercut rough cut out of DaVinci as a flat video, upload that to Descript, do filler-word removal and cutdowns, then export the polished timeline from Descript as a DaVinci Resolve XML. That Descript XML references the intermediate render, not your raw. This action rewrites it so every cut points back at the original raw file, with timecodes mapped to raw space. Cuts that straddle a select boundary are split into multiple raw clipitems with continuous timeline positions. Non-destructive: it writes a new XML and touches none of the inputs.

It wraps `connectors/buttercut-export/remap-descript-to-raw.py`. The render-to-raw map comes from `producer/selects-manifest.json`, so this only works after `/video selects` has produced that manifest.

### Workflow

```
Task Progress:
- [ ] Step 1: Pre-flight checks (preflight-remap.py)
- [ ] Step 2: Handle existing remap output (re-run prompt or proceed)
- [ ] Step 3: Resolve the Descript XML and the raw source (disambiguate if needed)
- [ ] Step 4: Run the remap
- [ ] Step 5: Verify, print confirmation, stop
```

### Step 1: Pre-flight checks

Run the bundled preflight script:

```bash
python3 /Users/jashia/Documents/1_Projects/ai-system/.claude/skills/video/scripts/preflight-remap.py <slug>
```

Exit-code contract:

- **Exit 2 (failed):** a required input is missing (no `selects-manifest.json`, the manifest's raw source is not on disk, no Descript-exported xml under `rough-cuts/`, or the remap script is missing). Print the `errors` array verbatim, then stop.
- **Exit 1 (rerun_prompt):** all inputs present, but the remap output already exists from a previous run. Proceed to Step 2.
- **Exit 0 (ready):** all inputs present, no existing output. Skip to Step 3.

The JSON payload reports `manifest_path`, `raw_path` and `raw_candidates` (the raw sources named in the manifest), `descript_xml` and `descript_candidates` (every xmeml under `rough-cuts/` carrying the `Exported by Descript` marker), `output_path`, and `remap_script`. Hold the payload for the rest of the workflow.

### Step 2: Handle existing remap output

Only reached on exit 1. Ask the user, verbatim:

```
The remapped xml already exists. Re-run? (y/n)
```

On `y`, continue to Step 3 (overwrite). On `n` or anything else, print `Exiting. No changes made.` and stop.

### Step 3: Resolve the Descript XML and the raw source

From the payload:

- **Descript XML:** if `descript_xml` is set (exactly one candidate), use it. If it is null because `descript_candidates` has more than one entry, list them and ask the user which one. Never auto-pick when ambiguous, and never feed the Buttercut rough-cut xml or a prior remap output into the remapper (the preflight already filters those out by the Descript marker).
- **Raw source:** if `raw_path` is set, use it. If it is null because the manifest names more than one source (`raw_candidates`, e.g. a multi-cam shoot), list them and ask which raw to remap onto.

### Step 4: Run the remap

```bash
python3 /Users/jashia/Documents/1_Projects/ai-system/connectors/buttercut-export/remap-descript-to-raw.py \
  --descript-xml <descript_xml> \
  --manifest <manifest_path> \
  --raw <raw_path> \
  --output <output_path>
```

The script prints the rough-cut span, fps, clip counts, and how many clips it split across select boundaries. If it exits non-zero, print its stderr and stop. Do not print the confirmation.

### Step 5: Verify, print confirmation, stop

Confirm the output references only the raw file:

```bash
grep -oE '<pathurl>[^<]+</pathurl>' <output_path> | sort -u
```

Expect a single `file://` URL pointing at the raw mp4. Then print exactly (substituting `output_path`):

```
Remapped edit ready at <output_path>. It references the original raw footage only, with the Descript cuts mapped to raw timecodes. Import it into your NLE (in DaVinci Resolve: File > Import > Timeline), then run /video polish when ready.
```

Use full absolute paths so they are cmd-clickable. Do not invoke any downstream skill. Stop.

### Constraints specific to `remap`

- **Non-destructive.** Writes a new xml only. Never edits the Descript export, the manifest, or the raw.
- **Detect, do not guess.** The Descript export is the xmeml under `rough-cuts/` carrying the `Exported by Descript` marker. If there are several, ask. Never remap the Buttercut rough-cut xml or a prior remap output.
- **Manifest is required.** If `selects-manifest.json` is missing the preflight fails. Run `/video selects` first.
- **Pre-flight failures must be loud.** Print the exact `errors` array with the absolute paths.
- **No auto-chain.** Wrapper stops after Step 5.
- **No em dashes anywhere.** Use periods, commas, colons, parens.
- **All paths are absolute.** Print full `/Users/jashia/...` paths so they are cmd-clickable.

## assets

Invoked as `/video assets <slug>`.

Generate the visual asset library for a video. Reads the associate producer's `animation-ideas.md`, classifies each item, and routes it to the right generator: Remotion for precise overlays, Replicate for generative B-roll, and a manual README for anything a human must provide. Writes the whole bundle to `assets/` in the working folder so the user can drag the folder into DaVinci. Idempotent (existing files are skipped) and cost-aware (Replicate spend is estimated and confirmed before the first call).

### Workflow

```
Task Progress:
- [ ] Step 1: Pre-flight checks (preflight-assets.py)
- [ ] Step 2: Handle existing assets/ (re-run prompt or proceed)
- [ ] Step 3: Parse and classify animation-ideas.md
- [ ] Step 4: Write the asset plan to assets/plan.json
- [ ] Step 5: Estimate AI generation cost, confirm with user if > $5
- [ ] Step 6: Generate Remotion overlays
- [ ] Step 7: Generate AI clips via Replicate
- [ ] Step 8: Write manual README and the top-level MANIFEST.md
- [ ] Step 9: Print confirmation and stop
```

### Step 1: Pre-flight checks

Run the bundled preflight script:

```bash
python3 /Users/jashia/Documents/1_Projects/ai-system/.claude/skills/video/scripts/preflight-assets.py <slug>
```

Exit codes:

- **2 (failed):** print the `errors` array from the JSON payload verbatim, then stop. Common failures are `animation-ideas.md` missing (run `/associate-producer` first), `selects-manifest.json` missing (run `/video selects` first), or the Replicate connector absent at `connectors/ai-video/replicate.py`.
- **1 (rerun_prompt):** `assets/` already contains generated files. Go to Step 2.
- **0 (ready):** all inputs are present and `assets/` is empty. Skip to Step 3.

Hold the JSON payload. It carries every absolute path you need later (assets_dir, overlays_dir, broll_dir, manual_dir, manifest_path, plan_path, remotion_dir, animation_ideas_path, selects_manifest_path).

### Step 2: Handle existing assets

Only reached on exit 1.

Ask the user verbatim:

```
assets/ already has generated files. Re-run? Existing files are kept (the action is idempotent, only missing assets are generated). (y/n)
```

On `y`, continue to Step 3. On `n` or anything else, print `Exiting. No changes made.` and stop.

### Step 3: Parse and classify

Run the parser, passing both the animation ideas file and the selects manifest:

```bash
python3 /Users/jashia/Documents/1_Projects/ai-system/.claude/skills/video/scripts/parse-animations.py \
  <animation_ideas_path> \
  <selects_manifest_path>
```

The script returns each animation item with: `id`, `name`, `anchor`, `offset_ms`, `duration_ms`, `target_timestamp` (resolved from the Timing Report table in the file, or the selects manifest as a fallback), `spec` (concatenated description), and `heuristic_class` (a first-pass guess at `remotion`, `ai-clip`, or `manual`).

**Review every item before treating the heuristic as final.** The heuristic looks for keywords like "B-roll" or "mood shot" → ai-clip, "screenshot" or "real photo" → manual, otherwise remotion. Override when the spec text makes the right answer obvious. Classification rules:

| Class      | When                                                          | Examples                                                                                                               |
| ---------- | ------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `remotion` | Precise, code-driven, deterministic                           | Lower thirds, title cards, code overlays, callout text, data viz, typing animations, file-tree visuals, brand graphics |
| `ai-clip`  | Generative, conceptual, atmospheric                           | B-roll, mood shots, abstract visuals, scene transitions, "the feeling of X" footage                                    |
| `manual`   | Needs a human or a real asset the system should not fabricate | Real screenshots of the user's app, photos of the user, hand-drawn diagrams, anything legally sensitive                |

### Step 4: Write the asset plan

Create the folder skeleton in the working folder using the paths from the preflight payload:

```bash
mkdir -p <overlays_dir> <broll_dir> <manual_dir>
```

Then write the classified plan to `<plan_path>` (which is `<assets_dir>/plan.json`). The file is the single source of truth for the rest of the workflow; every step updates it as it goes.

Shape:

```json
{
  "slug": "<slug>",
  "generated_at": "<ISO 8601 timestamp>",
  "items": [
    {
      "id": "G1",
      "name": "TwoBrains",
      "class": "remotion",
      "anchor": "Your AI has two brains",
      "offset_ms": 0,
      "duration_ms": 3000,
      "target_timestamp": "00:00:00,004",
      "target_path": "<assets_dir>/overlays/G1.mp4",
      "spec": "...",
      "model": null,
      "prompt": null,
      "status": "pending",
      "error": null
    }
  ]
}
```

`target_path` uses `.mp4` for ai-clips and for Remotion overlays that do not need transparency. Use `.mov` (ProRes 4444 with alpha) when the spec explicitly asks for transparency, callouts that sit over face-cam, or "alpha channel" anywhere in the description. For ai-clip items, populate `model` with a video model id and leave `prompt` to be filled at generation time in Step 7. **Two backends are available:** Replicate ids (`veo-3` [default], `veo-3-fast`, `kling-1.5`, `luma-ray`) and Gemini Veo ids (`veo-3.1-fast-generate-001` [default, $0.10/s 720p], `veo-3.1-generate-001` [quality, $0.40/s], `veo-3.1-lite-generate-001` [cheap drafts, $0.05/s, text-to-video only]). The older `veo-3.0-*`, `veo-2.0-*`, and `veo-3.1-*-preview` ids are deprecated (gone from the connector — they now error) so use only the three above. A Gemini id generates on the Vertex-first backend (free Cloud credit, then the paid Gemini key — same key as `/image`); see the routing rule in Step 5.

### Step 5: Cost estimate and confirmation

**Backend routing (applies to Step 5 and Step 7).** Pick the connector by the item's `model`:
- Gemini Veo ids (`veo-3.1-generate-001`, `veo-3.1-fast-generate-001`, `veo-3.1-lite-generate-001`) → `connectors/ai-video/gemini_veo.py` (Vertex-first; free Cloud credit, then paid key).
- Replicate ids (`veo-3`, `veo-3-fast`, `kling-1.5`, `luma-ray`) → `connectors/ai-video/replicate.py`.
Both expose the same `--prompt/--output/--model/--duration/--aspect-ratio/--estimate-only` flags, so only the script path changes.

For each `ai-clip` item, call the routed connector in estimate-only mode and sum:

```bash
# Replicate backend
python3 /Users/jashia/Documents/1_Projects/ai-system/connectors/ai-video/replicate.py \
  --estimate-only --model <model> --duration <seconds>
# — or — Gemini Veo backend
python3 /Users/jashia/Documents/1_Projects/ai-system/connectors/ai-video/gemini_veo.py \
  --estimate-only --model <model> --duration <seconds>
```

Round `duration_ms / 1000` up to the nearest whole second for billing purposes. Default model is `veo-3` (Replicate) unless the spec text names a different supported id from either backend.

Print a cost table to the user before generating:

```
| id | model | duration | est. cost |
|----|-------|----------|-----------|
| G3 | veo-3 | 5s       | $3.75     |
| G6 | veo-3 | 3s       | $2.25     |
| total |    |          | $6.00     |
```

**If the total exceeds $5.00, ask verbatim:**

```
Estimated AI-video cost: $X.XX. Proceed? (y/n)
```

On `n` or anything other than `y`, skip ai-clip generation entirely; Remotion and manual items still proceed. Mark every skipped ai-clip item as `status: "skipped"`, `error: "cost gate"` in `plan.json` and reflect this in the MANIFEST. If the total is ≤ $5.00, proceed without prompting.

### Step 6: Generate Remotion overlays

For each `remotion` item with `status: "pending"`:

1. **Idempotency check.** If `target_path` already exists on disk, set `status: "done"` in `plan.json` and skip.

2. **Locate or scaffold the Remotion project.** If `<remotion_dir>` exists (the preflight payload reports `remotion_exists`), add a new composition there. Otherwise scaffold one:

   ```bash
   cd <docs_folder> && npx create-video@latest --yes --blank --no-tailwind remotion
   ```

3. **Add the composition.** Edit `remotion/src/Root.tsx` (or `Composition.tsx`) to register a new `<Composition>` with `id={item.id}`, fps=30, `durationInFrames = Math.ceil(item.duration_ms / 1000 * 30)`. Implement the component from the spec text. For brand-conformant designs, use the Grounded Premium tokens: navy `#0A1628`, amber `#F59E0B`, Sora (headlines), Source Sans 3 (body). Consult the `/remotion` skill's rule files for component patterns (timing, sequencing, text animations, transparent videos).

4. **Render.** Use `.mp4` by default. Use `.mov` with ProRes 4444 alpha when the spec calls for transparency:

   ```bash
   cd <docs_folder>/remotion && npx remotion render <id> ../assets/overlays/<id>.mp4
   ```

   For alpha:

   ```bash
   cd <docs_folder>/remotion && npx remotion render <id> ../assets/overlays/<id>.mov \
     --codec=prores --prores-profile=4444 --pixel-format=yuva444p10le
   ```

5. **Update plan.json.** Set `status: "done"`. On failure, set `status: "error"` with the stderr text and continue with the next item. Do not abort the whole run.

### Step 7: Generate AI clips via Replicate

Only runs if the user did not deny the cost gate in Step 5.

For each `ai-clip` item with `status: "pending"`:

1. **Idempotency check.** If `target_path` already exists, mark `done` and skip.

2. **Build the prompt from the spec text.** Strip Remotion-specific instructions (scene layouts, frame counts, sub-beat tables) and keep the visual description. Keep prompts under 500 characters; `veo-3` and friends prefer concise prompts. Save the final prompt back into `plan.json` so the MANIFEST and any re-run can reproduce it.

3. **Call the routed connector** (Step 5 rule — Gemini Veo ids → `gemini_veo.py`, Replicate ids → `replicate.py`; same flags):

   ```bash
   # Replicate backend
   python3 /Users/jashia/Documents/1_Projects/ai-system/connectors/ai-video/replicate.py \
     --prompt "<built prompt>" --output <target_path> \
     --model <model> --duration <seconds> --aspect-ratio 16:9
   # — or — Gemini Veo backend (paid Gemini key)
   python3 /Users/jashia/Documents/1_Projects/ai-system/connectors/ai-video/gemini_veo.py \
     --prompt "<built prompt>" --output <target_path> \
     --model <model> --duration <seconds> --aspect-ratio 16:9
   ```

4. **Handle failures non-fatally.** If the connector exits non-zero or raises, capture stderr, set `status: "error"` with the message in `plan.json`, and continue with the next item. Do not abort.

5. **Update plan.json** as each clip completes.

### Step 8: Manual README and top-level MANIFEST

For every `manual` item, append a section to `<manual_dir>/README.md`. Create the file with a single intro paragraph if it does not exist yet:

```markdown
# Manual assets needed for <slug>

Each item below has to be produced by hand (real screenshot, photo, hand-drawn diagram, etc.) and dropped into this folder before the polish pass. The MANIFEST.md at the parent level references the expected filenames.

## <id> <name>

- **Target timestamp:** <target_timestamp, or "TBD">
- **Duration:** <duration_ms> ms
- **Why manual:** <one-line reason: real screenshot, sensitive content, hand-drawn, etc.>
- **Expected filename:** assets/manual/<id>.<ext> (.png for stills, .mp4 for clips)
- **Description:** <spec text from animation-ideas>
```

Then write `<assets_dir>/MANIFEST.md`, listing every item (Remotion + AI clips + manual) in target-timestamp order:

```markdown
# Asset Manifest: <slug>

Generated <ISO timestamp>. Re-run `/video assets <slug>` to refresh missing items.

| id  | name                   | timestamp    | source   | file                   | status  |
| --- | ---------------------- | ------------ | -------- | ---------------------- | ------- |
| G1  | TwoBrains              | 00:00:00,004 | remotion | assets/overlays/G1.mp4 | done    |
| G2  | MemoryVsKnowledgeSplit | 00:01:10,527 | remotion | assets/overlays/G2.mov | done    |
| G3  | ChaoticRepo            | 00:01:27,607 | ai-clip  | assets/broll/G3.mp4    | error   |
| G4  | MemPalaceFlash         | 00:03:55,954 | manual   | assets/manual/G4.png   | PROVIDE |

## Prompts and specs

### G1 TwoBrains (remotion)

<spec text used for the composition>

### G3 ChaoticRepo (ai-clip)

- **Model:** veo-3
- **Prompt:** <prompt used>
- **Error:** replicate timeout after 600s

### G4 MemPalaceFlash (manual)

- **Why manual:** Real GitHub readme screenshot, should not be fabricated.
- **Description:** <spec text>

## Cost

Replicate: $X.XX across N clips. M errored, K skipped (cost gate).
```

Sort the manifest table by `target_timestamp` when present so the user reads it in cut order.

### Step 9: Print confirmation and stop

Print exactly (substituting counts and the resolved slug):

```
Assets generated at /Users/jashia/Documents/1_Projects/videos/<slug>/assets/. <N> Remotion overlays, <M> AI clips, <K> manual items. Manifest at /Users/jashia/Documents/1_Projects/videos/<slug>/assets/MANIFEST.md. Open DaVinci and import the assets/ folder when ready.
```

Use full absolute paths so they are cmd-clickable. Do not invoke `/video polish` or any other downstream skill. Do not auto-import to DaVinci. Stop.

### Constraints specific to `assets`

- **Idempotent.** Check file existence before generating. The action is safe to re-run; only missing assets are produced.
- **No DaVinci automation.** Stop at the assets folder. The user opens DaVinci manually.
- **Replicate failures are non-fatal.** Log them in `plan.json` and `MANIFEST.md` as `status: "error"` and continue with the rest. Do not abort the whole run.
- **Cost discipline.** Sum estimates before any Replicate call. Ask for confirmation above $5.00. If the user declines, skip ai-clips and keep doing Remotion and manual.
- **Manual items are listed, not generated.** Never invent a screenshot or photo. The README tells the user exactly what to produce.
- **Pre-flight failures must be loud.** Print the exact `errors` array. The user should know which path is missing and what to do.
- **Do not modify `status`, `new`, or `selects` actions.** This action is composed alongside, not on top of, the others.
- **No em dashes anywhere.** Use periods, commas, colons, parens.
- **All paths are absolute.** Print full `/Users/jashia/...` paths everywhere.

## lay-in

Invoked as `/video lay-in <slug>`.

Place the motion-graphics assets onto the edit timeline by generating a full-stack DaVinci-importable timeline (FCP7 `xmeml`). The base edit (the `/video remap` output, or the `/video selects` rough cut) stays on V1 verbatim; every overlay and card is appended on tracks above it at the in-point encoded in its filename. The user then does **File > Import > Timeline** in DaVinci and the whole stack lands in one shot. Non-destructive: writes a new xml and touches none of the inputs.

Why import-XML and not the Resolve scripting API: the free version of DaVinci Resolve does not expose the scripting API (it is Studio-only, returns `None` both externally and in-app), but every edition imports timeline XML. The generated file is the equivalent automation that works on free Resolve.

**Naming contract.** Every asset filename starts with its in-point as MMSS (minutes then seconds): `1216_punch_kung-fu.mov` -> 12:16. Start frame = `round((mm*60 + ss) * fps)`, where fps is read from the base timeline (never assumed). Assets live under `assets/overlays/` (alpha `.mov`, packed onto overlay tracks above the face cam) and `assets/cards/` (opaque full-frame cutaways, placed on the top track). This is the `assets/` layout from a Remotion render; it is a superset of what `/video assets` emits, so a project may carry either.

### Workflow

```
Task Progress:
- [ ] Step 1: Pre-flight checks (preflight-lay-in.py)
- [ ] Step 2: Handle existing output (re-run prompt or proceed)
- [ ] Step 3: Resolve the base timeline (disambiguate if needed)
- [ ] Step 4: Run the lay-in
- [ ] Step 5: Verify, print confirmation, stop
```

### Step 1: Pre-flight checks

Run the bundled preflight script:

```bash
python3 /Users/jashia/Documents/1_Projects/ai-system/.claude/skills/video/scripts/preflight-lay-in.py <slug>
```

Exit-code contract:

- **Exit 2 (failed):** a required input is missing. Print the `errors` array verbatim, then stop. Common failures are no raw-referencing base timeline under `rough-cuts/` (run `/video remap` or `/video selects` first), no MMSS-named assets under `assets/overlays` or `assets/cards` (run `/video assets` or render the graphics first), or `ffprobe` not on PATH (`brew install ffmpeg`).
- **Exit 1 (rerun_prompt):** all inputs present, but the lay-in output already exists. Proceed to Step 2.
- **Exit 0 (ready):** all inputs present, no existing output. Skip to Step 3.

The JSON payload reports `base_xml` and `base_candidates` (raw-referencing timelines under `rough-cuts/`, Descript exports excluded), `overlay_count` and `card_count`, `assets_dir`, `output_path`, and `layin_script`. Hold the payload for the rest of the workflow.

### Step 2: Handle existing output

Only reached on exit 1. Ask the user, verbatim:

```
The full-stack graphics timeline already exists. Re-run? (y/n)
```

On `y`, continue to Step 3 (overwrite). On `n` or anything else, print `Exiting. No changes made.` and stop.

### Step 3: Resolve the base timeline

From the payload:

- If `base_xml` is set (one candidate, or the prefer-remap rule narrowed it to one), use it.
- If `base_xml` is null because `base_candidates` has more than one entry that the rule could not narrow, list them and ask the user which to build on. The remap output is the usual answer (the Descript-polished cut); the Buttercut rough cut is the answer only if no Descript round-trip happened. Never auto-pick when ambiguous, and never feed a prior `*-with-graphics.xml` back in (the preflight already filters those out).

If the user picks a base that differs from `output_path`, recompute the output as `<base-stem>-with-graphics.xml` in `rough-cuts/`.

### Step 4: Run the lay-in

```bash
python3 /Users/jashia/Documents/1_Projects/ai-system/.claude/skills/video/scripts/lay-in-graphics.py \
  --base <base_xml> \
  --assets-dir <assets_dir> \
  --output <output_path>
```

The script reads the base fps, ffprobes each asset for its frame count, parses MMSS into start frames, packs overlays onto as few tracks as possible (opening a second track only when two overlap in time), puts cards on top, appends the new tracks to the base, writes the xml, and prints a placement table plus a self-validation line. To preview without writing, add `--plan`. If the script exits non-zero, print its stderr and stop. Do not print the confirmation.

### Step 5: Verify, print confirmation, stop

Confirm the script's final line reports `graphics placed: <N>/<N>` matching `assets_total` from the preflight. Then print exactly (substituting `output_path`):

```
Full-stack timeline ready at <output_path>. Your remapped edit is on V1 (untouched); overlays and cards are on the tracks above at their MMSS in-points. In DaVinci: File > Import > Timeline, then pick this file. Check overlay alpha if any .mov shows a black box, and apply any freeze-frame holds or additive-card cuts noted in assets/MANIFEST.md by hand (the lay-in places clips at native length only). Finish in DaVinci, then /video upload when the final is rendered.
```

Use full absolute paths so they are cmd-clickable. Do not invoke any downstream skill. Stop.

### Constraints specific to `lay-in`

- **Non-destructive.** Writes a new xml only. Never edits the base timeline, the assets, the raw, or the manifest.
- **V1 is verbatim.** The face-cam base track is preserved exactly (ElementTree round-trip, including the `<file id=.. />` back-reference reuse). Only ADD tracks above it.
- **fps comes from the base timeline.** Read `<rate><timebase>` + `<ntsc>` from the base xml. Never assume 30. Warn loudly if any asset's source fps differs from the timeline.
- **Detect, do not guess the base.** Multiple raw-referencing timelines means ask. Prefer the remap output; never feed a prior lay-in output back in.
- **Track rule:** cards on top (opaque cutaways), overlays packed below them (alpha over face), a new overlay track only on genuine time-overlap. Freeze-frame HUD holds and additive-card cuts stay manual; the lay-in places at native length.
- **No DaVinci automation.** The scripting API is Studio-only and unavailable here. The import is a manual step. Stop at the generated xml.
- **No auto-chain.** Wrapper stops after Step 5.
- **No em dashes anywhere.** Use periods, commas, colons, parens.
- **All paths are absolute.** Print full `/Users/jashia/...` paths so they are cmd-clickable.

## upload

Invoked as `/video upload <slug>`.

Package and publish a finished video to YouTube. Drafts AI-written metadata from the script + transcript, generates an SRT captions track from the word-level transcript, generates thumbnail variants from face-cam frames, then waits behind a hard approval gate before calling `videos.insert`. Default privacy is `unlisted`. The user makes the final public/unlisted call from YouTube Studio.

This is the only `/video` action that touches an external service in a non-reversible way. The approval gate is non-negotiable. Never auto-publish.

### Workflow

```
Task Progress:
- [ ] Step 1: Pre-flight checks (preflight-upload.py)
- [ ] Step 2: Handle existing metadata (re-run prompt or proceed)
- [ ] Step 3: AI-draft metadata to producer/upload-metadata.md
- [ ] Step 4: Generate SRT captions
- [ ] Step 5: Generate thumbnail variants
- [ ] Step 6: Approval gate (HARD)
- [ ] Step 7: Upload via youtube_client.py (unlisted)
- [ ] Step 8: Write retrospective stub
- [ ] Step 9: Print confirmation and stop
```

### Step 1: Pre-flight checks

Run the bundled preflight script:

```bash
python3 /Users/jashia/Documents/1_Projects/ai-system/.claude/skills/video/scripts/preflight-upload.py <slug>
```

Exit-code contract:

- **Exit 2 (failed):** one or more required inputs are missing. The JSON's `errors` array lists every problem with absolute paths and a one-line fix. Print the errors verbatim. Stop.
- **Exit 1 (rerun_prompt):** all inputs are present, but `producer/upload-metadata.md` already exists from a previous run. Proceed to Step 2.
- **Exit 0 (ready):** all inputs present, no existing metadata. Skip to Step 3.

What it checks:

1. `finals/` exists and contains **exactly one** `.mp4`. If 0, fail. If 2+, fail with the candidate list so you can ask which is the publish target.
2. Obsidian meta folder exists with at least one of `script.md`, `task-list.md`, or `brief.md`.
3. A final transcript JSON exists. Resolution order: `transcripts/<final-stem>.json`, then `transcripts/final.json`, then a lone `.json` under `transcripts/`.
4. YouTube OAuth token exists at `~/.youtube_cli/token.json`. If missing, the fix is to run `uv run /Users/jashia/Documents/1_Projects/ai-system/connectors/youtube/youtube_client.py auth` (this uses the existing OAuth setup, do not invent a new auth flow).

The JSON payload reports `final_mp4`, `plan_file`, `transcript_path`, `metadata_path`, `retrospective_path`, and `final_candidates`. Hold onto it for the rest of the workflow.

If preflight failed specifically because `finals/` has 2+ mp4s, ask the user which `final_candidates` entry is the publish target, then re-run with the bad ones removed or moved aside before proceeding. Do not silently pick one.

### Step 2: Handle existing metadata

Only reached if preflight returned exit code 1.

Ask the user, verbatim:

```
upload-metadata.md already exists at <metadata_path>. Re-draft? (y/n)
```

On `y`, continue to Step 3 and overwrite the file. On `n`, skip to Step 4 (reuse the existing metadata). Any other response: print `Exiting. No changes made.` and stop.

### Step 3: AI-draft metadata

Read these three sources:

- `plan_file` from the preflight payload (one of `script.md`, `task-list.md`, `brief.md`).
- `transcript_path` from the preflight payload. Use the `text` field for narrative context. Use `segments` only if a sharper time-anchored quote is needed.
- (Optional) `producer/coverage.md` if it exists in the meta folder. It often has the framing the user actually delivered on camera.

Draft three artifacts:

1. **Title.** Under 70 chars total. Hook-oriented, specific. Avoid clickbait that doesn't match the content. Generally a verb + concrete object. The user's content is technical walkthroughs for builders, not lifestyle.
2. **Description.** Three paragraphs:
   - Paragraph 1: Hook + the gap this video closes (2-3 sentences).
   - Paragraph 2: What the viewer learns / sees demoed (2-4 sentences, can include a short bulleted list).
   - Paragraph 3: CTA + links. Defaults: AI Office Hours signup, subscribe ask, what the next video covers. Pull actual links from the user's prior descriptions if available, otherwise leave a clearly-marked `<link>` placeholder.
3. **Tags.** 10 to 15 relevant tags. Drawn from the content. Lowercase, no `#`, no quotes. Mix of broad (`ai workflow`, `claude code`) and specific (the pillar, the demo subject, named tools).

Write all three to `producer/upload-metadata.md` with this exact shape:

```markdown
---
slug: <slug>
final_mp4: <absolute path to the final mp4>
hook_word: <one or two words pulled from the title for thumbnail overlay>
captions_path: <absolute path the SRT will be written to, finals/<final-stem>.srt>
privacy_default: unlisted
drafted: <today YYYY-MM-DD>
---

# Title

<title text, single line>

# Description

<paragraph 1>

<paragraph 2>

<paragraph 3>

# Tags

tag1, tag2, tag3, ...
```

`hook_word` is the single most evocative word or short phrase from the title. Uppercase it in your head, the thumbnail script will handle the casing. Examples: title `Build a YouTube uploader in Claude Code` → hook `BUILD`. Title `Why I quit Grafana to build AI workflows` → hook `I QUIT`.

Do not invoke another skill. The draft is yours to write.

### Step 4: Generate SRT captions

Run the SRT generator against the resolved transcript:

```bash
python3 /Users/jashia/Documents/1_Projects/ai-system/.claude/skills/video/scripts/transcript-to-srt.py \
  <transcript_path> \
  -o <docs-folder>/finals/<final-stem>.srt
```

`<final-stem>` is the final mp4 filename without extension. The script groups words into ~7-second cues, breaking at sentence boundaries, and writes valid SRT.

If the script exits non-zero, print its stderr and stop. Do not proceed to thumbnails.

### Step 5: Generate thumbnail variants

Produce three 1280x720 thumbnails. Default to the **AI hybrid** path (striking on-brand imagery + the real headshot + a bold headline, via the `/image` skill); keep the ffmpeg frame-grab as a guaranteed floor and fallback.

**5a. Floor first (always works, no API).** Run the ffmpeg generator — it writes `thumbnail-v1/v2/v3.png` from face-cam frames with the hook word overlaid:

```bash
python3 /Users/jashia/Documents/1_Projects/ai-system/.claude/skills/video/scripts/generate-thumbnails.py \
  <final_mp4> \
  --hook "<hook_word from metadata frontmatter>" \
  --out-dir <docs-folder>/finals
```

If this exits non-zero, print stderr and stop (no thumbnails at all is a hard fail).

**5b. AI hybrid (preferred).** Follow the `/image` skill's `thumbnail` action to overwrite `thumbnail-v1.png` and `thumbnail-v2.png` with AI hybrids, leaving `-v3.png` as the ffmpeg floor. From `producer/upload-metadata.md`, choose a 3-6 word headline (curiosity hook, not the title verbatim) + an amber accent word, then for each of v1 and v2:

```bash
# 1) background imagery — no text (see references/thumbnail-prompts.md)
python3 /Users/jashia/Documents/1_Projects/ai-system/connectors/ai-image/gemini_image.py \
  --model gemini-2.5-flash-image --aspect-ratio 16:9 \
  --prompt "<imagery prompt for the topic; keep the right third darker; no text/words/logos>" \
  --output <docs-folder>/assets/thumbs/bg-1.png

# 2) composite the real headshot + brand headline onto it
uv run --with pillow,pyyaml python \
  /Users/jashia/Documents/1_Projects/ai-system/connectors/ai-image/compose_thumbnail.py \
  --background <docs-folder>/assets/thumbs/bg-1.png \
  --headline "<HEADLINE>" --accent-word "<WORD>" \
  --headshot "<auto-detected headshot — see /image skill>" --headshot-side right \
  --output <docs-folder>/finals/thumbnail-v1.png
```

Vary imagery/headline emphasis for v2. Read each PNG and apply the critique→iterate loop from the `/image` skill (legible at 120px, face prominent, on-brand). **If the AI path errors or no Gemini key is configured, skip 5b silently — the Step 5a ffmpeg variants stand as the floor.**

Output: `finals/thumbnail-v1.png`, `-v2.png`, `-v3.png` at 1280x720.

### Step 6: Approval gate (HARD)

This is the publish moment. Before this step, nothing has touched YouTube.

Print:

1. The full contents of `producer/upload-metadata.md` (title, description, tags) so the user can read what will be uploaded.
2. The three thumbnail variant paths, full absolute paths, so they're cmd-clickable.
3. A reminder line that default privacy is `unlisted`, not `public`.

Then ask, verbatim:

```
Review the metadata and thumbnails above.
Type 'publish v1' (or 'publish v2', 'publish v3') to upload with that thumbnail.
Type 'cancel' to abort. Anything else is treated as cancel.
```

Wait for the explicit response. **Do not default to publish on ambiguity.** Anything other than `publish v1|v2|v3` aborts: print `Cancelled. No upload.` and stop.

### Step 7: Upload via youtube_client.py

Only reached on `publish v1|v2|v3`.

Extract title, description, and tags from `upload-metadata.md`:

- The script intentionally writes the description and tags as plain markdown sections, not fenced blocks. Pass the metadata file directly as `--description-file` (the description sits between `# Description` and `# Tags`). If the YouTube description should not include the `# Tags` section verbatim, split the file at `# Tags` before passing the description and write the tags portion to a sidecar file. Recommended: emit two scratch files from the metadata under `producer/`: `upload-description.txt` and `upload-tags.txt`. Keep these out of the upload-metadata canonical doc.
- Pass tags via `--tags-file <tags file>` (newline or comma separated, `#` lines ignored).

Call the YouTube client. Default privacy stays `unlisted`:

```bash
uv run /Users/jashia/Documents/1_Projects/ai-system/connectors/youtube/youtube_client.py video upload \
  <final_mp4> \
  --title "<title from metadata>" \
  --description-file <docs-folder>/producer/upload-description.txt \
  --tags-file <docs-folder>/producer/upload-tags.txt \
  --thumbnail <docs-folder>/finals/thumbnail-v<N>.png \
  --captions <docs-folder>/finals/<final-stem>.srt \
  --captions-language en \
  --privacy unlisted
```

`<N>` is the variant from the user's `publish v<N>` response.

Capture the YouTube video ID and URL from the script's stdout. The script prints the URL as `URL: https://youtube.com/watch?v=<id>` and also emits a JSON object with `id`, `url`, and `privacy` at the end.

If the upload exits non-zero, print the stderr verbatim. Do not write a retrospective stub. Stop.

### Step 8: Write retrospective stub

On success, create or append to `<obs-folder>/retrospective.md`. If the file already exists, append a new section; do not overwrite prior retrospectives.

Template:

```markdown
---
slug: <slug>
published: <today YYYY-MM-DD>
youtube_id: <id>
youtube_url: <url>
privacy: unlisted
status: retrospective-pending
---

## Published <today YYYY-MM-DD>

- YouTube URL: <url>
- Privacy: unlisted
- Thumbnail used: thumbnail-v<N>.png

### 1% Better retrospective

Pending. Run the `/youtube-content` Phase 6 retrospective workflow when ready.
```

The presence of `retrospective.md` is what `/video status` reads to mark the video as `done`.

### Step 9: Print confirmation and stop

Print exactly (substituting actual values):

```
Uploaded to <youtube_url>. Privacy: unlisted. Review at YouTube Studio, set public when ready. Retrospective stub at <retrospective_path> (run the /youtube-content Phase 6 retrospective when ready).
```

Use full absolute paths so they are cmd-clickable. Do not invoke `/buffer`, `/linkedin-post`, `/x-post`, or any other distribution skill. Stop.

### Constraints specific to `upload`

- **Approval gate is non-negotiable.** No path leads to `videos.insert` without explicit `publish v1|v2|v3` from the user. Treat any other input as cancel.
- **Default privacy is `unlisted`.** Never pass `--privacy public` automatically. The user makes that decision in YouTube Studio.
- **No cross-platform fanout.** Do not auto-post to LinkedIn, X, Buffer, etc. That belongs to a future `/video distribute` action.
- **Reuse the existing OAuth flow.** Do not create new auth code. If the token is missing, the preflight tells the user to run `uv run youtube_client.py auth`.
- **Pre-flight failures are loud.** Print the `errors` array verbatim with the absolute paths and one-line fixes.
- **Captions failure is non-fatal for the video.** If `captions.insert` fails after the video uploads (e.g. quota or a malformed cue), the upload still counts. Report the captions error and continue with Step 8. The user can manually upload captions from YouTube Studio.
- **No em dashes anywhere.** Use periods, commas, colons, parens.
- **All paths are absolute.** Print full `/Users/jashia/...` paths so they are cmd-clickable.

## Constraints

- **`status` is read-only.** The status action must never create, move, or modify files in either tree. The Python script only calls `Path.is_file()`, `Path.is_dir()`, and `Path.iterdir()` (no writes).
- **Both trees are scanned.** A folder existing in only one tree is still listed; phase detection accounts for missing siblings.
- **Slugs are the join key.** The folder names must match between trees (the `videoNN-slug` convention from `/story-development` and `/video new`). Folders not starting with `video` are ignored.

## Related skills

- `/story-development` — creates the pre-production `script.md`
- `/associate-producer` — produces `selects-manifest.json`
- `/remotion` — final finishing
- `/youtube-content` — coordinator skill with phased workflow
