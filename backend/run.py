import sys
from flask import Flask
import logging
from app.routes.routes_fuentes import api_fuentes
from app.routes.routes_scraping import api_scraping
from app.routes.routes_areas import api_areas
from app.routes.routes_publicaciones import api_publicaciones
from app.routes.routes_conceptos import api_conceptos
<<<<<<< HEAD
from app.jobs.scraping_job import iniciar_scheduler_en_segundo_plano
=======
from app.mongo.mongo_utils import init_mongo, test_mongo_connection
from config import load_config_from_args

# Leer parámetro de entorno si se pasa
env_arg = None
if len(sys.argv) >= 3 and sys.argv[1] == "--env":
    env_arg = sys.argv[2]

config = load_config_from_args(env_arg)
logging.info("Configuración cargada")

# Inicializar conexión Mongo antes de arrancar la app
init_mongo(config["MONGO_URI"])
>>>>>>> af3d63087dfff132ec7a392268489740c65882bd


app = Flask(__name__)

# Iniciar el scheduler al levantar Flask
# iniciar_scheduler_en_segundo_plano()

# Todas las rutas dentro del blueprint tendrán prefijo /api
app.register_blueprint(api_fuentes, url_prefix='/api')
app.register_blueprint(api_scraping, url_prefix='/api')
app.register_blueprint(api_areas, url_prefix='/api')
app.register_blueprint(api_publicaciones, url_prefix='/api')
app.register_blueprint(api_conceptos, url_prefix='/api')

if __name__ == '__main__':
<<<<<<< HEAD
    app.run(debug=True, use_reloader=False)

=======
    
    # Probar la conexión a la base de datos al iniciar
    test_mongo_connection()
    app.run(debug=True)
>>>>>>> af3d63087dfff132ec7a392268489740c65882bd
