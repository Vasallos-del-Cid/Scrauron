import logging
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError


def init_mongo(uri):
    global client
    logging.info("Iniciando conexión a MongoDB...")
    #logging.info(f"DEBUG: mongo_uri = {uri}")
    client = MongoClient(uri)


def test_mongo_connection():
    logging.info("Test conexion a MongoDB...")
    try:
        client.admin.command('ping')
        logging.info("Conexión a MongoDB exitosa.")
    except Exception as e:
        logging.error(f"Error de conexión a MongoDB:\n{e}")
        raise e