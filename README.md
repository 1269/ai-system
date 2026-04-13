# AI System

> A personal AI system that learns who you are, remembers what you've done, and gets smarter every time you use it.

Most people use AI like a search engine. Start fresh every time, re-explain everything, get generic answers.

An AI system changes that. It gives any AI tool long-term memory, personalized context, and compound intelligence over time.

You're already using an AI **agent**. ChatGPT is one. Claude Code is one. Gemini is one. This repo is what every agent should *run on*: the infrastructure that makes them know you, remember what you've done, and get better the more you use them.

This repo is the open-source companion to my [YouTube channel](https://youtube.com/@jashia), where I build this system in public and teach you how to build your own.

---

## Start Here

Two ways in. Pick yours.

### Non-technical, 15 minutes, no code

Grab the [Starter Kit](starter-kit/AI-SYSTEM-STARTER.md). Paste one prompt into ChatGPT, Claude, or Gemini. It walks you through building a lightweight version of this system in any AI. No install required.

### Builders, clone and run

```bash
git clone https://github.com/1269/ai-system.git
cd ai-system
./install.sh
```

You now have a working AI system on your machine. Fork it, rip it apart, make it yours.

---

## What's in an AI System?

**Nine components, three tiers.**

### Tier 1: Foundation

The irreducible core. Without these, there is no system.

| # | Component | What It Is |
|---|-----------|------------|
| 1 | **Input & Capture** | How you talk to your agent. Typing, voice, transcripts, uploads. The surfaces where you show up (CLI, Slack, chat). |
| 2 | **Context Engineering** | Your agent's operating manual. The rules, skills, and system prompts that shape behavior. |
| 3 | **Memory** | Your agent's notebook. Facts about you, preferences, and pointers into knowledge, accumulated over time. |
| 4 | **The Model** | Your agent's brain. Claude, GPT, Gemini, or a local model. Interchangeable. |

### Tier 2: Capabilities

What the agent can actually do beyond talking.

| # | Component | What It Is |
|---|-----------|------------|
| 5 | **Skills** | Reusable capabilities. Packaged workflows your agent can invoke. |
| 6 | **Integrations** | Tools your agent can reach. Calendar, tasks, email, Slack, GitHub. |
| 7 | **Knowledge Base** | The library your agent references. Your notes, research, and frameworks, organized for retrieval. |

### Tier 3: Power Layer

What makes a system compound over time.

| # | Component | What It Is |
|---|-----------|------------|
| 8 | **Orchestration** | Multiple agents coordinating on a task. |
| 9 | **Automation** | Agents running on schedules, without you asking. |

---

## The Important Distinction

**Agents are not components. They're runtimes.** ChatGPT, Claude Code, and the custom agents you build all *use* the nine-component system. Swap the agent, keep the system. Your memory, your knowledge, your skills stay yours.

---

## Repo Structure

The repo mirrors the framework. Each numbered folder is a component.

```
ai-system/
├── 01-capture/         Input & Capture
├── 02-context/         Context Engineering
├── 03-memory/          Memory
├── 04-model/           The Model
├── 05-skills/          Skills
├── 06-integrations/    Integrations
├── 07-knowledge/       Knowledge Base
├── 08-orchestration/   Orchestration
├── 09-automation/      Automation
│
├── starter-kit/        15-min no-code entry
├── templates/          Copy-paste files for your own system
├── guides/             Deep dives, one per component
└── examples/           Real-world skills, integrations, setups
```

---

## Guides

Each guide maps to a component and ships alongside a video.

| # | Component | Guide | Video |
|---|-----------|-------|-------|
| — | Overview | [The 9 Components](guides/00-overview.md) | [Coming soon](https://youtube.com/@jashia) |
| 1 | Input & Capture | [Guide](guides/01-capture.md) | — |
| 2 | Context Engineering | [Guide](guides/02-context.md) | — |
| 3 | Memory | [Guide](guides/03-memory.md) | — |
| 4 | The Model | [Guide](guides/04-model.md) | — |
| 5 | Skills | [Guide](guides/05-skills.md) | — |
| 6 | Integrations | [Guide](guides/06-integrations.md) | — |
| 7 | Knowledge Base | [Guide](guides/07-knowledge.md) | — |
| 8 | Orchestration | [Guide](guides/08-orchestration.md) | — |
| 9 | Automation | [Guide](guides/09-automation.md) | — |

---

## Who This Is For

- **Knowledge workers** who use AI daily and want it to actually know them
- **Builders** who want a system, not scattered conversations
- **Teams** who want to give their AI tools shared memory and real context
- **Curious humans** who think "there has to be a better way to use this stuff"

---

## License

[MIT](LICENSE). Use it, fork it, make it yours. If you ship something cool, [tell me](https://youtube.com/@jashia).
