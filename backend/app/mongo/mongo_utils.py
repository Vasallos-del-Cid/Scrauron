import os
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from dotenv import load_dotenv

# Cargar variables del entorno desde .env
load_dotenv()

def get_mongo_collection():
    mongo_uri = os.getenv("MONGO_URI")
    client = MongoClient(mongo_uri)
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
