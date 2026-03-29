# V8 Agent OS Site

The public site for V8 Agent OS.

This repo is designed for Cloudflare Pages. It ships:

- the product landing page
- the in-page doc reader
- the install entry
- links to the three product repositories

## What this repo does

This repo hosts the static site only.

It does **not** duplicate the main product codebases.

The site reads:

- install scripts from [`v8-agent-os-engine`](https://github.com/justForever17/v8-agent-os-engine)
- product docs from `v8-agent-os-engine` and `v8-agent-os-web`
- repository links from the three public repos

This keeps the site lightweight while still showing the latest published docs and install commands.

## Deploy to Cloudflare Pages

1. Create a new GitHub repository from this folder.
2. Connect the repository to Cloudflare Pages.
3. Use these settings:
   - Framework preset: `None`
   - Build command: leave empty
   - Build output directory: `/`
4. Deploy.

## Local preview

Use any static file server.

Example:

```bash
python -m http.server 8789
```

Then open:

```text
http://127.0.0.1:8789/
```

## Structure

- `index.html` — English entry
- `zh/index.html` — Chinese entry
- `assets/` — shared styles, scripts, and brand assets

## Sponsor

Support the project here:

[https://afdian.com/a/justforever17](https://afdian.com/a/justforever17)

中文说明见 [README-ZH.md](./README-ZH.md)。
