from pymongo import MongoClient
from bson import ObjectId

from .mongo_utils import get_collection

from datetime import datetime
from app.llm.llm_utils import estimar_tono_publicacion

# GET
def get_publicaciones():
    publicaciones = list(get_collection("publicaciones").find())
    for p in publicaciones:
        p["_id"] = str(p["_id"])
    return publicaciones


def get_publicacion_by_id(pub_id):
    if not ObjectId.is_valid(pub_id):
        raise ValueError("ID no válido")
    pub = get_collection("publicaciones").find_one({"_id": ObjectId(pub_id)})
    if pub:
        pub["_id"] = str(pub["_id"])
    return pub


# POST
def create_publicacion(publicacion):
    url = publicacion.url.strip().lower()
    existe = get_collection("publicaciones").find_one({"url": url})

    if existe:
        print(f"⚠️ Ya existe publicación con URL: {url}")
        return None

    # Estimar el tono antes de guardar
    try:
        tono = estimar_tono_publicacion(publicacion)
        publicacion.tono = tono
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🎯 Tono estimado: {tono}")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Error al estimar el tono: {e}")
        publicacion.tono = None

    data = publicacion.to_dict()

    # Normalizar URL
    data["url"] = url

    # Limpiar _id nulo
    if "_id" in data and data["_id"] is None:
        del data["_id"]

    insert_result = get_collection("publicaciones").insert_one(data)
    return insert_result


# DELETE
def delete_publicacion(pub_id):
    if not ObjectId.is_valid(pub_id):
        raise ValueError("ID no válido")
    result = get_collection("publicaciones").delete_one({"_id": ObjectId(pub_id)})
    return result.deleted_count


# DELETE ALL
def delete_all_publicaciones():
    try:
        result = get_collection("publicaciones").delete_many({})
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔴 Se eliminaron {result.deleted_count} publicaciones")
        return result.deleted_count
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error eliminando publicaciones: {e}")
        raise


# UPDATE
def update_publicacion(pub_id, data):
    if not ObjectId.is_valid(pub_id):
        raise ValueError("ID no válido")
    if "_id" in data:
        del data["_id"]
    result = get_collection("publicaciones").update_one({"_id": ObjectId(pub_id)}, {"$set": data})
    if result.matched_count == 0:
        return None
    updated = get_collection("publicaciones").find_one({"_id": ObjectId(pub_id)})
    updated["_id"] = str(updated["_id"])
    return updated
