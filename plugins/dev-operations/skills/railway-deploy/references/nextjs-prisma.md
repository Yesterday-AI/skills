# Next.js + Prisma + PostgreSQL on Railway

Recipe for deploying a Next.js (App Router, standalone output) + Prisma +
PostgreSQL project to Railway via a multi-stage Dockerfile. Read on demand
from `SKILL.md` — only relevant when the project is Next.js+Prisma.

## Prerequisites

- Next.js with `output: "standalone"` in `next.config.mjs`
- Prisma + PostgreSQL with migrations in `prisma/migrations/`
- pnpm package manager
- Railway project linked (`railway link` or GitHub-connected)

## Files to add

### 1. `railway.toml`

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

### 2. `docker-entrypoint.sh`

Runs migrations before the server starts. **Critical** — without it, the
healthcheck passes (`SELECT 1` doesn't need tables) but real queries 500.

```sh
#!/bin/sh
set -e

echo "Running database migrations..."
node node_modules/prisma/build/index.js migrate deploy --schema=./prisma/schema.prisma
echo "Migrations complete."

echo "Starting server..."
exec node server.js
```

Make executable: `chmod +x docker-entrypoint.sh`.

### 3. `Dockerfile`

Multi-stage: deps → build → runner.

- **Base**: `node:20-alpine` + `openssl` (Prisma needs it).
- **Deps**: install all deps, generate Prisma client, flatten the prisma CLI
  + engines from pnpm's store into `/prisma-cli/` so the runner image can
  copy them as a flat tree.
- **Build**: `next build` → standalone output.
- **Runner**: minimal image with standalone server, Prisma client, Prisma
  CLI (for migrations), schema + migrations, entrypoint.

```dockerfile
# syntax=docker/dockerfile:1

# --- Base ---
FROM node:20-alpine AS base
RUN apk add --no-cache openssl
RUN corepack enable && corepack prepare pnpm@latest --activate
WORKDIR /app

# --- Dependencies ---
FROM base AS deps
COPY package.json pnpm-lock.yaml ./
COPY prisma ./prisma/
RUN pnpm install --frozen-lockfile
RUN pnpm exec prisma generate
# Flat prisma CLI dir for the production image
RUN mkdir -p /prisma-cli/node_modules && \
    cp -rL node_modules/.pnpm/prisma@*/node_modules/prisma /prisma-cli/node_modules/prisma && \
    cp -rL node_modules/.pnpm/prisma@*/node_modules/@prisma /prisma-cli/node_modules/@prisma

# --- Build ---
FROM base AS build
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN pnpm build

# --- Production ---
FROM base AS runner
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs && \
    adduser  --system --uid 1001 nextjs

COPY --from=build /app/public ./public
COPY --from=build --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=build --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=deps /app/node_modules/.pnpm/@prisma+client*/node_modules/@prisma/client ./node_modules/@prisma/client
COPY --from=deps /app/node_modules/.pnpm/@prisma+client*/node_modules/.prisma ./node_modules/.prisma
COPY --from=deps /prisma-cli/node_modules/prisma ./node_modules/prisma
COPY --from=deps /prisma-cli/node_modules/@prisma/engines ./node_modules/@prisma/engines
COPY prisma ./prisma/
COPY docker-entrypoint.sh ./docker-entrypoint.sh

USER nextjs

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["sh", "./docker-entrypoint.sh"]
```

Note: no `VOLUME` instructions — Railway rejects them.

### 4. Healthcheck route — `src/app/api/health/route.ts`

```ts
import { prisma } from "@/lib/prisma";
import { NextResponse } from "next/server";

export async function GET() {
  try {
    await prisma.$queryRaw`SELECT 1`;
    return NextResponse.json({ status: "ok", db: "connected" });
  } catch {
    return NextResponse.json(
      { status: "error", db: "unreachable" },
      { status: 503 }
    );
  }
}
```

## Prisma schema

`binaryTargets` must include the Alpine musl targets:

```prisma
generator client {
  provider      = "prisma-client-js"
  binaryTargets = ["native", "linux-musl-openssl-3.0.x", "linux-musl-arm64-openssl-3.0.x"]
}
```

## Railway env vars

Set via dashboard or `railway variable set`:

| Variable | Value | Notes |
|----------|-------|-------|
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` | matches `env()` in `prisma/schema.prisma` |
| `NEXTAUTH_URL` | `https://your-app.up.railway.app` | NextAuth callbacks |
| `NEXTAUTH_SECRET` | `openssl rand -base64 32` | random 32+ chars |

## Common issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Healthcheck passes, queries 500 | migrations not applied | ensure entrypoint runs `prisma migrate deploy` before `node server.js` |
| `Can't find Prisma schema` at startup | schema not in runner | `COPY prisma ./prisma/` in runner stage |
| `Query engine not found` | missing binary target | add `linux-musl-openssl-3.0.x` to `binaryTargets` |
| `prisma: not found` in entrypoint | CLI missing in runner | use the flat `/prisma-cli/` copy pattern |
| `Schema engine not found` for migrations | `@prisma/engines` not copied | `cp -rL` resolves pnpm symlinks; COPY engines into runner |
| `pnpm install` fails on Railway | lock file mismatch | run `pnpm install` locally, commit updated `pnpm-lock.yaml` |

## Checklist

1. [ ] `next.config.mjs` has `output: "standalone"`
2. [ ] Prisma schema has Alpine musl `binaryTargets`
3. [ ] `railway.toml` with Dockerfile builder
4. [ ] `Dockerfile` follows the multi-stage pattern above
5. [ ] `docker-entrypoint.sh` runs `prisma migrate deploy` before server start
6. [ ] `/api/health` route exists and pings the DB
7. [ ] `DATABASE_URL`, `NEXTAUTH_URL`, `NEXTAUTH_SECRET` set in Railway
8. [ ] Railway project linked or GitHub repo connected

## Debugging on Railway

- Build logs: dashboard → Deployments → Build Logs (or `railway logs --build`)
- Runtime logs: dashboard → Deploy Logs (or `railway logs`)
- Env vars: Settings → Variables (or `railway variable list`)
- After this setup, failed migrations crash on startup (visible in deploy
  logs) instead of silently serving 500s on every query.
