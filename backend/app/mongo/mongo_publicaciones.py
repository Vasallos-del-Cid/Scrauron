# mongo_publicaciones.py
import logging

# Este módulo gestiona la persistencia de objetos tipo "Publicacion" en MongoDB.
# Incluye operaciones CRUD y además estima automáticamente el tono emocional de
# la publicación utilizando un modelo LLM antes de guardarla.

from bson import ObjectId
from .mongo_utils import get_collection
from app.llm.llm_utils import estimar_tono_publicacion

# --------------------------------------------------
# Devuelve el objeto de colección Mongo para acceso directo (útil para spiders, por ejemplo)
def get_publicaciones():
    publicaciones = list(get_collection("publicaciones").find())
    for p in publicaciones:
        p["_id"] = str(p["_id"])  # Convierte ObjectId a string para serializar
    return publicaciones

# --------------------------------------------------
# Recupera una única publicación por su ID
def get_publicacion_by_id(pub_id):
    if not ObjectId.is_valid(pub_id):
        raise ValueError("ID no válido")
    pub = get_collection("publicaciones").find_one({"_id": ObjectId(pub_id)})
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
    existe = get_collection("publicaciones").find_one({
        "titulo": titulo,
        "url": url
    })

    if existe:
        logging.info(f"⚠️ Ya existe publicación con URL  : {url}")
        return None

    # Estima el tono usando LLM (basado en el título)
    # try:
    #     tono = estimar_tono_publicacion(publicacion)
    #     publicacion.tono = tono
    #     logging.info(f"🎯 Tono estimado: {tono}")
    # except Exception as e:
    #     logging.error(f"⚠️ Error al estimar el tono: {e}")
    #     publicacion.tono = None

    data = {
        "_id": ObjectId(publicacion._id),
        "titulo": publicacion.titulo,
        "url": publicacion.url,
        "fecha": publicacion.fecha,
        "fuente_id": ObjectId(publicacion.fuente_id),
    }
    data["url"] = url  # Asegura consistencia de formato de URL

    # Limpia el _id si viene vacío
    if "_id" in data and data["_id"] is None:
        del data["_id"]

    insert_result = get_collection("publicaciones").insert_one(data)
    return insert_result

# --------------------------------------------------
# Elimina una publicación por ID
def delete_publicacion(pub_id):
    if not ObjectId.is_valid(pub_id):
        raise ValueError("ID no válido")
    result = get_collection("publicaciones").delete_one({"_id": ObjectId(pub_id)})
    return result.deleted_count

# --------------------------------------------------
# Elimina todas las publicaciones de la colección
def delete_all_publicaciones():
    try:
        result = get_collection("publicaciones").delete_many({})
        logging.info(f" 🔴 Se eliminaron {result.deleted_count} publicaciones")
        return result.deleted_count
    except Exception as e:
        logging.error(f"❌ Error eliminando publicaciones:\n{e}")
        # raise e

# --------------------------------------------------
# Actualiza parcialmente una publicación por ID
def update_publicacion(pub_id, data):
    if not ObjectId.is_valid(pub_id):
        raise ValueError("ID no válido")

    # Evita modificar el _id directamente
    if "_id" in data:
        del data["_id"]

    result = get_collection("publicaciones").update_one({"_id": ObjectId(pub_id)}, {"$set": data})
    if result.matched_count == 0:
        return None

    # Devuelve la publicación actualizada
    updated = get_collection("publicaciones").find_one({"_id": ObjectId(pub_id)})
    updated["_id"] = str(updated["_id"])
    return updated
