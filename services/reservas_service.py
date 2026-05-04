"""
Servicio de Reservas - Lógica de negocio para CRUD de reservas.
"""
import sqlite3
import os
from dotenv import load_dotenv
from services.mesas_service import get_mesas_disponibles, ocupar_mesa, liberar_mesa

load_dotenv()
DB_NAME = os.getenv("DATABASE_NAME", "reservas.db")


def get_all_reservas():
    """Retorna todas las reservas del día actual."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nombre_cliente, cantidad_personas, fecha, hora, mesa_asignada
        FROM reservas
        ORDER BY hora ASC
    """)
    reservas = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return reservas


def get_reserva_by_id(reserva_id: int):
    """Retorna una reserva por su ID."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reservas WHERE id = ?", (reserva_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def buscar_reservas(query: str):
    """Busca reservas por nombre de cliente o ID."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM reservas
        WHERE nombre_cliente LIKE ? OR CAST(id AS TEXT) = ?
        ORDER BY hora ASC
    """, (f"%{query}%", query))
    reservas = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return reservas


def crear_reserva(nombre_cliente: str, cantidad_personas: int, fecha: str, hora: str):
    """
    Crea una nueva reserva.
    Verifica disponibilidad de mesas antes de confirmar.
    Retorna (reserva_dict, error_str).
    """
    mesas = get_mesas_disponibles(cantidad_personas)
    if not mesas:
        return None, f"No hay mesas disponibles para {cantidad_personas} personas."

    mesa_id = mesas[0]["id"]  # Asigna la mesa más pequeña que quepa

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO reservas (nombre_cliente, cantidad_personas, fecha, hora, mesa_asignada)
        VALUES (?, ?, ?, ?, ?)
    """, (nombre_cliente.strip(), cantidad_personas, fecha, hora, mesa_id))
    conn.commit()
    reserva_id = cursor.lastrowid
    conn.close()

    ocupar_mesa(mesa_id)

    return {
        "id": reserva_id,
        "nombre_cliente": nombre_cliente.strip(),
        "cantidad_personas": cantidad_personas,
        "fecha": fecha,
        "hora": hora,
        "mesa_asignada": mesa_id,
    }, None


def modificar_reserva(reserva_id: int, nombre_cliente: str, cantidad_personas: int, fecha: str, hora: str):
    """
    Modifica una reserva existente.
    Si cambia la cantidad de personas, busca nueva mesa adecuada.
    Retorna (reserva_dict, error_str).
    """
    reserva_actual = get_reserva_by_id(reserva_id)
    if not reserva_actual:
        return None, "Reserva no encontrada."

    mesa_id = reserva_actual["mesa_asignada"]

    # Si cambia la cantidad de personas, reasignar mesa
    if cantidad_personas != reserva_actual["cantidad_personas"]:
        liberar_mesa(mesa_id)
        mesas = get_mesas_disponibles(cantidad_personas)
        if not mesas:
            # Reocupar la mesa anterior si no hay alternativa
            ocupar_mesa(mesa_id)
            return None, f"No hay mesas disponibles para {cantidad_personas} personas."
        mesa_id = mesas[0]["id"]
        ocupar_mesa(mesa_id)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE reservas
        SET nombre_cliente = ?, cantidad_personas = ?, fecha = ?, hora = ?, mesa_asignada = ?
        WHERE id = ?
    """, (nombre_cliente.strip(), cantidad_personas, fecha, hora, mesa_id, reserva_id))
    conn.commit()
    conn.close()

    return {
        "id": reserva_id,
        "nombre_cliente": nombre_cliente.strip(),
        "cantidad_personas": cantidad_personas,
        "fecha": fecha,
        "hora": hora,
        "mesa_asignada": mesa_id,
    }, None


def eliminar_reserva(reserva_id: int):
    """
    Elimina una reserva y libera la mesa asociada.
    Retorna (True, None) o (False, error_str).
    """
    reserva = get_reserva_by_id(reserva_id)
    if not reserva:
        return False, "Reserva no encontrada."

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reservas WHERE id = ?", (reserva_id,))
    conn.commit()
    conn.close()

    liberar_mesa(reserva["mesa_asignada"])
    return True, None
