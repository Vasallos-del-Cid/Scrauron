from flask import Flask
import os
import logging

from app.config import cors_config, logqing_config, imprimir_mensaje_inicio
from app.service.jobs.scraping_job import iniciar_scheduler_en_segundo_plano
from app.mongo.mongo_utils import init_mongo
from app.routes.routes_fuentes import api_fuentes
from app.routes.routes_scraping import api_scraping
from app.routes.routes_areas import api_areas
from app.routes.routes_publicaciones import api_publicaciones
from app.routes.routes_conceptos import api_conceptos
from app.routes.routes_keywords import api_keywords
from app.config import load_config_from_args

def create_app(env_arg=None):
    """
    Crea la aplicación Flask y carga la configuración inicial.
    :param env_arg:
    :return:
    """

    # Evita ejecutar en proceso hijo del reloader
    if os.getenv("WERKZEUG_RUN_MAIN") != "true":
        imprimir_mensaje_inicio(env_arg)
    else:
        print("ℹ️ Reiniciando aplicación con HOT_RELOAD: 🔃 Recargando...")

    # Configurar el logging
    logqing_config()

    # Cargar configuración desde archivo .env
    try:
        configuracion = load_config_from_args(env_arg)
        logging.info("✅ Configuración cargada correctamente")

        # Inicializar conexión a Mongo
        init_mongo(configuracion["MONGO_URI"])

        # Iniciar el scheduler al levantar Flask
        if os.getenv("SCHEDULER_ENABLED", "false").lower() == "true":
            tiempo_schedule = os.getenv("SCRAPING_FREQUENCY", "default")
            logging.info(f"⚙️ Scheduler para el scraping 🕷️ ACTIVADO ✅ Reload cada: 🔃 {tiempo_schedule} Iniciando en segundo plano...")
            iniciar_scheduler_en_segundo_plano()
        else:
            logging.info("⚙️ Scheduler para el scraping 🕷️ DESACTIVADO ❌. Para activarlo, establece la variable de entorno SCHEDULER_ENABLED en True.")
        # Crear la aplicación Flask
        app = Flask(__name__)

        # Configuracion de CORS con la variable de entorno CORS_ORIGINS
        cors_config(app)

        # Registrar blueprints
        app.register_blueprint(api_fuentes, url_prefix='/api')
        app.register_blueprint(api_scraping, url_prefix='/api')
        app.register_blueprint(api_areas, url_prefix='/api')
        app.register_blueprint(api_publicaciones, url_prefix='/api')
        app.register_blueprint(api_conceptos, url_prefix='/api')
        app.register_blueprint(api_keywords, url_prefix='/api')

        # Puedes guardar config si la necesitas luego
        app.config.update(configuracion)
    except Exception as e:
        logging.error("❌ Error al cargar la configuración. Verifica el archivo .env o las variables de entorno.")
        raise e
    return app
