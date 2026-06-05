---
name: refactor-arch
description: >-
  Analisa, audita e refatora backends legados para o padrão MVC — agnóstico de
  linguagem e framework. Detecta a stack, mapeia a arquitetura, cruza o código
  contra um catálogo de anti-patterns e gera um relatório de auditoria; então
  PAUSA para confirmação humana (HITL) antes de qualquer refatoração. Use ao
  herdar/avaliar um backend legado, fazer auditoria de arquitetura/segurança,
  ou planejar migração para MVC.
---

# refactor-arch

Skill que conduz a avaliação e a evolução arquitetural de um backend legado como um
**workflow de 3 fases com human-in-the-loop (HITL)**. As Fases 1 e 2 são **somente
leitura** — nenhum arquivo é modificado. A Fase 3 (refatoração) só inicia após
**confirmação humana explícita** do relatório de auditoria.

> ⚠️ **Esta versão implementa as Fases 1 e 2 + o gate de confirmação.** A Fase 3
> (refatoração para MVC) ainda **não** está implementada nesta skill — ao chegar no gate,
> a skill para e aguarda. Veja [Fase 3](#fase-3--refatoração-pendente).

## Visão geral do workflow

```
┌── Fase 1 ─────────┐   ┌── Fase 2 ──────────┐   ┌─🛑 HITL ─────┐   ┌── Fase 3 ──────┐
│ Análise           │ → │ Auditoria          │ → │ Confirmação  │ → │ Refatoração    │
│ (detecta stack,   │   │ (relatório de      │   │ humana       │   │ (MVC + valida) │
│  mapeia arquit.)  │   │  achados CRIT→LOW) │   │ obrigatória  │   │  [pendente]    │
└───────────────────┘   └────────────────────┘   └──────────────┘   └────────────────┘
        somente leitura ──────────────────────────►│ gate │◄──── modifica arquivos
```

**Princípio inviolável:** nenhuma escrita/edição/remoção de arquivo do projeto-alvo antes
do gate de confirmação. Em caso de dúvida, pare e pergunte.

---

## Fase 1 — Análise

**Objetivo:** detectar linguagem, framework, banco de dados e mapear a arquitetura atual.
**Saída:** um resumo impresso. **Não modifica nada.**

### Heurísticas de detecção (agnósticas)

| Alvo | Sinais |
|---|---|
| **Linguagem** | `requirements.txt`/`*.py` → Python · `package.json`/`*.js`/`*.ts` → Node · `go.mod` → Go · `Gemfile` → Ruby · `composer.json` → PHP |
| **Framework** | `Flask(__name__)`/`flask==` → Flask · `fastapi`/`APIRouter` → FastAPI · `manage.py`/`settings.py` → Django · `require('express')` → Express |
| **Banco** | `sqlite3.connect`/`new sqlite3.Database` → SQLite cru · `flask_sqlalchemy`/`db.Model` → SQLAlchemy · `psycopg2`/`mysql.connector`/`mongoose` → Postgres/MySQL/Mongo · strings `CREATE TABLE`/`SELECT … FROM` → SQL manual |
| **Arquitetura** | tudo em 1 arquivo ou 1 classe "faz-tudo" → monólito/God Class · arquivos por papel importando-se direto, sem service/config → separação nominal · pastas `models/ routes/ services/ utils/` + blueprints/DI → camadas parciais |
| **Entry point / rotas** | bloco de bootstrap (`app.run`, `app.listen`, `if __name__ == "__main__"`); contar método+path dá a **superfície de rotas** a preservar |

### Passos

1. Listar os arquivos-fonte e dependências (sem executar o projeto).
2. Aplicar as heurísticas acima para identificar stack e arquitetura.
3. Mapear tabelas/entidades e a superfície de rotas (método + path).
4. Imprimir o resumo no formato:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem>
Framework:     <framework + versão>
Persistence:   <banco + driver/ORM>
Domain:        <domínio inferido>
Architecture:  <resumo da arquitetura atual>
Entry point:   <arquivo + como sobe>
Source files:  <N> analyzed (~<LOC> LOC)
DB tables:     <tabelas>
Endpoints:     <contagem + destaques>
================================
```

---

## Fase 2 — Auditoria

**Objetivo:** cruzar o código contra o catálogo de anti-patterns e emitir um relatório
estruturado. **Não modifica nada.**

### Passos

1. Para cada entrada do [`anti-patterns-catalog.md`](./anti-patterns-catalog.md), procurar
   os **sinais de detecção** no código. Registrar cada ocorrência com `arquivo:linha` exato.
2. Classificar cada achado pela **severidade** do catálogo (CRITICAL / HIGH / MEDIUM / LOW)
   e verificar **APIs deprecated** (seção própria do catálogo).
3. Preencher o relatório seguindo **exatamente** o [`audit-report-template.md`](./audit-report-template.md):
   cabeçalho, resumo com contagem por severidade, achados **ordenados CRITICAL → LOW**, e a
   seção de APIs Deprecated.
4. Salvar o relatório em `reports/audit-project-<N>.md` (criar a pasta `reports/` se preciso).
5. Apresentar o relatório ao usuário e **seguir para o gate**.

> O catálogo de princípios [`design-patterns-catalog.md`](./design-patterns-catalog.md)
> (SOLID, DRY, KISS, YAGNI, MVC, Object Calisthenics) é a régua-alvo: cada achado deve
> apontar para qual princípio a correção aproxima o código.

### Critérios mínimos do relatório

- ≥ 5 achados, incluindo ≥ 1 CRITICAL ou HIGH.
- Cada achado com `arquivo:linha` e os campos do template (Descrição, Impacto, Recomendação).
- Achados ordenados por severidade; deprecated em seção própria.

---

## 🛑 Gate de confirmação (HITL)

Ao terminar a Fase 2, a skill **PARA**. Antes de qualquer modificação:

1. Confirme em voz alta que **nenhum arquivo do projeto-alvo foi alterado** até aqui.
2. Apresente o resumo do relatório (contagem por severidade + total).
3. Pergunte explicitamente ao usuário, e **aguarde resposta**:

   > "Fase 2 concluída — relatório salvo em `reports/audit-project-<N>.md` (somente leitura).
   > Deseja que eu prossiga com a refatoração para MVC? Responda **sim** para continuar, ou
   > peça ajustes/esclarecimentos antes."

4. **Não prossiga** sem um "sim" (ou equivalente) explícito do usuário. Pedidos de
   esclarecimento, ajuste de achados ou nova auditoria **não** contam como aprovação.

---

## Fase 3 — Refatoração (pendente)

> 🚧 **Não implementada nesta versão da skill.** Mesmo após o "sim" no gate, esta versão
> não executa a refatoração: informe ao usuário que a Fase 3 será adicionada numa próxima
> iteração (depende do *playbook de refatoração* e das *guidelines de MVC* detalhadas).

Quando implementada, a Fase 3 deverá: reestruturar para MVC (config sem segredos, models,
repositório/queries parametrizadas, service layer, controllers finos, error handling
central, entry point limpo), **e validar** que a aplicação sobe sem erros e que **todos os
endpoints originais continuam respondendo**.

---

## Arquivos de referência

| Arquivo | Conteúdo | Status |
|---|---|---|
| [`anti-patterns-catalog.md`](./anti-patterns-catalog.md) | Catálogo de anti-patterns (sinais, severidade, impacto, correção) + deprecated | ✅ |
| [`design-patterns-catalog.md`](./design-patterns-catalog.md) | Princípios-alvo: SOLID, DRY, KISS, YAGNI, MVC (camadas), Object Calisthenics | ✅ |
| [`audit-report-template.md`](./audit-report-template.md) | Esqueleto padronizado do relatório de auditoria (Fase 2) | ✅ |
| *(pendente)* heurísticas de análise detalhadas | Referência dedicada da Fase 1 (hoje resumida inline acima) | ⏳ |
| *(pendente)* playbook de refatoração | ≥8 transformações antes/depois para a Fase 3 | ⏳ |

> **Auto-contida e copiável:** a skill não referencia caminhos fora desta pasta, podendo ser
> copiada para outros projetos sem ajustes. Não assuma uma stack específica.
