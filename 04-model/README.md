# 04. The Model

> Your agent's brain.

## What this is

The Model is the actual LLM doing the reasoning: Claude, GPT, Gemini, Llama, or a local model you run yourself. In a well-designed system, **the model is the most replaceable part.**

## What lives here

- `README.md` — how to swap models without losing your system
- Model-specific configs and adapters (Claude Code, GPT, Gemini CLI, local)

## Why it matters

Models change every few months. New ones get smarter, cheaper, or more private. If your system is designed right, swapping models is a config change, not a rebuild. Your memory, skills, knowledge, and rules all stay intact.

Most vendor-locked AI setups fail here. Don't build yours that way.

## Further reading

[Full guide](../guides/04-model.md)
