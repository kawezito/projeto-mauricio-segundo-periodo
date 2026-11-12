from typing import Optional


class MovimentacaoEstoque:
    def __init__(
        self,
        medicamento_id: int,
        tipo: str,
        quantidade: int,
        data_movimentacao: str,
        descricao: Optional[str] = None,
        id: Optional[int] = None,
        medicamento_nome: Optional[str] = None,
    ):
        self.id = id
        self.medicamento_id = medicamento_id
        self.medicamento_nome = medicamento_nome
        self.tipo = tipo.upper()
        self.quantidade = quantidade
        self.data_movimentacao = data_movimentacao
        self.descricao = descricao

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "medicamento_id": self.medicamento_id,
            "medicamento_nome": self.medicamento_nome,
            "tipo": self.tipo,
            "quantidade": self.quantidade,
            "data_movimentacao": self.data_movimentacao,
            "descricao": self.descricao,
        }
