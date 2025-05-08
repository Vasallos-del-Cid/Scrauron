import logging
import os
from pathlib import Path

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

    # Ruta absoluta al directorio del proyecto (donde esté .env)
    base_path = Path(__file__).resolve().parent.parent
    # Ruta base del .env con variables con secretos
    dotenv_base = base_path / ".env"
    load_dotenv(dotenv_base, override=False)
    # Cargar variables base no sensibles, sin sobrescribir las existentes
    dotenv_config = base_path / ".env.config"
    load_dotenv(dotenv_config, override=False)

    # Cargar el archivo .env correspondiente según el entorno
    if env_arg == "local":
        logging.info("ℹ️ Cargando configuración local (.env.local)")
        dotenv_local = base_path / ".env.local"
        load_dotenv(dotenv_local, override=True)  # Sobrescribe solo las que están en .env.local
    else:
        if env_arg is None:
            logging.info("ℹ️ Cargando configuración por defecto (.env)")

    # Leer use_reloader desde variable de entorno, por defecto en local es true, se usa para debug en pycharm
    use_reloader = os.getenv("FLASK_RELOAD", "true").lower() == "true"

    return {
        "MONGO_URI": os.getenv("MONGO_URI"),
        "USE_RELOADER": use_reloader,
        "OPENAI_MODEL": os.getenv("OPENAI_MODEL", "gpt-4"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")
    }
