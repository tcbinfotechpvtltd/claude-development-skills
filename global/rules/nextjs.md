---
paths:
  - "**/next.config.*"
  - "**/app/**/page.tsx"
  - "**/app/**/page.jsx"
  - "**/app/**/route.ts"
  - "**/app/**/route.js"
  - "**/app/**/actions.ts"
  - "**/middleware.ts"
  - "**/proxy.ts"
---
# eng-os rule: Next.js app code
Applies because a Next.js route, action or config file is being touched. Procedures and Next.js 16 upgrade traps: skill `custom-apps` ([nextjs.md](../skills/custom-apps/nextjs.md)).
- Every Server Action and route handler authenticates and checks ownership itself; proxy or middleware alone is never the authorization layer.
- Input is validated with a schema at the server boundary; only the fields the client needs are returned.
- Database and vendor calls live in a `server-only` data layer; secrets never sit in `NEXT_PUBLIC_*` variables.
- Request APIs (`cookies()`, `headers()`, `params`, `searchParams`) are awaited; per-user data is never cached under a shared key.
