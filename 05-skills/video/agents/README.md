# Tracy, the video editor agent

Tracy is a Claude Code sub-agent that does post-production: hand her an edit decision list and she builds the timeline in DaVinci Resolve Studio, puts the look on it, and lays in the graphics. She edited the video she was built in, "I Built an AI Video Editor. She Edited This Video."

Two files:

- [`video-editor.md`](video-editor.md): the agent. Name, model (Sonnet, on purpose: she works from a list another agent wrote), tools (file tools plus the DaVinci Resolve MCP server), and her steps.
- [`video-editor-persona.md`](video-editor-persona.md): who she is. Her voice, her taste as an editor, and what she protects (the lock, the inputs, the uncertain call, your time).

## Install

1. Copy `video-editor.md` to `.claude/agents/video-editor.md` in your project.
2. Copy `video-editor-persona.md` to `.claude/personas/video-editor.md` (the agent reads it from there first).
3. Connect the DaVinci Resolve MCP server (Resolve Studio; the free edition has no scripting API). The tool names in the agent's frontmatter are that server's.
4. Ask for her by name: "Tracy, build the timeline for <slug> from this EDL."

## Adapt it

- **The persona names me.** Swap "Ja Shia" for yourself, and change her taste to yours.
- **She runs my `/video` pipeline.** Her stages point at reference files in the video skill (`references/edit.md`, `cues.md`, `assets.md`, `lay-in.md`, `resolve-native.md`). The [skill in this repo](../) is an earlier version and does not have all of them yet, so treat the stage table as the shape to copy and point each row at your own steps.
- **Paths.** `$CP` is the root of the repo the agent lives in. Working files are `<your videos folder>/<slug>/`.
- Keep the agent file short (this one is under 100 lines) and put the deep detail in references it reads only when it needs them.
