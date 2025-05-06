import os
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
from ..models.concepto_interes import ConceptoInteres

# Conexión directa a MongoDB
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["baseDatosScrauron"]
coleccion = db["conceptos_interes"]

def get_conceptos():
    conceptos = list(coleccion.find())
    for c in conceptos:
        c["_id"] = str(c["_id"])
    return conceptos

def get_concepto_by_id(concepto_id: str):
    if not ObjectId.is_valid(concepto_id):
        return None
    raw = coleccion.find_one({"_id": ObjectId(concepto_id)})
    if raw:
        raw["_id"] = str(raw["_id"])
        return ConceptoInteres.from_dict(raw)  # ✅ no devuelvas raw directamente
    return None


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
            print(f"⚠️ No se encontró el concepto con _id: {concepto_id}")
        else:
            print(f"✅ Concepto actualizado correctamente: {concepto.nombre}")
    except Exception as e:
        print(f"❌ Error actualizando el concepto: {e}")
