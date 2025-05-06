import logging
import os
from dotenv import load_dotenv

def load_config_from_args(env_arg=None):
    logging.basicConfig(level=logging.INFO)
    if env_arg == "local":
        logging.info("Cargando configuración..." + str(env_arg))
        dotenv_path = ".env.local"
    else:
        if env_arg is None:
            logging.info("Cargando configuración por defecto...")
        dotenv_path = ".env"
    load_dotenv(dotenv_path, override=True)
    return {"MONGO_URI": os.getenv("MONGO_URI")}
