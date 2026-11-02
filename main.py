from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from src.exceptions import (
    IntervaloInvalidoError,
    ReservaNoEncontradaError,
    ReservaSuperpuestaError,
    SolicitanteInvalidoError,
    UnidadNoEncontradaError,
)
from src.models import Item
from src.repository import ReservationRepository
from src.service import LaboratoryService

ROOT_DIR = Path(__file__).resolve().parent
INVENTORY_PATH = ROOT_DIR / "data" / "inventory.json"
RESERVAS_PATH = ROOT_DIR / "data" / "reservas.json"


def load_inventory() -> list[Item]:
    with INVENTORY_PATH.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    return [Item(id=item["id"], name=item["name"]) for item in payload]


def parse_datetime(value: str) -> datetime:
    cleaned = value.strip()
    if "T" in cleaned:
        return datetime.fromisoformat(cleaned)
    if " " in cleaned:
        return datetime.fromisoformat(cleaned.replace(" ", "T"))
    return datetime.fromisoformat(cleaned)


def print_inventory(service: LaboratoryService) -> None:
    print("\nEquipos disponibles:")
    for item in service.inventory.values():
        print(f"- {item.id}: {item.name}")


def consultar_disponibilidad(service: LaboratoryService) -> None:
    item_id = input("Código del equipo: ").strip()
    start_text = input("Inicio (YYYY-MM-DDTHH:MM): ")
    end_text = input("Fin (YYYY-MM-DDTHH:MM): ")

    start_time = parse_datetime(start_text)
    end_time = parse_datetime(end_text)

    try:
        disponible = service.consultar_disponibilidad(item_id, start_time, end_time)
        if disponible:
            print("Disponible: sí.")
        else:
            print("Disponible: no.")
    except (UnidadNoEncontradaError, IntervaloInvalidoError) as exc:
        print(f"Error: {exc}")
    except ValueError:
        print("Error: formato de fecha inválido. Use YYYY-MM-DDTHH:MM.")


def crear_reserva(service: LaboratoryService) -> None:
    item_id = input("Código del equipo: ").strip()
    solicitante = input("Solicitante: ")
    start_text = input("Inicio (YYYY-MM-DDTHH:MM): ")
    end_text = input("Fin (YYYY-MM-DDTHH:MM): ")

    try:
        reserva = service.crear_reserva(
            item_id=item_id,
            solicitante=solicitante,
            start_time=parse_datetime(start_text),
            end_time=parse_datetime(end_text),
        )
        print(f"Reserva creada correctamente: {reserva.id} | {reserva.item_id} | {reserva.solicitante}")
    except (UnidadNoEncontradaError, IntervaloInvalidoError, SolicitanteInvalidoError, ReservaSuperpuestaError) as exc:
        print(f"Error: {exc}")
    except ValueError:
        print("Error: formato de fecha inválido. Use YYYY-MM-DDTHH:MM.")


def cancelar_reserva(service: LaboratoryService) -> None:
    reservation_id = input("ID de la reserva a cancelar: ").strip()
    try:
        reserva = service.cancelar_reserva(reservation_id)
        print(f"Reserva cancelada: {reserva.id} ({reserva.status.value})")
    except ReservaNoEncontradaError as exc:
        print(f"Error: {exc}")


def ver_historial(service: LaboratoryService) -> None:
    reservas = service.repository.get_all()
    if not reservas:
        print("No hay reservas registradas.")
        return

    print("\nHistorial de reservas:")
    for reserva in reservas:
        print(
            f"- {reserva.id} | equipo={reserva.item_id} | "
            f"solicitante={reserva.solicitante} | "
            f"inicio={reserva.start_time.isoformat(timespec='minutes')} | "
            f"fin={reserva.end_time.isoformat(timespec='minutes')} | "
            f"estado={reserva.status.value}"
        )


def cli() -> None:
    inventory = load_inventory()
    repository = ReservationRepository(storage_path=RESERVAS_PATH)
    service = LaboratoryService(inventory=inventory, repository=repository)

    print("Sistema de reservas del laboratorio")
    print("===================================")

    while True:
        print("\n1. Listar equipos")
        print("2. Consultar disponibilidad")
        print("3. Crear reserva")
        print("4. Cancelar reserva")
        print("5. Ver historial de reservas")
        print("0. Salir")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            print_inventory(service)
        elif opcion == "2":
            consultar_disponibilidad(service)
        elif opcion == "3":
            crear_reserva(service)
        elif opcion == "4":
            cancelar_reserva(service)
        elif opcion == "5":
            ver_historial(service)
        elif opcion == "0":
            print("Saliendo del sistema...")
            break
        else:
            print("Opción no válida. Intente nuevamente.")


if __name__ == "__main__":
    cli()
