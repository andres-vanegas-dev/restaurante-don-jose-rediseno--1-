"""
Modelo Mesa - Representa una mesa del restaurante.
"""
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
DB_NAME = os.getenv("DATABASE_NAME", "reservas.db")


class Mesa:
    def __init__(self, id, capacidad, disponible=True):
        self.id = id
        self.capacidad = capacidad
        self.disponible = disponible

    def to_dict(self):
        return {
            "id": self.id,
            "capacidad": self.capacidad,
            "disponible": self.disponible,
        }

    @staticmethod
    def init_db():
        """Inicializa la tabla de mesas si no existe y carga las mesas por defecto."""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mesas (
                id INTEGER PRIMARY KEY,
                capacidad INTEGER NOT NULL,
                disponible INTEGER NOT NULL DEFAULT 1
            )
        """)
        # Insertar mesas por defecto si la tabla está vacía
        cursor.execute("SELECT COUNT(*) FROM mesas")
        if cursor.fetchone()[0] == 0:
            mesas_default = [
                (1, 2), (2, 3), (3, 2), (4, 4),
                (5, 4), (6, 6), (7, 6), (8, 8)
            ]
            cursor.executemany(
                "INSERT INTO mesas (id, capacidad, disponible) VALUES (?, ?, 1)",
                mesas_default
            )
        conn.commit()
        conn.close()
