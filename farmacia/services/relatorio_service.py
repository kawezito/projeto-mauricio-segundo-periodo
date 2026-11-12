import csv
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Optional, List, Dict, Any
from repositories.medicamento_repository import MedicamentoRepository
from repositories.estoque_repository import EstoqueRepository
from repositories.venda_repository import VendaRepository

DEFAULT_REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"


class RelatorioService:
    def __init__(
        self,
        med_repo: MedicamentoRepository,
        est_repo: EstoqueRepository,
        venda_repo: VendaRepository,
        reports_dir: Optional[Path | str] = None,
    ):
        self.med_repo = med_repo
        self.est_repo = est_repo
        self.venda_repo = venda_repo
        self.reports_dir = Path(reports_dir) if reports_dir else DEFAULT_REPORTS_DIR
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def relatorio_medicamentos_cadastrados(self) -> List[Dict[str, Any]]:
        return [m.to_dict() for m in self.med_repo.listar_todos()]

    def relatorio_estoque_atual(self) -> List[Dict[str, Any]]:
        medicamentos = self.med_repo.listar_todos()
        resultado = []
        for m in medicamentos:
            status = "NORMAL"
            if m.estoque == 0:
                status = "SEM ESTOQUE"
            elif m.estoque <= m.estoque_minimo:
                status = "ESTOQUE BAIXO"

            dados = m.to_dict()
            dados["status"] = status
            resultado.append(dados)
        return resultado

    def relatorio_estoque_baixo(self) -> List[Dict[str, Any]]:
        return [m.to_dict() for m in self.med_repo.buscar_estoque_baixo()]

    def relatorio_proximos_vencimento(self, dias: int = 30) -> List[Dict[str, Any]]:
        data_limite = (datetime.now() + timedelta(days=dias)).strftime("%Y-%m-%d")
        return [m.to_dict() for m in self.med_repo.buscar_proximos_vencimento(data_limite)]

    def relatorio_historico_vendas(self) -> List[Dict[str, Any]]:
        return [v.to_dict() for v in self.venda_repo.listar_todas()]

    def relatorio_total_vendas_por_periodo(self, data_inicio: str, data_fim: str) -> Dict[str, Any]:
        dados = self.venda_repo.total_vendas_por_periodo(data_inicio, data_fim)
        centavos = dados.get("valor_total_centavos", 0)
        reais = (Decimal(centavos) / Decimal(100)).quantize(Decimal("0.01"))
        return {
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "total_vendas": dados.get("total_vendas", 0),
            "valor_total_centavos": centavos,
            "valor_total_reais": float(reais),
        }

    def relatorio_medicamentos_mais_vendidos(self, limite: int = 10) -> List[Dict[str, Any]]:
        ranking = self.venda_repo.medicamentos_mais_vendidos(limite)
        resultado = []
        for item in ranking:
            receita = (Decimal(item["receita_total_centavos"]) / Decimal(100)).quantize(Decimal("0.01"))
            d = dict(item)
            d["receita_total_reais"] = float(receita)
            resultado.append(d)
        return resultado

    def gerar_matriz_estoque(self) -> List[List[Any]]:
        cabecalho = [
            "ID",
            "Código",
            "Nome",
            "Fabricante",
            "Categoria",
            "Apresentação",
            "Preço (R$)",
            "Estoque Atual",
            "Estoque Mínimo",
            "Status",
            "Validade",
        ]
        matriz: List[List[Any]] = [cabecalho]

        for med in self.med_repo.listar_todos():
            status = "NORMAL"
            if med.estoque == 0:
                status = "SEM ESTOQUE"
            elif med.estoque <= med.estoque_minimo:
                status = "ESTOQUE BAIXO"

            linha = [
                med.id,
                med.codigo,
                med.nome,
                med.fabricante,
                med.categoria,
                med.apresentacao,
                f"{med.preco_em_reais():.2f}".replace(".", ","),
                med.estoque,
                med.estoque_minimo,
                status,
                med.data_validade,
            ]
            matriz.append(linha)

        return matriz

    def gerar_matriz_vendas(self) -> List[List[Any]]:
        cabecalho = ["ID Venda", "Data/Hora", "Cliente", "Total Itens", "Valor Total (R$)"]
        matriz: List[List[Any]] = [cabecalho]

        for v in self.venda_repo.listar_todas():
            total_itens = sum(item.quantidade for item in v.itens)
            linha = [
                v.id,
                v.data_venda,
                v.cliente_nome or "Cliente não identificado",
                total_itens,
                f"{v.valor_total_em_reais():.2f}".replace(".", ","),
            ]
            matriz.append(linha)

        return matriz

    def exportar_matriz_para_csv(self, matriz: List[List[Any]], caminho_arquivo: Path | str) -> str:
        caminho = Path(caminho_arquivo)
        caminho.parent.mkdir(parents=True, exist_ok=True)

        with open(caminho, mode="w", newline="", encoding="utf-8") as f:
            escritor = csv.writer(f, delimiter=";", quoting=csv.QUOTE_MINIMAL)
            for linha in matriz:
                escritor.writerow(linha)

        return str(caminho.resolve())

    def exportar_estoque_csv(self, nome_arquivo: Optional[str] = None) -> str:
        nome = nome_arquivo or f"relatorio_estoque_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        caminho = self.reports_dir / nome
        matriz = self.gerar_matriz_estoque()
        return self.exportar_matriz_para_csv(matriz, caminho)

    def exportar_vendas_csv(self, nome_arquivo: Optional[str] = None) -> str:
        nome = nome_arquivo or f"relatorio_vendas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        caminho = self.reports_dir / nome
        matriz = self.gerar_matriz_vendas()
        return self.exportar_matriz_para_csv(matriz, caminho)
