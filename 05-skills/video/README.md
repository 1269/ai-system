# /video — Video Production Pipeline Skill

A real, working Claude Code skill pulled straight from my system. It runs my entire YouTube production pipeline as one multi-action slash command:

| Action | What it does |
|--------|--------------|
| `status` | Scans project folders and reports each video's phase |
| `new` | Bootstraps a new video project with a Q&A intake |
| `record` | Live on-set producer: holds your script and interviews you one question at a time while you record |
| `selects` | Transcribes raw footage, runs coverage analysis, assembles a rough-cut NLE timeline |
| `remap` | Relinks a Descript-polished edit back to the original raw footage |
| `assets` | Generates Remotion overlays + AI B-roll from an animation-ideas doc |
| `lay-in` | Builds a DaVinci-importable timeline with all graphics placed at their in-points |
| `upload` | Drafts metadata, generates SRT captions + thumbnails, then publishes to YouTube behind a hard approval gate |

## How to use it

Drop the `video/` folder into your project's `.claude/skills/` directory. Claude Code picks it up automatically and you invoke it as `/video <action> <slug>`.

## What you'll need to adapt

This is shipped exactly as I run it, which means it is wired to my machine. Before it works on yours:

1. **Paths.** Every absolute path starts with `/Users/jashia/...`. Search and replace with your own project roots (working files, Obsidian vault, connectors).
2. **Connectors it calls that are not in this repo:** an MLX Whisper transcriber, a YouTube upload client (OAuth), Replicate / Gemini video generation, and a Buttercut XML exporter (`gem install buttercut`). The SKILL.md shows the exact interface each one needs, so you can swap in your own equivalents.
3. **Tools:** ffmpeg on PATH, Python 3, Ruby 3 (for Buttercut), Node (for Remotion).

Even if you never run it end to end, the SKILL.md is the artifact worth reading: it shows how to structure a large multi-action skill with preflight scripts, exit-code contracts, hard approval gates before irreversible actions, and explicit constraints per action.

## Layout

```
video/
├── SKILL.md                  the full skill definition (all 8 actions)
├── references/
│   └── on-set-producer.md    persona + turn loop for the record action
└── scripts/                  deterministic helpers the skill shells out to
    ├── scan-projects.py      phase detection for status
    ├── bootstrap-video-project.sh
    ├── preflight-*.py        input checks with exit-code contracts
    ├── transcript-to-srt.py
    ├── generate-thumbnails.py
    ├── parse-animations.py
    └── lay-in-graphics.py
```
