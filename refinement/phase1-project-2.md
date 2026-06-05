# Fase 1 — Análise · Projeto 2 (`ecommerce-api-legacy`)

> Saída da **Fase 1 (Análise)** da skill `refactor-arch` aplicada ao Projeto 2.
> Detecta stack, mapeia a arquitetura atual e imprime o resumo. Consolida as
> **heurísticas de detecção** (agora exercitadas em Node/Express) e o **catálogo de
> anti-patterns** específico deste projeto. Veja o Projeto 1 em
> [`phase1-project-1.md`](./phase1-project-1.md) — as heurísticas genéricas são as mesmas.

---

## 1. Resumo da Análise (output da Fase 1)

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      JavaScript (Node.js)
Framework:     Express 4.18.2
Persistence:   SQLite em memória (driver sqlite3 5.1.6, API por callbacks)
Domain:        LMS com checkout (usuários, cursos, matrículas, pagamentos, auditoria)
Architecture:  God Class — AppManager concentra DB + roteamento + regra de negócio;
               estado global mutável e segredos em utils.js
Entry point:   src/app.js (cria Express, instancia AppManager, sobe na porta 3000)
Source files:  3 files analyzed (~180 LOC)
DB tables:     users, courses, enrollments, payments, audit_logs
Endpoints:     3 rotas (POST /api/checkout, GET /api/admin/financial-report,
               DELETE /api/users/:id)
================================
```

### Mapa de arquivos

| Arquivo | LOC | Papel declarado | Papel real (o que de fato faz) |
|---|---|---|---|
| `src/app.js` | 14 | Bootstrap | Cria o Express, instancia `AppManager`, chama `initDb()`/`setupRoutes()` e sobe o servidor. É a única parte "limpa". |
| `src/AppManager.js` | 141 | "Manager" | **God Class**: cria conexão, define schema+seed, registra rotas e implementa toda a regra de checkout/relatório dentro dos handlers |
| `src/utils.js` | 25 | Utilidades | **Config com segredos hardcoded** + **estado global mutável** (`globalCache`, `totalRevenue`) + **cripto caseira quebrada** (`badCrypto`) |

### Fluxo atual

```
HTTP → app.js → AppManager.setupRoutes(app)
                      │  (handlers inline fazem tudo)
                      ├─ valida request
                      ├─ regra de negócio (pagamento, matrícula, relatório)
                      ├─ acesso a dados (this.db.run/get/all por callback)
                      └─ side-effects (console.log de cartão+chave, logAndCache global)
                 utils.js → config (segredos) + globalCache (estado global)
