from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ReservationStatus(Enum):
    ACTIVA = "ACTIVA"
    CANCELADA = "CANCELADA"


@dataclass(frozen=True)
class Item:
    id: str
    name: str


@dataclass
class Reservation:
    id: str
    item_id: str
    solicitante: str
    start_time: datetime
    end_time: datetime
    status: ReservationStatus

    def is_active(self) -> bool:
        return self.status == ReservationStatus.ACTIVA

    def conflicts_with(self, start: datetime, end: datetime) -> bool:
        return (
            self.is_active()
            and start < self.end_time
            and end > self.start_time
        )
