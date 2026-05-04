"""
Rutas HTTP para la gestión de reservas (CRUD completo).
"""
from flask import Blueprint, jsonify, request
from services import reservas_service
from utils.validaciones import validar_reserva_completa

reservas_bp = Blueprint("reservas", __name__, url_prefix="/reservas")


@reservas_bp.route("/", methods=["GET"])
def get_reservas():
    """GET /reservas — Lista todas las reservas."""
    query = request.args.get("q", "").strip()
    if query:
        reservas = reservas_service.buscar_reservas(query)
    else:
        reservas = reservas_service.get_all_reservas()
    return jsonify(reservas), 200


@reservas_bp.route("/<int:reserva_id>", methods=["GET"])
def get_reserva(reserva_id):
    """GET /reservas/<id> — Obtiene una reserva por ID."""
    reserva = reservas_service.get_reserva_by_id(reserva_id)
    if not reserva:
        return jsonify({"error": "Reserva no encontrada."}), 404
    return jsonify(reserva), 200


@reservas_bp.route("/", methods=["POST"])
def crear_reserva():
    """POST /reservas — Crea una nueva reserva."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Se requiere un cuerpo JSON."}), 400

    nombre = data.get("nombre_cliente", "")
    personas = data.get("cantidad_personas", 0)
    fecha = data.get("fecha", "")
    hora = data.get("hora", "")

    ok, msg = validar_reserva_completa(nombre, personas, fecha, hora)
    if not ok:
        return jsonify({"error": msg}), 422

    reserva, error = reservas_service.crear_reserva(nombre, int(personas), fecha, hora)
    if error:
        return jsonify({"error": error}), 409

    return jsonify(reserva), 201


@reservas_bp.route("/<int:reserva_id>", methods=["PUT"])
def modificar_reserva(reserva_id):
    """PUT /reservas/<id> — Modifica una reserva existente."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Se requiere un cuerpo JSON."}), 400

    nombre = data.get("nombre_cliente", "")
    personas = data.get("cantidad_personas", 0)
    fecha = data.get("fecha", "")
    hora = data.get("hora", "")

    ok, msg = validar_reserva_completa(nombre, personas, fecha, hora)
    if not ok:
        return jsonify({"error": msg}), 422

    reserva, error = reservas_service.modificar_reserva(reserva_id, nombre, int(personas), fecha, hora)
    if error:
        return jsonify({"error": error}), 409 if "disponibles" in error else 404

    return jsonify(reserva), 200


@reservas_bp.route("/<int:reserva_id>", methods=["DELETE"])
def eliminar_reserva(reserva_id):
    """DELETE /reservas/<id> — Elimina una reserva y libera la mesa."""
    ok, error = reservas_service.eliminar_reserva(reserva_id)
    if not ok:
        return jsonify({"error": error}), 404
    return jsonify({"mensaje": "Reserva eliminada correctamente."}), 200
