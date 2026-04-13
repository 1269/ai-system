# 08. Orchestration

> Multiple agents coordinating on a task.

## What this is

Orchestration is the layer where one agent delegates to others, or where specialized sub-agents run in parallel on different parts of a problem.

Examples:
- A planning agent that spawns a research agent, a code agent, and a reviewer agent
- Parallel sub-agents each exploring a different part of your codebase
- A manager agent routing tasks to the right specialist

## What lives here

```
orchestration/
├── README.md         patterns, when to use multi-agent
├── patterns/         reusable orchestration templates
└── examples/         real workflows
```

## Why it matters

Single-agent workflows hit a ceiling fast. Orchestration lets you break big problems into parallel work, use the right model for each subtask, and compose complex behaviors from simple agents.

**Note:** this repo intentionally keeps orchestration lightweight. For deep implementation, see the full course or book a consulting session.

## Further reading

[Full guide](../guides/08-orchestration.md)
