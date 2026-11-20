import sqlite3
from pathlib import Path
from typing import Optional

from database.connection import get_connection, init_db
from database.unit_of_work import SqliteUnitOfWork
from exporters.csv_exporter import CsvReportExporter
from repositories import (
    MedicamentoRepository,
    ClienteRepository,
    VendaRepository,
    EstoqueRepository,
)
from services import (
    MedicamentoService,
    ClienteService,
    EstoqueService,
    VendaService,
    RelatorioService,
)
from interfaces.repositories import (
    IMedicamentoRepository,
    IClienteRepository,
    IVendaRepository,
    IEstoqueRepository,
)
from interfaces.transaction import IUnitOfWork
from interfaces.exporter import IReportExporter


class Container:
    def __init__(
        self,
        db_path: Optional[str | Path] = None,
        reports_dir: Optional[str | Path] = None,
    ):
        self.base_dir = Path(__file__).resolve().parent
        self.db_path = Path(db_path) if db_path else self.base_dir / "data" / "farmacia.db"
        self.reports_dir = Path(reports_dir) if reports_dir else self.base_dir / "reports"

        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = get_connection(self.db_path)
        init_db(self.conn)

        self.uow: IUnitOfWork = SqliteUnitOfWork(self.conn)
        self.med_repo: IMedicamentoRepository = MedicamentoRepository(self.conn)
        self.cli_repo: IClienteRepository = ClienteRepository(self.conn)
        self.venda_repo: IVendaRepository = VendaRepository(self.conn)
        self.est_repo: IEstoqueRepository = EstoqueRepository(self.conn)
        self.exporter: IReportExporter = CsvReportExporter(reports_dir=self.reports_dir)

        self.med_service = MedicamentoService(self.med_repo)
        self.cli_service = ClienteService(self.cli_repo)
        self.est_service = EstoqueService(self.med_repo, self.est_repo, self.uow)
        self.venda_service = VendaService(
            self.venda_repo,
            self.med_repo,
            self.est_repo,
            self.cli_repo,
            self.uow,
        )
        self.rel_service = RelatorioService(
            self.med_repo,
            self.est_repo,
            self.venda_repo,
            self.exporter,
        )

        self._seed_dados_iniciais()

    def _seed_dados_iniciais(self) -> None:
        if not self.med_repo.listar_todos():
            self.med_service.cadastrar({
                "codigo": "7891010",
                "nome": "Paracetamol 750mg",
                "fabricante": "EMS",
                "categoria": "Analgésico",
                "apresentacao": "Comprimido",
                "preco": "12.50",
                "estoque": 30,
                "estoque_minimo": 10,
                "data_validade": "2027-12-31",
            })
            self.med_service.cadastrar({
                "codigo": "7892020",
                "nome": "Amoxicilina 500mg",
                "fabricante": "Medley",
                "categoria": "Antibiótico",
                "apresentacao": "Cápsula",
                "preco": "28.90",
                "estoque": 8,
                "estoque_minimo": 10,
                "data_validade": "2026-10-15",
            })
            self.med_service.cadastrar({
                "codigo": "7893030",
                "nome": "Ibuprofeno 600mg",
                "fabricante": "Neo Química",
                "categoria": "Anti-inflamatório",
                "apresentacao": "Comprimido",
                "preco": "18.00",
                "estoque": 50,
                "estoque_minimo": 15,
                "data_validade": "2027-08-20",
            })

        if not self.cli_repo.listar_todos():
            self.cli_service.cadastrar({
                "nome": "Mariana Souza",
                "telefone": "(85) 98888-1122",
                "email": "mariana@email.com",
            })
            self.cli_service.cadastrar({
                "nome": "Lucas Ferreira",
                "telefone": "(85) 97777-3344",
                "email": "lucas@email.com",
            })

    def fechar(self) -> None:
        if self.conn:
            self.conn.close()

