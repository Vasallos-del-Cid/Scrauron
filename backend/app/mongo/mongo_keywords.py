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
def create_keyword(keyword):
    data = keyword.to_dict()

    # Verifica si ya existe una keyword con el mismo nombre
    existing = get_collection("keywords").find_one({"nombre": data["nombre"]})
    if existing:
        existing["_id"] = str(existing["_id"])
        logging.info(f"Keyword ya existente: {existing['nombre']} — no se crea de nuevo.")
        return jsonify(existing), 200
    else:
        insert_result = get_collection("keywords").insert_one(data)
        logging.info(f"Keyword creada: {data['nombre']}")
        data["_id"] = str(insert_result.inserted_id)
        return jsonify(data), 201


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
def get_keywords_id_by_concepto_id(concepto_id):
    concepto = get_collection('conceptos_interes').find_one({"_id": concepto_id})
    keywords_oids = concepto.get('keywords_ids', [])
    keywords_ids = []
    for keyword_oid in keywords_oids:
        keywords_ids.append(str(keyword_oid))
    return keywords_ids