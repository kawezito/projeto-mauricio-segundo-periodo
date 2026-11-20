import re
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from models.medicamento import Medicamento
from interfaces.repositories import IMedicamentoRepository
from exceptions import (
    ValidacaoError,
    CodigoDuplicadoError,
    MedicamentoNaoEncontradoError,
    IntegridadeReferencialError,
)


class MedicamentoService:
    def __init__(self, repo: IMedicamentoRepository):
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
        preco_bruto = dados.get("preco")
        data_validade = dados.get("data_validade")

        if not codigo:
            raise ValidacaoError("Código do medicamento é obrigatório.")
        if not nome:
            raise ValidacaoError("Nome do medicamento é obrigatório.")
        if not fabricante:
            raise ValidacaoError("Fabricante é obrigatório.")
        if not categoria:
            raise ValidacaoError("Categoria é obrigatória.")
        if not apresentacao:
            raise ValidacaoError("Apresentação é obrigatória.")

        existente = self.repo.buscar_por_codigo(codigo)
        if existente is not None:
            raise CodigoDuplicadoError(f"Já existe medicamento cadastrado com o código '{codigo}'.")

        preco_centavos = self._converter_preco_centavos(preco_bruto)
        validade_validada = self._validar_data(str(data_validade))

        try:
            estoque = int(dados.get("estoque", 0))
            estoque_minimo = int(dados.get("estoque_minimo", 0))
        except (ValueError, TypeError) as err:
            raise ValidacaoError("Estoque e estoque mínimo devem ser números inteiros.") from err

        if estoque < 0 or estoque_minimo < 0:
            raise ValidacaoError("Estoque e estoque mínimo não podem ser negativos.")

        medicamento = Medicamento(
            codigo=codigo,
            nome=nome,
            fabricante=fabricante,
            categoria=categoria,
            apresentacao=apresentacao,
            preco_centavos=preco_centavos,
            estoque=estoque,
            estoque_minimo=estoque_minimo,
            data_validade=validade_validada,
        )

        novo_id = self.repo.inserir(medicamento)
        medicamento.id = novo_id
        return medicamento

    def atualizar(self, medicamento_id: int, dados: Dict[str, Any]) -> Medicamento:
        med = self.repo.buscar_por_id(medicamento_id)
        if med is None:
            raise MedicamentoNaoEncontradoError(f"Medicamento de ID {medicamento_id} não encontrado.")

        novo_codigo = str(dados.get("codigo", med.codigo)).strip()
        novo_nome = str(dados.get("nome", med.nome)).strip()
        novo_fab = str(dados.get("fabricante", med.fabricante)).strip()
        nova_cat = str(dados.get("categoria", med.categoria)).strip()
        nova_apres = str(dados.get("apresentacao", med.apresentacao)).strip()

        if not novo_codigo or not novo_nome or not novo_fab or not nova_cat or not nova_apres:
            raise ValidacaoError("Campos de texto obrigatórios não podem ficar vazios.")

        if novo_codigo != med.codigo:
            outro = self.repo.buscar_por_codigo(novo_codigo)
            if outro is not None and outro.id != med.id:
                raise CodigoDuplicadoError(f"O código '{novo_codigo}' já pertence a outro medicamento.")

        validade_validada = (
            self._validar_data(str(dados["data_validade"]))
            if "data_validade" in dados
            else med.data_validade
        )

        if "preco" in dados:
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
