import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from models.movimentacao_estoque import MovimentacaoEstoque

DEFAULT_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "movimentacoes.json"


class EstoqueRepository:
    def __init__(self, caminho_arquivo: Optional[Path | str] = None, med_repo=None):
        self.caminho_arquivo = Path(caminho_arquivo) if caminho_arquivo else DEFAULT_DATA_FILE
        self.med_repo = med_repo
        self.caminho_arquivo.parent.mkdir(parents=True, exist_ok=True)
        if not self.caminho_arquivo.exists():
            self._salvar_lista([])

    def _carregar_lista(self) -> List[Dict[str, Any]]:
        if not self.caminho_arquivo.exists():
            return []
        try:
            with open(self.caminho_arquivo, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _salvar_lista(self, movimentacoes: List[Dict[str, Any]]) -> None:
        with open(self.caminho_arquivo, "w", encoding="utf-8") as f:
            json.dump(movimentacoes, f, ensure_ascii=False, indent=4)

    def registrar_movimentacao(self, mov: MovimentacaoEstoque) -> int:
        movs = self._carregar_lista()
        proximo_id = max([m.get("id", 0) for m in movs], default=0) + 1
        mov.id = proximo_id

        nome_med = mov.medicamento_nome
        if not nome_med and self.med_repo:
            m = self.med_repo.buscar_por_id(mov.medicamento_id)
            if m:
                nome_med = m.nome

        registro = {
            "id": mov.id,
            "medicamento_id": mov.medicamento_id,
            "medicamento_nome": nome_med or f"Medicamento #{mov.medicamento_id}",
            "tipo": mov.tipo,
            "quantidade": mov.quantidade,
            "data_movimentacao": mov.data_movimentacao,
            "descricao": mov.descricao,
        }
        movs.append(registro)
        self._salvar_lista(movs)
        return mov.id

    def listar_por_medicamento(self, medicamento_id: int) -> List[Dict[str, Any]]:
        movs = [m for m in self._carregar_lista() if m.get("medicamento_id") == medicamento_id]
        return sorted(movs, key=lambda x: x.get("data_movimentacao", ""), reverse=True)

    def listar_todas(self) -> List[Dict[str, Any]]:
        return sorted(self._carregar_lista(), key=lambda x: x.get("data_movimentacao", ""), reverse=True)
