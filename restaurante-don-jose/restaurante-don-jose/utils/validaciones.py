"""
Funciones de validación reutilizables para el sistema de reservas.
"""
import re
from datetime import datetime


def validar_nombre(nombre: str) -> tuple[bool, str]:
    """Valida que el nombre del cliente sea válido."""
    if not nombre or not nombre.strip():
        return False, "El nombre del cliente no puede estar vacío."
    if len(nombre.strip()) < 2:
        return False, "El nombre debe tener al menos 2 caracteres."
    if len(nombre.strip()) > 100:
        return False, "El nombre no puede superar los 100 caracteres."
    if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s'-]+$", nombre.strip()):
        return False, "El nombre solo puede contener letras y espacios."
    return True, ""


def validar_cantidad_personas(cantidad) -> tuple[bool, str]:
    """Valida que la cantidad de personas sea un número válido."""
    try:
        cantidad = int(cantidad)
    except (ValueError, TypeError):
        return False, "La cantidad de personas debe ser un número entero."
    if cantidad < 1:
        return False, "Debe haber al menos 1 persona en la reserva."
    if cantidad > 20:
        return False, "No se pueden hacer reservas para más de 20 personas."
    return True, ""


def validar_fecha(fecha: str) -> tuple[bool, str]:
    """Valida que la fecha tenga formato YYYY-MM-DD y sea actual o futura."""
    try:
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d").date()
    except ValueError:
        return False, "La fecha debe tener el formato YYYY-MM-DD."
    if fecha_dt < datetime.now().date():
        return False, "No se pueden registrar reservas en fechas pasadas."
    return True, ""


def validar_hora(hora: str) -> tuple[bool, str]:
    """Valida que la hora tenga formato HH:MM."""
    try:
        datetime.strptime(hora, "%H:%M")
    except ValueError:
        return False, "La hora debe tener el formato HH:MM."
    return True, ""


def validar_reserva_completa(nombre, cantidad_personas, fecha, hora) -> tuple[bool, str]:
    """Ejecuta todas las validaciones necesarias para una reserva."""
    for validar, valor in [
        (validar_nombre, nombre),
        (validar_cantidad_personas, cantidad_personas),
        (validar_fecha, fecha),
        (validar_hora, hora),
    ]:
        ok, msg = validar(valor)
        if not ok:
            return False, msg
    return True, ""
