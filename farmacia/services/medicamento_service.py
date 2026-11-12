import re
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from models.medicamento import Medicamento
from repositories.medicamento_repository import MedicamentoRepository
from exceptions import (
    ValidacaoError,
    CodigoDuplicadoError,
    MedicamentoNaoEncontradoError,
    IntegridadeReferencialError,
)


class MedicamentoService:
    def __init__(self, repo: MedicamentoRepository):
        self.repo = repo

    def _validar_data(self, data_str: str) -> str:
        data_limpa = str(data_str).strip()
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", data_limpa):
            raise ValidacaoError("Data de validade deve estar no formato AAAA-MM-DD.")
        try:
            datetime.strptime(data_limpa, "%Y-%m-%d")
        except ValueError as err:
            raise ValidacaoError(f"Data de validade inválida no calendário: {err}") from err
        return data_limpa

    def _converter_preco_centavos(self, valor: Any) -> int:
        if valor is None:
            raise ValidacaoError("Preço de venda é obrigatório.")
        try:
            dec = Decimal(str(valor))
        except Exception as err:
            raise ValidacaoError(f"Preço com formato numérico inválido: {valor}") from err

        if dec < Decimal("0"):
            raise ValidacaoError("O preço de venda não pode ser negativo.")

        return int(round(dec * 100))

    def cadastrar(self, dados: Dict[str, Any]) -> Medicamento:
        codigo = str(dados.get("codigo", "")).strip()
        nome = str(dados.get("nome", "")).strip()
        fabricante = str(dados.get("fabricante", "")).strip()
        categoria = str(dados.get("categoria", "")).strip()
        apresentacao = str(dados.get("apresentacao", "")).strip()
        data_validade = str(dados.get("data_validade", "")).strip()

        if not codigo:
            raise ValidacaoError("O campo 'codigo' é obrigatório.")
        if not nome:
            raise ValidacaoError("O campo 'nome' é obrigatório.")
        if not fabricante:
            raise ValidacaoError("O campo 'fabricante' é obrigatório.")
        if not categoria:
            raise ValidacaoError("O campo 'categoria' é obrigatório.")
        if not apresentacao:
            raise ValidacaoError("O campo 'apresentacao' é obrigatório.")
        if not data_validade:
            raise ValidacaoError("O campo 'data_validade' é obrigatório.")

        data_validada = self._validar_data(data_validade)

        if "preco_centavos" in dados:
            preco_centavos = int(dados["preco_centavos"])
            if preco_centavos < 0:
                raise ValidacaoError("O preço de venda não pode ser negativo.")
        elif "preco" in dados:
            preco_centavos = self._converter_preco_centavos(dados["preco"])
        else:
            raise ValidacaoError("O preço de venda é obrigatório.")

        estoque = int(dados.get("estoque", 0))
        estoque_minimo = int(dados.get("estoque_minimo", 0))

        if estoque < 0:
            raise ValidacaoError("A quantidade em estoque não pode ser negativa.")
        if estoque_minimo < 0:
            raise ValidacaoError("A quantidade mínima de estoque não pode ser negativa.")

        existente = self.repo.buscar_por_codigo(codigo)
        if existente is not None:
            raise CodigoDuplicadoError(f"Já existe um medicamento cadastrado com o código '{codigo}'.")

        med = Medicamento(
            codigo=codigo,
            nome=nome,
            fabricante=fabricante,
            categoria=categoria,
            apresentacao=apresentacao,
            preco_centavos=preco_centavos,
            data_validade=data_validada,
            estoque=estoque,
            estoque_minimo=estoque_minimo,
        )

        novo_id = self.repo.inserir(med)
        med.id = novo_id
        return med

    def atualizar(self, medicamento_id: int, dados: Dict[str, Any]) -> Medicamento:
        med = self.repo.buscar_por_id(medicamento_id)
        if med is None:
            raise MedicamentoNaoEncontradoError(f"Medicamento de ID {medicamento_id} não encontrado.")

        novo_codigo = str(dados.get("codigo", med.codigo)).strip()
        if not novo_codigo:
            raise ValidacaoError("O código não pode ser vazio.")

        if novo_codigo != med.codigo:
            outro = self.repo.buscar_por_codigo(novo_codigo)
            if outro is not None and outro.id != medicamento_id:
                raise CodigoDuplicadoError(f"O código '{novo_codigo}' já está em uso por outro medicamento.")

        novo_nome = str(dados.get("nome", med.nome)).strip()
        novo_fab = str(dados.get("fabricante", med.fabricante)).strip()
        nova_cat = str(dados.get("categoria", med.categoria)).strip()
        nova_apres = str(dados.get("apresentacao", med.apresentacao)).strip()

        if not novo_nome or not novo_fab or not nova_cat or not nova_apres:
            raise ValidacaoError("Nome, fabricante, categoria e apresentação não podem ser vazios.")

        nova_validade = str(dados.get("data_validade", med.data_validade)).strip()
        validade_validada = self._validar_data(nova_validade)

        if "preco_centavos" in dados:
            preco_centavos = int(dados["preco_centavos"])
            if preco_centavos < 0:
                raise ValidacaoError("Preço em centavos não pode ser negativo.")
        elif "preco" in dados:
            preco_centavos = self._converter_preco_centavos(dados["preco"])
        else:
            preco_centavos = med.preco_centavos

        novo_estoque = int(dados.get("estoque", med.estoque))
        novo_minimo = int(dados.get("estoque_minimo", med.estoque_minimo))

        if novo_estoque < 0 or novo_minimo < 0:
            raise ValidacaoError("Estoque e estoque mínimo não podem ser negativos.")

        med.codigo = novo_codigo
        med.nome = novo_nome
        med.fabricante = novo_fab
        med.categoria = nova_cat
        med.apresentacao = nova_apres
        med.preco_centavos = preco_centavos
        med.data_validade = validade_validada
        med.estoque = novo_estoque
        med.estoque_minimo = novo_minimo

        self.repo.atualizar(med)
        return med

    def excluir(self, medicamento_id: int) -> bool:
        med = self.repo.buscar_por_id(medicamento_id)
        if med is None:
            raise MedicamentoNaoEncontradoError(f"Medicamento de ID {medicamento_id} não encontrado.")

        if self.repo.tem_vendas_associadas(medicamento_id):
            raise IntegridadeReferencialError(
                f"Não é permitido excluir o medicamento '{med.nome}' (Código {med.codigo}) "
                "pois existem vendas registradas para ele no histórico."
            )

        return self.repo.excluir(medicamento_id)

    def buscar_por_id(self, medicamento_id: int) -> Medicamento:
        med = self.repo.buscar_por_id(medicamento_id)
        if med is None:
            raise MedicamentoNaoEncontradoError(f"Medicamento de ID {medicamento_id} não encontrado.")
        return med

    def buscar_por_codigo(self, codigo: str) -> Medicamento:
        med = self.repo.buscar_por_codigo(codigo)
        if med is None:
            raise MedicamentoNaoEncontradoError(f"Medicamento de código '{codigo}' não encontrado.")
        return med

    def pesquisar_por_nome(self, termo: str) -> List[Medicamento]:
        if not termo or not termo.strip():
            return self.listar_todos()
        return self.repo.buscar_por_nome(termo.strip())

    def listar_todos(self) -> List[Medicamento]:
        return self.repo.listar_todos()

    def listar_por_categoria(self, categoria: str) -> List[Medicamento]:
        if not categoria or not categoria.strip():
            raise ValidacaoError("A categoria deve ser informada.")
        return self.repo.listar_por_categoria(categoria.strip())