```

Não há separação de camadas: a classe é simultaneamente repositório, service e
controller. `app.js` é o único "composition root", mas instancia tudo concretamente
(sem injeção de dependência).

### Tabelas e relacionamentos (inferidos de `AppManager.initDb`)

```
users(id, name, email, pass)
courses(id, title, price, active)
enrollments(id, user_id → users.id, course_id → courses.id)
payments(id, enrollment_id → enrollments.id, amount, status)
audit_logs(id, action, created_at)
```

> Sem FKs declaradas e **sem cascade** — o próprio `DELETE /api/users/:id` admite na
> resposta que deixa matrículas e pagamentos órfãos (ver M2).

---

## 2. Heurísticas de Detecção (exercitadas em Node/Express)

As heurísticas genéricas estão no doc do Projeto 1. Aqui registro os **sinais
específicos** que disparam para esta stack.

### 2.1 Linguagem · 2.2 Framework
| Sinal | Conclusão |
|---|---|
| `package.json` + `*.js` em `src/` | Node.js |
| `require('express')` / `express()` / `express ^4` em dependencies | **Express 4** |
| `app.get/post/delete(...)` | roteamento Express |

→ **Projeto 2:** `require('express')` em `app.js:1` + `"express": "^4.18.2"` ⇒ **Express 4.18.2**.

### 2.3 Banco de dados
| Sinal | Persistência |
|---|---|
| `require('sqlite3')` / `new sqlite3.Database(':memory:')` | **SQLite em memória** |
| `db.run/get/all(sql, params, callback)` | driver **por callbacks** (não-Promise) |
| Placeholders `?` nos `execute`/`run` | **queries parametrizadas** (sem SQLi) |

→ **Projeto 2:** `new sqlite3.Database(':memory:')` em `AppManager.js:7`; banco recriado a cada boot. **Importante:** todas as queries usam `?` (parametrizadas) ⇒ **não há SQL Injection** aqui — contraste direto com o Projeto 1.

### 2.4 Mapeamento de arquitetura — sinais de God Class
| Sinal | Conclusão |
|---|---|
| Uma classe que tem `this.db`, define rotas (`setupRoutes`) **e** regra de negócio | **God Class** (CRITICAL) |
| Handlers de rota com acesso a dados + regra inline | controller gordo |
| `let x = {}` exportado e mutado por outro módulo | estado global mutável |

→ **Projeto 2:** `AppManager` casa os três sinais ⇒ **God Class confirmada**.

### 2.5 Entry point e superfície de rotas
- Entry point: `app.listen(config.port, ...)` em `app.js:12`.
- Rotas declaradas em `AppManager.setupRoutes` → 3 endpoints a preservar na Fase 3.

---

## 3. Catálogo de Anti-Patterns (com sinais de detecção e severidade)

Distribuição mínima exigida (**≥1 CRITICAL/HIGH, ≥2 MEDIUM, ≥2 LOW**) coberta com folga.

### 🔴 CRITICAL

#### C1 — God Class (DB + roteamento + regra de negócio no mesmo lugar)
- **Sinal de detecção:** uma classe/arquivo que detém a conexão (`this.db`), registra rotas e implementa regra de negócio.
- **Evidência:** `AppManager.js:4-141` — `constructor`/`initDb` (dados) + `setupRoutes` (roteamento) + lógica de checkout/pagamento/relatório (`AppManager.js:28-129`) tudo na mesma classe.
- **Impacto:** zero testabilidade isolada, qualquer mudança arrisca tudo; viola completamente a separação de responsabilidades. (Rubrica: God Class = CRITICAL.)

#### C2 — Segredos hardcoded e exposição de dados sensíveis em log
- **Sinal de detecção:** chaves/senhas literais no código; `console.log` de cartão, token ou chave de gateway.
- **Evidência:** `utils.js:1-7` (`dbPass`, `paymentGatewayKey: "pk_live_..."`, `smtpUser`); `AppManager.js:45` faz `console.log` do **número do cartão completo** e da **chave do gateway**.
- **Impacto:** segredos versionados + PCI/dados de cartão vazando para o stdout/logs. Falha de segurança grave.

#### C3 — Criptografia caseira quebrada para senhas
- **Sinal de detecção:** função de hash artesanal (loop + base64/substring) em vez de algoritmo dedicado; senha em texto plano no seed.
- **Evidência:** `utils.js:18-24` (`badCrypto`: concatena base64 e corta em 10 chars — irreversível ≠ seguro, com colisões triviais); usada em `AppManager.js:68`. Seed grava `pass '123'` em texto plano (`AppManager.js:18`).
- **Impacto:** senhas efetivamente desprotegidas; impossível verificar credenciais com segurança.

> Qualquer **um** de C1–C3 já satisfaz "≥1 CRITICAL ou HIGH".

### 🟠 HIGH

#### H1 — Estado global mutável compartilhado
- **Sinal de detecção:** objeto/variável exportado e mutado por outro módulo (`let globalCache = {}` exportado).
- **Evidência:** `utils.js:9-10` (`globalCache`, `totalRevenue`) mutados por `logAndCache` (`utils.js:12-15`), chamado em `AppManager.js:59`.
- **Impacto:** acoplamento global, vazamento de memória (cache sem expiração), estado não isolável em testes.

#### H2 — Regra de negócio presa dentro do controller (handler) + callback hell
- **Sinal de detecção:** handler de rota com fluxo de negócio aninhado em vários callbacks (pyramid of doom), sem service layer.
- **Evidência:** `AppManager.js:28-78` (checkout: autoriza pagamento, cria usuário, matricula, registra pagamento e auditoria em ~5 níveis de callback aninhado); "autorização" por `cc.startsWith("4")` (`AppManager.js:46`).
- **Impacto:** ilegível, difícil de testar/evoluir; regra crítica (pagamento) acoplada ao HTTP e ao driver do banco.

#### H3 — Acoplamento concreto sem injeção de dependência
- **Sinal de detecção:** módulos instanciam dependências concretas diretamente; sem interface/inversão.
- **Evidência:** `AppManager` cria o `sqlite3.Database` no construtor (`AppManager.js:7`) e importa `config`/`badCrypto`/`logAndCache` direto de `utils` (`AppManager.js:2`).
- **Impacto:** impossível trocar banco/serviço ou mockar em teste sem editar a classe.

### 🟡 MEDIUM

#### M1 — Query N+1 com coordenação assíncrona manual
- **Sinal de detecção:** `forEach` disparando query por item, aninhado, com contadores manuais (`pending--`) em vez de JOIN/`Promise.all`.
- **Evidência:** `AppManager.js:80-129` (`financial-report`): para cada curso busca matrículas, para cada matrícula busca usuário **e** pagamento — N+1 em dois níveis, com `coursesPending`/`enrPending` controlando o fim.
- **Impacto:** explosão de queries proporcional a cursos×matrículas; lógica de término frágil e propensa a bug.

#### M2 — Falta de integridade referencial / delete sem cascade
- **Sinal de detecção:** `DELETE` que remove o pai sem tratar filhos; ausência de FK/`ON DELETE CASCADE`.
- **Evidência:** `AppManager.js:131-137` — deleta `users` e deixa `enrollments`/`payments` órfãos (a própria resposta admite: "ficaram sujos no banco"). Schema sem FKs (`AppManager.js:12-16`).
- **Impacto:** dados órfãos/inconsistentes; relatórios passam a contar registros quebrados.

#### M3 — Validação de entrada fraca e erros silenciados
- **Sinal de detecção:** valida só presença de alguns campos; sem validação de formato; callbacks que ignoram `err`.
- **Evidência:** checkout valida presença de `u/e/cid/cc` mas não `pwd`, sem formato de e-mail nem validação real de cartão (`AppManager.js:35`); vários callbacks ignoram `err` (ex.: `AppManager.js:104,131-136`); respostas de erro inconsistentes (texto puro vs JSON).
- **Impacto:** dados inválidos persistidos; falhas silenciosas difíceis de diagnosticar.

### 🟢 LOW

#### L1 — Nomes crípticos de variáveis
- **Sinal de detecção:** variáveis de uma letra / abreviações obscuras para dados de domínio.
- **Evidência:** `u, e, p, cid, cc` em `AppManager.js:29-33`; campos do body `usr/eml/pwd/c_id/card` (`api.http:8-12`).
- **Impacto:** legibilidade ruim, intenção pouco clara.

#### L2 — Magic numbers / strings soltos
- **Sinal de detecção:** literais de negócio sem constante nomeada.
- **Evidência:** `cc.startsWith("4")` (`AppManager.js:46`), senha default `"123456"` (`AppManager.js:68`), loop `10000` em `badCrypto` (`utils.js:20`), porta `3000` (`utils.js:5`).
- **Impacto:** intenção obscura, valores difíceis de ajustar com segurança.

#### L3 — Import/estado morto e inconsistências
- **Sinal de detecção:** símbolo importado e nunca usado; tabela criada e subutilizada; formato de resposta inconsistente.
- **Evidência:** `totalRevenue` importado em `AppManager.js:2` e nunca usado (e exportado "por valor", nunca refletindo mudanças); `audit_logs` apenas inserido, nunca lido; respostas ora `res.send(texto)`, ora `res.json(...)`.
- **Impacto:** ruído, confusão sobre o que está em uso.

### Cobertura da distribuição mínima exigida

| Severidade | Exigido | Encontrado neste projeto |
|---|---|---|
| CRITICAL/HIGH | ≥ 1 | **6** (C1–C3, H1–H3) |
| MEDIUM | ≥ 2 | **3** (M1–M3) |
| LOW | ≥ 2 | **3** (L1–L3) |

---

## 4. Detecção de APIs deprecated (sinal do catálogo)

- **Resultado:** sem API formalmente *deprecated* (Express 4 e `sqlite3` 5.1 são correntes),
  mas há um **padrão legado** relevante: **API por callbacks com coordenação manual**
  (`db.run/get/all` aninhados + contadores `pending--`).
- **Sinal de detecção:** uso de callbacks encadeados onde a lib oferece versão Promise;
  hashing artesanal onde existe biblioteca padrão.
- **Recomendação moderna:** migrar para `async/await` (ex.: wrapper `util.promisify`,
  `better-sqlite3` síncrono, ou `node:sqlite`), e **substituir `badCrypto` por `bcrypt`/`argon2`**.

---

## 5. Comparativo com o Projeto 1 (por que a skill precisa ser agnóstica)

| Aspecto | Projeto 1 (Flask) | Projeto 2 (Express) |
|---|---|---|
| Separação | Arquivos por papel (nominal) | **Tudo numa God Class** |
| SQL | **Injetável** (string concat) | Parametrizado (sem SQLi) |
| Segredos | `SECRET_KEY` hardcoded + exposto no /health | Chave de gateway/senha + **cartão logado** |
| Assíncrono | Síncrono | **Callback hell** + coordenação manual |
| Estado global | Conexão singleton | `globalCache`/`totalRevenue` mutáveis |

> A skill deve detectar **God Class** (P2) tanto quanto **monólito procedural** (P1), e
> reconhecer que a ausência de SQLi no P2 não significa ausência de problemas críticos.

---

## 6. Próximos passos

- **Fase 2 (Auditoria):** materializar este catálogo no template, ordenado CRITICAL → LOW,
  com `arquivo:linha`, e **pausar para confirmação humana**. Salvar em `reports/audit-project-2.md`.
- **Fase 3 (Refatoração):** quebrar a God Class em camadas MVC (config sem segredos; models/
  repositórios por entidade com queries parametrizadas — já ok; service layer para checkout e
  relatório; controllers finos; error handler central; remover estado global e `badCrypto`),
  validando que a app sobe e os **3 endpoints** continuam respondendo (`api.http`).
