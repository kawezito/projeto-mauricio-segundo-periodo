import json
from pathlib import Path
from typing import Optional, List
from models.cliente import Cliente

DEFAULT_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "clientes.json"


class ClienteRepository:
    """
    Repositório de persistência de Cliente baseado 100% em manipulação de arquivos JSON.
    Não utiliza banco de dados. Lê e escreve diretamente no arquivo 'clientes.json'.
    """

    def __init__(self, caminho_arquivo: Optional[Path | str] = None, venda_repo=None):
        self.caminho_arquivo = Path(caminho_arquivo) if caminho_arquivo else DEFAULT_DATA_FILE
        self.venda_repo = venda_repo
        self.caminho_arquivo.parent.mkdir(parents=True, exist_ok=True)
        if not self.caminho_arquivo.exists():
            self._salvar_lista([])

    def _carregar_lista(self) -> List[Cliente]:
        """Abre e lê o arquivo JSON, convertendo cada registro em objeto Cliente."""
        if not self.caminho_arquivo.exists():
            return []
        try:
            with open(self.caminho_arquivo, "r", encoding="utf-8") as f:
                dados = json.load(f)
                return [
                    Cliente(
                        id=d.get("id"),
                        nome=d.get("nome", ""),
                        telefone=d.get("telefone"),
                        email=d.get("email"),
                    )
                    for d in dados
                ]
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _salvar_lista(self, clientes: List[Cliente]) -> None:
        """Grava a lista completa de clientes no arquivo JSON."""
        dados = [c.to_dict() for c in clientes]
        with open(self.caminho_arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)

    def inserir(self, cliente: Cliente) -> int:
        """Adiciona um novo cliente e salva no arquivo com ID auto-incrementado."""
        clientes = self._carregar_lista()
        proximo_id = max([c.id for c in clientes if c.id is not None], default=0) + 1
        cliente.id = proximo_id
        clientes.append(cliente)
        self._salvar_lista(clientes)
        return cliente.id

    def atualizar(self, cliente: Cliente) -> bool:
        """Atualiza os dados de um cliente existente."""
        clientes = self._carregar_lista()
        for idx, c in enumerate(clientes):
            if c.id == cliente.id:
                clientes[idx] = cliente
                self._salvar_lista(clientes)
                return True
        return False

    def excluir(self, cliente_id: int) -> bool:
        """Remove o cliente do arquivo JSON."""
        clientes = self._carregar_lista()
        iniciais = len(clientes)
        clientes = [c for c in clientes if c.id != cliente_id]
        if len(clientes) < iniciais:
            self._salvar_lista(clientes)
            return True
        return False

    def buscar_por_id(self, cliente_id: int) -> Optional[Cliente]:
        """Busca cliente por ID."""
        for c in self._carregar_lista():
            if c.id == cliente_id:
                return c
        return None

    def buscar_por_nome(self, termo: str) -> List[Cliente]:
        """Pesquisa clientes por parte do nome (case-insensitive)."""
        termo_limpo = termo.strip().lower()
        encontrados = [c for c in self._carregar_lista() if termo_limpo in c.nome.lower()]
        return sorted(encontrados, key=lambda x: x.nome.lower())

    def listar_todos(self) -> List[Cliente]:
        """Lista todos os clientes em ordem alfabética."""
        return sorted(self._carregar_lista(), key=lambda x: x.nome.lower())

    def tem_vendas_associadas(self, cliente_id: int) -> bool:
        """Verifica se existem vendas vinculadas a este cliente."""
        if self.venda_repo is not None:
            return self.venda_repo.cliente_tem_vendas(cliente_id)
        return False
