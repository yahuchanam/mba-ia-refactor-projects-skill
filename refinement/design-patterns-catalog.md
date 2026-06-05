# Catálogo de Princípios & Padrões de Design

Catálogo de Design Patterns para ser utilizado para escrita e refatoração de códigos.
Cobre: **SOLID**, **DRY**, **KISS**, **YAGNI**, **MVC** e **Object Calisthenics**.

---

## SOLID

| Princípio | O que diz | Como aplicar | Indício de violação |
|---|---|---|---|
| **SRP** — Single Responsibility | Uma classe/módulo tem um único motivo para mudar | Separar responsabilidades em camadas (config / model / repository / service / controller); uma razão de mudança por unidade | God Class, controller "gordo", model que também faz negócio |
| **OCP** — Open/Closed | Aberto para extensão, fechado para modificação | Estender via abstração/estratégia/polimorfismo em vez de editar código existente | `if/elif`/`switch` gigante por tipo; alterar a mesma função a cada caso novo |
| **LSP** — Liskov Substitution | Subtipos devem ser substituíveis pelo tipo base sem quebrar o contrato | Subclasses honram contratos e invariantes; não restringir entrada nem ampliar efeitos | Subclasse que lança `NotImplemented`/ignora método; checagem de tipo concreto para desviar fluxo |
| **ISP** — Interface Segregation | Muitas interfaces pequenas e coesas, não uma "fat interface" | O cliente depende só do que usa; quebrar interfaces grandes por papel | Implementadores deixam métodos vazios ou lançam erro por não usá-los |
| **DIP** — Dependency Inversion | Depender de abstrações, não de implementações; alto nível não depende de baixo nível | Injetar dependências (construtor/factory); depender de interface/porta; montar tudo no composition root | Instanciar banco/serviço concreto no construtor; import direto de implementação |

## DRY · KISS · YAGNI

| Princípio | O que diz | Como aplicar | Indício de violação |
|---|---|---|---|
| **DRY** — Don't Repeat Yourself | Cada conhecimento tem uma representação única no sistema | Extrair validação/serialização/regra repetida; uma única fonte da verdade | Validação copiada entre handlers, serialização manual repetida, constantes duplicadas |
| **KISS** — Keep It Simple | A solução mais simples que resolve o problema atual | Fluxo linear, funções curtas, sem indireção/abstração sem ganho; preferir `async/await` a callbacks aninhados | Callback hell, ifs profundamente aninhados, camadas/abstrações que não pagam o custo |
| **YAGNI** — You Aren't Gonna Need It | Não implemente o que não é necessário agora | Remover código morto e feature especulativa; entregar só o que o requisito atual pede | Helpers/camadas nunca usados, colunas/flags sem leitura, generalização prematura |

## MVC (e camadas de apoio)

Arquitetura-alvo: cada camada com responsabilidade única e dependência fluindo de fora
(HTTP) para dentro (domínio).

| Camada | Responsabilidade | Faz | Não faz |
|---|---|---|---|
| **Config** | Configuração e segredos | Carregar settings de ambiente/`.env`; expor constantes de configuração | Conter regra de negócio ou segredo hardcoded |
| **Model** | Dados e regras invariantes do próprio dado | Definir entidade, mapeamento de persistência, validações de invariante | Parsing HTTP, roteamento, orquestração entre entidades |
| **Repository / Data Access** | Encapsular acesso a dados | Queries parametrizadas, CRUD, leituras especializadas (com `JOIN`/eager loading) | Regra de negócio, conhecer request/response |
| **Service** | Regra de negócio e orquestração (casos de uso) | Coordenar models/repositories, transações, disparar side-effects via abstração | Conhecer `request`/`response` ou detalhes de HTTP |
| **Controller** | Adaptar HTTP ao caso de uso | Validar/parsear entrada, chamar o service, montar resposta e status code | Regra de negócio, SQL, acesso direto ao banco |
| **View / Routes** | Declarar endpoints e serialização de saída | Mapear rota → controller; DTO de saída sem campos sensíveis | Lógica de negócio ou de acesso a dados |
| **Middleware / Error handler** | Preocupações transversais | Auth, CORS, logging, tratamento central de erros | Regra de negócio específica de domínio |

## Object Calisthenics

Diretrizes pragmáticas para classes/métodos pequenos e coesos (aplicar com bom senso).

| Regra | O que diz | Como aplicar / benefício |
|---|---|---|
| **1. Um nível de indentação por método** | Evite laços/ifs aninhados num mesmo método | Extrair métodos; cada um faz uma coisa, fica testável |
| **2. Não use `else`** | Prefira early return / guard clauses | Reduz ramificação e aninhamento; caminho feliz claro |
| **3. Encapsule primitivos com significado** | Tipos primitivos que carregam regra viram value objects | `Email`, `Money`, `Priority` centralizam validação e comportamento |
| **4. Coleções de primeira classe** | Uma coleção com regras ganha sua própria classe | Encapsula operações/invariantes da coleção num só lugar |
| **5. Um ponto por linha (Lei de Demeter)** | Não encadeie acessos atravessando objetos | Fale só com vizinhos diretos; reduz acoplamento estrutural |
| **6. Não abrevie** | Nomes completos e descritivos | Intenção explícita; menos comentários necessários |
| **7. Mantenha entidades pequenas** | Classes, arquivos e métodos curtos | Limita responsabilidade; facilita leitura e teste |
| **8. No máximo duas variáveis de instância** | Limite o estado por classe | Força coesão e composição em vez de classes "faz-tudo" |
| **9. Tell, don't ask (sem getters/setters expostos)** | Comportamento mora na classe dona do dado | Evita lógica espalhada manipulando estado cru de terceiros |

## Guia de uso

Durante escrita ou refatoração de código, cada anti-pattern corrigido deve aproximar o código de um ou mais destes princípios (não há limite de uso, desde que mantenha o código simples e seguindo o principio KISS). O catálogo de anti-patterns aponta **o que está errado**; este aponta **para onde mover**.
