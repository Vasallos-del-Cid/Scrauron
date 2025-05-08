# mongo_publicaciones.py

# Este módulo gestiona la persistencia de objetos tipo "Publicacion" en MongoDB.
# Incluye operaciones CRUD y además estima automáticamente el tono emocional de
# la publicación utilizando un modelo LLM antes de guardarla.

import os
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
from ..models.publicacion import Publicacion
from datetime import datetime
from app.llm.llm_utils import estimar_tono_publicacion

# --------------------------------------------------
# Conexión a MongoDB y configuración de índice único
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["baseDatosScrauron"]
coleccion = db["publicaciones"]

# Evita duplicados usando un índice único en título y URL
coleccion.create_index(
    [("titulo", 1), ("url", 1)],
    unique=True,
    name="titulo_url_unique"
)

# --------------------------------------------------
# Devuelve el objeto de colección Mongo para acceso directo (útil para spiders, por ejemplo)
def get_mongo_collection():
    return coleccion

# --------------------------------------------------
# Recupera todas las publicaciones en formato lista
def get_publicaciones():
    publicaciones = list(coleccion.find())
    for p in publicaciones:
        p["_id"] = str(p["_id"])  # Convierte ObjectId a string para serializar
    return publicaciones

# --------------------------------------------------
# Recupera una única publicación por su ID
def get_publicacion_by_id(pub_id):
    if not ObjectId.is_valid(pub_id):
        raise ValueError("ID no válido")
    pub = coleccion.find_one({"_id": ObjectId(pub_id)})
    if pub:
        pub["_id"] = str(pub["_id"])
    return pub

# --------------------------------------------------
# Crea una nueva publicación en la base de datos
# También estima automáticamente el tono del contenido
def create_publicacion(publicacion):

    # Normalizar campos clave
    url = publicacion.url.strip().lower()
    titulo = publicacion.titulo.strip()

    # Comprobar si ya existe la publicación con mismo título y url
    existe = coleccion.find_one({
        "titulo": titulo,
        "url": url
    })

    if existe:
        print(f"⚠️ Ya existe publicación con URL: {url}")
        return None

    # Estima el tono usando LLM (basado en el título)
    try:
        tono = estimar_tono_publicacion(publicacion)
        publicacion.tono = tono
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🎯 Tono estimado: {tono}")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Error al estimar el tono: {e}")
        publicacion.tono = None

    data = publicacion.to_dict()
    data["url"] = url  # Asegura consistencia de formato de URL

    # Limpia el _id si viene vacío
    if "_id" in data and data["_id"] is None:
        del data["_id"]

    insert_result = coleccion.insert_one(data)
    return insert_result

# --------------------------------------------------
# Elimina una publicación por ID
def delete_publicacion(pub_id):
    if not ObjectId.is_valid(pub_id):
        raise ValueError("ID no válido")
    result = coleccion.delete_one({"_id": ObjectId(pub_id)})
    return result.deleted_count

# --------------------------------------------------
# Elimina todas las publicaciones de la colección
def delete_all_publicaciones():
    try:
        result = coleccion.delete_many({})
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔴 Se eliminaron {result.deleted_count} publicaciones")
        return result.deleted_count
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error eliminando publicaciones: {e}")
        raise

# --------------------------------------------------
# Actualiza parcialmente una publicación por ID
def update_publicacion(pub_id, data):
    if not ObjectId.is_valid(pub_id):
        raise ValueError("ID no válido")

    # Evita modificar el _id directamente
    if "_id" in data:
        del data["_id"]

    result = coleccion.update_one({"_id": ObjectId(pub_id)}, {"$set": data})
    if result.matched_count == 0:
        return None

    # Devuelve la publicación actualizada
    updated = coleccion.find_one({"_id": ObjectId(pub_id)})
    updated["_id"] = str(updated["_id"])
    return updated
