# Fase 1 — Análise · Projeto 1 (`code-smells-project`)

> Saída da **Fase 1 (Análise)** da skill `refactor-arch` aplicada ao Projeto 1.
> Detecta stack, mapeia a arquitetura atual e imprime o resumo. Também consolida as
> **heurísticas de detecção** e o **catálogo de anti-patterns** que alimentarão as Fases 2 e 3.

---

## 1. Resumo da Análise (output da Fase 1)

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python 3
Framework:     Flask 3.1.1 (+ flask-cors 5.0.1)
Persistence:   SQLite (driver nativo sqlite3, SQL cru por string)
Domain:        API de E-commerce (produtos, usuários, pedidos, relatórios)
Architecture:  Monólito procedural — separação por nome de arquivo,
               sem camadas reais (sem services, sem repositórios, sem config)
Entry point:   app.py (Flask app + registro manual de rotas via add_url_rule)
Source files:  4 files analyzed (~780 LOC)
DB tables:     produtos, usuarios, pedidos, itens_pedido
Endpoints:     19 rotas (CRUD de produtos/usuários, pedidos, login,
               relatório de vendas, health, 2 rotas /admin perigosas)
================================
```

### Mapa de arquivos

| Arquivo | LOC | Papel declarado | Papel real (o que de fato faz) |
|---|---|---|---|
| `app.py` | 88 | Bootstrap + rotas | Cria o app, configura segredo **hardcoded**, registra 19 rotas e ainda define inline as rotas `/admin/reset-db` e `/admin/query` (SQL arbitrário) |
| `controllers.py` | 292 | Controllers HTTP | Parsing de request, validação **duplicada**, orquestração e **efeitos colaterais** (envio fake de e-mail/SMS/push via `print`) |
| `models.py` | 314 | "Models" | Mistura **acesso a dados (SQL cru)** + **regras de negócio** (cálculo de pedido, baixa de estoque, regras de desconto do relatório) |
| `database.py` | 86 | Conexão + schema | Singleton **global mutável** de conexão, criação de schema e seed embutidos |

### Fluxo atual

```
HTTP → app.py (add_url_rule) → controllers.py (valida + orquestra + notifica)
                                      ↓
                              models.py (SQL string-concat + regra de negócio)
                                      ↓
                              database.py (conexão global única)
