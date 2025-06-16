# mongo_conceptos.py
# Este módulo gestiona el acceso, creación y actualización de los documentos
# del tipo "ConceptoInteres" en MongoDB. Además, integra funciones de LLM
# para generar descripciones y keywords de forma automática.

from flask import jsonify
import logging
from datetime import datetime
from bson import ObjectId
import time
from pymongo.errors import AutoReconnect, NetworkTimeout, ConnectionFailure

from .mongo_utils import get_collection
from ..models.concepto_interes import ConceptoInteres
from ..service.llm.llm_utils import generar_descripcion_concepto, generar_keywords_descriptivos

# --------------------------------------------------------------------
# Recupera todos los conceptos desde la colección "conceptos_interes"
def get_conceptos():
    try:
        conceptos_raw = get_collection("conceptos_interes").find()
        conceptos = []
        for c in conceptos_raw:
            c["_id"] = str(c["_id"])
            c["keywords_ids"] = [str(kid) for kid in c.get("keywords_ids", [])]
            conceptos.append(c)
        return conceptos
    except Exception as e:
        logging.error(f"Error al recuperar conceptos: {e}")
        return []

# --------------------------------------------------------------------
# Devuelve los documentos de conceptos en bruto sin formatear
def get_conceptos_dict():
    try:
        conceptos_raw = list(get_collection("conceptos_interes").find())
        conceptos = []
        for c in conceptos_raw:
            conceptos.append(c)
        return conceptos
    except Exception as e:
        logging.error(f"Error al recuperar conceptos en bruto: {e}")
        return []

# --------------------------------------------------------------------
# Busca un concepto por su ID
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
# Devuelve una lista de conceptos a partir de una lista de IDs
def get_conceptos_ids(ids):
    try:
        return list(get_collection("conceptos_interes").find({"_id": {"$in": ids}}))
    except Exception as e:
        logging.error(f"Error al obtener conceptos por IDs: {e}")
        return []

# --------------------------------------------------------------------
# Inserta un nuevo concepto en la base de datos
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
# Elimina un concepto por su ID
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
# Actualiza un concepto dado un objeto ConceptoInteres
def update_concepto(concepto: ConceptoInteres):
    concepto_id = concepto._id
    if not concepto_id:
        raise ValueError("El concepto no tiene _id. No se puede actualizar.")

    data = {
        "_id": ObjectId(concepto._id),
        "nombre": concepto.nombre,
        "descripcion": concepto.descripcion,
        "keywords_ids": concepto.keywords_ids,
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
# Actualiza un concepto a partir de un diccionario, con reintentos si hay errores de red
def update_concepto_dict(concepto_dict: dict, max_retries=3, backoff_base=2):
    concepto_id = concepto_dict.get("_id")
    if not concepto_id:
        raise ValueError("El concepto no tiene _id. No se puede actualizar.")

    if "nombre" not in concepto_dict or not concepto_dict["nombre"]:
        logging.warning("El concepto no tiene nombre definido. Revisión necesaria.")

    attempt = 0
    while attempt < max_retries:
        try:
            result = get_collection("conceptos_interes").update_one(
                {"_id": ObjectId(concepto_id)},
                {"$set": concepto_dict}
            )
            if result.matched_count == 0:
                logging.warning(f"⚠️ No se encontró el concepto con _id: {concepto_id}")
            else:
                logging.info(f"✅ Concepto actualizado desde dict: {concepto_dict.get('nombre')}")
            return result
        except (AutoReconnect, NetworkTimeout, ConnectionFailure) as conn_err:
            wait = backoff_base ** attempt
            logging.warning(f"🔄 Reintentando actualización por fallo de red ({conn_err}), intento {attempt+1}/{max_retries}... Esperando {wait}s")
            time.sleep(wait)
            attempt += 1
        except Exception as e:
            logging.error(f"❌ Error inesperado actualizando concepto desde dict: {e}")
            raise

    logging.error(f"❌ Fallo persistente al actualizar concepto tras {max_retries} intentos.")
    raise ConnectionError("No se pudo actualizar el concepto por errores de conexión.")

# --------------------------------------------------------------------
# Genera y añade una descripción automática con LLM al concepto
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
# Genera keywords automáticas con LLM y las añade al concepto
def add_keywords_llm(concepto: ConceptoInteres):
    try:
        keywords = generar_keywords_descriptivos(concepto.descripcion)
        concepto.keywords_ids = [ObjectId(k._id) for k in keywords if k._id]
        update_concepto(concepto)
        return keywords
    except Exception as e:
        logging.error(f"❌ Error generando keywords con LLM: {e}")
        return []

# --------------------------------------------------------------------
# Añade keywords aceptadas manualmente al concepto y actualiza
def add_keywords_aceptadas(concepto: ConceptoInteres):
    try:
        concepto.keywords_ids = list(set(concepto.keywords_ids))
        update_concepto(concepto)
        return jsonify(concepto.to_dict()), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Error al guardar keywords en el concepto: {str(e)}"}), 500

# --------------------------------------------------------------------
# Recupera los conceptos de una determinada área por su ID
def get_conceptos_by_area_id(area_oid):
    area = get_collection('areas_de_trabajo').find_one({'_id': area_oid})
    if not area:
        return []

    conceptos_oids = area.get('conceptos_interes_ids', [])
    if not isinstance(conceptos_oids, list):
        return []

    conceptos = []
    for concepto_oid in conceptos_oids:
        concepto = get_collection('conceptos_interes').find_one({'_id': concepto_oid})
        if concepto:
            concepto["_id"] = str(concepto["_id"])
            concepto["keywords_ids"] = [str(k) for k in concepto.get("keywords_ids", [])]
            conceptos.append(concepto)

    return conceptos

# --------------------------------------------------------------------
# Serializa un documento de concepto para que sea compatible con JSON
def serialize_concepto(doc):
    doc["_id"] = str(doc["_id"])
    if "area_id" in doc:
        doc["area_id"] = str(doc["area_id"])
    return doc