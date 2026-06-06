# Criação de Skills — Refatoração Arquitetural Automatizada

Ao longo do curso você aprendeu o que são Skills e como elas permitem que um agente de IA atue como um especialista em tarefas específicas. Agora imagine o seguinte cenário: você herdou 3 projetos legados com problemas de arquitetura, segurança e qualidade de código. Revisar e corrigir tudo manualmente levaria dias.

Neste desafio, você vai criar uma Skill que automatiza esse processo — analisando, auditando e refatorando qualquer projeto para o padrão MVC, independente da tecnologia.

## Objetivo

Você deve entregar uma Skill capaz de:

- Analisar uma codebase detectando linguagem, framework e arquitetura atual
- Identificar anti-patterns e code smells, classificando por severidade com arquivo e linha exatos
- Gerar um relatório de auditoria estruturado com todos os achados
- Refatorar o projeto para o padrão MVC (Model-View-Controller), eliminando os problemas encontrados
- Validar o resultado garantindo que a aplicação continua funcionando após as mudanças

A skill deve ser agnóstica de tecnologia, funcionando com diferentes linguagens e frameworks.

## Contexto

### Definição de Severidades

Para padronizar a sua auditoria e os relatórios gerados pela IA, utilize a seguinte escala de classificação baseada em problemas de MVC e SOLID:

- **CRITICAL:** Falhas graves de arquitetura ou segurança que impedem o funcionamento correto, expõem dados sensíveis (ex: credenciais hardcoded, SQL Injection) ou violam completamente a separação de responsabilidades (ex: "God Class" contendo banco de dados, lógicas complexas e roteamento no mesmo arquivo).
- **HIGH:** Fortes violações do padrão MVC ou princípios SOLID que dificultam muito a manutenção e testes (ex: lógicas de negócio pesadas presas dentro de Controllers, forte acoplamento sem Injeção de Dependência, ou uso de estado global mutável em toda a aplicação).
- **MEDIUM:** Problemas de padronização, duplicação de código ou gargalos de performance moderada (ex: Queries N+1 no banco de dados, uso inadequado de middlewares, validações ausentes nas rotas).
- **LOW:** Melhorias de legibilidade, nomenclatura de variáveis ruins, ou "magic numbers" soltos pelo código.

### Exemplo de Uso no CLI

```bash
# Executar a skill no projeto com problemas
cd code-smells-project
claude "/refactor-arch"
```

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:      Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] God Class / God Method
File: models.py:1-350
Description: Arquivo único contém toda lógica de negócio, queries SQL, validação e formatação para 4 domínios diferentes.
Impact: Impossível testar em isolamento, qualquer mudança afeta tudo.
Recommendation: Separar em models e controllers por domínio.

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded como 'minha-chave-super-secreta-123'
...

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```

```
[... refatoração executada ...]

================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
src/
├── config/settings.py
├── models/
│   ├── produto_model.py
│   └── usuario_model.py
├── views/
│   └── routes.py
├── controllers/
│   ├── produto_controller.py
│   └── pedido_controller.py
├── middlewares/error_handler.py
└── app.py (composition root)

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

## Tecnologias obrigatórias

- **Ferramenta:** uma das três opções abaixo (não são aceitas outras ferramentas):
  - Claude Code
  - Gemini CLI
  - OpenAI Codex
- **Recurso:** Custom Skills (ou o equivalente na ferramenta escolhida)
- **Formato dos arquivos de referência:** Markdown
- **Projetos-alvo:** Python/Flask (2 projetos) e Node.js/Express (1 projeto) (fornecidos no repositório base)

> **Nota sobre a ferramenta:** Os exemplos deste documento usam o Claude Code (`.claude/skills/`) como referência, pois é a ferramenta utilizada no curso. Se você optar por Gemini CLI ou Codex, adapte o nome da pasta e o comando de invocação conforme a convenção dela — o conceito de skill e a estrutura interna (SKILL.md + arquivos de referência) permanecem os mesmos.

## Requisitos

### 1. Análise Manual dos Projetos

Antes de criar a skill, você deve entender os problemas que ela vai resolver.

**Tarefas:**

- Analisar o projeto `code-smells-project/` (Python/Flask — API de E-commerce)
- Analisar o projeto `ecommerce-api-legacy/` (Node.js/Express — LMS API com fluxo de checkout)
- Analisar o projeto `task-manager-api/` (Python/Flask — API de Task Manager)

Para cada projeto, identificar e documentar no mínimo 5 problemas, incluindo pelo menos:

