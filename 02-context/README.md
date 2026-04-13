# 02. Context Engineering

> Your agent's operating manual.

## What this is

Context Engineering is the discipline of assembling the rules, skills, and system prompts that shape how your agent behaves. It's the rulebook the agent reads before doing anything.

This is *Drawer 1* of the three-drawer model: **rules you author deliberately** for your agent.

## What lives here

- `AGENT.md` — the universal rulebook (works as CLAUDE.md / GEMINI.md / etc. via symlink)
- `skills/` — reusable packaged workflows (also shown in Tier 2, component 05)
- `templates/` — starter AGENT.md files for different use cases

## Why it matters

Without context engineering, every session starts from zero. With it, your agent opens with your voice, your preferences, your rules, and your working style loaded by default.

## Further reading

[Full guide](../guides/02-context.md)
