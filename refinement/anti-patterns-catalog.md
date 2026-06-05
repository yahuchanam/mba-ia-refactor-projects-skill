# Catálogo de Anti-Patterns

Catálogo **agnóstico de stack** para classificar achados de auditoria em qualquer backend,
independente de linguagem, framework ou nível de organização. Cada entrada traz **sinais de
detecção acionáveis** (grep-áveis, não genéricos), **severidade**, **impacto** e **direção de
correção**.

## Escala de severidade

| Nível | Definição |
|---|---|
| 🔴 **CRITICAL** | Falha grave de arquitetura/segurança: expõe dados sensíveis (credenciais hardcoded, SQL Injection) ou viola completamente a separação de responsabilidades (God Class com DB + lógica + roteamento juntos). |
| 🟠 **HIGH** | Forte violação de MVC/SOLID que dificulta muito manutenção e testes: regra de negócio presa em controllers, acoplamento sem DI, estado global mutável. |
| 🟡 **MEDIUM** | Padronização, duplicação ou performance moderada: queries N+1, validações ausentes, uso inadequado de middlewares. |
| 🟢 **LOW** | Legibilidade, nomenclatura ruim, magic numbers. |
| ⏳ **DEPRECATED** | Uso de API obsoleta; severidade efetiva varia (em geral LOW–MEDIUM) conforme risco de quebra. |

## Catálogo

