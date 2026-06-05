export const meta = {
  name: 'codebase-maturity-audit',
  description: 'Map functionality + maturity across the codebase, adversarially verify, and assess projeto.md drift for the pilot team',
  phases: [
    { title: 'Map', detail: 'parallel readers per subsystem -> functionality + maturity with evidence' },
    { title: 'Verify', detail: 'adversarially check each maturity claim (tests, gating, real wiring)' },
    { title: 'Synthesize', detail: 'functionality/maturity report + corrected projeto.md (pt-BR)' },
  ],
}

const ROOT = '/home/marvinborges/pipefy-workspace/pipefy-ai-memory-dev'

const LADDER = `Maturity ladder — choose EXACTLY one term:
- scaffold: code exists but is not functional end-to-end
- prototype: happy-path works, little/no tests or hardening
- functional-unproven: implemented AND tested, but never exercised against real data / in production (e.g. gated OFF by default, never run live)
- pilot-ready: implemented, tested, hardened — safe to put in front of pilot developers
- production-ready: pilot-ready PLUS operational maturity (deployed, observable, scaled)`

const HONESTY = `This report goes to the team that will RUN the PoC. Overclaiming maturity makes them hit walls and lose trust. Be ruthlessly honest: cite file:line or test names as evidence; distinguish "implemented + tested" from "gated off and never run" from "stub/TODO". Read the ACTUAL code, do not trust comments alone.`

const MAP_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['subsystem', 'functionality', 'maturity', 'test_coverage', 'gaps_risks', 'pilot_notes'],
  properties: {
    subsystem: { type: 'string' },
    functionality: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['capability', 'status', 'evidence'],
        properties: {
          capability: { type: 'string' },
          status: { enum: ['implemented', 'partial', 'stub', 'absent'] },
          evidence: { type: 'string', description: 'file:line, function, or test name' },
        },
      },
    },
    maturity: {
      type: 'object', additionalProperties: false,
      required: ['level', 'justification'],
      properties: {
        level: { enum: ['scaffold', 'prototype', 'functional-unproven', 'pilot-ready', 'production-ready'] },
        justification: { type: 'string' },
      },
    },
    test_coverage: { type: 'string' },
    gaps_risks: { type: 'array', items: { type: 'string' } },
    pilot_notes: { type: 'string' },
  },
}

const VERDICT_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['subsystem', 'checks', 'verdict', 'adjusted_level', 'notes'],
  properties: {
    subsystem: { type: 'string' },
    checks: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['claim', 'holds', 'evidence'],
        properties: { claim: { type: 'string' }, holds: { type: 'boolean' }, evidence: { type: 'string' } },
      },
    },
    verdict: { enum: ['confirmed', 'downgrade', 'upgrade'] },
    adjusted_level: { enum: ['scaffold', 'prototype', 'functional-unproven', 'pilot-ready', 'production-ready'] },
    notes: { type: 'string' },
  },
}

const SYNTH_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['executive_summary', 'overall_maturity', 'functionality_matrix', 'projeto_md_drift', 'pilot_readiness', 'recommended_projeto_md'],
  properties: {
    executive_summary: { type: 'string' },
    overall_maturity: { enum: ['scaffold', 'prototype', 'functional-unproven', 'pilot-ready', 'production-ready'] },
    functionality_matrix: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['area', 'what_it_does', 'maturity', 'pilot_ready'],
        properties: {
          area: { type: 'string' },
          what_it_does: { type: 'string' },
          maturity: { enum: ['scaffold', 'prototype', 'functional-unproven', 'pilot-ready', 'production-ready'] },
          pilot_ready: { type: 'boolean' },
        },
      },
    },
    projeto_md_drift: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['topic', 'doc_says', 'reality', 'action'],
        properties: {
          topic: { type: 'string' },
          doc_says: { type: 'string' },
          reality: { type: 'string' },
          action: { enum: ['rewrite', 'keep', 'remove', 'add'] },
        },
      },
    },
    pilot_readiness: {
      type: 'object', additionalProperties: false,
      required: ['ready', 'not_ready', 'operator_todo'],
      properties: {
        ready: { type: 'array', items: { type: 'string' } },
        not_ready: { type: 'array', items: { type: 'string' } },
        operator_todo: { type: 'array', items: { type: 'string' } },
      },
    },
    recommended_projeto_md: { type: 'string', description: 'full rewritten projeto.md in Brazilian Portuguese, honest about functionality + maturity, with a How-to-validate section for the pilot team' },
  },
}

