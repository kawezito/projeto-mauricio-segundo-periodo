from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from models.medicamento import Medicamento
from models.cliente import Cliente
from models.venda import Venda
from models.item_venda import ItemVenda
from models.movimentacao_estoque import MovimentacaoEstoque


class IMedicamentoRepository(ABC):
    @abstractmethod
    def inserir(self, med: Medicamento) -> int:
        pass

    @abstractmethod
    def atualizar(self, med: Medicamento) -> bool:
        pass

    @abstractmethod
    def atualizar_estoque(self, medicamento_id: int, novo_estoque: int) -> bool:
        pass

    @abstractmethod
    def excluir(self, medicamento_id: int) -> bool:
        pass

    @abstractmethod
    def buscar_por_id(self, medicamento_id: int) -> Optional[Medicamento]:
        pass

    @abstractmethod
    def buscar_por_codigo(self, codigo: str) -> Optional[Medicamento]:
        pass

    @abstractmethod
    def buscar_por_nome(self, nome_parcial: str) -> List[Medicamento]:
        pass

    @abstractmethod
    def listar_todos(self) -> List[Medicamento]:
        pass

    @abstractmethod
    def listar_por_categoria(self, categoria: str) -> List[Medicamento]:
        pass

    @abstractmethod
    def buscar_estoque_baixo(self) -> List[Medicamento]:
        pass

    @abstractmethod
    def buscar_sem_estoque(self) -> List[Medicamento]:
        pass

    @abstractmethod
    def buscar_proximos_vencimento(self, data_limite: str) -> List[Medicamento]:
        pass

    @abstractmethod
    def tem_vendas_associadas(self, medicamento_id: int) -> bool:
        pass


class IClienteRepository(ABC):
    @abstractmethod
    def inserir(self, cliente: Cliente) -> int:
        pass

    @abstractmethod
    def atualizar(self, cliente: Cliente) -> bool:
        pass

    @abstractmethod
    def excluir(self, cliente_id: int) -> bool:
        pass

    @abstractmethod
    def buscar_por_id(self, cliente_id: int) -> Optional[Cliente]:
        pass

    @abstractmethod
    def buscar_por_nome(self, termo: str) -> List[Cliente]:
        pass

    @abstractmethod
    def listar_todos(self) -> List[Cliente]:
        pass

    @abstractmethod
    def tem_vendas_associadas(self, cliente_id: int) -> bool:
        pass


class IVendaRepository(ABC):
    @abstractmethod
    def inserir_venda(self, venda: Venda) -> int:
        pass

    @abstractmethod
    def inserir_item(self, item: ItemVenda) -> int:
        pass

    @abstractmethod
    def listar_itens_da_venda(self, venda_id: int) -> List[ItemVenda]:
        pass

    @abstractmethod
    def buscar_por_id(self, venda_id: int) -> Optional[Venda]:
        pass

    @abstractmethod
    def listar_todas(self) -> List[Venda]:
        pass

    @abstractmethod
    def buscar_por_periodo(self, data_inicio: str, data_fim: str) -> List[Venda]:
        pass

    @abstractmethod
    def medicamentos_mais_vendidos(self, limite: int = 10) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def total_vendas_por_periodo(self, data_inicio: str, data_fim: str) -> Dict[str, Any]:
        pass


class IEstoqueRepository(ABC):
    @abstractmethod
    def registrar_movimentacao(self, mov: MovimentacaoEstoque) -> int:
        pass

    @abstractmethod
    def listar_por_medicamento(self, medicamento_id: int) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def listar_todas(self) -> List[Dict[str, Any]]:
        pass

