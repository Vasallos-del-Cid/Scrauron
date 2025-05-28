import logging
import os
from flask_cors import CORS
from pathlib import Path
from dotenv import load_dotenv

ascii_banner = r"""
///////////////////////////---------------\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
   _____    ____   _____     ____    _    _   _____     ____    _   _ 
  / ____|  / ___\ |  __ \   / __ \  | |  | | |  __ \   / __ \  | \ | |
 | (___   | |     | |__) | | |__| | | |  | | | |__) | | |  | | |  \| |
  \___ \  | |     |  _  /  |  __  | | |  | | |  _  /  | |  | | | . ` |
  ____) | | |____ | | \ \  | |  | | | |__| | | | \ \  | |__| | | |\  |
 |_____/   \____/ |_|  \_\ |_|  |_|  \____/  |_|  \_\  \____/  |_| \_|
                                Powered by IA (Ingenieros y Artilleros)
\\\\\\\\\\\\\\\\\-----------------------------------///////////////////
"""

def load_config_from_args(env_arg=None):
    """
    Carga la configuración desde un archivo .env y establece el nivel de logging,
    ademas establece la variable FLASK_RELOAD para el modo de desarrollo en intellij.
    Configura CORS para la aplicación Flask a partir de la propiedad CORS_ORIGINS.
    :param env_arg: Parámetro de entorno para cargar la configuración local o por defecto.
    :return:
    """

    # Ruta absoluta al directorio del proyecto (donde esté .env)
    base_path = Path(__file__).resolve().parent.parent
    # Ruta base del .env con variables con secretos
    dotenv_base = base_path / ".env"
    load_dotenv(dotenv_base, override=False)
    # Cargar variables base no sensibles, sin sobrescribir las existentes
    dotenv_config = base_path / ".env.config"
    load_dotenv(dotenv_config, override=False)
    logging.info("⚙️ Cargando configuración base (.env.config)")

    # Cargar el archivo .env correspondiente según el entorno
    if env_arg == "local":
        logging.info("⚙️ Cargando configuración del entorno local (.env.local)")
        dotenv_local = base_path / ".env.local"
        load_dotenv(dotenv_local, override=True)  # Sobrescribe solo las que están en .env.local
    else:
        if env_arg is None:
            logging.info("⚙️ Cargando configuración del entorno por defecto (.env)")

    # Leer use_reloader desde variable de entorno, por defecto en local es true, se usa para debug en pycharm
    use_reloader = os.getenv("FLASK_RELOAD", "true").lower() == "true"

    return {
        "MONGO_URI": os.getenv("MONGO_URI"),
        "USE_RELOADER": use_reloader,
        "OPENAI_MODEL": os.getenv("OPENAI_MODEL", "gpt-4o"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "CORS_ORIGINS": os.getenv("CORS_ORIGINS", "").split(","),
        "DEBUG": os.getenv("DEBUG", "false").lower() == "true",
    }

def logqing_config():
    """
    Configura el logging para la aplicación.
    :return:
    """
    # Configuración del logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)-7s : %(module)-17s: %(message)s',
        force=True  # esto es clave para que sobrescriba configuraciones previas
    )
   
    logging.basicConfig(level=logging.INFO)

    # Silenciar logs 
    logging.getLogger("pymongo").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("_base_client").setLevel(logging.WARNING)
    logging.getLogger("_trace").setLevel(logging.WARNING)
    logging.getLogger("_client").setLevel(logging.WARNING)
    logging.getLogger("engine").setLevel(logging.ERROR)
    logging.getLogger("logstats").setLevel(logging.WARNING)
    logging.getLogger("retry").setLevel(logging.WARNING)
    logging.getLogger('scrapy').setLevel(logging.WARNING)


def cors_config(app):
    """
    Configura CORS para la aplicación Flask a partir de la propiedad CORS_ORIGINS.
    :return:
    """
    allowed_origins = os.getenv("CORS_ORIGINS", "").split(",")
    if not allowed_origins or allowed_origins == [""]:
        logging.error("⚙️ ❌ No se han configurado orígenes permitidos para CORS.")
        raise RuntimeError("CORS_ORIGINS no está configurado correctamente. Debe especificar al menos un origen permitido.")
    # Configuración de CORS
    CORS(app, resources={r"/*": {"origins": allowed_origins}})

def imprimir_mensaje_inicio(env_arg):
    print(ascii_banner)
    print(f"ℹ️ Iniciando app... \n⚙️ Perfil de arranque: {env_arg}\n")
