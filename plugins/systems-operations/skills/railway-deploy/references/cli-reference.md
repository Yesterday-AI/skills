# Railway CLI Reference

Complete reference for the Railway CLI. Covers every command needed to
deploy, manage, and debug services. Read on demand from `SKILL.md`.

## Gotchas (full list)

1. **`railway init` only creates a project, NOT a service.** Create the app
   service separately with `railway add --service "name"`.
2. **`railway add --service` is interactive** unless you pass `--variables`
   inline. Always pass variables to skip the TUI prompt.
3. **`railway link` always re-prompts** for workspace/project. Use
   `railway service link <name>` to switch service within an already-linked
   project.
4. **`railway service list --json` does not exist.** Use `railway list --json`
   to get project/service info programmatically.
5. **`VOLUME` is banned in Dockerfiles** on Railway. Remove any `VOLUME`
   instructions or the build will fail.
6. **The CLI command is `railway variable`** (singular), not `railway
   variables`. Subcommands: `list`, `set`, `delete`. **There is no
   `variable get`** — use `railway variable list --kv` and grep.
7. Set `RAILWAY_NO_TELEMETRY=1` to suppress the telemetry prompt.
8. Use `--browserless` for `login` in scripts or headless environments.
   Browser login often fails.
9. **Template variables** use `${{ServiceName.VARIABLE_NAME}}` syntax
   (double curly braces). Resolved by Railway at runtime, not by your shell.
10. **`railway up` uploads the current directory.** It does NOT use git — it
    sends all files (respecting `.railwayignore` or `.gitignore`).
11. **`--variables "KEY=VAL"` with quotes breaks `spawnSync`/`execFileSync`.**
    The quotes become part of the key name (`"KEY` instead of `KEY`). Use
    `--variables KEY=VAL` without quotes.
12. **`railway run` is LOCAL only** — it injects env vars into a local
    command. **`railway ssh`** runs commands inside the actual container.
    Use `ssh` for bootstrap, migrations, or anything that needs the
    container's filesystem.

---

## Authentication

```bash
railway login                # interactive (browser)
railway login --browserless  # pairing code (scripts/headless)
railway whoami
railway logout
```

### Token-based auth (CI/CD & agents)

| Variable | Scope | Use case |
|----------|-------|----------|
| `RAILWAY_TOKEN` | single project | agent deployments, CI/CD |
| `RAILWAY_API_TOKEN` | full account | account-wide automation |

```bash
RAILWAY_TOKEN=xxx railway up --detach
```

---

## Project management

```bash
railway init                                 # create project (interactive workspace pick)
railway init --name "My Project"
railway link                                 # link cwd to existing project (interactive)
railway link -p <project-id> -s <service-name> -e production   # non-interactive
railway status [--json]
railway list [--json]
railway open                                 # open dashboard
railway unlink
railway project delete -p <project-id> -y
```

---

## Service management

### Create services

```bash
# Empty service (interactive)
railway add --service

# Empty service with variables (non-interactive)
railway add --service "api" \
  --variables PORT=3000 \
  --variables NODE_ENV=production \
  --variables 'DATABASE_URL=${{Postgres.DATABASE_URL}}'

# Database
railway add --database postgres
railway add --database mysql
railway add --database redis
railway add --database mongo

# From GitHub repo
railway add --repo user/repo

# From Docker image
railway add --image nginx:latest
```

### Link / switch services

```bash
railway service link <service-name>   # preferred — same project
railway service link                  # interactive picker
railway service status
railway service status --all
```

### Service operations

```bash
railway service redeploy -s <service-name>   # redeploy latest
railway service restart  -s <service-name>
railway service scale    -s <service-name>   # multi-region
railway service delete   <service-id>        # destructive
```

---

## Environment variables

```bash
railway variable list                  # current service
railway variable list --json
railway variable list --kv             # KEY=VALUE format
railway variable list -s Postgres      # specific service

railway variable set KEY=value
railway variable set API_KEY=secret123 DEBUG=true PORT=8080

# stdin (long values)
echo "long-value" | railway variable set SECRET_KEY --stdin

railway variable delete MY_VAR
```

There is no `railway variable get`. To read one value:

```bash
railway variable list --kv -s Postgres | grep '^DATABASE_URL='
```

### Template variables

Reference other services' variables with `${{}}`:

```bash
railway variable set 'DATABASE_URL=${{Postgres.DATABASE_URL}}'
```

Built-in database references:

```
${{Postgres.DATABASE_URL}}
${{Postgres.DATABASE_PUBLIC_URL}}
${{Redis.REDIS_URL}}
${{MySQL.MYSQL_URL}}
${{Mongo.MONGO_URL}}
```

Cross-service:

```
${{api.PORT}}
${{worker.API_KEY}}
```

Built-in runtime:

```
${{RAILWAY_PUBLIC_DOMAIN}}     # this service's public domain
${{RAILWAY_PRIVATE_DOMAIN}}    # this service's internal domain
${{RAILWAY_SERVICE_NAME}}
${{RAILWAY_ENVIRONMENT_NAME}}
```

### Bulk-set from .env file

```bash
while IFS='=' read -r key value; do
  [[ "$key" =~ ^#.*$ || -z "$key" ]] && continue
  railway variable set "$key=$value"
done < .env
```

---

## Deployment

```bash
railway up                   # streams build logs
railway up --detach          # returns immediately
railway up -s <service>
railway up --ci              # streams build, exits when build done
railway redeploy             # redeploy without new code
railway service redeploy -s <service>
railway down                 # remove latest deployment
```

### What `railway up` does

