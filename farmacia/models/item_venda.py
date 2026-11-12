from typing import Optional


class ItemVenda:
    def __init__(
        self,
        medicamento_id: int,
        quantidade: int,
        preco_unitario_centavos: int,
        subtotal_centavos: int,
        venda_id: Optional[int] = None,
        id: Optional[int] = None,
        medicamento_nome: Optional[str] = None,
    ):
        self.id = id
        self.venda_id = venda_id
        self.medicamento_id = medicamento_id
        self.quantidade = quantidade
        self.preco_unitario_centavos = preco_unitario_centavos
        self.subtotal_centavos = subtotal_centavos
        self.medicamento_nome = medicamento_nome

    def preco_unitario_em_reais(self) -> float:
        return self.preco_unitario_centavos / 100

    def subtotal_em_reais(self) -> float:
        return self.subtotal_centavos / 100

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "venda_id": self.venda_id,
            "medicamento_id": self.medicamento_id,
            "medicamento_nome": self.medicamento_nome,
            "quantidade": self.quantidade,
            "preco_unitario_centavos": self.preco_unitario_centavos,
            "preco_unitario_reais": self.preco_unitario_em_reais(),
            "subtotal_centavos": self.subtotal_centavos,
            "subtotal_reais": self.subtotal_em_reais(),
        }