- 1 de severidade CRITICAL ou HIGH
- 2 de severidade MEDIUM
- 2 de severidade LOW

Documentar os achados na seção "Análise Manual" do seu `README.md`

> **Dica:** Não precisa encontrar todos os problemas — foque nos que têm maior impacto arquitetural. Use os projetos como insumo para entender quais padrões sua skill precisa detectar.

> **Por que 3 projetos?** Dois são Python/Flask (com níveis de organização diferentes) e um é Node.js/Express. Sua skill precisa funcionar nos 3 para provar que é verdadeiramente agnóstica de tecnologia — lidando tanto com código completamente desestruturado quanto com projetos que já possuem alguma separação de camadas.

### 2. Criação da Skill

Agora que você conhece os problemas, crie uma skill que os detecte, gere um relatório de auditoria e corrija automaticamente.

**Tarefas:**

Criar a skill dentro do projeto `code-smells-project/` e implementar o SKILL.md com 3 fases sequenciais:

- **Fase 1 — Análise:** Detectar stack, mapear arquitetura atual, imprimir resumo
- **Fase 2 — Auditoria:** Cruzar código contra catálogo de anti-patterns, gerar relatório, pedir confirmação
- **Fase 3 — Refatoração:** Reestruturar para o padrão MVC, validar que funciona

Criar arquivos de referência em Markdown que forneçam à skill o conhecimento necessário para executar as 3 fases. Os arquivos devem cobrir **obrigatoriamente** as seguintes áreas de conhecimento:

| Área de conhecimento | O que deve conter |
|---|---|
| Análise de projeto | Heurísticas para detecção de linguagem, framework, banco de dados e mapeamento de arquitetura |
| Catálogo de anti-patterns | Anti-patterns com sinais de detecção e classificação de severidade |
| Template de relatório | Formato padronizado do relatório de auditoria (Fase 2) |
| Guidelines de arquitetura | Regras do padrão MVC alvo (camadas Models, Views/Routes e Controllers, responsabilidades de cada uma) |
| Playbook de refatoração | Padrões concretos de transformação para cada anti-pattern (com exemplos de código) |

> **Nota:** Você tem liberdade para organizar os arquivos de referência como preferir — pode usar os nomes e a quantidade de arquivos que fizer sentido para sua skill. O importante é que todas as 5 áreas de conhecimento estejam cobertas. O nome da skill (`refactor-arch`) e o arquivo `SKILL.md` são obrigatórios e não devem ser alterados. O path da skill segue a convenção da ferramenta escolhida (no Claude Code, por exemplo, é `.claude/skills/refactor-arch/`).

**Requisitos da skill:**

- Deve ser agnóstica de tecnologia — deve funcionar corretamente nos 3 projetos fornecidos, independente da stack ou nível de organização
- O catálogo de anti-patterns deve conter no mínimo 8 anti-patterns com severidade distribuída (CRITICAL, HIGH, MEDIUM, LOW)
- O catálogo deve incluir detecção de APIs deprecated — identificar uso de APIs obsoletas e recomendar o equivalente moderno
- O playbook deve ter no mínimo 8 padrões de transformação com exemplos de código antes/depois
- A Fase 2 deve pausar e pedir confirmação antes de modificar qualquer arquivo
- A Fase 3 deve validar o resultado (boot da aplicação + endpoints funcionando)

### 3. Execução da Skill

Execute sua skill nos 3 projetos e valide que ela funciona em todas as stacks.

#### Projeto 1 — code-smells-project (Python/Flask)

Invocar a skill no Claude Code:

```bash
claude "/refactor-arch"
```

> **Nota:** O comando acima é o exemplo com Claude Code. Se você estiver usando Gemini CLI ou Codex, utilize o comando equivalente para invocar uma skill na sua ferramenta.

- Verificar que a Fase 1 detecta corretamente a stack e imprime o resumo
- Verificar que a Fase 2 encontra no mínimo 5 dos problemas documentados na sua análise manual
- Confirmar a execução da Fase 3
- Verificar que a Fase 3:
  - Cria a estrutura de diretórios baseada em MVC
  - A aplicação inicia sem erros
  - Os endpoints originais continuam respondendo
- Salvar o relatório de auditoria (output da Fase 2) em `reports/audit-project-1.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

Prove que sua skill é reutilizável em outro projeto de backend, mas com stack diferente.

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `ecommerce-api-legacy/`
- Invocar a skill:

```bash
cd ../ecommerce-api-legacy
claude "/refactor-arch"
```

- Verificar que as 3 fases executam corretamente neste projeto
- Salvar o relatório em `reports/audit-project-2.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 3 — task-manager-api (Python/Flask)

