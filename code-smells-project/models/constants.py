"""Named domain constants — replaces magic numbers/strings scattered in the code."""

# Produtos
CATEGORIAS_VALIDAS = [
    "informatica",
    "moveis",
    "vestuario",
    "geral",
    "eletronicos",
    "livros",
]
CATEGORIA_PADRAO = "geral"
NOME_MIN_LEN = 2
NOME_MAX_LEN = 200

# Pedidos
STATUS_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]
STATUS_PADRAO = "pendente"

# Relatório de vendas — faixas de desconto sobre o faturamento (limiar, taxa)
DISCOUNT_TIERS = [
    (10000, 0.10),
    (5000, 0.05),
    (1000, 0.02),
]

# Paginação — padrão e teto aplicados em todas as listagens
PAGE_SIZE_DEFAULT = 20
PAGE_SIZE_MAX = 100
