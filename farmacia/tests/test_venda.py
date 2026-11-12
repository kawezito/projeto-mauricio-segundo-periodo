import unittest
import sys
import tempfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from repositories.medicamento_repository import MedicamentoRepository
from repositories.cliente_repository import ClienteRepository
from repositories.estoque_repository import EstoqueRepository
from repositories.venda_repository import VendaRepository
from services.medicamento_service import MedicamentoService
from services.cliente_service import ClienteService
from services.venda_service import VendaService
from exceptions import EstoqueInsuficienteError


class TestVenda(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        data_path = Path(self.temp_dir.name)
        self.venda_repo = VendaRepository(data_path / "vendas.json")
        self.cli_repo = ClienteRepository(data_path / "clientes.json", venda_repo=self.venda_repo)
        self.med_repo = MedicamentoRepository(data_path / "medicamentos.json", venda_repo=self.venda_repo)
        self.est_repo = EstoqueRepository(data_path / "movimentacoes.json", med_repo=self.med_repo)
        self.venda_repo.cliente_repo = self.cli_repo

        self.med_service = MedicamentoService(self.med_repo)
        self.cli_service = ClienteService(self.cli_repo)
        self.venda_service = VendaService(
            self.venda_repo, self.med_repo, self.est_repo, self.cli_repo
        )

        self.med = self.med_service.cadastrar({
            "codigo": "V01",
            "nome": "Dipirona 500mg",
            "fabricante": "EMS",
            "categoria": "Analgésico",
            "apresentacao": "Comprimido",
            "preco": 10.0,
            "estoque": 15,
            "estoque_minimo": 5,
            "data_validade": "2027-12-31",
        })

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_venda_valida_e_baixa_estoque(self):
        carrinho = [{"medicamento_id": self.med.id, "quantidade": 2}]
        venda = self.venda_service.registrar_venda(carrinho)

        self.assertIsNotNone(venda.id)
        self.assertEqual(venda.valor_total_centavos, 2000)
        self.assertEqual(venda.valor_total_em_reais(), 20.0)

        med_atualizado = self.med_service.buscar_por_id(self.med.id)
        self.assertEqual(med_atualizado.estoque, 13)

        movs = self.est_repo.listar_por_medicamento(self.med.id)
        self.assertEqual(len(movs), 1)
        self.assertEqual(movs[0]["tipo"], "SAIDA")

    def test_bloqueio_estoque_insuficiente_e_consistencia(self):
        carrinho_invalido = [{"medicamento_id": self.med.id, "quantidade": 50}]
        with self.assertRaises(EstoqueInsuficienteError):
            self.venda_service.registrar_venda(carrinho_invalido)

        vendas = self.venda_service.listar_todas()
        self.assertEqual(len(vendas), 0)

        med_atualizado = self.med_service.buscar_por_id(self.med.id)
        self.assertEqual(med_atualizado.estoque, 15)


if __name__ == "__main__":
    unittest.main()