1. Reads `.railwayignore` (falls back to `.gitignore`).
2. Compresses and uploads the directory.
3. Detects build method: Dockerfile or Railpack (Nixpacks).
4. Builds and deploys the container.

---

## Domains & networking

### Public domains

```bash
railway domain                        # *.up.railway.app
railway domain --port 8080
railway domain example.com            # custom
railway domain example.com --port 8080
railway domain --port 3000 -s api
```

Custom domain → add a CNAME pointing at the `*.up.railway.app` URL. Railway
auto-provisions SSL.

### Private networking

Same-project services communicate over encrypted Wireguard tunnels via
internal DNS — zero config:

```
http://<service-name>.railway.internal:<PORT>
```

Examples:

```
http://api.railway.internal:3000
http://worker.railway.internal:8080
```

- Each environment has its own isolated network.
- Free egress, low latency.
- Always use this for service-to-service calls.

---

## Logs & debugging

```bash
railway logs                       # current service
railway logs -s <service>
railway logs -n 100                # last 100 lines
railway logs --build               # build logs
railway logs -s api 2>&1 | grep -i error
```

### Shell access

```bash
railway ssh                        # in-container shell
railway connect                    # db shell (Postgres/Mysql/Redis/Mongo)
```

### Run with Railway env

```bash
railway run npm start              # local cmd, Railway env injected
railway run python manage.py migrate
railway shell                      # interactive shell with vars
```

### Common debug recipes

| Symptom | First check |
|---------|-------------|
| Service won't start | `railway logs -s <svc>` — runtime crash? |
| Healthcheck fails | endpoint returns 200? port matches `[deploy]`? |
| DB connection refused | `railway variable list -s <svc>` — `DATABASE_URL` set? |
| Service-to-service 404 | use `<name>.railway.internal:<port>`, not public URL |
| Build fails | `railway logs --build` — Docker/Nixpacks output |
| "No project linked" | `railway link -p <id> -s <name>` |
| "Unauthorized" | `RAILWAY_TOKEN` expired — regenerate in dashboard |
| Build OOM | optimise Dockerfile (multi-stage, .dockerignore), or upgrade plan |
| Deploy stuck | `railway redeploy -s <svc>`; if no help, check healthcheck |

---

## Config as code (`railway.toml`)

Place at project root. **Config in code overrides dashboard settings.**

```toml
[build]
builder = "DOCKERFILE"                       # or "RAILPACK" (default)
dockerfilePath = "Dockerfile.railway"
buildCommand = "yarn build"
watchPatterns = ["src/**", "package.json"]   # only redeploy on these changes

[deploy]
startCommand = "node server.js"              # override CMD
preDeployCommand = "npm run db:migrate"      # run before start
healthcheckPath = "/api/health"
healthcheckTimeout = 60
restartPolicyType = "ON_FAILURE"             # ON_FAILURE | ALWAYS | NEVER
restartPolicyMaxRetries = 5
cronSchedule = "*/15 * * * *"
drainingSeconds = 10                         # SIGTERM → SIGKILL grace
```

### Environment overrides

```toml
[environments.staging.deploy]
startCommand = "npm run staging"

[environments.pr.deploy]
startCommand = "npm run preview"
```

---

## Environments

```bash
railway environment              # switch (interactive)
railway environment new staging
railway environment delete dev
```

---

## Volumes

```bash
railway volume list
railway volume add
railway volume delete
```

---

## Practical patterns

### Programmatic project info (JSON)

```bash
railway list --json | node -e "
  let d=''; process.stdin.on('data',c=>d+=c);
  process.stdin.on('end',()=>{
    const projects = JSON.parse(d);
    for (const p of projects) {
      const svcs = p.services?.edges?.map(e => e.node.name) || [];
      console.log(p.name + ': ' + svcs.join(', '));
    }
  });"

railway status --json
```

### Database access from local machine

```bash
# Connection URL
railway variable list --kv -s Postgres | grep '^DATABASE_PUBLIC_URL='

# Direct shell
railway connect

# Or pipe into psql
psql "$(railway variable list --kv -s Postgres | grep '^DATABASE_PUBLIC_URL=' | cut -d= -f2-)"
```

### Full-stack deploy

```bash
railway init --name "my-app"

railway add --service "api" \
  --variables PORT=3000 \
  --variables NODE_ENV=production \
  --variables 'DATABASE_URL=${{Postgres.DATABASE_URL}}'

railway add --service "web" \
  --variables PORT=8080 \
  --variables 'API_URL=http://api.railway.internal:3000'

railway add --database postgres

railway service link api && (cd api && railway up --detach)
railway service link web && (cd web && railway up --detach)

railway service link api && railway domain --port 3000
railway service link web && railway domain --port 8080
```

---

## Cost management

Railway bills by resource usage (CPU, RAM, egress). Open
`railway open` → Usage tab. Tips:

- Use private networking between services — no egress charges.
- Scale dev/staging down when idle.
- Set memory/CPU limits in service settings to cap runaway costs.
- `[build] watchPatterns` to avoid unnecessary rebuilds.

---

## Secrets best practices

- Never hardcode secrets in code or Dockerfiles.
- Always use `railway variable set` (or dashboard) for secrets.
- Reference shared secrets across services with `${{Service.VAR}}` template
  syntax — single source of truth.

---

## Global flags

| Flag | Short | Purpose |
|------|-------|---------|
| `--service <name>` | `-s` | Target a specific service |
| `--environment <name>` | `-e` | Target a specific environment |
| `--json` | | JSON output |
| `--yes` | `-y` | Skip confirmations |
| `--help` | `-h` | Show help |
| `--version` | `-V` | Show version |
