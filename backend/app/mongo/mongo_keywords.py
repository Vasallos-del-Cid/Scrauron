# mongo_keywords.py

# Este módulo gestiona operaciones CRUD sobre documentos de tipo "Keyword" en MongoDB.
# Cada keyword representa un concepto clave asociado a noticias y temas de interés.

import logging
from flask import jsonify
from bson import ObjectId
from .mongo_utils import get_collection
from ..models.keyword import Keyword

# --------------------------------------------------
# Recupera todas las keywords almacenadas
def get_keywords():
    keywords = list(get_collection("keywords").find())
    for kw in keywords:
        kw["_id"] = str(kw["_id"])
    return keywords

# --------------------------------------------------
# Recupera una keyword por su ID
def get_keyword_by_id(keyword_id: str):
    if not ObjectId.is_valid(keyword_id):
        return None
    raw = get_collection("keywords").find_one({"_id": ObjectId(keyword_id)})
    if raw:
        raw["_id"] = str(raw["_id"])
        return Keyword.from_dict(raw)
    return None

# --------------------------------------------------
# Recupera una keyword por su nombre exacto (case-sensitive)
def get_keyword_by_nombre(nombre: str):
    raw = get_collection("keywords").find_one({"nombre": nombre})
    if raw:
        raw["_id"] = str(raw["_id"])
        return Keyword.from_dict(raw)
    return None

# --------------------------------------------------
# Crea una nueva keyword si no existe una con el mismo nombre
# mongo_keywords.py
def create_keyword(keyword):
    data = keyword.to_dict()
    existing = get_collection("keywords").find_one({"nombre": data["nombre"]})

    if existing:
        existing["_id"] = str(existing["_id"])
        logging.info(f"Keyword ya existente: {existing['nombre']} — no se crea de nuevo.")
        return existing, 200        # ← Dict + status, SIN jsonify
    else:
        insert_id = get_collection("keywords").insert_one(data).inserted_id
        logging.info(f"Keyword creada: {data['nombre']}")
        data["_id"] = str(insert_id)
        return data, 201            # ← Dict + status



# --------------------------------------------------
# Elimina una keyword por su ID
def delete_keyword(keyword_id):
    if not ObjectId.is_valid(keyword_id):
        raise ValueError("ID no válido")

    result = get_collection("keywords").delete_one({"_id": ObjectId(keyword_id)})
    return result.deleted_count

# --------------------------------------------------
# Actualiza parcialmente una keyword existente
def update_keyword(keyword_id, data):
    if not ObjectId.is_valid(keyword_id):
        raise ValueError("ID no válido")

    if "_id" in data:
        del data["_id"]

    result = get_collection("keywords").update_one(
        {"_id": ObjectId(keyword_id)},
        {"$set": data}
    )

    if result.matched_count == 0:
        return None

    updated_keyword = get_collection("keywords").find_one({"_id": ObjectId(keyword_id)})
    updated_keyword["_id"] = str(updated_keyword["_id"])
    return updated_keyword

# --------------------------------------------------
# Devuelve las keywords de un concepto

def get_keywords_by_concepto_id(concepto_id):
    # Asegura que el ID sea un ObjectId
    if not isinstance(concepto_id, ObjectId):
        concepto_id = ObjectId(concepto_id)

    concepto = get_collection('conceptos_interes').find_one({"_id": concepto_id})
    if not concepto:
        return []

    keywords_oids = concepto.get('keywords_ids', [])
    keywords_dict = []

    for keyword_oid in keywords_oids:
        keyword = get_collection('keywords').find_one({"_id": keyword_oid})
        if keyword:
            # Serializa campos ObjectId a string para evitar errores
            keyword["_id"] = str(keyword["_id"])
            keywords_dict.append(keyword)

    return keywords_dict


def get_keywords_by_publicacion(publicacion_id):
    try:
        # Asegura que sea un ObjectId válido
        if not ObjectId.is_valid(publicacion_id):
            raise ValueError("ID de publicación no válido")

        pub_oid = ObjectId(publicacion_id)
        publicacion = get_collection("publicaciones").find_one({"_id": pub_oid})
        if not publicacion:
            return []

        keyword_ids = publicacion.get("keywords_relacionadas_ids", [])
        if not keyword_ids:
            return []

        # Buscar todas las keywords en una sola consulta
        keywords = get_collection("keywords").find({"_id": {"$in": keyword_ids}})
        result = []
        for kw in keywords:
            kw["_id"] = str(kw["_id"])  # Convierte ObjectId a string para JSON
            result.append(kw)

        return result

    except Exception as e:
        # Devuelve el error para el manejo adecuado
        raise RuntimeError(f"Error al obtener keywords de la publicación: {e}")