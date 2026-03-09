# AI System

> A personal AI system that learns who you are, remembers what you've done, and gets smarter every time you use it.

Most people use AI like a search engine — start fresh every time, re-explain everything, get generic answers. An AI system changes that. It gives any AI tool long-term memory, personalized context, and daily rituals that compound over time.

This repo is the open-source companion to my [YouTube channel](https://youtube.com/@jashia), where I build this system in public and teach you how to build your own.

---

## Start Here

**New to this?** Grab the [Starter Kit](starter-kit/AI-SYSTEM-STARTER.md). It's a single prompt you paste into any AI (ChatGPT, Claude, Gemini) that walks you through building your own system in ~15 minutes. No coding required.

**Want to go deeper?** Check the [guides](guides/) for detailed walkthroughs on specific capabilities.

---

## What's in an AI System?

```
┌─────────────────────────────────────────────┐
│              YOUR AI SYSTEM                 │
│                                             │
│  ┌───────────┐  ┌───────────┐  ┌─────────┐ │
│  │  Context   │  │  Memory   │  │ Rituals │ │
│  │  (who you  │  │  (what it │  │ (daily  │ │
│  │   are)     │  │  learned) │  │ habits) │ │
│  └───────────┘  └───────────┘  └─────────┘ │
│                                             │
│  ┌───────────┐  ┌───────────┐  ┌─────────┐ │
│  │  Skills    │  │   Tools   │  │  Voice  │ │
│  │  (reusable │  │  (integra-│  │ (talk,  │ │
│  │  prompts)  │  │   tions)  │  │ don't   │ │
│  │           │  │           │  │  type)   │ │
│  └───────────┘  └───────────┘  └─────────┘ │
└─────────────────────────────────────────────┘
```

**6 components, built in layers:**

| Component | What It Does | Complexity |
|-----------|-------------|------------|
| **Context** | Tells AI who you are, how you work, what you're building | Starter Kit |
| **Memory** | Stores decisions, patterns, and solutions across sessions | Starter Kit |
| **Rituals** | Daily prompts that keep you and your AI aligned | Starter Kit |
| **Skills** | Reusable prompts for tasks you repeat (emails, planning, analysis) | Easy |
| **Tools** | Connections to your calendar, tasks, notes, email | Medium |
| **Voice** | Talk to your AI system instead of typing | Advanced |

You don't need all six on day one. The Starter Kit gives you the first three.

---

## Repo Structure

```
ai-system/
├── starter-kit/          # Start here — one prompt, any AI, 15 minutes
├── templates/            # Copy-paste files for your own system
├── guides/               # Deep dives on each component
├── examples/             # Real-world skill and integration examples
└── diagrams/             # Architecture visuals
```

---

## Guides

Each guide corresponds to a video on the channel. Start with #1 and go in order, or jump to whatever you need.

| # | Guide | Video |
|---|-------|-------|
| 1 | [Getting Started](guides/01-getting-started.md) | [I'm Building My Own AI System](https://youtube.com/@jashia) |
| 2 | Daily Workflows *(coming soon)* | — |
| 3 | Second Brain Setup *(coming soon)* | — |
| 4 | Voice Pipeline *(coming soon)* | — |
| 5 | Memory Patterns *(coming soon)* | — |

---

## Who This Is For

- **Non-technical people** who use AI daily and want it to actually know them
- **Vibe coders** who build with AI and want a system, not just scattered conversations
- **Builders** who want to see how a real AI system is designed and evolving

---

## License

[MIT](LICENSE) — use it, fork it, make it yours.
