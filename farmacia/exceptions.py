class FarmaciaError(Exception):
    pass


class ValidacaoError(FarmaciaError):
    pass


class CodigoDuplicadoError(FarmaciaError):
    pass


class MedicamentoNaoEncontradoError(FarmaciaError):
    pass


class ClienteNaoEncontradoError(FarmaciaError):
    pass


class VendaNaoEncontradaError(FarmaciaError):
    pass


class EstoqueInsuficienteError(FarmaciaError):
    pass


class IntegridadeReferencialError(FarmaciaError):
    pass


class OperacaoInvalidaError(FarmaciaError):
    pass
