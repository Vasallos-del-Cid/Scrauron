import logging
import os
from dotenv import load_dotenv
from pymongo import MongoClient

def get_db():
    if db is None:
        raise Exception("❌ MongoDB no ha sido inicializado. Llama a init_mongo() primero.")
    return db


def get_collection(nombre):
    """
    Devuelve la colección de MongoDB especificada por nombre.
    :param nombre:
    :return: la colección para hacer consultas.
    """
    return get_db()[nombre]


def init_mongo(uri=None):
    """
    Inicializa la conexión a MongoDB y crea la base de datos.
    :param uri: la cadeba de conexión a MongoDB. Si no se proporciona, se carga desde el archivo .env.
    """
    global client, db

    load_dotenv()
    mongo_uri = uri or os.getenv("MONGO_URI")

    # COMENTARIO descomentar para ver la URI de conexión
    # logging.info(f"📡 Conectando a MongoDB: {mongo_uri}")
    client = MongoClient(mongo_uri)

    # Comprobación de conexión
    test_mongo_connection()

    db = client["baseDatosScrauron"]

    # Crear índices u otras configuraciones
    config_mongo_index_publicaciones(db["publicaciones"])
    config_mongo_index_keywords(db["keywords"])

def test_mongo_connection():
    logging.info("Test conexion a MongoDB...")
    try:
        client.admin.command('ping')
        logging.info("✅ Conexión a MongoDB exitosa.")
    except Exception as e:
        logging.error(f"❌ Error de conexión a MongoDB:\n{e}")
        raise e


def config_mongo_index_publicaciones(coleccion):
    try:
        # Indice único combinación de título u url. Evita duplicados en BBDD.
        coleccion.create_index(
            [("titulo", 1), ("url", 1)],
            unique=True,
            name="titulo_url_unique"
        )

    except Exception as e:
        logging.warning(f"❌ Error al crear índice de: {coleccion}\n {e}")

def config_mongo_index_keywords(coleccion):
    try:
        # Indice único combinación de título u url. Evita duplicados en BBDD.
        coleccion.create_index(
            "nombre",
            unique=True,
            name="nombre_keyword_unique"
        )

    except Exception as e:
        logging.warning(f"❌ Error al crear índice de: {coleccion}\n {e}")
