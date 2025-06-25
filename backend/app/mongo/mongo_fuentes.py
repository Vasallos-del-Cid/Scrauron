# mongo_fuentes.py

import logging
from flask import jsonify
from .mongo_utils import get_collection
from ..models.fuente import Fuente
from bson import ObjectId

# --------------------------------------------------
def get_fuentes():
    fuentes = list(get_collection("fuentes").find())
    for f in fuentes:
        f["_id"] = str(f["_id"])  
    return fuentes

def get_fuentes_dict():
    """
    Devuelve una lista de documentos fuente como diccionarios.
    """
    return list(get_collection("fuentes").find())

# --------------------------------------------------
def get_fuente_by_id(fuente_id: str):
    if not ObjectId.is_valid(fuente_id):
        return None
    raw = get_collection("fuentes").find_one({"_id": ObjectId(fuente_id)})
    if raw:
        raw["_id"] = str(raw["_id"])
        return Fuente.from_dict(raw)
    return None

# --------------------------------------------------
def create_fuente(fuente: Fuente):
    data = fuente.to_dict()

    error = validar_url_fuente(data)
    if error is not None:
        logging.error(f"❌ Fallo al guardar fuente: {error}")
        return jsonify(error), 409

    insert_result = get_collection("fuentes").insert_one(data)
    logging.info(f"✅ Fuente guardada: {insert_result}")
    data["_id"] = str(insert_result.inserted_id)
    return jsonify(data), 201

# --------------------------------------------------
def delete_fuente(fuente_id):
    if not ObjectId.is_valid(fuente_id):
        raise ValueError("ID no válido")

    result = get_collection("fuentes").delete_one({"_id": ObjectId(fuente_id)})
    return result.deleted_count

# --------------------------------------------------
def update_fuente(fuente_id, data):
    if not ObjectId.is_valid(fuente_id):
        raise ValueError("ID no válido")

    error = validar_url_fuente(data, fuente_id)
    if error is not None:
        logging.error(f"❌ Fallo al guardar fuente: {error}")
        raise ValueError(error)

    if "_id" in data:
        del data["_id"]

    # Solo incluimos campos válidos para evitar errores
    campos_validos = [
        "nombre", "url", "tipo", "activa", "fecha_alta",
        "etiqueta_titulo", "etiqueta_contenido", "url_imagen"  
    ]
    update_data = {key: data[key] for key in data if key in campos_validos}

    result = get_collection("fuentes").update_one(
        {"_id": ObjectId(fuente_id)},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        return None

    updated_fuente = get_collection("fuentes").find_one({"_id": ObjectId(fuente_id)})
    updated_fuente["_id"] = str(updated_fuente["_id"])
    return updated_fuente

# --------------------------------------------------
def validar_url_fuente(fuente: dict, fuente_id: str = None):
    """
    Valida si la URL es válida y no está duplicada.
    """
    if "url" in fuente:
        url = fuente["url"]
        if not (url.startswith("http://") or url.startswith("https://")):
            return "URL no válida. Debe comenzar con http:// o https://"

        fuente_misma_url = get_collection("fuentes").find_one({"url": url})

        if fuente_misma_url:
            if "_id" in fuente or fuente_id:
                id = fuente_id if fuente_id else fuente["_id"]
                if str(fuente_misma_url["_id"]) == str(id):
                    return None  
                else:
                    return {"error": "Ya existe una fuente con esa URL"}
            else:
                return {"error": "Ya existe una fuente con esa URL"}
    return None