const SUBSYSTEMS = [
  { key: 'hot-path', files: 'app/main.py, app/schemas.py', focus: 'POST /capture (idempotency, write-time scanner), POST /retrieve (hybrid scoring cosine+FTS+recency+repo_boost, repo_doc_map weight multiplier, cross-repo self damping, content dedupe, session delta), governance endpoints /sessions /purge /flag /admin/*' },
  { key: 'auth-isolation', files: 'app/auth.py, app/db.py, db/init/01_schema.sql', focus: 'Google OIDC (JWKS, iss/aud/exp/email_verified, domain, 60s leeway) vs dev X-Dev-Email; per-wing RLS (FORCE), wing_tx SET LOCAL fail-closed, non-superuser/no-BYPASSRLS role; which tables are RLS vs shared and WHY' },
  { key: 'embeddings-scoring', files: 'app/embeddings.py, app/config.py', focus: 'pluggable e5 vs hashing backends, embedding_model_version + re-embed on model change, vector dim 768; the scoring weight tables and repo_doc_map weight semantics' },
  { key: 'ingestion-wiki', files: 'app/ingest.py, app/gitlab_client.py, app/normalize.py, app/vault.py', focus: 'GitLab ingest (chunk by heading, idempotent by blob SHA, is_doc_path exclusions incl changelog), the Obsidian vault wiki (wikilink resolution incl cross-repo gitlab.com URLs, Related-docs sections from index similarity, repo_doc_map relations in READMEs, _index MOC retirement), vault ingest guard' },
  { key: 'distillation', files: 'app/distill.py, app/scanner.py, app/rerank.py, app/tracing.py', focus: 'Phase-3 per-wing distillation: composite cursor, sensitive-repo skip, RAW scanner pre-Haiku, forced strict Haiku tool (5 MemPalace types), deterministic drops, dedup, kill-switch + per-feature toggles; secret scanner; optional rerank; LangSmith tracing. NOTE the gating defaults.' },
  { key: 'pilot-ops', files: 'app/report.py, Makefile, install.sh', focus: 'pilot metrics aggregation + weekly report (retrieve_metrics, percentiles, per-wing through wing_tx), the make entrypoints, the standalone install.sh client installer' },
  { key: 'client-pipemem', files: 'pipemem/ (cli.py, hooks.py, install.py, auth.py, config.py, store.py, api.py, __init__.py)', focus: 'CLI + editor hook shell: Claude Code UserPromptSubmit injection + Stop capture, Cursor capture-only, fail-open discipline, dev vs oidc device-code auth, 0600 credential store, idempotent hook install with ownership regex (incl legacy aimem wrappers)' },
  { key: 'deploy', files: 'Dockerfile, .dockerignore, chart/ (all templates + values.yaml), k8s/staging, k8s/production, docs/deploy.md', focus: 'multi-stage non-root image, Helm chart (API Deployment/Service/Ingress/ConfigMap/SA, CronJobs ingest+distill with DISTILL_ENABLED only in the distill job), env overlays, existingSecret pattern, .gitlab-ci.yml intentionally absent. Assess whether anything is actually DEPLOYED.' },
  { key: 'tests-docs', files: 'tests/ (all), docs/phases/, docs/plans/0001-ai-memory-dev-poc.md, docs/gates/, docs/architecture.md, CLAUDE.md, README.md', focus: 'test coverage breadth (run: cd ' + ROOT + ' && uv run pytest -q to get the real count; which subsystems have isolation/adversarial/regression tests), and how accurately the docs/phases status reflects reality' },
  { key: 'live-state', files: 'live database + git', focus: 'Query the ACTUAL running state, do not just read code. Run: cd ' + ROOT + ' && docker compose exec -T db psql -U postgres -d ai_memory -c "SELECT count(DISTINCT repo), count(*) FROM doc_chunks" and "SELECT repository, count(*) FROM repo_doc_map GROUP BY repository" and "SELECT count(*) FROM team_memories" and "SELECT count(*) FROM sessions". Also: git log --oneline -20 and git remote -v. Report: how many repos indexed, how many chunks, how many repos have a curation map, whether ANY team_memories exist (was distillation ever run?), how many real sessions, whether a production/staging deploy exists. This is the maturity reality vs the code capability.' },
]

const mapPrompt = (s) => `You are auditing the subsystem "${s.key}" of a developer-only memory/context PoC (FastAPI + Postgres/pgvector; client = pipemem hooks). Repo root: ${ROOT}.

Read these files (and anything they import that matters): ${s.files}
Focus: ${s.focus}

For each distinct capability, state status (implemented/partial/stub/absent) with file:line or test-name evidence. Then assign ONE maturity level for the subsystem as a whole.

${LADDER}

${HONESTY}`

