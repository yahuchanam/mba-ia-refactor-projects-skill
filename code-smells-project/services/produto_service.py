"""Produto business logic: validation (single source of truth) + use cases."""

from models import constants
from models.serializers import produto_to_dict
from utils.errors import NotFoundError, ValidationError


class ProdutoService:
    def __init__(self, repo, db) -> None:
        self.repo = repo
        self.db = db

    def _validate(self, dados: dict) -> dict:
        if not dados:
            raise ValidationError("Dados inválidos")
        for campo in ("nome", "preco", "estoque"):
            if campo not in dados:
                raise ValidationError(f"{campo.capitalize()} é obrigatório")

        nome = dados["nome"]
        preco = dados["preco"]
        estoque = dados["estoque"]
        descricao = dados.get("descricao", "")
        categoria = dados.get("categoria", constants.CATEGORIA_PADRAO)

        if not isinstance(preco, (int, float)) or preco < 0:
            raise ValidationError("Preço não pode ser negativo")
        if not isinstance(estoque, int) or estoque < 0:
            raise ValidationError("Estoque não pode ser negativo")
        if len(nome) < constants.NOME_MIN_LEN:
            raise ValidationError("Nome muito curto")
        if len(nome) > constants.NOME_MAX_LEN:
            raise ValidationError("Nome muito longo")
        if categoria not in constants.CATEGORIAS_VALIDAS:
            raise ValidationError(
                "Categoria inválida. Válidas: " + str(constants.CATEGORIAS_VALIDAS)
            )

        return {
            "nome": nome,
            "descricao": descricao,
            "preco": preco,
            "estoque": estoque,
            "categoria": categoria,
        }

    def listar(self, limit: int, offset: int):
        rows = self.repo.all(limit, offset)
        return [produto_to_dict(r) for r in rows], self.repo.count()

    def obter(self, produto_id: int) -> dict:
        row = self.repo.get(produto_id)
        if not row:
            raise NotFoundError("Produto não encontrado")
        return produto_to_dict(row)

    def buscar(self, termo, categoria, preco_min, preco_max, limit, offset):
        rows = self.repo.search(termo, categoria, preco_min, preco_max, limit, offset)
        return [produto_to_dict(r) for r in rows]

    def criar(self, dados: dict) -> int:
        clean = self._validate(dados)
        produto_id = self.repo.create(**clean)
        self.db.commit()
        return produto_id

    def atualizar(self, produto_id: int, dados: dict) -> None:
        if not self.repo.get(produto_id):
            raise NotFoundError("Produto não encontrado")
        clean = self._validate(dados)
        self.repo.update(produto_id, **clean)
        self.db.commit()

    def deletar(self, produto_id: int) -> None:
        if not self.repo.get(produto_id):
            raise NotFoundError("Produto não encontrado")
        self.repo.delete(produto_id)
        self.db.commit()
