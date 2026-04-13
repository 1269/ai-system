# 03. Memory

> Your agent's notebook.

## What this is

Memory is where the agent records what it learns about *you* across sessions. Not the full corpus of your knowledge (that's Component 07), but the *gist* plus *pointers*.

Think of a book you've read. You remember a few key concepts. You know where the book lives on your shelf. You don't remember every word. That's what agent memory should do: store the gist, point to the source.

This is *Drawer 2* of the three-drawer model: **facts and preferences the agent observes over time.**

## What lives here

```
memory/
├── INDEX.md          one-line pointers to every entry, always loaded
├── user/             who you are, preferences, context
├── feedback/         learned rules ("don't do X because Y")
├── project/          active initiatives, deadlines, state
└── reference/        pointers into your Knowledge Base (gist + source + link)
```

Each memory file is plain markdown with frontmatter. Portable across any model.

## Why it matters

Without memory, you re-explain yourself every session. With memory, your agent knows your preferences, remembers decisions you've made, and evolves alongside you.

## Further reading

[Full guide](../guides/03-memory.md)
