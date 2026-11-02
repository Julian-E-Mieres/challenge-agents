from datetime import datetime

import pytest

from src.exceptions import (
    IntervaloInvalidoError,
    ReservaSuperpuestaError,
    SolicitanteInvalidoError,
)
from src.models import Item, ReservationStatus
from src.repository import ReservationRepository
from src.service import LaboratoryService


@pytest.fixture
def inventory():
    return [
        Item(id="MIC-01", name="Microscopio digital"),
        Item(id="MIC-02", name="Microscopio digital"),
        Item(id="OSC-01", name="Osciloscopio"),
        Item(id="MUL-01", name="Multímetro"),
        Item(id="FUE-01", name="Fuente de alimentación"),
    ]


@pytest.fixture
def service_with_repo(tmp_path, inventory):
    repo_path = tmp_path / "reservas.json"
    repository = ReservationRepository(storage_path=repo_path)
    service = LaboratoryService(inventory=inventory, repository=repository)
    return service, repository, repo_path


def test_req_res_01_creacion_exitosa_de_reserva_activa(service_with_repo):
    service, repository, _ = service_with_repo

    reserva = service.crear_reserva(
        item_id="MIC-01",
        solicitante="Ana López",
        start_time=datetime(2026, 1, 10, 10, 0),
        end_time=datetime(2026, 1, 10, 11, 0),
    )

    assert reserva.status == ReservationStatus.ACTIVA
    assert reserva.id
    assert reserva.item_id == "MIC-01"
    assert reserva.solicitante == "Ana López"
    assert repository.get_by_id(reserva.id) is not None


def test_req_res_02_rechazo_con_solicitante_invalido(service_with_repo):
    service, _, _ = service_with_repo

    for solicitante in ["", "   ", None, 123]:
        with pytest.raises(SolicitanteInvalidoError):
            service.crear_reserva(
                item_id="MIC-01",
                solicitante=solicitante,
                start_time=datetime(2026, 1, 10, 10, 0),
                end_time=datetime(2026, 1, 10, 11, 0),
            )


def test_req_res_03_rechazo_con_intervalo_invalido(service_with_repo):
    service, _, _ = service_with_repo

    with pytest.raises(IntervaloInvalidoError):
        service.crear_reserva(
            item_id="MIC-01",
            solicitante="Estudiante",
            start_time=datetime(2026, 1, 10, 11, 0),
            end_time=datetime(2026, 1, 10, 11, 0),
        )


def test_req_res_04_rechazo_con_solapamiento_total_parcial_o_envolvente(service_with_repo):
    service, _, _ = service_with_repo

    service.crear_reserva(
        item_id="MIC-01",
        solicitante="Pedro",
        start_time=datetime(2026, 1, 10, 10, 0),
        end_time=datetime(2026, 1, 10, 12, 0),
    )

    cases = [
        (datetime(2026, 1, 10, 9, 0), datetime(2026, 1, 10, 10, 30)),
        (datetime(2026, 1, 10, 10, 30), datetime(2026, 1, 10, 11, 30)),
        (datetime(2026, 1, 10, 9, 0), datetime(2026, 1, 10, 13, 0)),
    ]

    for start_time, end_time in cases:
        with pytest.raises(ReservaSuperpuestaError):
            service.crear_reserva(
                item_id="MIC-01",
                solicitante="Laura",
                start_time=start_time,
                end_time=end_time,
            )


def test_req_res_05_aceptacion_de_reservas_contiguas_consecutivas(service_with_repo):
    service, _, _ = service_with_repo

    primera = service.crear_reserva(
        item_id="MIC-01",
        solicitante="Ana",
        start_time=datetime(2026, 1, 10, 10, 0),
        end_time=datetime(2026, 1, 10, 11, 0),
    )
    segunda = service.crear_reserva(
        item_id="MIC-01",
        solicitante="Beto",
        start_time=datetime(2026, 1, 10, 11, 0),
        end_time=datetime(2026, 1, 10, 12, 0),
    )

    assert primera.status == ReservationStatus.ACTIVA
    assert segunda.status == ReservationStatus.ACTIVA
    assert service.consultar_disponibilidad(
        "MIC-01",
        datetime(2026, 1, 10, 11, 0),
        datetime(2026, 1, 10, 12, 0),
    ) is False


