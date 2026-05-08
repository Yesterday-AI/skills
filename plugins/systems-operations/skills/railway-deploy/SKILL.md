---
name: railway-deploy
description: >
  Deploy, manage, and debug services on Railway via the Railway CLI. Covers
  authentication, project + service creation, env variables, private
  networking, logs, and config-as-code. Use whenever creating, deploying, or
  troubleshooting Railway services. See references/ for the full CLI command
  reference and a Next.js+Prisma deploy recipe.
---

# Railway Deploy

Operate Railway from the CLI: create projects, add services + databases, set
variables, deploy, debug. Optimised for agent + CI use (token-based auth,
non-interactive flags).

## When to use

- Creating a new Railway project / service / database
- Deploying local code or a Docker image to Railway
- Setting env vars or wiring services together via private networking
- Tailing logs or SSH-ing into a running container
- Debugging a failing deploy (build, healthcheck, migration)

## References

Read these on demand — do not pre-load.

- [`references/cli-reference.md`](references/cli-reference.md) — complete CLI:
  every command, flag, template-variable syntax, `railway.toml` schema,
  practical patterns. Open when you need an exact command or flag.
- [`references/nextjs-prisma.md`](references/nextjs-prisma.md) — Next.js
  (standalone) + Prisma + PostgreSQL deploy recipe: Dockerfile, entrypoint
  with `prisma migrate deploy`, healthcheck route, common pitfalls. Open
  only when deploying a Next.js+Prisma app.

## Authentication

CI / agents → set one env var, no `railway login` needed:

| Variable | Scope | Use case |
|----------|-------|----------|
| `RAILWAY_TOKEN` | single project | agent deploys, CI |
| `RAILWAY_API_TOKEN` | full account | account-wide automation |

Interactive (humans only): `railway login` (or `--browserless` in headless
shells). Verify with `railway whoami` / `railway status`.

Also set `RAILWAY_NO_TELEMETRY=1` to silence the telemetry prompt.

## Top gotchas (read before acting)

These bite repeatedly. The full list is in the CLI reference.

1. **`railway init` creates a project, not a service.** Always follow with
   `railway add --service "<name>"` to create the app service.
2. **`railway add --service` is interactive** unless you pass `--variables`
   inline. Pass them to skip the TUI.
3. **Variable command is `railway variable` (singular).** Plural exists in
   older docs/skills but is wrong in current CLI. Subcommands: `list`,
   `set`, `delete`. There is **no `variable get`** — use
   `railway variable list --kv` and grep.
4. **`--variables KEY=VAL` without quotes** in `spawnSync`/`execFileSync`.
   Quotes get parsed as part of the key.
5. **`railway link` always re-prompts.** To switch service inside an
   already-linked project, use `railway service link <name>`.
6. **`VOLUME` is banned in Dockerfiles** on Railway — build will fail. Strip
   any `VOLUME` instructions.
7. **`railway up` uploads the working directory** (respecting
   `.railwayignore` → `.gitignore`). It is **not** git-based.
8. **`railway run` is local; `railway ssh` is in-container.** Use `ssh` for
   migrations, bootstrap, or anything touching container fs.
9. **Template variables use `${{Service.VAR}}`** (double braces). Resolved
   by Railway at runtime, not by your shell — escape `$` in heredocs/scripts.

## Core workflows

### Deploy a new service from local code

```bash
railway init --name "my-app"
railway add --service "api" \
  --variables PORT=3000 \
  --variables NODE_ENV=production \
  --variables 'DATABASE_URL=${{Postgres.DATABASE_URL}}'
railway add --database postgres
railway service link api
railway up --detach
railway domain --port 3000
railway logs
```

### Add a service to an existing project

```bash
railway add --service "worker" \
  --variables 'DATABASE_URL=${{Postgres.DATABASE_URL}}' \
  --variables 'API_URL=http://api.railway.internal:3000'
railway service link worker
railway up --detach
```

### Service-to-service networking

Internal DNS, zero config, free egress, encrypted:

```
http://<service-name>.railway.internal:<PORT>
```

Always prefer this over the public domain for service-to-service calls.

### Debug a failing deploy

```bash
railway status                     # what's linked?
railway logs -s <service>          # runtime logs
railway logs -s <service> --build  # build logs
railway ssh -s <service>           # poke around in the container
railway variable list -s <service> # confirm env
```

Healthcheck failing? Verify the endpoint returns 200 and the port matches
the one Railway is probing (set in `railway.toml` `[deploy] healthcheckPath`
+ exposed `PORT`).

### Config as code

Place `railway.toml` at project root — it overrides dashboard settings:

```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
healthcheckPath = "/api/health"
healthcheckTimeout = 30
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

Full schema (env overrides, cron, watchPatterns, preDeployCommand, …) in the
CLI reference.

## Quick command index

```bash
railway status [--json]                       # current link
railway list [--json]                         # all projects
railway add --service "<name>" --variables K=V
railway add --database postgres|mysql|redis|mongo
railway service link <name>                   # switch service in project
railway variable list [--kv] [-s <svc>]
railway variable set K=V [K2=V2 …]
railway up [--detach] [--ci] [-s <svc>]
railway redeploy [-s <svc>]
railway domain [--port N] [-s <svc>] [<custom>]
railway logs [-s <svc>] [--build] [-n N]
railway ssh [-s <svc>]                        # in-container shell
railway run <cmd>                             # local cmd with railway env
railway connect                               # db shell
```

For anything not listed here, open `references/cli-reference.md`.
