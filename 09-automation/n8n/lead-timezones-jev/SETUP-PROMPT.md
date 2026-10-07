# Setup prompt: self-hosted n8n that Claude Code can build in

This is the prompt from the video. Hand it to [Claude Code](https://claude.com/claude-code) and it sets up n8n the way I did: running on your machine in Docker, with the TypeSafe AI node installed and n8n's MCP server connected, so Claude Code can build workflows straight into your n8n.

**You need:** Docker Desktop (or Docker Engine) installed and running, Claude Code, and a TypeSafe AI API key from [typesafe.ai](https://typesafe.ai) for the Jev node.

**How to use it:** open Claude Code in the folder where you want n8n to live (I keep mine in my data system, next to my CRM: `data/apps/n8n`), then paste everything in the block below. Claude Code does the installs and the checks. It stops and hands you the few steps that need you: creating your n8n account, pasting your API key into n8n, and approving the MCP connection. Your keys and passwords go into n8n in the browser, never into the chat.

```text
Set up a self-hosted n8n instance on this machine that you (Claude Code) can build workflows in, through n8n's MCP server. Work in the current folder. Go step by step, check each step worked before moving on, and stop and tell me exactly what to do whenever a step needs me in the browser. Never ask me to paste a password, API key or OAuth code into this chat.

1. Check Docker. Confirm Docker is installed and running (docker info, docker compose version). If it isn't, stop and tell me how to install or start it for my OS.

2. Write the compose file. Read n8n's official Docker install docs (https://docs.n8n.io/hosting/installation/docker/) and the n8n repo (https://github.com/n8n-io/n8n), then write compose.yaml in this folder with:
   - the official image docker.n8n.io/n8nio/n8n, pinned to the current stable version (not "latest"); look up the current stable release
   - the default SQLite database (no Postgres; one person or a small team doesn't need it)
   - port 5678 bound to 127.0.0.1 only, so the editor is reachable at http://localhost:5678 from this machine and not from the network
   - a named volume n8n_data mounted at /home/node/.n8n (workflows, credentials, the database and the encryption key live there)
   - GENERIC_TIMEZONE and TZ set to my local time zone (check this machine's time zone)
   - N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true, N8N_RUNNERS_ENABLED=true, N8N_DIAGNOSTICS_ENABLED=false
   - restart: unless-stopped
   Put a short comment at the top with the editor URL and the up, down and logs commands.

3. Start it. Run docker compose up -d, wait until http://localhost:5678 responds, and show me the last lines of the container log.

4. My account (me, in the browser). Tell me to open http://localhost:5678 and create the owner account. Wait until I say it's done.

5. The TypeSafe AI node (me, in the browser). Tell me to install the verified community node @typesafe-ai/n8n-nodes-typesafe-ai: Settings, Community Nodes, Install, then that package name (or search "TypeSafe AI" in the nodes panel). Then tell me to add a credential of type "TypeSafe AI API" and paste my key from typesafe.ai into it. Wait until I say both are done.

6. The MCP server (me in the browser, then you). Tell me to open Settings, find the instance-level MCP page, turn on MCP access, and copy the connection command n8n shows for Claude Code. When I paste that command here, run it to add the n8n MCP server to Claude Code, then tell me to finish the sign-in in the browser it opens and approve access. If the MCP tools don't show up in this session afterwards, tell me to restart Claude Code in this folder and continue from step 7.

7. Prove it works. Using the n8n MCP server, list what you can see on the instance (workflows, and whether the TypeSafe AI node is available). Tell me in two or three lines what you found.

8. The template (optional, ask me first). Offer to bring in the "Lead time zones with Jev" workflow from https://github.com/1269/ai-system/tree/main/09-automation/n8n/lead-timezones-jev. If I say yes, download lead-timezones-jev.json and either create it in my n8n through the MCP server, or tell me to import it with Import from File, whichever works. Then tell me to open the Jev node and select my TypeSafe AI API credential, and to edit `me` in the sample leads node (my business, ideal customer and time zone) before I run it.

When everything is done, give me a short summary: where compose.yaml is, the editor URL, how to stop, start and update n8n (change the pinned version and run docker compose up -d), and where my data lives (the n8n_data volume) so I know not to delete it.
```

## Notes

- **Why localhost only?** The editor and the MCP server can change everything in your n8n. Binding the port to `127.0.0.1` keeps them on your machine. If you want n8n reachable from other devices or from webhooks on the internet, that's a separate step (a reverse proxy or a tunnel with HTTPS), not part of this setup.
- **Why SQLite?** It's n8n's default and it's plenty for one person or a small team. Postgres is worth it when you run n8n in queue mode with workers.
- **Updating.** Change the pinned version in `compose.yaml` and run `docker compose up -d`. Your workflows and credentials stay in the `n8n_data` volume.
- **Backups.** Everything that matters is in the `n8n_data` volume, including the encryption key your saved credentials depend on. Back up the volume, not just exported workflows.

See the [README](./README.md) for what the workflow does and how to swap in your own leads.
