# 06. Integrations

> Tools your agent can reach.

## What this is

Integrations connect your agent to the systems you already use: calendar, tasks, email, Slack, GitHub, notes, documents. Typically implemented via MCP servers or API clients.

If a skill is *what* the agent can do, an integration is *where* it can do it.

## What lives here

```
integrations/
├── slack/            read, search, post (with approval)
├── google/           Gmail, Calendar, Drive, Docs
├── github/           PRs, issues, repos
└── (bring your own)
```

## Why it matters

An agent without integrations can only talk. An agent *with* integrations can act: schedule meetings, send messages, update tasks, commit code. That's where the time savings come from.

## Further reading

[Full guide](../guides/06-integrations.md)
