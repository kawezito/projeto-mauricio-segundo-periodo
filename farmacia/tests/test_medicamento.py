import unittest
import sys
import tempfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from repositories.medicamento_repository import MedicamentoRepository
from repositories.venda_repository import VendaRepository
from services.medicamento_service import MedicamentoService
from models.venda import Venda
from models.item_venda import ItemVenda
from exceptions import (
    ValidacaoError,
    CodigoDuplicadoError,
    MedicamentoNaoEncontradoError,
    IntegridadeReferencialError,
)


class TestMedicamento(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        data_path = Path(self.temp_dir.name)
        self.venda_repo = VendaRepository(data_path / "vendas.json")
        self.repo = MedicamentoRepository(data_path / "medicamentos.json", venda_repo=self.venda_repo)
        self.service = MedicamentoService(self.repo)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_cadastro_valido(self):
        med = self.service.cadastrar({
            "codigo": "M01",
            "nome": "Paracetamol 750mg",
            "fabricante": "EMS",
            "categoria": "Analgésico",
            "apresentacao": "Comprimido",
            "preco": "12.50",
            "estoque": 20,
            "estoque_minimo": 5,
            "data_validade": "2027-12-31",
        })
        self.assertIsNotNone(med.id)
        self.assertEqual(med.codigo, "M01")
        self.assertEqual(med.preco_centavos, 1250)
        self.assertEqual(med.preco_em_reais(), 12.5)

    def test_impedimento_codigo_duplicado(self):
        dados = {
            "codigo": "M01",
            "nome": "Dipirona",
            "fabricante": "Neo Química",
            "categoria": "Analgésico",
            "apresentacao": "Gotas",
            "preco": 8.0,
            "estoque": 10,
            "estoque_minimo": 2,
            "data_validade": "2027-01-01",
        }
        self.service.cadastrar(dados)
        with self.assertRaises(CodigoDuplicadoError):
            self.service.cadastrar(dados)

    def test_validacoes_campos_obrigatorios(self):
        with self.assertRaises(ValidacaoError):
            self.service.cadastrar({"codigo": "", "nome": "A"})
        with self.assertRaises(ValidacaoError):
            self.service.cadastrar({
                "codigo": "M02",
                "nome": "Remédio",
                "fabricante": "F",
                "categoria": "C",
                "apresentacao": "A",
                "preco": -5.0,
                "data_validade": "2027-01-01",
            })

    def test_exclusao_e_bloqueio_com_vendas(self):
        med = self.service.cadastrar({
            "codigo": "M03",
            "nome": "Omeprazol",
            "fabricante": "Medley",
            "categoria": "Antiácido",
            "apresentacao": "Cápsula",
            "preco": 20.0,
            "data_validade": "2027-01-01",
        })
        self.assertTrue(self.service.excluir(med.id))

        med2 = self.service.cadastrar({
            "codigo": "M04",
            "nome": "Losartana",
            "fabricante": "EMS",
            "categoria": "Anti-hipertensivo",
            "apresentacao": "Comprimido",
            "preco": 10.0,
            "data_validade": "2027-01-01",
        })
        venda = Venda(
            data_venda="2026-11-12T10:00:00",
            valor_total_centavos=1000,
            itens=[
                ItemVenda(
                    medicamento_id=med2.id,
                    quantidade=1,
                    preco_unitario_centavos=1000,
                    subtotal_centavos=1000,
                )
            ],
        )
        self.venda_repo.inserir_venda_completa(venda)

        with self.assertRaises(IntegridadeReferencialError):
            self.service.excluir(med2.id)


if __name__ == "__main__":
    unittest.main()
