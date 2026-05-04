"""
Rutas HTTP para la gestión de mesas.
"""
from flask import Blueprint, jsonify, request
from services import mesas_service

mesas_bp = Blueprint("mesas", __name__, url_prefix="/mesas")


@mesas_bp.route("/", methods=["GET"])
def get_mesas():
    """GET /mesas — Lista todas las mesas con su estado."""
    mesas = mesas_service.get_all_mesas()
    return jsonify(mesas), 200


@mesas_bp.route("/disponibles", methods=["GET"])
def get_disponibles():
    """GET /mesas/disponibles?personas=N — Mesas disponibles para N personas."""
    personas = request.args.get("personas", 1, type=int)
    mesas = mesas_service.get_mesas_disponibles(personas)
    return jsonify(mesas), 200


@mesas_bp.route("/stats", methods=["GET"])
def get_stats():
    """GET /mesas/stats — Estadísticas generales del restaurante."""
    stats = mesas_service.get_stats()
    return jsonify(stats), 200