Agora o teste com um projeto Python/Flask que já possui alguma organização de camadas (models, routes, services, utils).

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `task-manager-api/`
- Invocar a skill:

```bash
cd ../task-manager-api
claude "/refactor-arch"
```

- Verificar que:
  - A Fase 1 detecta corretamente Python/Flask como stack e identifica o domínio de Task Manager
  - A Fase 2 identifica problemas mesmo em um projeto parcialmente organizado
  - A Fase 3 melhora a estrutura sem quebrar a aplicação (todos os endpoints devem continuar respondendo)
- Salvar o relatório em `reports/audit-project-3.md`
- Commitar o código refatorado do projeto no repositório

> **Nota:** Este projeto já possui alguma separação de camadas, mas isso não significa que a arquitetura está adequada. A skill deve identificar tanto problemas de código (segurança, performance, qualidade) quanto oportunidades de melhoria arquitetural. Se houver mudanças estruturais necessárias, a skill deve propô-las e executá-las.

#### Validação

Para cada projeto refatorado, valide o seguinte checklist:

```markdown
## Checklist de Validação

### Fase 1 — Análise
- [ ] Linguagem detectada corretamente
- [ ] Framework detectado corretamente
- [ ] Domínio da aplicação descrito corretamente
- [ ] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [ ] Relatório segue o template definido nos arquivos de referência
- [ ] Cada finding tem arquivo e linhas exatos
- [ ] Findings ordenados por severidade (CRITICAL → LOW)
- [ ] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (se aplicável)
- [ ] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para visualização ou roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
```

> **Dica:** Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Entregável

Repositório público no GitHub (fork do repositório base) contendo:

- Skill completa em `.claude/skills/refactor-arch/` (dentro dos 3 projetos)
- Código refatorado dos 3 projetos (resultado da execução da Fase 3, commitado no repositório)
- Relatórios de auditoria em `reports/` (3 arquivos)
- `README.md` atualizado

### Estrutura do repositório

Faça um fork do repositório base contendo os três projetos com code smells.

> **Nota:** A estrutura abaixo usa Claude Code como exemplo (`.claude/skills/`). Se estiver usando outra ferramenta, adapte os caminhos conforme a convenção dela.

```
desafio-skills/
├── README.md                              # Sua documentação
│
├── code-smells-project/                   # Projeto 1 — Python/Flask (API de E-commerce)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← SUA SKILL AQUI
│   │           ├── SKILL.md
│   │           └── (arquivos de referência)
│   ├── app.py
│   ├── controllers.py
│   ├── models.py
│   ├── database.py
│   └── requirements.txt
│
├── ecommerce-api-legacy/                  # Projeto 2 — Node.js/Express (LMS API com checkout)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── src/
│   │   ├── app.js
│   │   ├── AppManager.js
│   │   └── utils.js
│   ├── api.http
│   └── package.json
│
├── task-manager-api/                      # Projeto 3 — Python/Flask (API de Task Manager)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── app.py
│   ├── database.py
│   ├── seed.py
│   ├── requirements.txt
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
│
└── reports/                               # Relatórios gerados
    ├── audit-project-1.md                 # Saída da Fase 2 no projeto 1
    ├── audit-project-2.md                 # Saída da Fase 2 no projeto 2
    └── audit-project-3.md                 # Saída da Fase 2 no projeto 3
```

**O que você vai criar:**

- `.claude/skills/refactor-arch/` — A skill completa (SKILL.md + arquivos de referência)
- Código refatorado dos 3 projetos — resultado da execução da Fase 3, commitado no repositório
- `reports/audit-project-{1,2,3}.md` — Relatório de auditoria de cada projeto
- `README.md` — Documentação do seu processo

**O que já vem pronto:**

- `code-smells-project/` — API de E-commerce Python/Flask com code smells intencionais
- `ecommerce-api-legacy/` — LMS API Node.js/Express (com fluxo de checkout) e problemas de implementação
- `task-manager-api/` — API de Task Manager Python/Flask com organização parcial e problemas de segurança/qualidade

> **Dica:** Cada projeto contém problemas intencionais de diferentes severidades (CRITICAL, HIGH, MEDIUM, LOW), incluindo falhas de segurança, violações arquiteturais e problemas de qualidade de código. Parte do desafio é identificá-los por conta própria através da análise manual do código.

