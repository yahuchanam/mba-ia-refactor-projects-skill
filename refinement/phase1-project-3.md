# Fase 1 — Análise · Projeto 3 (`task-manager-api`)

> Análise do Projeto 3 — o caso mais difícil: o projeto **já possui separação de
> camadas** (`models/ routes/ services/ utils/`), porém os smells estão *dentro* de uma
> estrutura organizada (segurança/qualidade **e** arquitetura). Heurísticas genéricas:
> ver [`phase1-project-1.md`](./phase1-project-1.md).

---

## 1. Resumo da Análise (output da Fase 1)

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python 3
Framework:     Flask 3.0.0 (+ flask-cors, marshmallow, requests, python-dotenv)
Persistence:   SQLite via ORM Flask-SQLAlchemy 3.1.1 (sqlite:///tasks.db)
Domain:        Task Manager (usuários, tasks, categorias, relatórios)
Architecture:  Camadas PARCIAIS — models/ routes/ services/ utils/ com Blueprints,
               porém regra de negócio nos controllers, camadas mortas e
               duplicação. "Organizado" só na superfície.
Entry point:   app.py (cria app, registra 3 blueprints, db.create_all em import)
Source files:  15 .py files analyzed (~1160 LOC)
DB tables:     users, tasks, categories  (FKs declaradas: tasks→users, tasks→categories)
Endpoints:     22 rotas (CRUD de tasks/users/categories, busca, stats,
               relatórios, login com token FAKE, health)
================================
```

### Mapa de pastas

| Caminho | LOC | Papel declarado | Papel real |
|---|---|---|---|
| `app.py` | 34 | Bootstrap | App + config **com SECRET_KEY hardcoded** + registra blueprints + `db.create_all()` em import |
| `database.py` | 3 | Extensão DB | Instancia `SQLAlchemy()` — ok |
| `models/user.py` | 38 | Model User | Model + **hashing MD5** + `to_dict` **vaza `password`** |
| `models/task.py` | 60 | Model Task | Model + métodos de validação/`is_overdue` (pouco usados pelas rotas) |
| `models/category.py` | 21 | Model Category | Model simples — ok |
| `routes/task_routes.py` | 299 | Controllers | Validação + **regra de negócio** (overdue, stats) + **N+1** + serialização manual |
| `routes/user_routes.py` | 211 | Controllers | CRUD + **login com token fake** + **mass-assignment de `role`** |
| `routes/report_routes.py` | 223 | Controllers | **Agregação de relatório inteira no controller** + N+1 + categorias |
| `services/notification_service.py` | 48 | Service | **Nunca importado** (camada morta) + **credenciais SMTP hardcoded** |
| `utils/helpers.py` | 116 | Utilidades | Validações/constantes em sua maioria **não usadas** (rotas duplicam a lógica) |
| `seed.py` | 99 | Seed | Popula users/categories/tasks (rodar antes do 1º boot) |

### Fluxo atual

```
HTTP → app.py (blueprints) → routes/*.py
                                  │  (controllers gordos)
                                  ├─ validação inline (duplicando utils/ e models/)
                                  ├─ regra de negócio (overdue, stats, agregação de relatório)
                                  ├─ acesso a dados (Model.query... com N+1)
                                  └─ serialização manual (duplicando to_dict)
   services/notification_service.py  → NUNCA chamado (morto)
   utils/helpers.py                  → process_task_data / constantes → quase nunca usados
```

> Existe estrutura de camadas, mas **a dependência não flui por elas**: os controllers
> reimplementam validação/serialização/regra que já existem (ou deveriam existir) em
> `models/`, `utils/` e `services/`. Organização nominal, não arquitetural.

### Tabelas e relacionamentos (`models/`)

```
users(id, name, email[unique], password, role, active, created_at)
categories(id, name, description, color, created_at)
tasks(id, title, description, status, priority, user_id → users.id,
      category_id → categories.id, created_at, updated_at, due_date, tags[CSV])
```

> Aqui **há FKs declaradas** (`db.ForeignKey`) e relationships — melhor que P1/P2. Mas
> `tags` é armazenada como CSV em `String(500)` (modelagem pobre).

---

## 2. Heurísticas de Detecção (exercitadas em projeto já em camadas)

Genéricas no doc do P1. Sinais **novos** que importam quando o projeto *parece* organizado:

| Sinal | Conclusão |
|---|---|
| `flask_sqlalchemy` / `db.Model` / `db.Column` | ORM SQLAlchemy ⇒ queries parametrizadas (sem SQLi) |
| Pastas `models/ routes/ services/ utils/` + `Blueprint(...)` | camadas **declaradas** |
| Service/util **definido mas nunca importado** (`grep -r NotificationService` → só a definição) | **camada morta** (HIGH) |
| Mesma regra (ex.: cálculo de "overdue") repetida em vários arquivos | regra no controller + duplicação |
| `to_dict()`/`validate_*` existem no model mas o controller monta dict/valida na mão | camadas não respeitadas |
| `hashlib.md5(`/`hashlib.sha1(` para senha | hashing fraco (CRITICAL) |
| Campo sensível (`password`) presente em `to_dict`/serialização | exposição de dados (CRITICAL) |
| `datetime.utcnow()` / `Model.query.get(` | **APIs deprecated** (ver §4) |

→ **Projeto 3:** todos os sinais acima disparam. **Não se pode** concluir "já está
em MVC, nada a fazer" só por ver as pastas.

---

## 3. Catálogo de Anti-Patterns (com sinais de detecção e severidade)

Distribuição mínima exigida (**≥1 CRITICAL/HIGH, ≥2 MEDIUM, ≥2 LOW**) coberta com folga.

### 🔴 CRITICAL

#### C1 — Hashing de senha fraco (MD5, sem salt)
- **Sinal de detecção:** `hashlib.md5`/`sha1` aplicado a senha; comparação por igualdade de hash.
- **Evidência:** `models/user.py:29` (`set_password` usa `hashlib.md5`) e `:32` (`check_password` compara MD5). Sem salt, vulnerável a rainbow tables; seed grava senhas fracas (`seed.py:19,26,33`).
- **Impacto:** senhas efetivamente quebráveis. Falha de segurança grave.

#### C2 — Exposição do hash de senha nas respostas da API
- **Sinal de detecção:** campo `password`/`senha` presente em `to_dict`/serialização retornada por endpoints.
- **Evidência:** `models/user.py:21` inclui `'password'` no `to_dict`; vazado por `GET /users/<id>` (`user_routes.py:33`), pela resposta de **criar usuário** (`user_routes.py:85`) e pelo **login** (`user_routes.py:209`).
- **Impacto:** todo hash de senha trafega para o cliente — vazamento direto de credencial.

#### C3 — Segredos hardcoded (SECRET_KEY + credenciais SMTP)
- **Sinal de detecção:** `SECRET_KEY`/senha/token literais no código, sem env/`.env`.
- **Evidência:** `app.py:13` (`SECRET_KEY = 'super-secret-key-123'`); `services/notification_service.py:9-10` (`email_user`/`email_password = 'senha123'`). O projeto até depende de `python-dotenv`, mas **não o usa**.
- **Impacto:** segredos versionados/expostos; conta de e-mail comprometível.

### 🟠 HIGH

#### H1 — Regra de negócio presa nos controllers (rotas gordas)
- **Sinal de detecção:** cálculo/agregação de domínio dentro do handler de rota, em vez de service/model.
- **Evidência:** cálculo de "overdue" inline em `task_routes.py:30-39, 71-80, 283-287` e `user_routes.py:171-180`; **agregação completa do relatório** em `report_routes.py:13-101` (contagens, produtividade por usuário); `task_stats` em `task_routes.py:273-299`. `models/task.py` tem `is_overdue`/`validate_*` mas as rotas **não usam**.
- **Impacto:** regra não testável sem HTTP, espalhada e divergente; viola SRP/MVC mesmo com a pasta `routes/` existindo.

#### H2 — Camadas mortas / dependência que não flui pelas camadas
- **Sinal de detecção:** service/util definido e **nunca importado**; controllers duplicando o que a camada oferece.
- **Evidência:** `services/notification_service.py` (`NotificationService`) **não é importado em lugar nenhum**; `utils/helpers.py` define `process_task_data`, `validate_email`, `sanitize_string`, `VALID_STATUSES`, `MAX_TITLE_LENGTH` etc. — porém as rotas **reimplementam** validação/regex inline (`user_routes.py:61,106`; `task_routes.py:96-114`).
- **Impacto:** ilusão de arquitetura; manutenção piora porque há duas fontes da verdade.

#### H3 — Autenticação quebrada + mass-assignment de privilégio
- **Sinal de detecção:** "token" previsível/fake; ausência de guarda de auth em rotas destrutivas; campo `role`/permissão setável pelo cliente.
- **Evidência:** login devolve `'fake-jwt-token-' + id` (`user_routes.py:210`) — previsível e não verificado; **nenhuma** rota exige auth (qualquer um faz `DELETE /users/<id>`); `role` aceito do body em `create_user` (`user_routes.py:52,78`) e `update_user` (`user_routes.py:119-122`) ⇒ **escalada de privilégio** (cliente se torna `admin`).
- **Impacto:** sem segurança real de acesso; qualquer cliente vira admin ou apaga dados.

### 🟡 MEDIUM

#### M1 — Query N+1 (e ausência de paginação)
- **Sinal de detecção:** `Model.query.get/filter_by` dentro de laço; `len(rel)` disparando lazy-load por item; endpoints sem `limit/offset`.
- **Evidência:** `task_routes.py:41-57` (por task, busca `User` e `Category`); `report_routes.py:53-68` (por usuário, `Task.query.filter_by`); `user_routes.py:22` (`len(u.tasks)` por usuário). Nenhum endpoint de listagem pagina (retorna tudo).
- **Impacto:** queries proporcionais ao volume; resolvível com `join`/`selectinload` e paginação.

#### M2 — Duplicação massiva (regra, serialização e validação)
- **Sinal de detecção:** mesmo bloco copiado em vários arquivos; serialização manual onde já existe `to_dict`.
- **Evidência:** lógica de "overdue" repetida em ≥5 lugares (ver H1); serialização manual de task em `task_routes.py:17-28` e `user_routes.py:162-169` em vez de `Task.to_dict`; validação de status/priority repetida em rotas, `models/task.py` **e** `utils/helpers.py`.
- **Impacto:** correção precisa ser replicada; alta chance de divergência/bug.

#### M3 — `except:` nu, erros silenciados e `print` como log
- **Sinal de detecção:** `except:`/`except Exception` sem tratamento; `print(...)` para log; respostas de erro inconsistentes.
- **Evidência:** `except:` nu em `task_routes.py:62,236`, `user_routes.py:130,149`, `report_routes.py:186,207,221`, `helpers.parse_date:46,49`; `print` em vários handlers (`task_routes.py:149,153`; `user_routes.py:83,89`); sem logging estruturado.
- **Impacto:** falhas mascaradas (até `KeyboardInterrupt`), difícil diagnosticar; sem observabilidade.

### 🟢 LOW

#### L1 — Magic numbers / constantes duplicadas (ignorando as de `utils`)
- **Sinal de detecção:** literais de negócio repetidos inline existindo constante nomeada.
- **Evidência:** limites de título `3`/`200`, `priority 1..5`, senha `< 4` repetidos em `task_routes.py:96-114` e `user_routes.py:64`; listas de status hardcoded inline (`task_routes.py:110,177`) enquanto `utils/helpers.py:110-116` define `VALID_STATUSES`, `MAX_TITLE_LENGTH`, `MIN_PASSWORD_LENGTH` **sem uso**.
- **Impacto:** intenção obscura, valores fáceis de divergir.

#### L2 — Código verboso / não-idiomático
- **Sinal de detecção:** `if cond: return True else: return False`; `type(x) == list`; ifs aninhados para um booleano; dict montado campo a campo.
- **Evidência:** `models/user.py:34-38` (`is_admin`), `models/task.py:38-60` (validações e `is_overdue` em ifs aninhados), `type(tags) == list` (`task_routes.py:141,210`) em vez de `isinstance`.
- **Impacto:** legibilidade e manutenção reduzidas.

#### L3 — Imports e helpers mortos
- **Sinal de detecção:** imports sem uso; funções definidas e nunca chamadas.
- **Evidência:** `utils/helpers.py:3-7` importa `os, sys, math, json, hashlib` (não usados) e define `generate_id`, `calculate_percentage`, `sanitize_string`, `is_valid_color` em sua maioria sem uso; `task_routes.py:7` importa `json, os, sys, time` sem uso.
- **Impacto:** ruído, confusão sobre o que está em uso.

### Cobertura da distribuição mínima exigida

| Severidade | Exigido | Encontrado neste projeto |
|---|---|---|
| CRITICAL/HIGH | ≥ 1 | **6** (C1–C3, H1–H3) |
| MEDIUM | ≥ 2 | **3** (M1–M3) |
| LOW | ≥ 2 | **3** (L1–L3) |

---

## 4. Detecção de APIs deprecated (sinal do catálogo) ⭐

Diferente de P1/P2, **aqui há APIs deprecated reais** — principal achado de "deprecated" do desafio.

#### D1 — `datetime.utcnow()` (deprecated no Python 3.12+)
- **Sinal de detecção:** chamadas a `datetime.utcnow()` (retorna *naive datetime*; marcado deprecated).
- **Evidência:** `models/user.py:14`, `models/task.py:15-16,52`, `task_routes.py:31,…`, `report_routes.py:35,42,45`, `utils/helpers.py:38`, `seed.py:66-75` — uso pervasivo.
- **Equivalente moderno:** `datetime.now(datetime.UTC)` (timezone-aware).

#### D2 — `Model.query.get(id)` (legacy/deprecated na SQLAlchemy 2.0)
- **Sinal de detecção:** `X.query.get(pk)` (API Query legada).
- **Evidência:** `User.query.get(...)`, `Task.query.get(...)`, `Category.query.get(...)` em todas as rotas (`task_routes.py:42,51,67,158`; `user_routes.py:29,94`; `report_routes.py:105,192,213`).
- **Equivalente moderno:** `db.session.get(Model, pk)`.
