# V8 Agent OS Site

Public bilingual landing site for **V8 Agent OS**.

This repo exists to make one feeling land fast: **V8 Agent OS is for people who are tired of re-explaining the same project, drowning in tool catalogs, and losing control once an agent starts running.**

Within seconds, the site should make four things obvious:

1. V8 helps you **repeat yourself less**.
2. V8 keeps **tool noise under control** even when the catalog is large.
3. V8 makes long-running work **visible, steerable, and approval-friendly**.
4. V8 can turn successful screen work into **more reusable execution** instead of leaving it as a one-off trick.

## What this site should do

- sell the product in human language instead of maintainer language
- make install feel direct and low-friction
- point GitHub, docs, and install back to the unified [`v8-agent-os`](https://github.com/justForever17/v8-agent-os) repository
- keep English and Chinese pages structurally aligned

## What this site should never sound like

- a maintenance manual
- an internal architecture review
- a split-repo migration note
- a feature checklist trying to out-shout OpenClaw

## Install entry

The public install story stays intentionally simple:

- Windows

```powershell
powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/justForever17/v8-agent-os/main/bootstrap.ps1 | iex"
```

- Linux / macOS

```bash
curl -fsSL https://raw.githubusercontent.com/justForever17/v8-agent-os/main/bootstrap.sh | bash
```

Those commands pull from the repository root, install the required dependencies, and bring up Admin + Engine. Web still ships separately.

## Local preview

Use any static file server.

```bash
python -m http.server 8789
```

Then open:

```text
http://127.0.0.1:8789/
```

## Repository layout

| Path | Purpose |
| --- | --- |
| `index.html` | English landing page |
| `zh/index.html` | Chinese landing page |
| `assets/` | Shared styles, scripts, and brand assets |

## Keep aligned with

- the public story in [`v8-agent-os`](https://github.com/justForever17/v8-agent-os)
- the actual bootstrap scripts in the repo root
- the current docs exposed from the unified main repository

## Support V8 Agent OS

If this project helps your team stop repeating itself, keep long-running work under control, and trust agent systems more, you can support ongoing work here:

[https://afdian.com/a/justForever17](https://afdian.com/a/justforever17)