### README.md deve conter

**A) Seção "Análise Manual":**

- Lista dos problemas identificados manualmente em cada projeto
- Classificação por severidade
- Justificativa de por que cada problema é relevante

**B) Seção "Construção da Skill":**

- Decisões de design: como estruturou o SKILL.md e os arquivos de referência
- Quais anti-patterns incluiu no catálogo e por quê
- Como garantiu que a skill é agnóstica de tecnologia
- Desafios encontrados e como resolveu

**C) Seção "Resultados":**

- Resumo dos relatórios de auditoria dos 3 projetos (quantos findings por severidade em cada)
- Comparação antes/depois da estrutura de cada projeto
- Checklist de validação preenchido para cada projeto
- Screenshots ou logs mostrando as aplicações rodando após refatoração
- Observações sobre como a skill se comportou em stacks diferentes

**D) Seção "Como Executar":**

- Pré-requisitos (a ferramenta escolhida — Claude Code, Gemini CLI ou Codex — instalada e configurada)
- Comandos para executar a skill em cada projeto
- Como validar que a refatoração funcionou

### Ordem de execução sugerida

**1. Analisar os projetos manualmente**

Leia o código dos três projetos e documente os problemas encontrados.

**2. Criar a skill**

Escreva o SKILL.md e os arquivos de referência.

**3. Executar nos 3 projetos**

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

Salve a saída da Fase 2 de cada projeto em `reports/audit-project-{1,2,3}.md`.

**4. Iterar**

Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Critérios de Aceite

A skill deve atingir os seguintes mínimos em **todos os 3 projetos**:

| Critério | Requisito |
|---|---|
| Fase 1 detecta stack corretamente | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 encontra >= 5 findings | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 inclui pelo menos 1 CRITICAL ou HIGH | OBRIGATÓRIO (3/3 projetos) |
| Fase 3 aplicação funciona após refatoração | OBRIGATÓRIO (3/3 projetos) |

**IMPORTANTE:** Todos os critérios devem ser atingidos nos 3 projetos, não apenas em um!

> **Sobre o projeto 3 (task-manager-api):** Este projeto já possui alguma organização. "aplicação funciona" significa que a API inicia sem erros e todos os endpoints continuam respondendo corretamente.

## Referências

