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
- a feature checklist trying to out-shout competitors

## Preview install entry

The public desktop entry is the Windows Desktop Preview on the main repository's [GitHub Releases](https://github.com/justForever17/v8-agent-os/releases). It is still an unsigned preview, not a signed stable build or an auto-update promise. Phone ships as a separate Android Preview APK and pairs through the desktop control center.

The main repository's `bootstrap.ps1` / `bootstrap.sh` scripts install dependencies and start services, defaulting to Engine + Admin. They are not Electron desktop installers. The full source-tree desktop preview entry is:

```powershell
.\v8os.cmd preview --rebuild
```

Simple narrative check before publishing:

```bash
python scripts/audit_public_narrative.py
```

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
- the real responsibility boundaries between GitHub Releases, `v8os preview`, and bootstrap
- the current docs exposed from the unified main repository

## Support V8 Agent OS

If this project helps your team stop repeating itself, keep long-running work under control, and trust agent systems more, you can support ongoing work here:

[https://afdian.com/a/justForever17](https://afdian.com/a/justforever17)
