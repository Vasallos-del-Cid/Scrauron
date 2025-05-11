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
    error = validar_url_fuente(data)
    if not error is None:
        logging.error(f" Fallo al guardar fuente: {error}")
        return jsonify(error), 409
    else:
        insert_result = get_collection("fuentes").insert_one(data)
        logging.info(f"Fuente guardada: {insert_result}")
        data["_id"] = str(insert_result.inserted_id)  # convertir el ObjectId a string
        return jsonify(data), 201  # 201 Created


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

    error = validar_url_fuente(data, fuente_id)
    if not error is None:
        logging.error(f" Fallo al guardar fuente: {error}")
        raise ValueError(f"❌ {error}")

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


def validar_url_fuente(fuente: Fuente, fuente_id: str = None):
    """
    Valida si la URL de la fuente es válida.
    :param fuente_id:
    :param fuente: objeto fuente a validar.
    :return: True si la URL es válida, False en caso contrario.
    """

    # Verifica la "url" neuva o a actualizar, si existe
    if "url" in fuente:
        url = fuente["url"]
        if not (url.startswith("http://") or url.startswith("https://")):
            return "URL no válida. Debe comenzar con http:// o https://"
        fuente_misma_url = get_collection("fuentes").find_one({"url": url})

        # Si existe una fuente con la misma URL, verifica si es ella misma (mismo id) o si esta repetida
        if fuente_misma_url:
            if "_id" in fuente or fuente_id:
                id = fuente_id if fuente_id else fuente["_id"]
                if str(fuente_misma_url["_id"]) == str(id):
                    return None
                else:
                    return "Ya existe una fuente con esa URL"
            else:
                return "Ya existe una fuente con esa URL"
    return None
