# Node.js — operations

Modern Node/TypeScript web backends (Express, Fastify, NestJS, Koa, Hapi, Next API routes).

## Detect
`package.json`; `*.js`/`*.mjs`/`*.ts`; `node_modules/`. Package manager by lockfile:
`package-lock.json` → npm · `pnpm-lock.yaml` → pnpm · `yarn.lock` → yarn · `bun.lockb` → bun.
Read `package.json` `scripts` and prefer the project's own commands over guessing.

## Dependencies & install
- npm: `npm ci` (lockfile present) or `npm install`
- pnpm: `pnpm install --frozen-lockfile` (or `pnpm install`)
- yarn: `yarn install --immutable` (or `yarn install`)
- bun: `bun install`

## Run / stop environment
- Project script: `npm run dev` / `npm start` (pnpm/yarn/bun equivalents).
- Raw entry: `node server.js` · TS via `npx tsx server.ts`, or build then `node dist/server.js`.
- **Config via env:** load with `dotenv` inside the app, or set values **inside** your script —
  never prefix env on the command line.
- A long-running server must be stopped; **prefer in-process verification** (below) so there is no
  process to start or stop.

## Tests (when needed)
`npm test`, or the runner directly: `npx jest`, `npx vitest run`, `node --test`, `npx mocha`.

## Lint · format · build
- Lint: `npx eslint .` (or `npx biome check .`)
- Format: `npx prettier --check .` (or `npx biome format .`)
- Types: `npx tsc --noEmit` · Build: `npm run build`

## Verify the route surface in-process
Drive the app object without a socket:
- Express/Koa/Connect → `supertest`: `await request(app).get('/path')`
- Fastify → `app.inject({ method, url })`
- Nest → `Test.createTestingModule(...)` + `supertest`

Write `verify_routes.mjs` / `.ts` that imports the app, sets config internally, hits every Phase 1
route, asserts status/shape, and exits non-zero on failure. Run as ONE command:
`node verify_routes.mjs` (or `npx tsx verify_routes.ts`).

## Permission notes
Invoke through `npm`/`npx`/`pnpm`/`yarn`/`bun`/`node` (program-name-first). Avoid
`./node_modules/.bin/<tool>` — use `npx <tool>`.
