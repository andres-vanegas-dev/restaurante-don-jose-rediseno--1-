"""
Servicio de Mesas - Lógica de negocio para gestión de mesas.
"""
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
DB_NAME = os.getenv("DATABASE_NAME", "reservas.db")


def get_all_mesas():
    """Retorna todas las mesas con su estado actual."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.id, m.capacidad, m.disponible,
               r.nombre_cliente, r.hora
        FROM mesas m
        LEFT JOIN reservas r ON m.id = r.mesa_asignada
            AND r.fecha = DATE('now', 'localtime')
        ORDER BY m.id
    """)
    mesas = []
    for row in cursor.fetchall():
        mesas.append({
            "id": row["id"],
            "capacidad": row["capacidad"],
            "disponible": bool(row["disponible"]),
            "reserva_cliente": row["nombre_cliente"],
            "reserva_hora": row["hora"],
        })
    conn.close()
    return mesas


def get_mesas_disponibles(cantidad_personas: int):
    """Retorna las mesas disponibles para la cantidad de personas indicada."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, capacidad FROM mesas
        WHERE disponible = 1 AND capacidad >= ?
        ORDER BY capacidad ASC
    """, (cantidad_personas,))
    mesas = [{"id": row["id"], "capacidad": row["capacidad"]} for row in cursor.fetchall()]
    conn.close()
    return mesas


def ocupar_mesa(mesa_id: int):
    """Marca una mesa como ocupada."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE mesas SET disponible = 0 WHERE id = ?", (mesa_id,))
    conn.commit()
    conn.close()


def liberar_mesa(mesa_id: int):
    """Marca una mesa como disponible."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE mesas SET disponible = 1 WHERE id = ?", (mesa_id,))
    conn.commit()
    conn.close()


def get_stats():
    """Retorna estadísticas generales de las mesas."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM mesas")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM mesas WHERE disponible = 1")
    libres = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM reservas WHERE fecha = DATE('now', 'localtime')")
    reservas_hoy = cursor.fetchone()[0]
    cursor.execute("SELECT COALESCE(SUM(cantidad_personas), 0) FROM reservas WHERE fecha = DATE('now', 'localtime')")
    comensales_hoy = cursor.fetchone()[0]
    conn.close()
    return {
        "total_mesas": total,
        "mesas_libres": libres,
        "mesas_ocupadas": total - libres,
        "reservas_hoy": reservas_hoy,
        "comensales_hoy": comensales_hoy,
    }
