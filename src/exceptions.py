class UnidadNoEncontradaError(Exception):
    """Se produjo cuando una unidad no existe en el inventario."""


class IntervaloInvalidoError(Exception):
    """Se produjo cuando un intervalo de tiempo es inválido."""


class SolicitanteInvalidoError(Exception):
    """Se produjo cuando el solicitante no es válido."""


class ReservaSuperpuestaError(Exception):
    """Se produjo cuando una reserva se superpone con otra activa."""


class ReservaNoEncontradaError(Exception):
    """Se produjo cuando una reserva no existe o no coincide."""
