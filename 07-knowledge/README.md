# 07. Knowledge Base

> The library your agent can reference.

## What this is

Your Knowledge Base is the external corpus your agent queries on demand: your notes, research, frameworks, book summaries, project briefs, and captured learnings.

This is *Drawer 3* of the three-drawer model: **reference material you curate**, queried when relevant.

Unlike Memory (which stores gist and pointers), the Knowledge Base holds full content. Memory tells the agent *where the book lives*. The Knowledge Base *is the book.*

## What lives here

A recommended structure using the **PSA method** (Projects, Systems, Archives):

```
knowledge/
├── 1-projects/       what you're actively working on
├── 2-systems/        durable frameworks, methods, tools you use
└── 3-archives/       completed projects, reference material
```

Most users will symlink this folder to an existing Obsidian vault, Notion workspace, or notes directory.

## Why it matters

Your agent is only as smart as the material it can reach. A well-organized Knowledge Base turns your years of notes into something your agent can surface at exactly the right moment.

## Further reading

[Full guide](../guides/07-knowledge.md)
