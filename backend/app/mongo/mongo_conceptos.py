import os
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
from ..models.concepto_interes import ConceptoInteres
from ..llm.llm_utils import generar_descripcion_concepto, generar_keywords_descriptivos

# Conexión a MongoDB
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["baseDatosScrauron"]
coleccion = db["conceptos_interes"]

def get_conceptos():
    conceptos_raw = list(coleccion.find())
    conceptos = []
    for c in conceptos_raw:
        c["_id"] = str(c["_id"])
        c["publicaciones_relacionadas_ids"] = [str(pid) for pid in c.get("publicaciones_relacionadas_ids", [])]
        conceptos.append(c)
    return conceptos

def get_conceptos_dict():
    conceptos_raw = list(coleccion.find())
    conceptos = []
    for c in conceptos_raw:
        c.setdefault("publicaciones_relacionadas_ids", [])
        if not isinstance(c["publicaciones_relacionadas_ids"], list):
            c["publicaciones_relacionadas_ids"] = []
        conceptos.append(c)
    return conceptos

def get_concepto_by_id(concepto_id: str):
    if not ObjectId.is_valid(concepto_id):
        return None
    raw = coleccion.find_one({"_id": ObjectId(concepto_id)})
    if raw:
        return ConceptoInteres.from_dict(raw)
    return None

def get_conceptos_ids(ids):
    return list(coleccion.find({"_id": {"$in": ids}}))

def create_concepto(concepto):
    data = concepto.to_dict()
    if "_id" in data and data["_id"] is None:
        del data["_id"]
    insert_result = coleccion.insert_one(data)
    return insert_result

def delete_concepto(concepto_id):
    if not ObjectId.is_valid(concepto_id):
        raise ValueError("ID no válido")
    result = coleccion.delete_one({"_id": ObjectId(concepto_id)})
    return result.deleted_count

def update_concepto(concepto: ConceptoInteres):
    data = concepto.to_dict()
    concepto_id = data.pop("_id", None)

    if not concepto_id:
        raise ValueError("El concepto no tiene _id. No se puede actualizar.")

    try:
        result = coleccion.update_one(
            {"_id": ObjectId(concepto_id)},
            {"$set": data}
        )
        if result.matched_count == 0:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ No se encontró el concepto con _id: {concepto_id}")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Concepto actualizado correctamente: {concepto.nombre}")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error actualizando el concepto: {e}")

def update_concepto_dict(concepto_dict: dict):
    concepto_id = concepto_dict.get("_id")
    if not concepto_id:
        raise ValueError("El concepto no tiene _id. No se puede actualizar.")

    try:
        result = coleccion.update_one(
            {"_id": ObjectId(concepto_id)},
            {"$set": concepto_dict}
        )
        if result.matched_count == 0:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ No se encontró el concepto con _id: {concepto_id}")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Concepto actualizado correctamente: {concepto_dict.get('nombre')}")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error actualizando el concepto: {e}")

def add_descripcion_llm(concepto: ConceptoInteres):
    descripcion = generar_descripcion_concepto(concepto.nombre)
    concepto.descripcion = descripcion
    update_concepto(concepto)
    return descripcion

def add_keywords_llm(concepto: ConceptoInteres):
    keywords = generar_keywords_descriptivos(concepto.descripcion)
    concepto.keywords = keywords
    update_concepto(concepto)
    return keywords