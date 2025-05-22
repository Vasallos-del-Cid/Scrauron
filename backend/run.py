import sys
from app import create_app

# Leer parámetro de entorno si se pasa
env_arg = None

if len(sys.argv) >= 3 and sys.argv[1] == "--env":
    env_arg = sys.argv[2]

# Crear app y cargar configuracion inicial en __init__.py
app = create_app(env_arg)

# Inicializar la app
if __name__ == '__main__':

     app.run(debug=app.config["DEBUG"], use_reloader=app.config["USE_RELOADER"])