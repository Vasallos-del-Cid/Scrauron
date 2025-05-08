import logging
import os
from dotenv import load_dotenv


def load_config_from_args(env_arg=None):
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)-5s : %(module)-15s: %(message)s',
        force = True  # esto es clave para que sobrescriba configuraciones previas
    )
    if env_arg == "local":
        logging.info("ℹ️ Cargando configuración..." + str(env_arg))
        dotenv_path = "../.env.local"
    else:
        if env_arg is None:
            logging.info("ℹ️ Cargando configuración por defecto...")
        dotenv_path = "../.env"
    load_dotenv(dotenv_path, override=True)

    # Leer use_reloader desde variable de entorno, por defecto en local es true, se usa para debug en pycharm
    use_reloader = os.getenv("FLASK_RELOAD", "true").lower() == "true"

    return {
        "MONGO_URI": os.getenv("MONGO_URI"),
        "USE_RELOADER": use_reloader
    }