| Anti-pattern | Severidade | Sinais | Impacto | Correção |
|---|:---:|---|---|---|
| **SQL Injection** | 🔴 CRITICAL | SQL montado com concatenação/f-string/template interpolando entrada do usuário em `execute/query/run`, em vez de placeholders (`?`, `:nome`, `$1`) | Leitura/alteração/destruição de dados e bypass de autenticação | Queries parametrizadas / query builder / ORM |
| **Segredos e credenciais hardcoded** | 🔴 CRITICAL | Literais de `SECRET_KEY`/senha/API key/token no código; ausência de `.env` ou variáveis de ambiente (mesmo com lib de env instalada) | Segredo versionado e exposto; sessão/integração comprometível | Carregar de ambiente/secret manager; remover do histórico |
| **Exposição de dados sensíveis** | 🔴 CRITICAL | Campo de senha/segredo presente na serialização de saída; `print`/log de cartão, token, chave ou PII | Vazamento direto de credenciais/PII para clientes ou logs | DTO de saída sem campos sensíveis; redigir/filtrar logs |
| **Armazenamento inseguro de senha** | 🔴 CRITICAL | Senha gravada sem hash; `md5`/`sha1` para senha; função de hashing artesanal; comparação direta de senha | Senhas quebráveis/expostas; autenticação não confiável | `bcrypt`/`argon2`/`werkzeug.security` com salt |
| **God Class / God Module** | 🔴 CRITICAL | Uma classe/arquivo detém a conexão de banco, registra rotas **e** implementa regra de negócio; arquivo "model" que também faz negócio | Zero testabilidade isolada; qualquer mudança arrisca tudo; viola SRP/MVC | Separar em config / model / repository / service / controller |
| **Endpoint de execução arbitrária** | 🔴 CRITICAL | Rota que recebe SQL/comando do corpo e executa direto; rota destrutiva sem autenticação | RCE-equivalente sobre o banco; cliente lê/escreve/reseta tudo | Remover; substituir por operações específicas autenticadas |
| **Regra de negócio na camada errada** | 🟠 HIGH | Cálculo/agregação/orquestração de domínio dentro do handler de rota ou do acesso a dados; controllers "gordos"; service layer ausente ou ignorada | Regra não testável sem HTTP/DB, espalhada e divergente | Mover regra para service layer; controller só orquestra HTTP |
| **Estado global mutável** | 🟠 HIGH | Conexão/variável global mutável; objeto exportado e mutado por outro módulo; singleton compartilhado entre threads | Condições de corrida, acoplamento global, estado não isolável; vazamento de memória | Escopo por request / injeção; cache com ciclo de vida explícito |
| **Side-effects de infraestrutura no controller** | 🟠 HIGH | Controller disparando e-mail/SMS/push/notificação direto, sem service/fila | Controller acoplado a infra, impossível testar/mockar; mistura HTTP com entrega | Extrair para service/notification layer; idealmente assíncrono |
| **Acoplamento sem injeção de dependência** | 🟠 HIGH | Dependências concretas instanciadas no construtor/topo; imports diretos de implementação; sem interface/inversão | Impossível trocar/mocar banco ou serviços sem editar a classe | Injetar dependências (construtor/factory/container) |
| **Camadas mortas / dependência que não flui** | 🟠 HIGH | Service/util definido e **nunca importado**; controllers reimplementam o que a camada já oferece (validação/serialização) | Ilusão de arquitetura; duas fontes da verdade; manutenção pior | Ligar as camadas ou remover o código morto; uma fonte da verdade |
| **Autenticação quebrada + escalada de privilégio** | 🟠 HIGH | Token previsível/fake; rotas destrutivas sem guarda de auth; campo `role`/permissão aceito do corpo da request (mass-assignment) | Sem controle de acesso real; cliente vira admin ou apaga dados | Auth real verificada, middleware de autorização, allow-list de campos |
| **Callback hell / orquestração assíncrona pobre** | 🟠 HIGH | Fluxo de negócio aninhado em vários callbacks (pyramid of doom); coordenação manual com contadores em vez de `Promise.all`/`async-await` | Ilegível, frágil, difícil de testar; lógica de término propensa a bug | `async/await` + driver com Promises; transações |
| **Query N+1** | 🟡 MEDIUM | Query dentro de laço; acesso a relação disparando lazy-load por item; uma query por elemento da coleção | Queries proporcionais ao volume; degradação de performance | `JOIN`/eager loading/agregação em SQL |
| **Lógica duplicada** | 🟡 MEDIUM | Blocos de validação copiados entre handlers; mesma serialização repetida; mesma regra em vários arquivos | Correção precisa ser replicada; fonte de divergência/bug | Extrair validadores/serializers/utilitários reutilizáveis |
| **Validação de entrada ausente ou fraca** | 🟡 MEDIUM | Rota sem validação de formato (e-mail, data, tipos); valida só presença; sem schema | Dados inválidos persistidos; erros tardios | Validação por schema na borda; mensagens consistentes |
| **Tratamento de erro pobre + log via `print`** | 🟡 MEDIUM | `except`/`catch` sem ação; callbacks que ignoram o erro; `print`/`console.log` para log; respostas de erro inconsistentes | Falhas mascaradas; sem observabilidade | Logging estruturado; error handler central; exceções específicas |
| **Falta de integridade referencial** | 🟡 MEDIUM | Schema sem FK/`ON DELETE CASCADE`; `DELETE` do pai que deixa filhos órfãos | Dados órfãos/inconsistentes; relatórios contam registros quebrados | FKs + cascade ou tratamento transacional explícito |
| **Listagem sem paginação** | 🟡 MEDIUM | Retorno de toda a tabela (`.all()`/`SELECT *`); ausência de `limit`/`offset`/cursor | Payload e memória sem limite; latência | Paginação (limit/offset ou cursor) com defaults sãos |
| **Magic numbers / literais sem nome** | 🟢 LOW | Números/strings de negócio soltos (limites, faixas, percentuais) sem constante nomeada | Intenção obscura; difícil de ajustar com segurança | Constantes/config nomeadas |
| **Nomenclatura ruim / shadowing** | 🟢 LOW | Builtin sombreado; variáveis de uma letra; mistura de idiomas | Legibilidade e consistência reduzidas | Nomes descritivos e consistentes |
| **Código morto / imports não usados** | 🟢 LOW | Import sem uso; função definida e nunca chamada; coluna/campo criado e nunca lido | Ruído; confusão sobre o que está em uso | Remover; manter só o que é usado |
| **Código verboso / não-idiomático** | 🟢 LOW | `if cond: return True else: return False`; `type(x) == list`; ifs aninhados para um booleano; dict montado à mão onde há serializer | Manutenção e legibilidade reduzidas | Retornar a expressão booleana; `isinstance`; reuso de serializer |
| **Formato de resposta inconsistente** | 🟢 LOW | Envelopes que variam (objeto cru/texto/wrapper); códigos de status irregulares entre rotas | Contrato imprevisível para o cliente | Padronizar envelope e códigos (response/error handler) |
| **Uso de API deprecated** | ⏳ DEPRECATED | Import/uso de símbolo marcado como deprecated na versão da lib em uso; padrão substituído por API mais nova (ex.: `datetime.utcnow()`, API de ORM legada tipo `query.get()`, callbacks onde há Promise, hashing artesanal) | Quebra futura, avisos de deprecação, comportamento sutil incorreto (ex.: datetime *naive*) | Migrar ao equivalente moderno (ex.: `datetime.now(UTC)`, `session.get()`, `async/await`, `bcrypt`/`argon2`) |

