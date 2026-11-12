from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from models.venda import Venda
from models.item_venda import ItemVenda
from models.movimentacao_estoque import MovimentacaoEstoque
from repositories.venda_repository import VendaRepository
from repositories.medicamento_repository import MedicamentoRepository
from repositories.estoque_repository import EstoqueRepository
from repositories.cliente_repository import ClienteRepository
from exceptions import (
    ValidacaoError,
    MedicamentoNaoEncontradoError,
    ClienteNaoEncontradoError,
    EstoqueInsuficienteError,
    VendaNaoEncontradaError,
)


class VendaService:
    """
    Serviço que implementa as regras de negócio de vendas (RF07, RF08) via manipulação de arquivos.
    Garante a consistência atômica: valida todo o carrinho antes de efetivar qualquer baixa de estoque.
    """

    def __init__(
        self,
        venda_repo: VendaRepository,
        med_repo: MedicamentoRepository,
        est_repo: EstoqueRepository,
        cli_repo: ClienteRepository,
    ):
        self.venda_repo = venda_repo
        self.med_repo = med_repo
        self.est_repo = est_repo
        self.cli_repo = cli_repo

    def _obter_data_hora_atual(self) -> str:
        """Retorna o timestamp atual em formato ISO 8601 (AAAA-MM-DDTHH:MM:SS)."""
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    def registrar_venda(
        self,
        itens: List[Dict[str, Any]],
        cliente_id: Optional[int] = None,
        data_venda: Optional[str] = None,
    ) -> Venda:
        """
        RF07: Registra uma venda contendo um ou mais medicamentos.
        
        Utiliza laço WHILE no processamento sequencial dos itens do carrinho (Requisito 7.2).
        Valida a disponibilidade total antes de alterar os arquivos em disco.
        """
        if not itens:
            raise ValidacaoError("A venda deve conter pelo menos um medicamento no carrinho.")

        # 1. Validação opcional de cliente
        cliente_nome = None
        if cliente_id is not None:
            cliente = self.cli_repo.buscar_por_id(cliente_id)
            if cliente is None:
                raise ClienteNaoEncontradoError(f"Cliente de ID {cliente_id} não encontrado.")
            cliente_nome = cliente.nome

        # 2. Processamento sequencial do carrinho com laço WHILE (Requisito Acadêmico 7.2)
        itens_preparados: List[ItemVenda] = []
        demandas_acumuladas: Dict[int, int] = {}
        medicamentos_cache: Dict[int, Any] = {}

        indice = 0
        total_itens_carrinho = len(itens)

        while indice < total_itens_carrinho:
            item_dados = itens[indice]

            if not isinstance(item_dados, dict):
                raise ValidacaoError(f"O item na posição {indice + 1} deve ser um dicionário.")

            if "medicamento_id" not in item_dados:
                raise ValidacaoError(f"O item {indice + 1} não possui 'medicamento_id'.")

            try:
                med_id = int(item_dados["medicamento_id"])
                quantidade = int(item_dados.get("quantidade", 0))
            except (ValueError, TypeError) as err:
                raise ValidacaoError(f"ID ou quantidade com formato inválido no item {indice + 1}: {err}") from err

            if quantidade <= 0:
                raise ValidacaoError(f"A quantidade no item {indice + 1} deve ser estritamente maior que zero.")

            # Carrega medicamento e guarda em cache
            if med_id not in medicamentos_cache:
                med = self.med_repo.buscar_por_id(med_id)
                if med is None:
                    raise MedicamentoNaoEncontradoError(f"Medicamento de ID {med_id} não encontrado.")
                medicamentos_cache[med_id] = med

            med = medicamentos_cache[med_id]

            # Define preço unitário (preserva o preço no momento da venda)
            if "preco_unitario_centavos" in item_dados:
                preco_unit = int(item_dados["preco_unitario_centavos"])
                if preco_unit < 0:
                    raise ValidacaoError("Preço unitário não pode ser negativo.")
            elif "preco_unitario" in item_dados:
                preco_unit = int(round(Decimal(str(item_dados["preco_unitario"])) * 100))
                if preco_unit < 0:
                    raise ValidacaoError("Preço unitário não pode ser negativo.")
            else:
                preco_unit = med.preco_centavos

            # Acumula demanda total para evitar venda que supere o estoque
            demandas_acumuladas[med_id] = demandas_acumuladas.get(med_id, 0) + quantidade
            if demandas_acumuladas[med_id] > med.estoque:
                raise EstoqueInsuficienteError(
                    f"Estoque insuficiente para o medicamento '{med.nome}' (ID {med.id}). "
                    f"Disponível: {med.estoque}, Solicitado: {demandas_acumuladas[med_id]}."
                )

            subtotal_centavos = quantidade * preco_unit
            itens_preparados.append(
                ItemVenda(
                    venda_id=0,
                    medicamento_id=med_id,
                    quantidade=quantidade,
                    preco_unitario_centavos=preco_unit,
                    subtotal_centavos=subtotal_centavos,
                    medicamento_nome=med.nome,
                )
            )

            indice += 1

        # 3. Calcula total geral da venda
        valor_total_centavos = sum(item.subtotal_centavos for item in itens_preparados)
        timestamp = data_venda or self._obter_data_hora_atual()

        venda = Venda(
            cliente_id=cliente_id,
            cliente_nome=cliente_nome,
            data_venda=timestamp,
            valor_total_centavos=valor_total_centavos,
            itens=itens_preparados,
        )

        # 4. Gravação atômica nos arquivos (tudo previamente validado)
        venda_id = self.venda_repo.inserir_venda_completa(venda)
        venda.id = venda_id

        # Atualiza estoque e registra saídas nos arquivos físicos
        for item in itens_preparados:
            med = medicamentos_cache[item.medicamento_id]
            novo_estoque = med.estoque - item.quantidade
            self.med_repo.atualizar_estoque(item.medicamento_id, novo_estoque)

            mov_saida = MovimentacaoEstoque(
                medicamento_id=item.medicamento_id,
                medicamento_nome=med.nome,
                tipo="SAIDA",
                quantidade=item.quantidade,
                data_movimentacao=timestamp,
                descricao=f"Saída por Venda #{venda_id}",
            )
            self.est_repo.registrar_movimentacao(mov_saida)

        return venda

    def buscar_por_id(self, venda_id: int) -> Venda:
        """RF08: Consulta venda por ID com todos os itens."""
        venda = self.venda_repo.buscar_por_id(venda_id)
        if venda is None:
            raise VendaNaoEncontradaError(f"Venda de ID {venda_id} não encontrada.")
        return venda

    def listar_todas(self) -> List[Venda]:
        """RF08: Lista todas as vendas registradas no arquivo."""
        return self.venda_repo.listar_todas()

    def buscar_por_periodo(self, data_inicio: str, data_fim: str) -> List[Venda]:
        """RF08: Consulta vendas em um intervalo de datas."""
        if not data_inicio or not data_fim:
            raise ValidacaoError("Datas de início e fim são obrigatórias.")
        return self.venda_repo.buscar_por_periodo(data_inicio, data_fim)

    def consultar_resumo_periodo(self, data_inicio: str, data_fim: str) -> Dict[str, Any]:
        """RF08: Retorna total financeiro e quantidade de vendas em um período."""
        resumo = self.venda_repo.total_vendas_por_periodo(data_inicio, data_fim)
        centavos = resumo.get("valor_total_centavos", 0)
        reais = (Decimal(centavos) / Decimal(100)).quantize(Decimal("0.01"))
        return {
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "total_vendas": resumo.get("total_vendas", 0),
            "valor_total_centavos": centavos,
            "valor_total_reais": float(reais),
        }
