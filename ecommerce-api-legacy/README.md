# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
npm install
npm start
```

A aplicação sobe em `http://localhost:3000`. O banco SQLite é em memória e já carrega seeds automaticamente no boot.

Exemplos de requisições estão em `api.http`.

## Configuração

- `PORT`: porta HTTP, com padrão `3000`.
- `DATABASE_FILENAME`: arquivo SQLite, com padrão `:memory:`.
- `ADMIN_TOKEN`: token Bearer obrigatório para o relatório financeiro e a exclusão de usuários.

Sem `ADMIN_TOKEN`, a aplicação inicia normalmente, mas as rotas administrativas respondem `503`
até que uma credencial seja configurada.

## Validação

```bash
npm run format:check
npm run lint
npm run build
npm test
```