```

Não há camada de configuração, nem service layer, nem repositório, nem
serialização/DTO dedicada. A "separação" existente é apenas nominal: três arquivos
que se importam diretamente, sem inversão de dependência.

### Tabelas e relacionamentos (inferidos de `database.py`)

```
produtos(id, nome, descricao, preco, estoque, categoria, ativo, criado_em)
usuarios(id, nome, email, senha, tipo, criado_em)
pedidos(id, usuario_id → usuarios.id, status, total, criado_em)
itens_pedido(id, pedido_id → pedidos.id, produto_id → produtos.id, quantidade, preco_unitario)
```

> Relacionamentos existem por convenção (`usuario_id`, `pedido_id`, `produto_id`),
> mas **sem FKs declaradas** — integridade referencial fica por conta da aplicação.

---

## 2. Heurísticas de Detecção (reutilizáveis pela skill)

Sinais que a Fase 1 usa para classificar qualquer projeto, de forma agnóstica de stack.

### 2.1 Linguagem
| Sinal | Conclusão |
|---|---|
| `*.py`, `requirements.txt`, `pyproject.toml`, `Pipfile` | Python |
| `*.js/*.ts`, `package.json` | Node.js |
| `*.go` + `go.mod` / `*.rb` + `Gemfile` / `*.php` + `composer.json` | Go / Ruby / PHP |

→ **Projeto 1:** presença de `app.py`, `controllers.py`, `models.py`, `database.py` + `requirements.txt` ⇒ **Python**.

### 2.2 Framework
| Sinal | Framework |
|---|---|
| `from flask import Flask` / `Flask(__name__)` / `flask==` no requirements | **Flask** |
| `from fastapi import` / `APIRouter` | FastAPI |
| `django` no requirements / `manage.py` / `settings.py` | Django |
| `require('express')` / `express()` | Express |

→ **Projeto 1:** `from flask import Flask` em `app.py:1` + `flask==3.1.1` ⇒ **Flask 3.1.1**. CORS via `flask_cors`.

### 2.3 Banco de dados
| Sinal | Persistência |
|---|---|
| `import sqlite3` / `sqlite3.connect(...)` | SQLite cru |
| `flask_sqlalchemy` / `SQLAlchemy()` / `db.Model` | ORM SQLAlchemy |
| `psycopg2` / `mysql.connector` / `mongoose` | Postgres / MySQL / MongoDB |
| Strings `CREATE TABLE`, `SELECT ... FROM` | SQL manual (sem ORM) |

→ **Projeto 1:** `sqlite3.connect("loja.db")` em `database.py:10` + SQL por string ⇒ **SQLite com SQL cru** (sem ORM). Schema e seed criados em runtime no `get_db()`.

### 2.4 Mapeamento de arquitetura
| Sinal | Arquitetura inferida |
|---|---|
| Tudo num arquivo / 1 classe "faz-tudo" | Monólito / God Class |
| Arquivos por papel (`controllers`, `models`) mas importando-se direto, sem camada de service/config | **Monólito procedural com separação nominal** |
| Pastas `models/ routes/ services/ utils/` + blueprints / DI | Parcialmente em camadas (MVC incompleto) |

→ **Projeto 1:** arquivos por papel, porém com SQL+negócio juntos em `models.py`, efeitos colaterais nos controllers e estado global em `database.py` ⇒ **monólito procedural, separação só de nome**.

### 2.5 Pontos de entrada e superfície de rotas
- Entry point: bloco `if __name__ == "__main__":` em `app.py:80` → `app.run(...)`.
- Rotas: `app.add_url_rule(...)` (registro manual) + `@app.route` inline.
- Contar endpoints e mapear método+path dá a **superfície a preservar** na validação da Fase 3.

---

## 3. Catálogo de Anti-Patterns (com sinais de detecção e severidade)

Cada item traz: **sinal de detecção** (acionável, não genérico), **evidência no Projeto 1** com `arquivo:linha`, **severidade** e **impacto**. O catálogo cobre a distribuição mínima exigida — pelo menos **1 CRITICAL/HIGH, 2 MEDIUM e 2 LOW** — e vai além para servir de base à Fase 2.

### 🔴 CRITICAL

#### C1 — SQL Injection por concatenação de string
- **Sinal de detecção:** `cursor.execute(...)` recebendo `"... " + variavel` / f-string / `%` com entrada do usuário, em vez de parâmetros (`?` / `:nome`).
- **Evidência:** `models.py:28` (`"... WHERE id = " + str(id)`), `models.py:47-50` (INSERT produto), `models.py:109-111` (login: `email`/`senha` concatenados → bypass de autenticação), `models.py:289-297` (busca com `LIKE '%"+termo+"%'`). Padrão repetido em **todas** as funções de `models.py`.
- **Impacto:** vazamento/alteração/destruição de dados e bypass de login. Falha de segurança grave.

#### C2 — Credenciais e segredos hardcoded
- **Sinal de detecção:** literais de `SECRET_KEY`, senha, API key, token no código; segredos retornados em respostas HTTP.
- **Evidência:** `app.py:7` (`SECRET_KEY = "minha-chave-super-secreta-123"`) e, pior, o mesmo segredo **exposto no payload** de `/health` em `controllers.py:289`.
- **Impacto:** segredo versionado e publicamente exposto; sessão/assinatura comprometível.

#### C3 — Endpoint de execução de SQL arbitrário
- **Sinal de detecção:** rota que recebe SQL/comando do corpo da request e executa direto (`request...get("sql")` → `cursor.execute`).
- **Evidência:** `app.py:59-78` (`POST /admin/query` executa qualquer SQL) e `app.py:47-57` (`POST /admin/reset-db` apaga todas as tabelas) — ambos sem autenticação.
- **Impacto:** RCE-equivalente sobre o banco; qualquer cliente reseta ou lê/escreve tudo.

#### C4 — Senhas em texto plano (sem hashing) e expostas
- **Sinal de detecção:** coluna `senha`/`password` gravada sem hash; comparação direta no login; campo de senha presente no SELECT/serialização.
- **Evidência:** seed grava senhas cruas (`database.py:76-78`); `models.py:127-129` insere senha sem hash; `get_todos_usuarios` (`models.py:79-86`) **retorna `senha`** e `GET /usuarios` a expõe.
- **Impacto:** vazamento direto de credenciais de todos os usuários.

> Qualquer **um** de C1–C4 já satisfaz o requisito de "≥1 CRITICAL ou HIGH".

### 🟠 HIGH

#### H1 — Regra de negócio dentro da camada de dados ("model" gordo)
- **Sinal de detecção:** funções/arquivos de acesso a dados que também decidem regras (cálculo de totais, validação de estoque, faixas de desconto).
- **Evidência:** `models.py:133-169` (`criar_pedido`: valida estoque, calcula total, dá baixa no estoque — orquestração de negócio) e `models.py:235-273` (`relatorio_vendas`: regras de desconto). Não há service layer.
- **Impacto:** impossível testar a regra sem o banco; mudança de regra mexe no acesso a dados. Violação direta de SRP/MVC.

#### H2 — Estado global mutável / conexão singleton compartilhada
- **Sinal de detecção:** variável global de conexão; `check_same_thread=False`; ausência de pool/escopo por request.
- **Evidência:** `database.py:4` (`db_connection = None` global) + `database.py:10` (`check_same_thread=False`). Uma única conexão compartilhada entre threads.
- **Impacto:** condições de corrida, acoplamento global, difícil de isolar em testes.

#### H3 — Efeitos colaterais de infraestrutura dentro do controller
- **Sinal de detecção:** controller disparando e-mail/SMS/push/notificação diretamente (sem service/fila).
- **Evidência:** `controllers.py:208-210` (envio fake de e-mail/SMS/push no `criar_pedido`) e `controllers.py:248-250` (notificações no update de status).
- **Impacto:** controller acoplado a side-effects, sem como testar/mockar; mistura HTTP com notificação.

### 🟡 MEDIUM

#### M1 — Query N+1
- **Sinal de detecção:** `cursor.execute` dentro de laço `for`, uma query por item da coleção.
- **Evidência:** `models.py:187-199` (`get_pedidos_usuario`) e `models.py:219-231` (`get_todos_pedidos`): para cada pedido consulta itens, e para cada item consulta o nome do produto. Pode virar dezenas de queries por request.
- **Impacto:** degradação de performance proporcional ao volume; resolvível com JOIN.

#### M2 — Lógica de validação duplicada e mapeamento repetido
- **Sinal de detecção:** blocos de validação copiados entre handlers; mesma conversão `row → dict` repetida.
- **Evidência:** validação quase idêntica em `controllers.py:28-54` (`criar_produto`) e `controllers.py:72-90` (`atualizar_produto`); mapeamento produto→dict repetido em `models.py:12-21, 31-40, 304-313`.
- **Impacto:** correção precisa ser feita em vários lugares; fonte de divergência e bugs.

#### M3 — `print()` como logging e validação de entrada ausente/inconsistente
- **Sinal de detecção:** `print(...)` para log; rotas sem validação de formato (e-mail), sem schema.
- **Evidência:** `print` espalhado (`controllers.py:8,11,57,161,179,208-210`); `criar_usuario` (`controllers.py:146-165`) e `login` não validam formato de e-mail; sem validação de tipo nos campos numéricos vindos de `/produtos/busca`.
- **Impacto:** sem níveis de log nem observabilidade; dados inválidos chegam ao banco.

### 🟢 LOW

#### L1 — Magic numbers
- **Sinal de detecção:** números literais com significado de negócio sem constante nomeada.
- **Evidência:** faixas/percentuais de desconto `10000/5000/1000` e `0.1/0.05/0.02` em `models.py:257-262`; limites de nome `2`/`200` em `controllers.py:47-50`.
- **Impacto:** intenção obscura, difícil de ajustar com segurança.

#### L2 — Nomenclatura ruim e shadowing de builtin
- **Sinal de detecção:** parâmetro `id` (sombreia builtin), mistura PT/EN, variáveis não descritivas.
- **Evidência:** `id` como parâmetro em `models.py:24,54,65,89` e `controllers.py:14,64,98`; mistura de idiomas (`buscar_produtos`/`get_todos_pedidos`).
- **Impacto:** legibilidade e consistência reduzidas.

#### L3 — Código morto / campos não usados
- **Sinal de detecção:** import sem uso; coluna criada mas nunca lida; resposta com formato inconsistente.
- **Evidência:** `import sqlite3` não usado em `models.py:2`; coluna `ativo` criada em `database.py:22` e nunca filtrada/utilizada nas queries; envelope de resposta varia (`sucesso`/`erro`/`dados` nem sempre presentes).
- **Impacto:** ruído, confusão sobre o que está em uso.

### Cobertura da distribuição mínima exigida

| Severidade | Exigido | Encontrado neste projeto |
|---|---|---|
| CRITICAL/HIGH | ≥ 1 | **7** (C1–C4, H1–H3) |
| MEDIUM | ≥ 2 | **3** (M1–M3) |
| LOW | ≥ 2 | **3** (L1–L3) |

---

## 4. Detecção de APIs deprecated (sinal do catálogo)

Verificação obrigatória do catálogo. **Neste projeto não foi encontrada API deprecated**
relevante: Flask 3.1 e `sqlite3` estão em uso corrente; nenhuma chamada a APIs removidas
(ex.: `flask.Markup`, `@app.before_first_request`, `werkzeug.url_encode`). O sinal de
detecção fica registrado para os Projetos 2 e 3:
- **Sinal:** import/uso de símbolo marcado como deprecated na versão da lib em uso
  (ex.: `before_first_request`, `Markup` movido para `markupsafe`, `datetime.utcnow()`).
- **Recomendação:** substituir pelo equivalente moderno e fixar versão.

---

## 5. Próximos passos

- **Fase 2 (Auditoria):** materializar este catálogo no template de relatório de auditoria,
  ordenado CRITICAL → LOW, com `arquivo:linha` exatos, e **pausar para confirmação humana**
  antes de qualquer alteração. Salvar em `reports/audit-project-1.md`.
- **Fase 3 (Refatoração):** reestruturar para MVC (config sem segredo hardcoded, models de
  dados, repositório/queries parametrizadas, service layer para regra de negócio, controllers
  finos, error handling central, entry point limpo) e validar que **a app sobe e os 19
  endpoints continuam respondendo**.
