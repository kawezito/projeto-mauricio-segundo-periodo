from typing import Optional

class Cliente:
    def __init__(
        self,
        nome: str,
        telefone: Optional[str] = None,
        email: Optional[str] = None,
        id: Optional[int] = None,
    ):
        self.id = id
        self.nome = nome
        self.telefone = telefone
        self.email = email

    def to_dict(self) -> dict:
        """Retorna os dados do cliente em formato de dicionário."""
        return {
            "id": self.id,
            "nome": self.nome,
            "telefone": self.telefone,
            "email": self.email,
        }