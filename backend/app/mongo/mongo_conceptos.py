# mongo_conceptos.py
# Este módulo gestiona el acceso, creación y actualización de los documentos
# del tipo "ConceptoInteres" en MongoDB. Además, integra funciones de LLM
# para generar descripciones y keywords de forma automática.

import logging
from datetime import datetime
from bson import ObjectId

from .mongo_utils import get_collection
from ..models.concepto_interes import ConceptoInteres
from ..llm.llm_utils import generar_descripcion_concepto, generar_keywords_descriptivos


# --------------------------------------------------------------------
# Recupera todos los conceptos de la colección y convierte ObjectId a string
def get_conceptos():
    conceptos_raw = list(get_collection("conceptos_interes").find())
    conceptos = []
    for c in conceptos_raw:
        c["_id"] = str(c["_id"])
        c["publicaciones_relacionadas_ids"] = [str(pid) for pid in c.get("publicaciones_relacionadas_ids", [])]
        conceptos.append(c)
    return conceptos


# --------------------------------------------------------------------
# Recupera los conceptos tal y como están en Mongo (sin transformar a clase)
def get_conceptos_dict():
    conceptos_raw = list(get_collection("conceptos_interes").find())
    conceptos = []
    for c in conceptos_raw:
        c.setdefault("publicaciones_relacionadas_ids", [])
        if not isinstance(c["publicaciones_relacionadas_ids"], list):
            c["publicaciones_relacionadas_ids"] = []
        conceptos.append(c)
    return conceptos


# --------------------------------------------------------------------
# Busca un concepto por su ID y lo convierte a instancia de clase
def get_concepto_by_id(concepto_id: str):
    if not ObjectId.is_valid(concepto_id):
        return None
    raw = get_collection("conceptos_interes").find_one({"_id": ObjectId(concepto_id)})
    if raw:
        return ConceptoInteres.from_dict(raw)
    return None


# --------------------------------------------------------------------
# Devuelve los conceptos que tengan IDs en la lista dada
def get_conceptos_ids(ids):
    return list(get_collection("conceptos_interes").find({"_id": {"$in": ids}}))


# --------------------------------------------------------------------
# Crea un nuevo concepto en MongoDB
def create_concepto(concepto):
    data = concepto.to_dict()
    if "_id" in data and data["_id"] is None:
        del data["_id"]
    insert_result = get_collection("conceptos_interes").insert_one(data)
    return insert_result


# --------------------------------------------------------------------
# Elimina un concepto por su ID
def delete_concepto(concepto_id):
    if not ObjectId.is_valid(concepto_id):
        raise ValueError("ID no válido")
    result = get_collection("conceptos_interes").delete_one({"_id": ObjectId(concepto_id)})
    return result.deleted_count


# --------------------------------------------------------------------
# Actualiza un concepto a partir de su instancia
def update_concepto(concepto: ConceptoInteres):
    data = concepto.to_dict()
    concepto_id = data.pop("_id", None)

    if not concepto_id:
        raise ValueError("El concepto no tiene _id. No se puede actualizar.")

    try:
        result = get_collection("conceptos_interes").update_one(
            {"_id": ObjectId(concepto_id)},
            {"$set": data}
        )
        if result.matched_count == 0:
            logging.warning(f"⚠️ No se encontró el concepto con _id: {concepto_id}")
        else:
            logging.info(f"✅ Concepto actualizado correctamente: {concepto.nombre}")
    except Exception as e:
        logging.error(f"❌ Error actualizando el concepto: {e}")


# --------------------------------------------------------------------
# Actualiza un concepto a partir de un diccionario
def update_concepto_dict(concepto_dict: dict):
    concepto_id = concepto_dict.get("_id")
    if not concepto_id:
        raise ValueError("El concepto no tiene _id. No se puede actualizar.")

    try:
        result = get_collection("conceptos_interes").update_one(
            {"_id": ObjectId(concepto_id)},
            {"$set": concepto_dict}
        )
        if result.matched_count == 0:
            logging.warning(f"⚠️ No se encontró el concepto con _id: {concepto_id}")
        else:
            logging.info(f"✅ Publicación relacionada con concepto: {concepto_dict.get('nombre')} -> actualizado correctamente.")
    except Exception as e:
        logging.error(f"❌ Error actualizando el concepto: {e}")


# --------------------------------------------------------------------
# Usa el modelo LLM para generar una descripción automática del concepto
def add_descripcion_llm(concepto: ConceptoInteres):
    descripcion = generar_descripcion_concepto(concepto.nombre)
    concepto.descripcion = descripcion
    update_concepto(concepto)
    return descripcion


# --------------------------------------------------------------------
# Usa el modelo LLM para generar keywords representativas de un concepto
def add_keywords_llm(concepto: ConceptoInteres):
    keywords = generar_keywords_descriptivos(concepto.descripcion)
    concepto.keywords = keywords
    update_concepto(concepto)
    return keywords