- [Claude Code: Skills](https://docs.anthropic.com/en/docs/claude-code/skills) — Documentação oficial sobre como criar e estruturar Skills
- [Claude Code: Overview](https://docs.anthropic.com/en/docs/claude-code/overview) — Visão geral do Claude Code e suas capacidades
- [The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) — Guia completo da Anthropic sobre construção de Skills
- [Equipping Agents for the Real World with Agent Skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills) — Blog oficial da Anthropic sobre Agent Skills

---

## Dicas Finais

- **Comece pela análise manual** — entender os problemas profundamente é essencial para criar uma skill que os detecte.
- **O SKILL.md é um prompt** — ele instrui o agente sobre o que fazer, enquanto os arquivos de referência fornecem o conhecimento de domínio.
- **Seja específico nos sinais de detecção** — "código ruim" não ajuda; "query SQL dentro de loop for" é acionável.
- **Teste incrementalmente** — não tente criar a skill perfeita de primeira.
- **A skill deve ser copiável** — se ela só funciona em um projeto específico, está acoplada demais. Teste nos 3 projetos para validar.
- **Projetos diferentes exigem adaptação** — a Fase 3 de um projeto já parcialmente organizado não vai ter as mesmas transformações de um monolito. Sua skill deve se adaptar ao contexto.
- **Pedir confirmação na Fase 2 é obrigatório** — o humano deve revisar o relatório antes de qualquer modificação.
- **Consulte as referências do curso** — revise a documentação oficial da ferramenta escolhida e os materiais das aulas para relembrar a estrutura e anatomia de uma skill.


# Resolução do desafio

A primeira parte do desafio analisai todos os projetos, um por vez, registrando e classificando os problemas.

## Análise Manual

Análise manual (Fase 1) de cada projeto-alvo — detecção de stack, mapeamento da
arquitetura atual e catálogo de anti-patterns com severidade e `arquivo:linha`.

| Projeto | Refinamento |
|---|---|
| Projeto 1 — `code-smells-project` (Python/Flask) | [phase1-project-1.md](refinement/phase1-project-1.md) |
| Projeto 2 — `ecommerce-api-legacy` (Node.js/Express) | [phase1-project-2.md](refinement/phase1-project-2.md) |
| Projeto 3 — `task-manager-api` (Python/Flask) | [phase1-project-3.md](refinement/phase1-project-3.md) |

## Construção da Skill

A skill começou como um único `SKILL.md` e evoluiu, por iterações, para um mapa que delega o
conhecimento a arquivos lidos sob demanda (progressive disclosure):

```
.claude/skills/refactor-arch/
├── SKILL.md                       # mapa: fluxo das 3 fases + gate HITL + índice de referência
├── rules/
│   ├── execution-conventions.md   # como rodar comandos sem fricção de permissão
│   └── stacks/{node,python,go,ruby,php,jvm,dotnet}.md
├── references/
│   ├── anti-patterns-catalog.md   # sinais de detecção + severidade (Fase 2)
│   ├── design-patterns-catalog.md # SOLID · DRY · KISS · YAGNI · MVC · Object Calisthenics
│   ├── audit-report-template.md   # formato do relatório
│   └── refactoring-playbook.md    # 14 transformações antes/depois
└── scripts/safe_remove.py         # remoção guardrailed (Fase 3)
```

### Estrutura

O `SKILL.md` orquestra três fases sequenciais com um único ponto de confirmação humana. As fases 1
e 2 são read-only; a fase 3 só inicia após `y` explícito no gate, que permanece no mapa para nunca
ser pulado.

### Catálogo e playbook

O catálogo reúne mais de 20 anti-patterns, descritos por sinal de detecção e correção, sem citar
projeto ou linguagem. Cobre todas as severidades — de SQL Injection, segredos hardcoded e God Class
(CRITICAL) a N+1 e validação fraca (MEDIUM) e magic numbers (LOW) — e inclui detecção de APIs
deprecated. As correções ficam no playbook, em pseudocódigo neutro, com 14 transformações
antes/depois.

### Agnosticismo de tecnologia

A fase 1 detecta a stack e a fase 3 lê apenas o `rules/stacks/<stack>.md` correspondente (Node,
Python, Go, Ruby, PHP, JVM, .NET). Cada arquivo descreve como instalar dependências, subir e parar
o ambiente, rodar testes e lint/format/build, e verificar as rotas in-process. O mapa não contém
caminho ou comando fixo de stack.

### Desafios e soluções

Orquestração da fase 3 — a refatoração é decomposta em tarefas paralelizáveis, com escala automática
(passe in-place para monolito pequeno; subagentes em git worktrees para projeto grande) e iteração
até a verificação passar.

Segurança sem remover rotas — uma versão removia endpoints perigosos, como `/admin/query`, e parava
para perguntar no meio da fase 3. A regra foi invertida para corrigir no lugar: SQL Injection vira
query parametrizada, e rota administrativa exposta sem proteção ganha autenticação e autorização. A
superfície de rotas nunca diminui e a fase roda sem nova interrupção.

Fricção de permissão — comandos compostos, prefixos de variável de ambiente, opções antes do
subcomando (`git -C`) e binários por caminho (`.venv/bin/pip`) disparam pedidos de aprovação. As
regras de execução foram reunidas em `execution-conventions.md`, pré-autorizadas via `allowed-tools`
e `settings.json`, e a verificação passou a usar test client in-process, sem servidor real nem `curl`.

## Resultados

### Projeto 1 — code-smells-project (Python/Flask, SQLite cru)

Refatorado e commitado (`0890d14`).

| Antes | Depois |
|---|---|
| 4 arquivos (`app.py`, `controllers.py`, `models.py`, `database.py`), ~780 LOC, monolito | MVC em camadas: `config/ models/ repositories/ services/ controllers/ routes/ middlewares/ utils/` + `tests/` |
| SQL por concatenação, segredo hardcoded, senha em plaintext, `/admin/*` sem auth | queries parametrizadas, config via env, hash salgado, `/admin/*` atrás de autenticação/admin (`middlewares/auth.py`) |
| sem service layer, conexão global mutável, sem paginação | services por domínio, conexão por request, `utils/pagination.py` |

#### Auditoria da fase 2

O relatório é exibido na sessão (read-only; por decisão de design não é persistido em disco). Traz
ao menos 5 findings, com no mínimo 1 CRITICAL, ordenados de CRITICAL a LOW, alinhados à
[análise manual](refinement/phase1-project-1.md) (7 CRITICAL/HIGH, 3 MEDIUM, demais LOW).

#### Validação da fase 3

- [x] Estrutura em camadas MVC
- [x] Configuração extraída para `config/`, sem valores hardcoded
- [x] Models e serializers
- [x] Rotas, controllers e services separados
- [x] Error handling central em `middlewares/error_handler.py`
- [x] Entry point claro (`app.py` como composition root)
- [x] Smoke test embarcado em `tests/test_smoke.py`
- [x] Endpoints originais preservados, incluindo `/admin/*`, agora protegidos

### Projeto 2 — ecommerce-api-legacy (Node.js/Express, SQLite cru)

Refatorado e commitado (`bbe8f39`).

| Antes | Depois |
|---|---|
| 3 arquivos em `src/`, ~180 LOC, `AppManager` concentrando banco, rotas e regras de negócio | MVC em camadas: `config/ models/ repositories/ services/ controllers/ routes/ middlewares/ security/ database/` + `test/` |
| credenciais hardcoded, cartão e chave de pagamento em log, senha em plaintext/hash caseiro, rotas administrativas sem auth | config via env, logs sem dados sensíveis, hash `scrypt` com salt, relatório e exclusão atrás de autenticação admin |
| callbacks aninhados, relatório com N+1, conexão concreta dentro do God Class, sem integridade referencial | `async/await`, query set-based paginada, dependências injetadas, transações serializadas e foreign keys com cascade |

#### Auditoria da fase 2

O relatório é exibido na sessão (read-only; por decisão de design não é persistido em disco).
Foram encontrados 18 findings: 4 CRITICAL, 5 HIGH, 5 MEDIUM, 3 LOW e 1 API deprecated, alinhados à
[análise manual](refinement/phase1-project-2.md).

#### Validação da fase 3

- [x] Estrutura em camadas MVC
- [x] Configuração extraída para `config/`, sem segredos hardcoded
- [x] Models, repositories e services separados
- [x] Rotas e controllers sem lógica de negócio ou acesso direto ao banco
- [x] Error handling central em `middlewares/errorHandler.js`
- [x] Entry point claro (`src/app.js` como composition root)
- [x] Testes de rota embarcados em `test/routes.test.js`
- [x] Endpoints originais preservados; relatório e exclusão agora protegidos por `ADMIN_TOKEN`
- [x] Format, lint, build, testes e `npm audit` verdes

## Como Executar

### Pré-requisitos

- Claude Code instalado
- Python 3 e [`uv`](https://docs.astral.sh/uv/) (ou `pip`) para os projetos Flask
- Node 18+ para o projeto Express

### Rodar a skill

### Projeto 1 - Code Smells Project

A partir da raiz de cada projeto:

```bash
cd code-smells-project
claude "/refactor-arch"
```

O fluxo passa pela fase 1 (análise, read-only), pela fase 2 (auditoria, read-only) e pelo gate
`Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]`. Responda `y` para iniciar a fase 3,
que refatora de forma autônoma até a verificação passar. A pasta `.claude/` é a mesma nos três
projetos via symlink, então o comando não muda entre eles.

#### Subir o projeto refatorado

```bash
cd code-smells-project
uv venv
uv pip install -r requirements.txt
uv run python app.py          # http://localhost:5000  (cria e popula loja.db no boot)
```

Segredos vêm do ambiente (`SECRET_KEY`, `DB_PATH`), com fallback de desenvolvimento.

#### Validar

A fase 3 roda format, lint e testes e verifica as rotas in-process. Para conferir à mão, rode o
smoke test embarcado:

```bash
uv run python -m pytest tests/
```

### Projeto 2 - Ecommerce API Legacy

A partir da raiz do projeto:

```bash
cd ecommerce-api-legacy
claude "/refactor-arch"
```

O fluxo é o mesmo: análise e auditoria read-only, gate de confirmação e fase 3 autônoma. A skill
detecta Node.js, Express e SQLite, preserva as três rotas originais e protege as operações
administrativas no lugar, sem reduzir a superfície da API.

#### Subir o projeto refatorado

```bash
cd ecommerce-api-legacy
npm install
ADMIN_TOKEN=dev-admin-token npm start    # http://localhost:3000
```

`PORT`, `DATABASE_FILENAME` e `ADMIN_TOKEN` vêm do ambiente. Sem `ADMIN_TOKEN`, a aplicação inicia,
mas as rotas administrativas respondem `503` até que a credencial seja configurada.

#### Validar

A fase 3 roda Prettier, ESLint, verificação de sintaxe, testes de rota in-process e auditoria de
dependências. Para repetir a validação:

```bash
npm run format:check
npm run lint
npm run build
npm test
npm audit --audit-level=low
```
