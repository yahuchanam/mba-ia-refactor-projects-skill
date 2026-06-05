# Template do Relatório de Auditoria

```markdown
================================
ARCHITECTURE AUDIT REPORT
================================
Projeto:       {{nome-do-projeto}}
Stack:         {{linguagem}} + {{framework}} ({{persistência}})
Arquitetura:   {{resumo da arquitetura atual}}
Arquivos:      {{N}} analisados | ~{{LOC}} linhas
Data:          {{YYYY-MM-DD}}

## Resumo
CRITICAL: {{n}} | HIGH: {{n}} | MEDIUM: {{n}} | LOW: {{n}} | DEPRECATED: {{n}}
Total: {{N}} achados

## Achados

### [CRITICAL] 1. <Nome do anti-pattern>
- **Arquivo:** <caminho:linha>
- **Descrição:** <o que foi encontrado>
- **Impacto:** <consequência>
- **Recomendação:** <direção de correção>

### [HIGH] 2. <Nome do anti-pattern>
- **Arquivo:** <caminho:linha>
- **Descrição:** ...
- **Impacto:** ...
- **Recomendação:** ...

### [MEDIUM] 3. <Nome do anti-pattern>
- **Arquivo:** <caminho:linha>
- **Descrição:** ...
- **Impacto:** ...
- **Recomendação:** ...

### [LOW] 4. <Nome do anti-pattern>
- **Arquivo:** <caminho:linha>
- **Descrição:** ...
- **Impacto:** ...
- **Recomendação:** ...

## APIs Deprecated
- **<API obsoleta>** em <caminho:linha> → usar **<equivalente moderno>**

================================
Total: {{N}} achados
================================

Relatório somente leitura — nenhum arquivo foi modificado.
```
