# mongo_fuentes.py

# Este módulo gestiona operaciones CRUD sobre documentos de tipo "Fuente" en MongoDB.
# Cada fuente representa un sitio web o dominio monitorizado para extraer noticias.
import logging

from flask import jsonify
from .mongo_utils import get_collection
from ..models.fuente import Fuente
from bson import ObjectId

def get_fuentes():
    fuentes = list(get_collection("fuentes").find())
    for f in fuentes:
        f["_id"] = str(f["_id"])  # Convertir ObjectId para que sea serializable en JSON
    return fuentes

# --------------------------------------------------
# Recupera una fuente concreta por su ID
def get_fuente_by_id(fuente_id: str):
    if not ObjectId.is_valid(fuente_id):
        return None
    raw = get_collection("fuentes").find_one({"_id": ObjectId(fuente_id)})
    if raw:
        raw["_id"] = str(raw["_id"])  # Asegura compatibilidad con from_dict
        return Fuente.from_dict(raw)
    return None

# --------------------------------------------------
# Crea una nueva fuente si no existe una con la misma URL
def create_fuente(fuente):
    data = fuente.to_dict()

    # Verificar si ya existe una fuente con la misma URL
    if get_collection("fuentes").find_one({"url": data["url"]}):
        error = {"error": "Ya existe una fuente con esa URL"}
        logging.error(f" Fallo al guardar fuente: {error}")
        return jsonify(error), 409
    else:
        insert_result = get_collection("fuentes").insert_one(data)
        logging.info(f"Fuente guardada: {insert_result}")
        data["_id"] = str(insert_result.inserted_id)  # convertir el ObjectId a string
        return jsonify(data), 201 # 201 Created

# --------------------------------------------------
# Elimina una fuente de la colección por su ID
def delete_fuente(fuente_id):
    if not ObjectId.is_valid(fuente_id):
        raise ValueError("ID no válido")

    result = get_collection("fuentes").delete_one({"_id": ObjectId(fuente_id)})
    return result.deleted_count

# --------------------------------------------------
# Actualiza parcialmente una fuente existente
def update_fuente(fuente_id, data):
    if not ObjectId.is_valid(fuente_id):
        raise ValueError("ID no válido")

    # Previene la sobreescritura del _id
    if "_id" in data:
        del data["_id"]

    result = get_collection("fuentes").update_one(
        {"_id": ObjectId(fuente_id)},
        {"$set": data}
    )

    if result.matched_count == 0:
        return None

    # Recuperar el documento actualizado
    updated_fuente = get_collection("fuentes").find_one({"_id": ObjectId(fuente_id)})
    updated_fuente["_id"] = str(updated_fuente["_id"])
    return updated_fuente
