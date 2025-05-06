import logging
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError


def init_mongo(uri):
    global client
    logging.info("Iniciando conexión a MongoDB...")
    #logging.info(f"DEBUG: mongo_uri = {uri}")
    client = MongoClient(uri)

def get_mongo_collection():
    db = client["baseDatosScrauron"]
    coleccion = db["noticias"]

    # Crear índice único para evitar duplicados de título+url
    try:
        coleccion.create_index([("url", 1), ("titulo", 1)], unique=True)
    except DuplicateKeyError as e:
        print(f"Índice no creado: ya existen duplicados. {e}")
    except Exception as e:
        print(f"Error al crear índice: {e}")

    return coleccion

def test_mongo_connection():
    logging.info("Test conexion a MongoDB...")
    try:
        client.admin.command('ping')
        logging.info("Conexión a MongoDB exitosa.")
    except Exception as e:
        logging.error(f"Error de conexión a MongoDB:\n{e}")
        raise e