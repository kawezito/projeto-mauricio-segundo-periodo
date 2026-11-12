import json
from pathlib import Path
from typing import Optional, List
from models.medicamento import Medicamento

DEFAULT_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "medicamentos.json"


class MedicamentoRepository:
    """
    Repositório de persistência de Medicamento baseado 100% em manipulação de arquivos JSON.
    Não utiliza banco de dados. Lê e escreve diretamente no arquivo 'medicamentos.json'.
    """

    def __init__(self, caminho_arquivo: Optional[Path | str] = None, venda_repo=None):
        self.caminho_arquivo = Path(caminho_arquivo) if caminho_arquivo else DEFAULT_DATA_FILE
        self.venda_repo = venda_repo
        self.caminho_arquivo.parent.mkdir(parents=True, exist_ok=True)
        if not self.caminho_arquivo.exists():
            self._salvar_lista([])

    def _carregar_lista(self) -> List[Medicamento]:
        """Abre e lê o arquivo JSON, convertendo cada registro em objeto Medicamento."""
        if not self.caminho_arquivo.exists():
            return []
        try:
            with open(self.caminho_arquivo, "r", encoding="utf-8") as f:
                dados = json.load(f)
                return [
                    Medicamento(
                        id=d.get("id"),
                        codigo=d.get("codigo", ""),
                        nome=d.get("nome", ""),
                        fabricante=d.get("fabricante", ""),
                        categoria=d.get("categoria", ""),
                        apresentacao=d.get("apresentacao", ""),
                        preco_centavos=d.get("preco_centavos", 0),
                        data_validade=d.get("data_validade", ""),
                        estoque=d.get("estoque", 0),
                        estoque_minimo=d.get("estoque_minimo", 0),
                    )
                    for d in dados
                ]
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _salvar_lista(self, medicamentos: List[Medicamento]) -> None:
        """Grava a lista completa de medicamentos no arquivo JSON com indentação e UTF-8."""
        dados = [m.to_dict() for m in medicamentos]
        with open(self.caminho_arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)

    def inserir(self, med: Medicamento) -> int:
        """Gera o próximo ID sequencial, adiciona o medicamento e salva no arquivo."""
        medicamentos = self._carregar_lista()
        proximo_id = max([m.id for m in medicamentos if m.id is not None], default=0) + 1
        med.id = proximo_id
        medicamentos.append(med)
        self._salvar_lista(medicamentos)
        return med.id

    def atualizar(self, med: Medicamento) -> bool:
        """Atualiza os dados de um medicamento existente no arquivo JSON."""
        medicamentos = self._carregar_lista()
        for idx, m in enumerate(medicamentos):
            if m.id == med.id:
                medicamentos[idx] = med
                self._salvar_lista(medicamentos)
                return True
        return False

    def atualizar_estoque(self, medicamento_id: int, novo_estoque: int) -> bool:
        """Altera a quantidade em estoque de um medicamento no arquivo."""
        medicamentos = self._carregar_lista()
        for m in medicamentos:
            if m.id == medicamento_id:
                m.estoque = novo_estoque
                self._salvar_lista(medicamentos)
                return True
        return False

    def excluir(self, medicamento_id: int) -> bool:
        """Remove o medicamento do arquivo JSON."""
        medicamentos = self._carregar_lista()
        iniciais = len(medicamentos)
        medicamentos = [m for m in medicamentos if m.id != medicamento_id]
        if len(medicamentos) < iniciais:
            self._salvar_lista(medicamentos)
            return True
        return False

    def buscar_por_id(self, medicamento_id: int) -> Optional[Medicamento]:
        """Busca medicamento por ID."""
        for m in self._carregar_lista():
            if m.id == medicamento_id:
                return m
        return None

    def buscar_por_codigo(self, codigo: str) -> Optional[Medicamento]:
        """Busca medicamento pelo código exato."""
        cod_limpo = codigo.strip()
        for m in self._carregar_lista():
            if m.codigo.strip() == cod_limpo:
                return m
        return None

    def buscar_por_nome(self, nome_parcial: str) -> List[Medicamento]:
        """Pesquisa medicamentos pelo nome (case-insensitive)."""
        termo = nome_parcial.strip().lower()
        resultados = [m for m in self._carregar_lista() if termo in m.nome.lower()]
        return sorted(resultados, key=lambda x: x.nome.lower())

    def listar_todos(self) -> List[Medicamento]:
        """Lista todos os medicamentos em ordem alfabética."""
        return sorted(self._carregar_lista(), key=lambda x: x.nome.lower())

    def listar_por_categoria(self, categoria: str) -> List[Medicamento]:
        """Filtra medicamentos por categoria (case-insensitive)."""
        cat = categoria.strip().lower()
        return [m for m in self._carregar_lista() if m.categoria.strip().lower() == cat]

    def buscar_estoque_baixo(self) -> List[Medicamento]:
        """Retorna medicamentos com estoque menor ou igual ao estoque mínimo."""
        return [m for m in self._carregar_lista() if m.estoque <= m.estoque_minimo]

    def buscar_sem_estoque(self) -> List[Medicamento]:
        """Retorna medicamentos com estoque zerado."""
        return [m for m in self._carregar_lista() if m.estoque == 0]

    def buscar_proximos_vencimento(self, data_limite: str) -> List[Medicamento]:
        """Retorna medicamentos com data de validade menor ou igual à data limite (ISO 8601)."""
        return sorted(
            [m for m in self._carregar_lista() if m.data_validade <= data_limite],
            key=lambda x: x.data_validade,
        )

    def tem_vendas_associadas(self, medicamento_id: int) -> bool:
        """Verifica se existem vendas vinculadas a este medicamento."""
        if self.venda_repo is not None:
            return self.venda_repo.medicamento_tem_vendas(medicamento_id)
        return False
