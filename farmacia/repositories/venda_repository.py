import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from models.venda import Venda
from models.item_venda import ItemVenda

DEFAULT_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "vendas.json"


class VendaRepository:
    """
    Repositório de persistência de Venda e ItemVenda baseado 100% em manipulação de arquivos JSON.
    Não utiliza banco de dados. Lê e escreve diretamente no arquivo 'vendas.json'.
    """

    def __init__(self, caminho_arquivo: Optional[Path | str] = None, cliente_repo=None):
        self.caminho_arquivo = Path(caminho_arquivo) if caminho_arquivo else DEFAULT_DATA_FILE
        self.cliente_repo = cliente_repo
        self.caminho_arquivo.parent.mkdir(parents=True, exist_ok=True)
        if not self.caminho_arquivo.exists():
            self._salvar_lista([])

    def _carregar_lista(self) -> List[Venda]:
        """Abre e lê o arquivo JSON, convertendo cada registro em objeto Venda com seus itens."""
        if not self.caminho_arquivo.exists():
            return []
        try:
            with open(self.caminho_arquivo, "r", encoding="utf-8") as f:
                dados = json.load(f)
                vendas = []
                for d in dados:
                    itens = [
                        ItemVenda(
                            id=it.get("id"),
                            venda_id=it.get("venda_id", d.get("id")),
                            medicamento_id=it.get("medicamento_id"),
                            quantidade=it.get("quantidade", 0),
                            preco_unitario_centavos=it.get("preco_unitario_centavos", 0),
                            subtotal_centavos=it.get("subtotal_centavos", 0),
                            medicamento_nome=it.get("medicamento_nome"),
                        )
                        for it in d.get("itens", [])
                    ]
                    v = Venda(
                        id=d.get("id"),
                        cliente_id=d.get("cliente_id"),
                        cliente_nome=d.get("cliente_nome"),
                        data_venda=d.get("data_venda", ""),
                        valor_total_centavos=d.get("valor_total_centavos", 0),
                        itens=itens,
                    )
                    vendas.append(v)
                return vendas
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _salvar_lista(self, vendas: List[Venda]) -> None:
        """Grava a lista completa de vendas e itens no arquivo JSON."""
        dados = [v.to_dict() for v in vendas]
        with open(self.caminho_arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)

    def inserir_venda_completa(self, venda: Venda) -> int:
        """Salva a venda com todos os seus itens no arquivo JSON."""
        vendas = self._carregar_lista()
        proximo_id = max([v.id for v in vendas if v.id is not None], default=0) + 1
        venda.id = proximo_id

        # Atribui id aos itens
        for idx, item in enumerate(venda.itens, 1):
            item.id = idx
            item.venda_id = venda.id

        # Preenche cliente_nome se não estiver setado
        if venda.cliente_id and not venda.cliente_nome and self.cliente_repo:
            cli = self.cliente_repo.buscar_por_id(venda.cliente_id)
            if cli:
                venda.cliente_nome = cli.nome

        vendas.append(venda)
        self._salvar_lista(vendas)
        return venda.id

    def inserir_venda(self, venda: Venda) -> int:
        return self.inserir_venda_completa(venda)

    def inserir_item(self, item: ItemVenda) -> int:
        # Mantido para compatibilidade, o salvamento é feito pela venda completa
        return item.id or 1

    def buscar_por_id(self, venda_id: int) -> Optional[Venda]:
        """Busca venda por ID com todos os seus itens."""
        for v in self._carregar_lista():
            if v.id == venda_id:
                return v
        return None

    def listar_todas(self) -> List[Venda]:
        """Retorna todas as vendas ordenadas da mais recente para a mais antiga."""
        return sorted(self._carregar_lista(), key=lambda x: x.data_venda, reverse=True)

    def buscar_por_periodo(self, data_inicio: str, data_fim: str) -> List[Venda]:
        """Filtra vendas realizadas dentro de um intervalo de datas."""
        vendas = [
            v for v in self._carregar_lista()
            if data_inicio <= v.data_venda <= data_fim
        ]
        return sorted(vendas, key=lambda x: x.data_venda)

    def medicamentos_mais_vendidos(self, limite: int = 10) -> List[Dict[str, Any]]:
        """Calcula o ranking de medicamentos mais vendidos agregando os itens das vendas."""
        totais: Dict[int, Dict[str, Any]] = {}
        for v in self._carregar_lista():
            for it in v.itens:
                med_id = it.medicamento_id
                if med_id not in totais:
                    totais[med_id] = {
                        "medicamento_id": med_id,
                        "nome": it.medicamento_nome or f"Medicamento #{med_id}",
                        "total_unidades_vendidas": 0,
                        "receita_total_centavos": 0,
                    }
                totais[med_id]["total_unidades_vendidas"] += it.quantidade
                totais[med_id]["receita_total_centavos"] += it.subtotal_centavos

        ranking = sorted(totais.values(), key=lambda x: x["total_unidades_vendidas"], reverse=True)
        return ranking[:limite]

    def total_vendas_por_periodo(self, data_inicio: str, data_fim: str) -> Dict[str, Any]:
        """Calcula a contagem de vendas e total faturado no intervalo."""
        filtradas = self.buscar_por_periodo(data_inicio, data_fim)
        total_centavos = sum(v.valor_total_centavos for v in filtradas)
        return {
            "total_vendas": len(filtradas),
            "valor_total_centavos": total_centavos,
        }

    def medicamento_tem_vendas(self, medicamento_id: int) -> bool:
        """Verifica se um medicamento específico já foi vendido."""
        for v in self._carregar_lista():
            for it in v.itens:
                if it.medicamento_id == medicamento_id:
                    return True
        return False

    def cliente_tem_vendas(self, cliente_id: int) -> bool:
        """Verifica se um cliente específico já realizou compras."""
        for v in self._carregar_lista():
            if v.cliente_id == cliente_id:
                return True
        return False
