# 01. Input & Capture

> This is how you talk to an agent.

## What this is

Input & Capture is the component where the human meets the system. It has two halves people usually blur together:

- **Interface** — *where* you show up (Claude Code CLI, Slack, voice, web chat, mobile).
- **Capture** — *what* comes in through that interface (typed messages, transcripts, uploads, clipboard snippets).

The interface is where you show up. Capture is what comes with you when you do.

## What lives here

- `transcripts/` — meeting/voice/video transcripts the system can ingest
- `voice/` — voice note pipeline (optional, advanced)
- Interface configs for Slack, CLI, or other front-ends

## Why it matters

Garbage in, garbage out. A well-designed capture layer means your agent gets the *real* signal — your actual thoughts, your real meetings, your whole day — not just whatever you remember to type.

## Further reading

[Full guide](../guides/01-capture.md)
