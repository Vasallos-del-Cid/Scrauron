import logging
import os
from dotenv import load_dotenv


def load_config_from_args(env_arg=None):
    """
    Carga la configuración desde un archivo .env y establece el nivel de logging,
    ademas establece la variable FLASK_RELOAD para el modo de desarrollo en intellij.
    :param env_arg:
    :return:
    """

    # Configuración del logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)-5s : %(module)-15s: %(message)s',
        force=True  # esto es clave para que sobrescriba configuraciones previas
    )

    # Cargar el archivo .env correspondiente según el entorno
    # Ruta base del .env
    dotenv_base = "../.env"
    load_dotenv(dotenv_base, override=False)  # Cargar variables base, sin sobrescribir las existentes

    if env_arg == "local":
        logging.info("ℹ️ Cargando configuración local (.env.local)")
        dotenv_local = "../.env.local"
        load_dotenv(dotenv_local, override=True)  # Sobrescribe solo las que están en .env.local
    else:
        if env_arg is None:
            logging.info("ℹ️ Cargando configuración por defecto (.env)")

    # Leer use_reloader desde variable de entorno, por defecto en local es true, se usa para debug en pycharm
    use_reloader = os.getenv("FLASK_RELOAD", "true").lower() == "true"

    return {
        "MONGO_URI": os.getenv("MONGO_URI"),
        "USE_RELOADER": use_reloader
    }
