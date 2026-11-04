# Next.js / React / Node

## Architecture
- App Router. Server Components are the default; add `"use client"` only to the leaf components that need interactivity or browser APIs.
- A server-only data access layer (`import "server-only"`) owns every database and vendor call, checks authorization and returns minimal DTOs. Components never query the database directly.
- Route handlers (`route.ts`) for external APIs and webhooks. Server Actions for the app's own forms.
- `error.tsx`, `loading.tsx` and `not-found.tsx` at the route levels that need them. Parallel-route slots need a `default.js`.
- Validate every input with a schema (zod) at the server boundary. Share types, never trust them.

## Next.js 16 changes that break upgrades
- Request APIs are async only: `await cookies()`, `headers()`, `draftMode()`, `params` and `searchParams`.
- `middleware` is renamed `proxy` (Node runtime only; apps that need the edge runtime keep `middleware`).
- Turbopack is the default for `next dev` and `next build`. A custom `webpack` config fails the build unless you pass `--webpack`.
- `next lint` is removed: run ESLint directly.
- `serverRuntimeConfig`/`publicRuntimeConfig` and AMP are removed.
- `next/image` is stricter: local IPs are blocked, at most 3 redirects, a 4-hour minimum cache TTL, quality `[75]` by default.
- Since Next.js 15, `fetch` and `GET` route handlers are not cached by default, and the client router cache no longer reuses page segments.
- Use the official codemod first, then fix what remains, then run the full test suite.

## Caching (Cache Components)
New apps enable `cacheComponents` (the default in `create-next-app` since 16.4, and planned as the default in Next.js 17). Mark cacheable work with `"use cache"`, `cacheLife` and `cacheTag`. `revalidateTag` now takes a `cacheLife` second argument; `updateTag` and `refresh` are new. Uncached data must sit inside `<Suspense>`, or the build fails. Never cache per-user or permission-dependent data under a shared key.

## Server Actions and route handlers (official data-security guide)
- Anyone can call them with a direct POST: authenticate and check ownership and role inside every one (no IDOR).
- Return only the fields the client needs. Rate-limit expensive or OTP-type actions.
- Self-hosting on several servers: set `NEXT_SERVER_ACTIONS_ENCRYPTION_KEY`. Behind a proxy or CDN: set `serverActions.allowedOrigins`.
- Audit `proxy.ts` and every `route.ts` as public attack surface.

## Deploy shape (VPS)
`next build`, then `next start` (or `output: "standalone"`) under systemd or PM2 behind nginx with TLS. Pin the Node version (`.nvmrc` or `engines`). `NEXT_PUBLIC_*` values are inlined at build time, so either build per environment or keep environment-specific values server-side and read them at runtime; only the second allows building once and promoting the same artifact. Watch Core Web Vitals after release.

Sources (checked 2026-11-04): nextjs.org blog (16.4) and upgrade guides (v15, v16), nextjs.org/docs/app/guides/data-security, react.dev/versions, nodejs release schedule.
