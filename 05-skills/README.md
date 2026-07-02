# 05. Skills

> Capabilities your agent can call.

## What this is

Skills are packaged, reusable workflows. Each one bundles instructions, optional tools, and supporting files into a single callable unit your agent can invoke by name.

A skill is the difference between "here's a 2000-word prompt I paste every Monday" and "`/weekly-review`".

## What lives here

```
skills/
├── video/                 REAL: my full video production pipeline (see below)
├── daily-checkin.md       start your day right
├── capture.md             quick capture of anything
├── weekly-review.md       end-of-week reflection
├── skill-creator.md       meta-skill for building new skills
└── (your skills here)
```

## A real one to download

[`video/`](video/) is a working skill lifted straight from my system: an 8-action video production pipeline (bootstrap, on-set producer, transcribe + selects, Descript remap, asset generation, timeline lay-in, gated YouTube upload). Download it, read its [README](video/README.md) for what to adapt, and use its SKILL.md as a reference for structuring your own multi-action skills.

## Why it matters

Skills turn one-off prompts into a durable library. The more you use your system, the more valuable it gets. Compounding, not repetition.

## Further reading

[Full guide](../guides/05-skills.md)