def test_req_res_06_simultaneidad_en_unidades_distintas(service_with_repo):
    service, _, _ = service_with_repo

    reserva_1 = service.crear_reserva(
        item_id="MIC-01",
        solicitante="Ana",
        start_time=datetime(2026, 1, 10, 15, 0),
        end_time=datetime(2026, 1, 10, 16, 0),
    )
    reserva_2 = service.crear_reserva(
        item_id="MIC-02",
        solicitante="Luis",
        start_time=datetime(2026, 1, 10, 15, 0),
        end_time=datetime(2026, 1, 10, 16, 0),
    )

    assert reserva_1.item_id == "MIC-01"
    assert reserva_2.item_id == "MIC-02"
    assert service.consultar_disponibilidad(
        "MIC-02",
        datetime(2026, 1, 10, 15, 30),
        datetime(2026, 1, 10, 15, 45),
    ) is False


def test_req_res_07_cancelacion_libera_el_intervalo(service_with_repo):
    service, repository, _ = service_with_repo

    reserva = service.crear_reserva(
        item_id="MIC-01",
        solicitante="María",
        start_time=datetime(2026, 1, 10, 9, 0),
        end_time=datetime(2026, 1, 10, 10, 0),
    )

    reserva_cancelada = service.cancelar_reserva(reserva.id)

    assert reserva_cancelada.id == reserva.id
    assert reserva_cancelada.status.value == "CANCELADA"
    assert repository.get_by_id(reserva.id).status.value == "CANCELADA"
    assert service.consultar_disponibilidad(
        "MIC-01",
        datetime(2026, 1, 10, 9, 0),
        datetime(2026, 1, 10, 10, 0),
    ) is True

    nueva = service.crear_reserva(
        item_id="MIC-01",
        solicitante="Juan",
        start_time=datetime(2026, 1, 10, 9, 0),
        end_time=datetime(2026, 1, 10, 10, 0),
    )

    assert nueva.item_id == "MIC-01"
    assert nueva.status == ReservationStatus.ACTIVA


def test_req_res_08_persistencia_al_reiniciar_repository(tmp_path, inventory):
    repo_path = tmp_path / "reservas.json"
    repository = ReservationRepository(storage_path=repo_path)
    service = LaboratoryService(inventory=inventory, repository=repository)

    reserva_activa = service.crear_reserva(
        item_id="MIC-01",
        solicitante="Ana",
        start_time=datetime(2026, 1, 12, 8, 0),
        end_time=datetime(2026, 1, 12, 9, 0),
    )
    reserva_cancelada = service.crear_reserva(
        item_id="MIC-02",
        solicitante="Luis",
        start_time=datetime(2026, 1, 12, 10, 0),
        end_time=datetime(2026, 1, 12, 11, 0),
    )
    service.cancelar_reserva(reserva_cancelada.id)

    reloaded_repository = ReservationRepository(storage_path=repo_path)
    reloaded_service = LaboratoryService(inventory=inventory, repository=reloaded_repository)

    assert len(reloaded_repository.get_all()) == 2
    assert reloaded_repository.get_by_id(reserva_activa.id).status == ReservationStatus.ACTIVA
    assert reloaded_repository.get_by_id(reserva_cancelada.id).status == ReservationStatus.CANCELADA
    assert reloaded_service.consultar_disponibilidad(
        "MIC-01",
        datetime(2026, 1, 12, 8, 30),
        datetime(2026, 1, 12, 8, 45),
    ) is False
    assert reloaded_service.consultar_disponibilidad(
        "MIC-02",
        datetime(2026, 1, 12, 10, 0),
        datetime(2026, 1, 12, 11, 0),
    ) is True
