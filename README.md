# V8 Agent OS Site

> This is the **public site** repository for **V8 Agent OS**.

## The place where people decide whether this product is real

If the app repos build the machine, this repository makes people want to trust it.

Most agent products are easy to demo and hard to believe.  
**This site exists to show V8 Agent OS as it really is:** a runtime-first agent operating system built for memory, recovery, automation, MCP, skills, OpenClaw plugins, and multi-node coordination.

## Why the site lives in its own repository

Because the public face of the product deserves its own release rhythm.

This repository owns:

- the bilingual landing pages
- the runtime story
- the installation entry points
- the in-page doc reader
- the public map across Web, Admin, Engine, and Site

That separation lets the product story evolve without dragging runtime code around with it.

## What V8 Agent OS is saying out loud here

| What people usually get | What V8 Agent OS is trying to deliver |
| --- | --- |
| a smart chat tab | a runtime-first operating surface |
| disposable context | long-lived memory that keeps paying off |
| giant tool lists | MCP and skills exposed only when they matter |
| plugin reach without discipline | OpenClaw reach on top of a steadier runtime spine |

OpenClaw gives you reach.  
**V8 Agent OS adds memory, orchestration, safety, recovery, and runtime discipline.**

## Where the site pulls truth from

- install scripts come from [`v8-agent-os-engine`](https://github.com/justForever17/v8-agent-os-engine)
- public docs come from `v8-agent-os-engine` and `v8-agent-os-web`
- repo links point to the four public V8 Agent OS repositories

That keeps the site light while the source repositories keep owning the truth.

## Deploy to Cloudflare Pages

1. Connect this repository to Cloudflare Pages.
2. Use:
   - Framework preset: `None`
   - Build command: leave empty
   - Build output directory: `/`
3. Deploy.

## Preview locally

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
| `index.html` | English product page |
| `zh/index.html` | Chinese product page |
| `assets/` | Shared styles, scripts, and brand assets |

## Keep exploring

- [README in Chinese](./README-ZH.md)
- [V8 Agent OS Web](https://github.com/justForever17/v8-agent-os-web)
- [V8 Agent OS Admin](https://github.com/justForever17/v8-agent-os-admin)
- [V8 Agent OS Engine](https://github.com/justForever17/v8-agent-os-engine)

---

## Sponsor V8 Agent OS

> **Help V8 Agent OS keep getting stronger**
>
> If this project helps your team remember more, automate more, and trust agent systems more, you can support the next stage here:
>
> [https://afdian.com/a/justforever17](https://afdian.com/a/justforever17)

---

> “We become what we behold. We shape our tools, and thereafter our tools shape us.”
>
> “我们眼之所见重塑了我们；我们塑造了工具，此后工具塑造了我们。”
>
> — Marshall McLuhan
