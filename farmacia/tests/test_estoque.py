import unittest
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from repositories.medicamento_repository import MedicamentoRepository
from repositories.estoque_repository import EstoqueRepository
from services.medicamento_service import MedicamentoService
from services.estoque_service import EstoqueService
from exceptions import ValidacaoError


class TestEstoque(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        data_path = Path(self.temp_dir.name)
        self.med_repo = MedicamentoRepository(data_path / "medicamentos.json")
        self.est_repo = EstoqueRepository(data_path / "movimentacoes.json", med_repo=self.med_repo)
        self.med_service = MedicamentoService(self.med_repo)
        self.est_service = EstoqueService(self.med_repo, self.est_repo)

        self.med1 = self.med_service.cadastrar({
            "codigo": "E01",
            "nome": "Dorflex",
            "fabricante": "Sanofi",
            "categoria": "Relaxante",
            "apresentacao": "Comprimido",
            "preco": 10.0,
            "estoque": 5,
            "estoque_minimo": 10,
            "data_validade": (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d"),
        })

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_entrada_de_estoque(self):
        res = self.est_service.registrar_entrada(self.med1.id, 15)
        self.assertEqual(res["tipo"], "ENTRADA")
        self.assertEqual(res["novo_estoque"], 20)

        m = self.med_service.buscar_por_id(self.med1.id)
        self.assertEqual(m.estoque, 20)

    def test_impedimento_quantidade_invalida(self):
        with self.assertRaises(ValidacaoError):
            self.est_service.registrar_entrada(self.med1.id, 0)
        with self.assertRaises(ValidacaoError):
            self.est_service.registrar_entrada(self.med1.id, -10)

    def test_consulta_estoque_baixo(self):
        baixos = self.est_service.consultar_estoque_baixo()
        self.assertEqual(len(baixos), 1)
        self.assertEqual(baixos[0].codigo, "E01")


if __name__ == "__main__":
    unittest.main()
