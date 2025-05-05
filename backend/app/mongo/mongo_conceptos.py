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

def get_concepto_by_id(concepto_id):
    if not ObjectId.is_valid(concepto_id):
        raise ValueError("ID no válido")
    concepto = coleccion.find_one({"_id": ObjectId(concepto_id)})
    if concepto:
        concepto["_id"] = str(concepto["_id"])
    return concepto

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

def update_concepto(concepto_id, data):
    if not ObjectId.is_valid(concepto_id):
        raise ValueError("ID no válido")
    if "_id" in data:
        del data["_id"]
    result = coleccion.update_one({"_id": ObjectId(concepto_id)}, {"$set": data})
    if result.matched_count == 0:
        return None
    updated = coleccion.find_one({"_id": ObjectId(concepto_id)})
    updated["_id"] = str(updated["_id"])
    return updated
