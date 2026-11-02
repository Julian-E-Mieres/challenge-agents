from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .exceptions import ReservaNoEncontradaError
from .models import Reservation, ReservationStatus


class ReservationRepository:
    def __init__(self, storage_path: str | Path | None = None):
        base_path = Path(storage_path) if storage_path is not None else Path(__file__).resolve().parents[1] / "data" / "reservas.json"
        self.storage_path = Path(base_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        if self.storage_path.exists():
            self._reservations = self._load()
        else:
            self._reservations: List[Reservation] = []

    def _load(self) -> List[Reservation]:
        with self.storage_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        reservations: List[Reservation] = []
        for item in payload:
            reservations.append(
                Reservation(
                    id=item["id"],
                    item_id=item["item_id"],
                    solicitante=item["solicitante"],
                    start_time=datetime.fromisoformat(item["start_time"]),
                    end_time=datetime.fromisoformat(item["end_time"]),
                    status=ReservationStatus(item["status"]),
                )
            )
        return reservations

    def _save(self) -> None:
        data = [
            {
                "id": reservation.id,
                "item_id": reservation.item_id,
                "solicitante": reservation.solicitante,
                "start_time": reservation.start_time.isoformat(timespec="minutes"),
                "end_time": reservation.end_time.isoformat(timespec="minutes"),
                "status": reservation.status.value,
            }
            for reservation in self._reservations
        ]

        directory = self.storage_path.parent
        temp_path = directory / f"{self.storage_path.name}.tmp"
        with temp_path.open("w", encoding="utf-8") as temp_file:
            json.dump(data, temp_file, ensure_ascii=False, indent=2)
            temp_file.write("\n")

        os.replace(temp_path, self.storage_path)

    def add(self, reservation: Reservation) -> None:
        self._reservations.append(reservation)
        self._save()

    def update(self, reservation: Reservation) -> None:
        for index, current in enumerate(self._reservations):
            if current.id == reservation.id:
                self._reservations[index] = reservation
                self._save()
                return
        raise ReservaNoEncontradaError(f"Reserva con id '{reservation.id}' no encontrada.")

    def get_by_id(self, reservation_id: str) -> Optional[Reservation]:
        for reservation in self._reservations:
            if reservation.id == reservation_id:
                return reservation
        return None

    def get_all(self) -> List[Reservation]:
        return list(self._reservations)

    def get_active_by_item(self, item_id: str) -> List[Reservation]:
        return [
            reservation for reservation in self._reservations
            if reservation.item_id == item_id and reservation.is_active()
        ]
