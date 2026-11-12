from typing import Optional, List
from .item_venda import ItemVenda


class Venda:
    def __init__(
        self,
        data_venda: str,
        valor_total_centavos: int = 0,
        cliente_id: Optional[int] = None,
        id: Optional[int] = None,
        cliente_nome: Optional[str] = None,
        itens: Optional[List[ItemVenda]] = None,
    ):
        self.id = id
        self.cliente_id = cliente_id
        self.cliente_nome = cliente_nome
        self.data_venda = data_venda
        self.valor_total_centavos = valor_total_centavos
        self.itens: List[ItemVenda] = itens if itens is not None else []

    def valor_total_em_reais(self) -> float:
        return self.valor_total_centavos / 100

    def adicionar_item(self, item: ItemVenda) -> None:
        self.itens.append(item)
        self.valor_total_centavos += item.subtotal_centavos

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "cliente_id": self.cliente_id,
            "cliente_nome": self.cliente_nome,
            "data_venda": self.data_venda,
            "valor_total_centavos": self.valor_total_centavos,
            "valor_total_reais": self.valor_total_em_reais(),
            "itens": [item.to_dict() for item in self.itens],
        }
