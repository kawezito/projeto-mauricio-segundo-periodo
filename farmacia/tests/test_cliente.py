import unittest
import sys
import tempfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from repositories.cliente_repository import ClienteRepository
from repositories.venda_repository import VendaRepository
from services.cliente_service import ClienteService
from models.venda import Venda
from exceptions import (
    ValidacaoError,
    IntegridadeReferencialError,
)


class TestCliente(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        data_path = Path(self.temp_dir.name)
        self.venda_repo = VendaRepository(data_path / "vendas.json")
        self.repo = ClienteRepository(data_path / "clientes.json", venda_repo=self.venda_repo)
        self.service = ClienteService(self.repo)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_cadastro_valido(self):
        c = self.service.cadastrar({
            "nome": "Carlos Silva",
            "telefone": "(11) 98765-4321",
            "email": "carlos@email.com",
        })
        self.assertIsNotNone(c.id)
        self.assertEqual(c.nome, "Carlos Silva")

    def test_nome_obrigatorio(self):
        with self.assertRaises(ValidacaoError):
            self.service.cadastrar({"nome": "   ", "email": "teste@email.com"})

    def test_busca_por_nome(self):
        self.service.cadastrar({"nome": "Ana Maria"})
        self.service.cadastrar({"nome": "Bruno Lima"})

        resultados = self.service.pesquisar_por_nome("ana")
        self.assertEqual(len(resultados), 1)
        self.assertEqual(resultados[0].nome, "Ana Maria")

    def test_impedimento_exclusao_com_vendas(self):
        c = self.service.cadastrar({"nome": "Cliente com Compras"})
        venda = Venda(cliente_id=c.id, data_venda="2026-11-12T10:00:00", valor_total_centavos=500)
        self.venda_repo.inserir_venda_completa(venda)

        with self.assertRaises(IntegridadeReferencialError):
            self.service.excluir(c.id)


if __name__ == "__main__":
    unittest.main()
