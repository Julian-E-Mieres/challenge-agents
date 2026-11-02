from __future__ import annotations

import uuid
from datetime import datetime
from typing import Iterable, List

from .exceptions import (
    IntervaloInvalidoError,
    ReservaNoEncontradaError,
    ReservaSuperpuestaError,
    SolicitanteInvalidoError,
    UnidadNoEncontradaError,
)
from .models import Item, Reservation, ReservationStatus
from .repository import ReservationRepository


class LaboratoryService:
    def __init__(self, inventory: Iterable[Item], repository: ReservationRepository):
        self.inventory = {item.id: item for item in inventory}
        self.repository = repository

    def consultar_disponibilidad(
        self,
        item_id: str,
        start_time: datetime,
        end_time: datetime,
    ) -> bool:
        if item_id not in self.inventory:
            raise UnidadNoEncontradaError(f"La unidad '{item_id}' no existe en el inventario.")

        if start_time >= end_time:
            raise IntervaloInvalidoError("El intervalo de reserva debe tener start_time < end_time.")

        active_reservations = self.repository.get_active_by_item(item_id)
        return not any(
            reservation.conflicts_with(start_time, end_time)
            for reservation in active_reservations
        )

    def crear_reserva(
        self,
        item_id: str,
        solicitante: str,
        start_time: datetime,
        end_time: datetime,
    ) -> Reservation:
        if item_id not in self.inventory:
            raise UnidadNoEncontradaError(f"La unidad '{item_id}' no existe en el inventario.")

        if start_time >= end_time:
            raise IntervaloInvalidoError("El intervalo de reserva debe tener start_time < end_time.")

        if not isinstance(solicitante, str) or not solicitante.strip():
            raise SolicitanteInvalidoError("El solicitante debe ser una cadena de texto no vacía.")

        if not self.consultar_disponibilidad(item_id, start_time, end_time):
            raise ReservaSuperpuestaError(
                f"La unidad '{item_id}' ya tiene una reserva activa en ese intervalo."
            )

        reservation = Reservation(
            id=str(uuid.uuid4()),
            item_id=item_id,
            solicitante=solicitante.strip(),
            start_time=start_time,
            end_time=end_time,
            status=ReservationStatus.ACTIVA,
        )
        self.repository.add(reservation)
        return reservation

    def cancelar_reserva(self, reservation_id: str) -> Reservation:
        reservation = self.repository.get_by_id(reservation_id)
        if reservation is None:
            raise ReservaNoEncontradaError(f"No existe una reserva con id '{reservation_id}'.")

        reservation.status = ReservationStatus.CANCELADA
        self.repository.update(reservation)
        return reservation
