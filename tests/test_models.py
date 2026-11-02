from datetime import datetime

from src.models import Reservation, ReservationStatus


def test_reserva_activa_conflicta_con_intervalo_solapado():
    reserva = Reservation(
        id="R-001",
        item_id="MIC-01",
        solicitante="Ana",
        start_time=datetime(2026, 1, 1, 10, 0),
        end_time=datetime(2026, 1, 1, 11, 0),
        status=ReservationStatus.ACTIVA,
    )

    assert reserva.is_active() is True
    assert reserva.conflicts_with(
        datetime(2026, 1, 1, 10, 30),
        datetime(2026, 1, 1, 10, 45),
    ) is True


def test_reserva_no_conflicta_con_limites_consecutivos_exactos():
    reserva = Reservation(
        id="R-002",
        item_id="MIC-02",
        solicitante="Luis",
        start_time=datetime(2026, 1, 1, 11, 0),
        end_time=datetime(2026, 1, 1, 12, 0),
        status=ReservationStatus.ACTIVA,
    )

    assert reserva.conflicts_with(
        datetime(2026, 1, 1, 10, 0),
        datetime(2026, 1, 1, 11, 0),
    ) is False
    assert reserva.conflicts_with(
        datetime(2026, 1, 1, 12, 0),
        datetime(2026, 1, 1, 13, 0),
    ) is False


def test_reserva_cancelada_no_conflicta():
    reserva = Reservation(
        id="R-003",
        item_id="OSC-01",
        solicitante="Maria",
        start_time=datetime(2026, 1, 1, 9, 0),
        end_time=datetime(2026, 1, 1, 10, 0),
        status=ReservationStatus.CANCELADA,
    )

    assert reserva.is_active() is False
    assert reserva.conflicts_with(
        datetime(2026, 1, 1, 9, 30),
        datetime(2026, 1, 1, 9, 45),
    ) is False
