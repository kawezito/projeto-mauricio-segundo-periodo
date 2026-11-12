from typing import Optional


class Medicamento:
    def __init__(
        self,
        codigo: str,
        nome: str,
        fabricante: str,
        categoria: str,
        apresentacao: str,
        preco_centavos: int,
        data_validade: str,
        estoque: int = 0,
        estoque_minimo: int = 0,
        id: Optional[int] = None,
    ):
        self.id = id
        self.codigo = codigo
        self.nome = nome
        self.fabricante = fabricante
        self.categoria = categoria
        self.apresentacao = apresentacao
        self.preco_centavos = preco_centavos
        self.data_validade = data_validade
        self.estoque = estoque
        self.estoque_minimo = estoque_minimo

    def preco_em_reais(self) -> float:
        return self.preco_centavos / 100

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "codigo": self.codigo,
            "nome": self.nome,
            "fabricante": self.fabricante,
            "categoria": self.categoria,
            "apresentacao": self.apresentacao,
            "preco_centavos": self.preco_centavos,
            "preco_reais": self.preco_em_reais(),
            "estoque": self.estoque,
            "estoque_minimo": self.estoque_minimo,
            "data_validade": self.data_validade,
        }
