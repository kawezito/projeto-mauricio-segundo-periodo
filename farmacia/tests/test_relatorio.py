import unittest
import sys
import tempfile
import csv
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from repositories.medicamento_repository import MedicamentoRepository
from repositories.cliente_repository import ClienteRepository
from repositories.estoque_repository import EstoqueRepository
from repositories.venda_repository import VendaRepository
from services.medicamento_service import MedicamentoService
from services.venda_service import VendaService
from services.relatorio_service import RelatorioService


class TestRelatorio(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        data_path = Path(self.temp_dir.name)
        self.venda_repo = VendaRepository(data_path / "vendas.json")
        self.cli_repo = ClienteRepository(data_path / "clientes.json", venda_repo=self.venda_repo)
        self.med_repo = MedicamentoRepository(data_path / "medicamentos.json", venda_repo=self.venda_repo)
        self.est_repo = EstoqueRepository(data_path / "movimentacoes.json", med_repo=self.med_repo)
        self.venda_repo.cliente_repo = self.cli_repo

        self.med_service = MedicamentoService(self.med_repo)
        self.venda_service = VendaService(
            self.venda_repo, self.med_repo, self.est_repo, self.cli_repo
        )

        self.rel_service = RelatorioService(
            self.med_repo, self.est_repo, self.venda_repo, reports_dir=data_path / "reports"
        )

        self.med = self.med_service.cadastrar({
            "codigo": "R01",
            "nome": "Ibuprofeno",
            "fabricante": "EMS",
            "categoria": "Anti-inflamatório",
            "apresentacao": "Comprimido",
            "preco": 15.0,
            "estoque": 2,
            "estoque_minimo": 5,
            "data_validade": "2027-10-10",
        })

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_matriz_e_exportacao_csv(self):
        matriz = self.rel_service.gerar_matriz_estoque()
        self.assertIsInstance(matriz, list)
        self.assertEqual(matriz[0][0], "ID")
        self.assertEqual(matriz[0][1], "Código")

        arquivo_csv = self.rel_service.exportar_estoque_csv("teste.csv")
        self.assertTrue(os.path.exists(arquivo_csv))

        with open(arquivo_csv, "r", encoding="utf-8") as f:
            linhas = list(csv.reader(f, delimiter=";"))
            self.assertGreaterEqual(len(linhas), 2)
            self.assertEqual(linhas[1][1], "R01")


if __name__ == "__main__":
    unittest.main()
