# mongo_conceptos.py
# Este módulo gestiona el acceso, creación y actualización de los documentos
# del tipo "ConceptoInteres" en MongoDB. Además, integra funciones de LLM
# para generar descripciones y keywords de forma automática.

from flask import jsonify
import logging
from datetime import datetime
from bson import ObjectId

from .mongo_utils import get_collection
from ..models.concepto_interes import ConceptoInteres
from ..service.llm.llm_utils import generar_descripcion_concepto, generar_keywords_descriptivos


# --------------------------------------------------------------------
def get_conceptos():
    try:
        conceptos_raw = get_collection("conceptos_interes").find()
        conceptos = []
        for c in conceptos_raw:
            c["_id"] = str(c["_id"])
            c["keywords_ids"] = [str(kid) for kid in c.get("keywords_ids", [])]
            c["publicaciones_relacionadas_ids"] = [str(pid) for pid in c.get("publicaciones_relacionadas_ids", [])]
            conceptos.append(c)
        return conceptos  # <-- devuelves los datos crudos
    except Exception as e:
        logging.error(f"Error al recuperar conceptos: {e}")
        return []


# --------------------------------------------------------------------
def get_conceptos_dict():
    try:
        conceptos_raw = list(get_collection("conceptos_interes").find())
        conceptos = []
        for c in conceptos_raw:
            c.setdefault("publicaciones_relacionadas_ids", [])
            if not isinstance(c["publicaciones_relacionadas_ids"], list):
                c["publicaciones_relacionadas_ids"] = []
            conceptos.append(c)
        return conceptos
    except Exception as e:
        logging.error(f"Error al recuperar conceptos en bruto: {e}")
        return []


# --------------------------------------------------------------------
def get_concepto_by_id(concepto_id: str):
    if not ObjectId.is_valid(concepto_id):
        logging.warning(f"ID no válido: {concepto_id}")
        return None
    try:
        raw = get_collection("conceptos_interes").find_one({"_id": ObjectId(concepto_id)})
        return ConceptoInteres.from_dict(raw) if raw else None
    except Exception as e:
        logging.error(f"Error al buscar concepto por ID: {e}")
        return None


# --------------------------------------------------------------------
def get_conceptos_ids(ids):
    try:
        return list(get_collection("conceptos_interes").find({"_id": {"$in": ids}}))
    except Exception as e:
        logging.error(f"Error al obtener conceptos por IDs: {e}")
        return []


# --------------------------------------------------------------------
def create_concepto(concepto):
    try:
        data = concepto.to_dict()
        if "_id" in data and data["_id"] is None:
            del data["_id"]
        insert_result = get_collection("conceptos_interes").insert_one(data)
        logging.info(f"✅ Concepto creado: {concepto.nombre}")
        return insert_result
    except Exception as e:
        logging.error(f"❌ Error creando concepto: {e}")
        return None


# --------------------------------------------------------------------
def delete_concepto(concepto_id):
    if not ObjectId.is_valid(concepto_id):
        raise ValueError("ID no válido")
    try:
        result = get_collection("conceptos_interes").delete_one({"_id": ObjectId(concepto_id)})
        return result.deleted_count
    except Exception as e:
        logging.error(f"Error al eliminar concepto: {e}")
        return 0


# --------------------------------------------------------------------
def update_concepto(concepto: ConceptoInteres):
    concepto_id = concepto._id
    if not concepto_id:
        raise ValueError("El concepto no tiene _id. No se puede actualizar.")

    # Construir manualmente el diccionario manteniendo los ObjectId
    data = {
        "_id": ObjectId(concepto._id),
        "nombre": concepto.nombre,
        "descripcion": concepto.descripcion,
        "keywords_ids": concepto.keywords_ids,
        "publicaciones_relacionadas_ids": concepto.publicaciones_relacionadas_ids,
    }

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
        raise

# --------------------------------------------------------------------
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
            logging.info(f"✅ Concepto actualizado desde dict: {concepto_dict.get('nombre')}")
    except Exception as e:
        logging.error(f"❌ Error actualizando concepto desde dict: {e}")
        raise


# --------------------------------------------------------------------
def add_descripcion_llm(concepto: ConceptoInteres):
    try:
        descripcion = generar_descripcion_concepto(concepto.nombre)
        concepto.descripcion = descripcion
        update_concepto(concepto)
        return descripcion
    except Exception as e:
        logging.error(f"Error generando descripción con LLM: {e}")
        return None


# --------------------------------------------------------------------
def add_keywords_llm(concepto: ConceptoInteres):
    try:
        # Generar y guardar keywords como objetos con _id
        keywords = generar_keywords_descriptivos(concepto.descripcion)

        # Asignar solo los ObjectId de las keywords al concepto
        concepto.keywords_ids = [ObjectId(k._id) for k in keywords if k._id]

        # Guardar el concepto actualizado en Mongo
        update_concepto(concepto)

        return keywords

    except Exception as e:
        logging.error(f"❌ Error generando keywords con LLM: {e}")
        return []

# --------------------------------------------------------------------
def add_keywords_aceptadas(concepto: ConceptoInteres):
    try:
        # Sobrescribe completamente las keywords anteriores (ya deben estar en concepto.keywords_ids)
        concepto.keywords_ids = list(set(concepto.keywords_ids))  # elimina duplicados por si acaso

        update_concepto(concepto)

        return jsonify(concepto.to_dict()), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Error al guardar keywords en el concepto: {str(e)}"}), 500

# --------------------------------------------------------------------


def get_conceptos_by_area_id(area_oid):
    area = get_collection('areas_de_trabajo').find_one({'_id': area_oid})
    if not area:
        return []

    conceptos_oids = area.get('conceptos_interes_ids', [])
    conceptos = []

    for concepto_oid in conceptos_oids:
        concepto = get_collection('conceptos_interes').find_one({'_id': concepto_oid})
        if concepto:
            # Convertimos los ObjectId a string antes de devolver
            concepto["_id"] = str(concepto["_id"])
            concepto["keywords_ids"] = [str(k) for k in concepto.get("keywords_ids", [])]
            concepto["publicaciones_relacionadas_ids"] = [str(p) for p in concepto.get("publicaciones_relacionadas_ids", [])]
            conceptos.append(concepto)

    return conceptos


# --------------------------------------------------------------------

def serialize_concepto(doc):
    doc["_id"] = str(doc["_id"])
    if "area_id" in doc:
        doc["area_id"] = str(doc["area_id"])
    return doc
