from typing import Optional, List, Dict, Any
from models.cliente import Cliente
from repositories.cliente_repository import ClienteRepository
from exceptions import (
    ValidacaoError,
    ClienteNaoEncontradoError,
    IntegridadeReferencialError,
)


class ClienteService:
    def __init__(self, repo: ClienteRepository):
        self.repo = repo

    def cadastrar(self, dados: Dict[str, Any]) -> Cliente:
        nome = str(dados.get("nome", "")).strip()
        telefone = dados.get("telefone")
        email = dados.get("email")

        if not nome:
            raise ValidacaoError("O nome do cliente é obrigatório.")

        tel_limpo = str(telefone).strip() if telefone is not None and str(telefone).strip() else None
        email_limpo = str(email).strip() if email is not None and str(email).strip() else None

        cliente = Cliente(nome=nome, telefone=tel_limpo, email=email_limpo)
        novo_id = self.repo.inserir(cliente)
        cliente.id = novo_id
        return cliente

    def atualizar(self, cliente_id: int, dados: Dict[str, Any]) -> Cliente:
        cliente = self.repo.buscar_por_id(cliente_id)
        if cliente is None:
            raise ClienteNaoEncontradoError(f"Cliente de ID {cliente_id} não encontrado.")

        novo_nome = str(dados.get("nome", cliente.nome)).strip()
        if not novo_nome:
            raise ValidacaoError("O nome do cliente não pode ser vazio.")

        novo_tel = dados.get("telefone", cliente.telefone)
        novo_email = dados.get("email", cliente.email)

        cliente.nome = novo_nome
        cliente.telefone = str(novo_tel).strip() if novo_tel is not None and str(novo_tel).strip() else None
        cliente.email = str(novo_email).strip() if novo_email is not None and str(novo_email).strip() else None

        self.repo.atualizar(cliente)
        return cliente

    def excluir(self, cliente_id: int) -> bool:
        cliente = self.repo.buscar_por_id(cliente_id)
        if cliente is None:
            raise ClienteNaoEncontradoError(f"Cliente de ID {cliente_id} não encontrado.")

        if self.repo.tem_vendas_associadas(cliente_id):
            raise IntegridadeReferencialError(
                f"Não é permitido excluir o cliente '{cliente.nome}' pois existem vendas associadas a ele no arquivo de vendas."
            )

        return self.repo.excluir(cliente_id)

    def buscar_por_id(self, cliente_id: int) -> Cliente:
        cliente = self.repo.buscar_por_id(cliente_id)
        if cliente is None:
            raise ClienteNaoEncontradoError(f"Cliente de ID {cliente_id} não encontrado.")
        return cliente

    def pesquisar_por_nome(self, termo: str) -> List[Cliente]:
        if not termo or not termo.strip():
            return self.listar_todos()
        return self.repo.buscar_por_nome(termo.strip())

    def listar_todos(self) -> List[Cliente]:
        return self.repo.listar_todos()
