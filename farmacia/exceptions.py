"""
Exceções de negócio para o Sistema de Gerenciamento de Farmácia.
"""


class FarmaciaError(Exception):
    """Exceção base para todas as exceções do sistema."""
    pass


class ValidacaoError(FarmaciaError):
    """Lançada quando dados obrigatórios estão ausentes ou inválidos."""
    pass


class CodigoDuplicadoError(FarmaciaError):
    """Lançada quando se tenta cadastrar um medicamento com código já existente."""
    pass


class MedicamentoNaoEncontradoError(FarmaciaError):
    """Lançada quando um medicamento pesquisado não é encontrado."""
    pass


class ClienteNaoEncontradoError(FarmaciaError):
    """Lançada quando um cliente pesquisado não é encontrado."""
    pass


class VendaNaoEncontradaError(FarmaciaError):
    """Lançada quando uma venda pesquisada não é encontrada."""
    pass


class EstoqueInsuficienteError(FarmaciaError):
    """Lançada quando a quantidade de venda ou saída excede o estoque disponível."""
    pass


class IntegridadeReferencialError(FarmaciaError):
    """Lançada quando a exclusão é impedida por vendas vinculadas."""
    pass


class OperacaoInvalidaError(FarmaciaError):
    """Lançada quando uma operação viola o fluxo de negócio do sistema."""
    pass

