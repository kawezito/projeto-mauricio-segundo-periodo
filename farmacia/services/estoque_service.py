from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from models.medicamento import Medicamento
from models.movimentacao_estoque import MovimentacaoEstoque
from repositories.medicamento_repository import MedicamentoRepository
from repositories.estoque_repository import EstoqueRepository
from exceptions import (
    ValidacaoError,
    MedicamentoNaoEncontradoError,
)


class EstoqueService:
    def __init__(
        self,
        med_repo: MedicamentoRepository,
        est_repo: EstoqueRepository,
    ):
        self.med_repo = med_repo
        self.est_repo = est_repo

    def _obter_data_hora_atual(self) -> str:
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    def registrar_entrada(
        self,
        medicamento_id: int,
        quantidade: int,
        descricao: Optional[str] = "Entrada manual de reposição",
        data_movimentacao: Optional[str] = None,
    ) -> Dict[str, Any]:
        if quantidade <= 0:
            raise ValidacaoError("A quantidade de entrada deve ser estritamente maior que zero.")

        med = self.med_repo.buscar_por_id(medicamento_id)
        if med is None:
            raise MedicamentoNaoEncontradoError(f"Medicamento de ID {medicamento_id} não encontrado.")

        timestamp = data_movimentacao or self._obter_data_hora_atual()
        novo_estoque = med.estoque + quantidade

        self.med_repo.atualizar_estoque(medicamento_id, novo_estoque)

        mov = MovimentacaoEstoque(
            medicamento_id=medicamento_id,
            medicamento_nome=med.nome,
            tipo="ENTRADA",
            quantidade=quantidade,
            data_movimentacao=timestamp,
            descricao=descricao,
        )
        mov_id = self.est_repo.registrar_movimentacao(mov)

        return {
            "movimentacao_id": mov_id,
            "medicamento_id": medicamento_id,
            "medicamento_nome": med.nome,
            "tipo": "ENTRADA",
            "quantidade": quantidade,
            "estoque_anterior": med.estoque,
            "novo_estoque": novo_estoque,
            "data_movimentacao": timestamp,
            "descricao": descricao,
        }

    def consultar_estoque_atual(self, medicamento_id: int) -> Dict[str, Any]:
        med = self.med_repo.buscar_por_id(medicamento_id)
        if med is None:
            raise MedicamentoNaoEncontradoError(f"Medicamento de ID {medicamento_id} não encontrado.")

        return {
            "medicamento_id": med.id,
            "codigo": med.codigo,
            "nome": med.nome,
            "estoque": med.estoque,
            "estoque_minimo": med.estoque_minimo,
            "estoque_baixo": med.estoque <= med.estoque_minimo,
            "sem_estoque": med.estoque == 0,
            "data_validade": med.data_validade,
        }

    def consultar_estoque_baixo(self) -> List[Medicamento]:
        return self.med_repo.buscar_estoque_baixo()

    def consultar_sem_estoque(self) -> List[Medicamento]:
        return self.med_repo.buscar_sem_estoque()

    def consultar_proximos_vencimento(self, dias: int = 30) -> List[Medicamento]:
        if dias < 0:
            raise ValidacaoError("A quantidade de dias não pode ser negativa.")

        data_limite = (datetime.now() + timedelta(days=dias)).strftime("%Y-%m-%d")
        return self.med_repo.buscar_proximos_vencimento(data_limite)

    def listar_historico_movimentacoes(self, medicamento_id: Optional[int] = None) -> List[Dict[str, Any]]:
        if medicamento_id is not None:
            med = self.med_repo.buscar_por_id(medicamento_id)
            if med is None:
                raise MedicamentoNaoEncontradoError(f"Medicamento de ID {medicamento_id} não encontrado.")
            return self.est_repo.listar_por_medicamento(medicamento_id)
        return self.est_repo.listar_todas()
