
import os
from flask import Flask, render_template
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Importar modelos para inicializar la base de datos
from models.mesa import Mesa
from models.reserva import Reserva

# Importar blueprints de rutas
from routes.reservas_routes import reservas_bp
from routes.mesas_routes import mesas_bp


def create_app():
    """Factory de la aplicación Flask."""
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "clave-secreta-default")

    # Inicializar base de datos SQLite
    Mesa.init_db()
    Reserva.init_db()

    # Registrar blueprints
    app.register_blueprint(reservas_bp)
    app.register_blueprint(mesas_bp)

    # Ruta principal — sirve el dashboard
    @app.route("/")
    def index():
        restaurant_name = os.getenv("RESTAURANT_NAME", "Restaurante de Don José")
        return render_template("index.html", restaurant_name=restaurant_name)

    return app


if __name__ == "__main__":
    app = create_app()
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    print(f"Restaurante de Don José — Servidor corriendo en http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)