const verifyPrompt = (s, map) => `Adversarially verify the maturity audit of subsystem "${s.key}". Repo root: ${ROOT}.

The mapper claimed level "${map.maturity.level}": ${map.maturity.justification}
Functionality claims: ${JSON.stringify(map.functionality)}

Your job is to REFUTE, not agree. Pick the 2-4 most load-bearing claims (especially anything called "implemented", "tested", "pilot-ready", or any security/isolation guarantee) and check them against reality:
- Do the cited tests actually exist? (grep the tests/ dir.) If a feature is "tested", name the test.
- Is the feature actually wired into the request path, or just defined? (read app/main.py call sites.)
- Is it gated OFF by default? (check app/config.py defaults.) Gated-off-and-never-run = at most "functional-unproven", NOT "pilot-ready".
- Use Bash to grep/inspect; you MAY run "cd ${ROOT} && uv run pytest --co -q tests/<file>" to confirm tests collect.

Return your checks, then a verdict (confirmed/downgrade/upgrade) and the adjusted level you would defend to the pilot team.

${LADDER}`

const synthPrompt = (verified) => `You are writing the maturity + functionality assessment of a developer-only memory/context PoC, to be communicated to the team that will RUN the pilot. Repo root: ${ROOT}.

You have per-subsystem maps and adversarial verdicts (use the ADJUSTED levels from the verdicts when they downgrade):
${JSON.stringify(verified)}

FIRST, Read ${ROOT}/projeto.md — the ORIGINAL vision doc (pt-BR). It predates the implementation and has drifted. You MUST explicitly assess these known drift points (and find any others):
1. "API com protocolo MCP" / "via HTTP CLI ou Streamable/MCP" — was MCP actually built? (Reality: HTTP + a thin pipemem CLI/hook client; MCP was researched and NOT built.)
2. "rodará o mempalace em Server Side" / "rodará o mempalace" — does it run MemPalace, or reimplement its techniques from scratch in Python?
3. "não sei se faz sentido usar ChromaDB ou Postgre com FTS" — this OPEN question is resolved (Postgres + pgvector + FTS, e5-base 768d). 
4. DoD: "autenticação no Google @pipefy.com" + "mapeados os padrões/regras/docs/guidelines para CADA repositório" — what fraction of the DoD is actually met? (OIDC works; curation map is pilot-scope only, not all repos.)
5. Anything in projeto.md that is now true, newly added (distillation/team memory, security/RLS model, wiki, weighted curation, metrics), or still aspirational.

Produce:
- executive_summary: 3-5 sentences a tech lead can read in 30s.
- overall_maturity: one ladder term for the project as a whole, defensible.
- functionality_matrix: one row per major area (hot path, isolation/security, ingestion+wiki, team distillation, client/hooks, deploy, auth), with what it does, its maturity, and pilot_ready boolean.
- projeto_md_drift: every point where projeto.md disagrees with reality, with doc_says vs reality and an action.
- pilot_readiness: ready[], not_ready[], operator_todo[] (concrete steps the operators must do before/while running the pilot).
- recommended_projeto_md: a FULL rewritten projeto.md in BRAZILIAN PORTUGUESE. Keep the doc's communicative spirit but make it HONEST and useful to the pilot team: what the project is, how it works (real architecture: HTTP + pipemem hooks, NOT MCP), current functionality + maturity per area, what is gated/unproven, the security/privacy model in one paragraph, and a "Como o time valida a PoC" section with concrete steps (install via install.sh, login, use Claude Code in pipeui/hub-ui/bricks, what good enrichment looks like, how to flag/purge, where to give feedback). Mark clearly what is NOT yet ready (production deploy, distillation never run live, curation map covers only pilot repos). Do NOT invent features that the maps did not confirm.

${LADDER}`

phase('Map')
const results = await pipeline(
  SUBSYSTEMS,
  (s) => agent(mapPrompt(s), { label: `map:${s.key}`, phase: 'Map', schema: MAP_SCHEMA }),
  (map, s) => agent(verifyPrompt(s, map), { label: `verify:${s.key}`, phase: 'Verify', schema: VERDICT_SCHEMA })
        .then((v) => ({ subsystem: s.key, map, verdict: v })),
)
const verified = results.filter(Boolean)
log(`mapped + verified ${verified.length}/${SUBSYSTEMS.length} subsystems`)
const downgrades = verified.filter((r) => r.verdict && r.verdict.verdict === 'downgrade')
log(`adversarial downgrades: ${downgrades.length} (${downgrades.map((d) => d.subsystem).join(', ') || 'none'})`)

phase('Synthesize')
const synthesis = await agent(synthPrompt(verified), { label: 'synthesize', phase: 'Synthesize', schema: SYNTH_SCHEMA })
return { synthesis, verified_count: verified.length, downgrades: downgrades.map((d) => d.subsystem) }
