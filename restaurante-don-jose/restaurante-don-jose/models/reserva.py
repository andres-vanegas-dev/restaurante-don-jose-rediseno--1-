"""
Modelo Reserva - Representa una reserva del restaurante.
"""
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
DB_NAME = os.getenv("DATABASE_NAME", "reservas.db")


class Reserva:
    def __init__(self, id, nombre_cliente, cantidad_personas, fecha, hora, mesa_asignada):
        self.id = id
        self.nombre_cliente = nombre_cliente
        self.cantidad_personas = cantidad_personas
        self.fecha = fecha
        self.hora = hora
        self.mesa_asignada = mesa_asignada

    def to_dict(self):
        return {
            "id": self.id,
            "nombre_cliente": self.nombre_cliente,
            "cantidad_personas": self.cantidad_personas,
            "fecha": self.fecha,
            "hora": self.hora,
            "mesa_asignada": self.mesa_asignada,
        }

    @staticmethod
    def init_db():
        """Inicializa la tabla de reservas si no existe."""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reservas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_cliente TEXT NOT NULL,
                cantidad_personas INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                hora TEXT NOT NULL,
                mesa_asignada INTEGER NOT NULL,
                FOREIGN KEY (mesa_asignada) REFERENCES mesas(id)
            )
        """)
        conn.commit()
        conn.close()
