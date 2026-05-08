---
name: butler-deploy
description: >
  Publish or update an HTML5 game on itch.io via the butler CLI. Covers
  install, login, channel push with versioning, and first-time page setup.
  Use when deploying a web game build (e.g. dist/) to an itch.io channel.
---

# Butler Deploy

Push HTML5 game builds to itch.io with the [butler CLI](https://itchio.itch.io/butler).
Butler does delta uploads (only changed files after the first push) and the
game is live the moment the push completes.

## When to use

- First-time publish of a web build to itch.io
- Updating an existing itch.io page with a new build
- Wiring an itch.io deploy step into CI

## Prerequisites

### 1. Install butler (one-time, per machine)

```bash
# macOS
brew install butler

# Linux
curl -L -o butler.zip https://broth.itch.ovh/butler/linux-amd64/LATEST/archive/default
unzip butler.zip
mv butler /usr/local/bin/butler

# Windows
scoop install butler
# or download from https://itchio.itch.io/butler
```

### 2. Authenticate (one-time, per machine)

```bash
butler login
# Opens browser → authorize → return to terminal.
```

For CI: set `BUTLER_API_KEY` instead (generate at
<https://itch.io/user/settings/api-keys>). No `butler login` needed.

### 3. Create the itch.io page (one-time, in browser)

Butler refuses the first push if the target page does not exist.

1. <https://itch.io/dashboard> → **Create new project**
2. Settings:
   - **Kind:** HTML
   - **Viewport size:** match your build (e.g. 1280×720)
   - **"This file will be played in the browser"**: checked
3. Save as **Draft** (publish after verifying the first push).

After the page exists, all future deploys are fully scripted.

## Core command

```bash
butler push <build-dir> <user>/<game>:<channel> --userversion <version>
```

| Argument | Example | Meaning |
|----------|---------|---------|
| `<build-dir>` | `dist/` | local directory to upload |
| `<user>/<game>` | `acme/spacelander` | itch.io target |
| `<channel>` | `html5` | upload channel (`html5`, `windows`, `linux`, `osx`, …) |
| `--userversion` | `1.4.2` | stamps the upload (optional but recommended) |

Example:

```bash
butler push dist/ acme/spacelander:html5 --userversion 1.4.2
```

## Common patterns

### Build then push

Wire build + push together — pick whichever fits your stack:

```bash
# Direct
npm run build && butler push dist/ acme/spacelander:html5 --userversion "$(node -p "require('./package.json').version")"

# Make
make build && butler push build/web acme/spacelander:html5

# Project npm script (optional convenience)
# package.json: "deploy": "butler push dist/ $ITCH_GAME:html5 --userversion $npm_package_version"
ITCH_GAME=acme/spacelander npm run deploy
```

### Channel-per-platform

```bash
butler push dist/web    acme/spacelander:html5
butler push dist/win    acme/spacelander:windows
butler push dist/linux  acme/spacelander:linux
butler push dist/osx    acme/spacelander:osx
```

### Verify after push

```bash
butler status acme/spacelander            # all channels, latest version + state
butler status acme/spacelander:html5      # one channel
```

## Useful butler commands

```bash
butler login                              # interactive auth (browser)
butler logout
butler push <dir> <user>/<game>:<channel> [--userversion VER] [--ignore PATTERN]
butler status <user>/<game>[:<channel>]
butler fetch  <user>/<game>:<channel> <out-dir>   # download a build
butler validate <dir>                     # sanity-check a build dir
butler --version
```

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `butler: command not found` | not installed | install per step 1 |
| `404 Not found` on first push | itch.io page doesn't exist | create the project page in browser first |
| `401 Unauthorized` | not logged in / bad API key | `butler login`, or fix `BUTLER_API_KEY` |
| `403 Forbidden` | account doesn't own the target | check `<user>/<game>` slug matches a project you own |
| Push silently uploads everything every time | `dist/` content non-deterministic (timestamps, build hashes) | rebuild with stable filenames, or `--ignore` volatile files |
| `--userversion` shows up empty on itch.io | flag value missing/empty | confirm the version env / `package.json` field is set before invoking |
